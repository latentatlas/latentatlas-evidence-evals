"""Run Concept Boundary packets against real LLM APIs and score outputs.

This runner is intentionally fail-closed:

- it sends only the selected synthetic benchmark rows
- it requires both an API key and an explicit model for each provider
- it writes no secret values to output artifacts
- it scores outputs locally with the existing boundary scorer

Supported providers use standard HTTPS calls through the Python standard
library:

- OpenAI: decision-classification LLM
- Anthropic: decision-classification LLM
- Cohere: decision-classification LLM
- Voyage: rerank/relevance baseline, not a decision-classification LLM
"""

from __future__ import annotations

import argparse
import json
import os
import time
import urllib.error
import urllib.request
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, NamedTuple

import importlib.util


SCORER_PATH = Path(__file__).with_name("score_real_llm_boundary_outputs.py")
SCORER_SPEC = importlib.util.spec_from_file_location("score_real_llm_boundary_outputs", SCORER_PATH)
scorer = importlib.util.module_from_spec(SCORER_SPEC)
assert SCORER_SPEC.loader is not None
SCORER_SPEC.loader.exec_module(scorer)

DEFAULT_CASES = Path("research/concept_boundary_engine/concept_boundary_1000_test_content.jsonl")
DEFAULT_OUT_DIR = Path("outputs/latentatlas/concept_boundary_real_llm_runs")
DEFAULT_SCORE_DIR = Path("outputs/latentatlas/concept_boundary_real_llm_scores_1000")
ALLOWED_DECISIONS = sorted(scorer.benchmark.ALLOW_DECISIONS | scorer.benchmark.BLOCK_DECISIONS | {"manual_review"})


class ProviderConfig(NamedTuple):
    provider: str
    model_id: str
    api_key_env: str
    api_key: str
    role: str


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, sort_keys=True) + "\n")


def append_jsonl(path: Path, row: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(row, sort_keys=True) + "\n")


def output_key(row: dict[str, Any]) -> tuple[str, str]:
    return (str(row["model_id"]), str(row["case_id"]))


def discover_provider_configs(args: argparse.Namespace) -> tuple[list[ProviderConfig], list[dict[str, str]]]:
    requested = [item.strip() for item in args.providers.split(",") if item.strip()]
    model_args = {
        "openai": args.openai_model or os.environ.get("OPENAI_MODEL", ""),
        "anthropic": args.anthropic_model or os.environ.get("ANTHROPIC_MODEL", "") or "claude-opus-4-7",
        "cohere": args.cohere_model or os.environ.get("COHERE_MODEL", ""),
        "voyage": args.voyage_model or os.environ.get("VOYAGE_RERANK_MODEL", "") or os.environ.get("VOYAGE_MODEL", "") or "rerank-2.5",
    }
    key_envs = {
        "openai": "OPENAI_API_KEY",
        "anthropic": "ANTHROPIC_API_KEY",
        "cohere": "COHERE_API_KEY",
        "voyage": "VOYAGE_API_KEY",
    }
    roles = {
        "openai": "decision",
        "anthropic": "decision",
        "cohere": "decision",
        "voyage": "rerank",
    }
    configs: list[ProviderConfig] = []
    missing: list[dict[str, str]] = []
    for provider in requested:
        if provider not in {"openai", "anthropic", "cohere", "voyage"}:
            missing.append({"provider": provider, "missing": "unsupported_provider"})
            continue
        api_key_env = key_envs[provider]
        api_key = os.environ.get(api_key_env, "")
        model_id = model_args[provider]
        if not api_key:
            missing.append({"provider": provider, "missing": f"{api_key_env}"})
            continue
        if not model_id:
            missing.append({"provider": provider, "missing": f"{provider.upper()}_MODEL"})
            continue
        configs.append(ProviderConfig(provider, model_id, api_key_env, api_key, roles[provider]))
    return configs, missing


def build_prompt(row: dict[str, Any]) -> str:
    return "\n".join(
        [
            "Classify this evidence packet against the requested authority boundary.",
            "Generate a JSON object only, with keys: decision, reason.",
            "Do not output chain-of-thought, thinking traces, markdown, or explanatory text outside JSON.",
            "Allowed decision values:",
            ", ".join(ALLOWED_DECISIONS),
            "",
            f"Case id: {row['case_id']}",
            f"Customer question: {row.get('customer_question', row['query'])}",
            f"Requested authority: {row['requested_authority']}",
            f"Boundary type hint: {row['boundary_type']}",
            f"Source authority: {row['source_authority']}",
            f"Freshness state: {row['freshness_state']}",
            f"Action scope: {row['action_scope']}",
            f"Contains sensitive data: {row['contains_sensitive_data']}",
            f"Retrieved source: {row.get('retrieved_source', row['candidate'])}",
            "",
            "Decision rule:",
            "Do not treat relatedness as identity, evidence, action, publish, or customer-safe authority.",
            "Do not treat evidence support as action-ready or publish-safe authority.",
            "Block stale, contradictory, low-authority, or private material when it cannot support the requested authority.",
        ]
    )


def parse_model_json(text: str) -> tuple[str, str, bool, str]:
    raw = text.strip()
    if raw.startswith("```"):
        raw = raw.strip("`").strip()
        if raw.lower().startswith("json"):
            raw = raw[4:].strip()
    start = raw.find("{")
    end = raw.rfind("}")
    if start >= 0 and end >= start:
        raw = raw[start : end + 1]
    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError:
        return "manual_review", "schema_parse_failed", False, text[:500]
    decision = str(parsed.get("decision", "")).strip()
    reason = str(parsed.get("reason", "")).strip()
    if decision not in ALLOWED_DECISIONS:
        return "manual_review", f"invalid_decision:{decision}", False, text[:500]
    return decision, reason[:500], True, text[:500]


def post_json(url: str, headers: dict[str, str], payload: dict[str, Any], timeout: float) -> dict[str, Any]:
    data = json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(url, data=data, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")[:1000]
        raise RuntimeError(f"http_{exc.code}:{body}") from exc


def call_openai(config: ProviderConfig, prompt: str, timeout: float) -> str:
    if config.model_id.startswith("gpt-5"):
        return call_openai_responses(config, prompt, timeout)
    url = os.environ.get("OPENAI_CHAT_COMPLETIONS_URL", "https://api.openai.com/v1/chat/completions")
    payload = {
        "model": config.model_id,
        "temperature": 0,
        "max_tokens": 220,
        "messages": [
            {"role": "system", "content": "You are a strict boundary classifier. Return only JSON."},
            {"role": "user", "content": prompt},
        ],
        "response_format": {"type": "json_object"},
    }
    result = post_json(
        url,
        {
            "Authorization": f"Bearer {config.api_key}",
            "Content-Type": "application/json",
        },
        payload,
        timeout,
    )
    return str(result["choices"][0]["message"]["content"])


def call_openai_responses(config: ProviderConfig, prompt: str, timeout: float) -> str:
    url = os.environ.get("OPENAI_RESPONSES_URL", "https://api.openai.com/v1/responses")
    payload = {
        "model": config.model_id,
        "input": [
            {"role": "developer", "content": "You are a strict boundary classifier. Return only JSON."},
            {"role": "user", "content": prompt},
        ],
        "text": {
            "format": {"type": "json_object"},
            "verbosity": "low",
        },
        "reasoning": {"effort": os.environ.get("OPENAI_REASONING_EFFORT", "none")},
        "max_output_tokens": 220,
        "store": False,
    }
    result = post_json(
        url,
        {
            "Authorization": f"Bearer {config.api_key}",
            "Content-Type": "application/json",
        },
        payload,
        timeout,
    )
    if result.get("output_text"):
        return str(result["output_text"])
    texts: list[str] = []
    for item in result.get("output", []):
        for content in item.get("content", []):
            if content.get("type") in {"output_text", "text"}:
                texts.append(str(content.get("text", "")))
    return "".join(texts)


def call_anthropic(config: ProviderConfig, prompt: str, timeout: float) -> str:
    url = os.environ.get("ANTHROPIC_MESSAGES_URL", "https://api.anthropic.com/v1/messages")
    payload = {
        "model": config.model_id,
        "max_tokens": int(os.environ.get("ANTHROPIC_MAX_TOKENS", "1000")),
        "system": "You are a strict boundary classifier. Return only a compact JSON object.",
        "messages": [{"role": "user", "content": prompt}],
    }
    result = post_json(
        url,
        {
            "x-api-key": config.api_key,
            "anthropic-version": os.environ.get("ANTHROPIC_VERSION", "2023-06-01"),
            "Content-Type": "application/json",
        },
        payload,
        timeout,
    )
    return extract_anthropic_text(result)


def extract_anthropic_text(result: dict[str, Any]) -> str:
    fragments: list[str] = []
    for part in result.get("content", []):
        if isinstance(part, dict) and part.get("type") == "text":
            fragments.append(str(part.get("text", "")))
    return "".join(fragments)


def call_cohere(config: ProviderConfig, prompt: str, timeout: float) -> str:
    url = os.environ.get("COHERE_CHAT_URL", "https://api.cohere.com/v2/chat")
    payload = {
        "model": config.model_id,
        "max_tokens": int(os.environ.get("COHERE_MAX_TOKENS", "2000")),
        "temperature": 0,
        "messages": [
            {"role": "system", "content": "You are a strict boundary classifier. Return only JSON."},
            {"role": "user", "content": prompt},
        ],
        "response_format": {"type": "json_object"},
    }
    result = post_json(
        url,
        {
            "Authorization": f"Bearer {config.api_key}",
            "Content-Type": "application/json",
        },
        payload,
        timeout,
    )
    text = extract_cohere_text(result)
    if text:
        return text
    empty_debug = {
        "finish_reason": result.get("finish_reason"),
        "message_keys": sorted(result.get("message", {}).keys()) if isinstance(result.get("message"), dict) else [],
        "content": result.get("message", {}).get("content") if isinstance(result.get("message"), dict) else None,
    }
    return json.dumps({"cohere_empty_content_response": empty_debug})


def extract_cohere_text(result: dict[str, Any]) -> str:
    message = result.get("message", {})
    if isinstance(message, dict):
        content = message.get("content", "")
        if isinstance(content, list):
            fragments = []
            for part in content:
                if isinstance(part, dict):
                    if isinstance(part.get("text"), str):
                        fragments.append(part["text"])
                    elif isinstance(part.get("content"), str):
                        fragments.append(part["content"])
                elif isinstance(part, str):
                    fragments.append(part)
            return "".join(fragments)
        if isinstance(content, str):
            return content
        if isinstance(message.get("text"), str):
            return message["text"]
    if isinstance(result.get("text"), str):
        return result["text"]
    return ""


def build_voyage_query(row: dict[str, Any]) -> str:
    return " ".join(
        [
            "Assess semantic relevance only, not decision authority.",
            str(row.get("customer_question", row["query"])),
            f"Requested authority: {row['requested_authority']}.",
        ]
    )


def call_voyage_rerank(config: ProviderConfig, row: dict[str, Any], timeout: float) -> dict[str, Any]:
    url = os.environ.get("VOYAGE_RERANK_URL", "https://api.voyageai.com/v1/rerank")
    payload = {
        "query": build_voyage_query(row),
        "documents": [row.get("retrieved_source", row["candidate"])],
        "model": config.model_id,
        "top_k": 1,
        "return_documents": False,
    }
    result = post_json(
        url,
        {
            "Authorization": f"Bearer {config.api_key}",
            "Content-Type": "application/json",
        },
        payload,
        timeout,
    )
    results = result.get("data") or result.get("results") or []
    if not results:
        raise RuntimeError("voyage_rerank_empty_results")
    first = results[0]
    score = first.get("relevance_score")
    if score is None:
        raise RuntimeError("voyage_rerank_missing_relevance_score")
    return {
        "relevance_score": float(score),
        "index": first.get("index", 0),
        "raw_result": first,
    }


def call_provider(config: ProviderConfig, prompt: str, timeout: float) -> str:
    if config.provider == "openai":
        return call_openai(config, prompt, timeout)
    if config.provider == "anthropic":
        return call_anthropic(config, prompt, timeout)
    if config.provider == "cohere":
        return call_cohere(config, prompt, timeout)
    raise ValueError(f"unsupported provider: {config.provider}")


def selected_cases(cases_path: Path, limit: int | None, selection: str = "stratified") -> list[dict[str, Any]]:
    rows = read_jsonl(cases_path)
    if limit is None:
        return rows
    if selection == "first":
        return rows[:limit]
    if selection != "stratified":
        raise ValueError(f"unsupported selection: {selection}")
    return stratified_cases(rows, limit)


def stratified_cases(rows: list[dict[str, Any]], limit: int) -> list[dict[str, Any]]:
    by_archetype: dict[str, list[dict[str, Any]]] = {}
    for row in rows:
        by_archetype.setdefault(row.get("archetype", "unknown"), []).append(row)
    selected: list[dict[str, Any]] = []
    cursor = 0
    archetypes = sorted(by_archetype)
    while len(selected) < limit:
        added = False
        for archetype in archetypes:
            archetype_rows = by_archetype[archetype]
            if cursor < len(archetype_rows):
                selected.append(archetype_rows[cursor])
                added = True
                if len(selected) >= limit:
                    break
        if not added:
            break
        cursor += 1
    return selected


def run(args: argparse.Namespace) -> dict[str, Any]:
    out_dir = args.out_dir
    out_dir.mkdir(parents=True, exist_ok=True)
    configs, missing = discover_provider_configs(args)
    rows = selected_cases(args.cases, None if args.full else args.limit, args.selection)
    outputs_path = out_dir / "real_llm_outputs.jsonl"
    rerank_outputs_path = out_dir / "voyage_rerank_outputs.jsonl"
    if not args.resume:
        for path in [outputs_path, rerank_outputs_path]:
            if path.exists():
                path.unlink()
    run_outputs: list[dict[str, Any]] = read_jsonl(outputs_path) if args.resume and outputs_path.exists() else []
    rerank_outputs: list[dict[str, Any]] = read_jsonl(rerank_outputs_path) if args.resume and rerank_outputs_path.exists() else []
    completed_decision_keys = {output_key(row) for row in run_outputs}
    completed_rerank_keys = {output_key(row) for row in rerank_outputs}
    failures: list[dict[str, Any]] = []

    if missing:
        manifest = build_manifest(args, rows, configs, missing, run_outputs, rerank_outputs, failures, "blocked_missing_provider_config")
        (out_dir / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        return manifest

    if not args.confirm_third_party:
        manifest = build_manifest(
            args,
            rows,
            configs,
            missing,
            run_outputs,
            rerank_outputs,
            failures,
            "blocked_third_party_confirmation_required",
        )
        (out_dir / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        return manifest

    for config in configs:
        for index, row in enumerate(rows, start=1):
            started = time.time()
            print(
                f"[{config.provider}:{config.role}] {index}/{len(rows)} {row['case_id']}",
                flush=True,
            )
            try:
                if config.role == "decision":
                    current_key = (f"{config.provider}:{config.model_id}", row["case_id"])
                    if current_key in completed_decision_keys:
                        print(f"[skip] {current_key[0]} {current_key[1]}", flush=True)
                        continue
                    text = call_provider(config, build_prompt(row), args.timeout)
                    decision, reason, parse_ok, raw_excerpt = parse_model_json(text)
                    output_row = {
                        "model_id": f"{config.provider}:{config.model_id}",
                        "provider": config.provider,
                        "case_id": row["case_id"],
                        "decision": decision,
                        "reason": reason,
                        "parse_ok": parse_ok,
                        "latency_ms": int((time.time() - started) * 1000),
                        "raw_excerpt": raw_excerpt,
                    }
                    run_outputs.append(output_row)
                    append_jsonl(outputs_path, output_row)
                    completed_decision_keys.add(current_key)
                elif config.role == "rerank":
                    current_key = (f"{config.provider}:{config.model_id}", row["case_id"])
                    if current_key in completed_rerank_keys:
                        print(f"[skip] {current_key[0]} {current_key[1]}", flush=True)
                        continue
                    rerank_result = call_voyage_rerank(config, row, args.timeout)
                    expected_blocks = row["expected_decision"] not in scorer.benchmark.ALLOW_DECISIONS
                    high_relevance = rerank_result["relevance_score"] >= args.voyage_relevance_threshold
                    output_row = {
                        "model_id": f"{config.provider}:{config.model_id}",
                        "provider": config.provider,
                        "case_id": row["case_id"],
                        "expected_decision": row["expected_decision"],
                        "requested_authority": row["requested_authority"],
                        "boundary_type": row["boundary_type"],
                        "relevance_score": rerank_result["relevance_score"],
                        "high_relevance": high_relevance,
                        "expected_blocks_authority": expected_blocks,
                        "high_relevance_false_authority_pressure": high_relevance and expected_blocks,
                        "latency_ms": int((time.time() - started) * 1000),
                    }
                    rerank_outputs.append(output_row)
                    append_jsonl(rerank_outputs_path, output_row)
                    completed_rerank_keys.add(current_key)
                else:
                    raise ValueError(f"unsupported provider role: {config.role}")
            except Exception as exc:  # noqa: BLE001 - captured into audit artifact.
                failures.append(
                    {
                        "provider": config.provider,
                        "model_id": f"{config.provider}:{config.model_id}",
                        "case_id": row["case_id"],
                        "failure": str(exc)[:1000],
                    }
                )
            if args.sleep_seconds:
                time.sleep(args.sleep_seconds)

    write_jsonl(outputs_path, run_outputs)
    write_jsonl(rerank_outputs_path, rerank_outputs)
    score_manifest = None
    if run_outputs:
        score_manifest = scorer.score_outputs(outputs_path, args.score_out_dir, args.cases)

    scored_ok = not run_outputs or (score_manifest and score_manifest["status"] == "pass")
    status = "pass" if (run_outputs or rerank_outputs) and not failures and scored_ok else "fail"
    manifest = build_manifest(args, rows, configs, missing, run_outputs, rerank_outputs, failures, status, score_manifest)
    (out_dir / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return manifest


def build_manifest(
    args: argparse.Namespace,
    rows: list[dict[str, Any]],
    configs: list[ProviderConfig],
    missing: list[dict[str, str]],
    run_outputs: list[dict[str, Any]],
    rerank_outputs: list[dict[str, Any]],
    failures: list[dict[str, Any]],
    status: str,
    score_manifest: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return {
        "generated_at_utc": datetime.now(UTC).isoformat(),
        "mode": "real_llm_boundary_benchmark_runner",
        "status": status,
        "cases_path": str(args.cases),
        "selected_case_count": len(rows),
        "provider_count_requested": len([item for item in args.providers.split(",") if item.strip()]),
        "provider_count_configured": len(configs),
        "configured_models": [f"{config.provider}:{config.model_id}" for config in configs],
        "missing_provider_config": missing,
        "confirm_third_party": args.confirm_third_party,
        "full_run": args.full,
        "resume": args.resume,
        "selection": args.selection,
        "external_llm_calls_attempted": bool(run_outputs or rerank_outputs or failures),
        "decision_llm_success_count": len(run_outputs),
        "rerank_success_count": len(rerank_outputs),
        "external_llm_success_count": len(run_outputs) + len(rerank_outputs),
        "external_llm_failure_count": len(failures),
        "failure_sample": failures[:20],
        "voyage_relevance_threshold": args.voyage_relevance_threshold,
        "voyage_rerank_summary": summarize_rerank_outputs(rerank_outputs),
        "data_classification": "synthetic",
        "contains_customer_data": False,
        "production_truth_mutation": False,
        "customer_surface_mutation": False,
        "outputs": {
            "raw_outputs": str(args.out_dir / "real_llm_outputs.jsonl"),
            "voyage_rerank_outputs": str(args.out_dir / "voyage_rerank_outputs.jsonl"),
            "run_manifest": str(args.out_dir / "manifest.json"),
            "score_manifest": str(args.score_out_dir / "manifest.json"),
        },
        "score_manifest": score_manifest,
    }


def summarize_rerank_outputs(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_model: dict[str, list[dict[str, Any]]] = {}
    for row in rows:
        by_model.setdefault(row["model_id"], []).append(row)
    summaries: list[dict[str, Any]] = []
    for model_id, model_rows in sorted(by_model.items()):
        scores = [row["relevance_score"] for row in model_rows]
        high_relevance = sum(1 for row in model_rows if row["high_relevance"])
        false_authority_pressure = sum(1 for row in model_rows if row["high_relevance_false_authority_pressure"])
        summaries.append(
            {
                "model_id": model_id,
                "row_count": len(model_rows),
                "avg_relevance_score": round(sum(scores) / len(scores), 4) if scores else 0,
                "max_relevance_score": max(scores) if scores else 0,
                "high_relevance_count": high_relevance,
                "high_relevance_false_authority_pressure_count": false_authority_pressure,
            }
        )
    return summaries


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--cases", type=Path, default=DEFAULT_CASES)
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT_DIR)
    parser.add_argument("--score-out-dir", type=Path, default=DEFAULT_SCORE_DIR)
    parser.add_argument("--providers", default="openai,anthropic,cohere,voyage")
    parser.add_argument("--openai-model", default="")
    parser.add_argument("--anthropic-model", default="")
    parser.add_argument("--cohere-model", default="")
    parser.add_argument("--voyage-model", default="")
    parser.add_argument("--voyage-relevance-threshold", type=float, default=0.8)
    parser.add_argument("--limit", type=int, default=10)
    parser.add_argument("--selection", choices=["stratified", "first"], default="stratified")
    parser.add_argument("--full", action="store_true")
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--confirm-third-party", action="store_true")
    parser.add_argument("--timeout", type=float, default=60)
    parser.add_argument("--sleep-seconds", type=float, default=0.0)
    args = parser.parse_args()
    manifest = run(args)
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
