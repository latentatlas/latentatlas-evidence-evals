"""Fresh-process offline matrix. No live credentials or publication switch."""
import argparse
from datetime import datetime, timezone
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys

from contract import ROOT, LAB, SOURCE, CORE, PREDECESSOR, HELPERS, SEEDS, ARMS, ORDERS, PROFILES, SCHEDULES, ADMISSION_PHASES, matrix, condition_name, plan, require
from audit import audit, sha

sys.path.append(str(ROOT.parent/"scope_transition_v01"))
spec = importlib.util.spec_from_file_location("source_prior_runner", ROOT.parent/"scope_transition_v01/run_rehearsal.py")
prior = importlib.util.module_from_spec(spec); spec.loader.exec_module(prior)


def save(path, value):
    with path.open("x") as f: json.dump(value, f, ensure_ascii=False, indent=2)


def protected(exclude):
    frozen = json.loads((PREDECESSOR/"local-matrix-v01/PLAN.json").read_text())["protected_hashes"]
    paths = [LAB/p for p in frozen]
    paths += [p for p in SOURCE.rglob("*") if p.is_file() and "__pycache__" not in p.parts]
    paths += [p for d in (PREDECESSOR, HELPERS) for p in d.rglob("*") if p.is_file() and "__pycache__" not in p.parts]
    for folder in ROOT.glob("local-*"):
        if folder != exclude:
            paths += [p for p in folder.rglob("*") if p.is_file() and "__pycache__" not in p.parts]
    require(all(sha(LAB/p) == h for p, h in frozen.items()), "Previous protected evidence changed")
    return {str(p.relative_to(LAB)): sha(p) for p in sorted(set(paths))}


def run(out, conditions):
    require(out.parent == ROOT and out.name.startswith("local-"), "Use a new local-* child directory")
    runtime = prior.verify_runtime()
    upstream = json.loads((LAB/"application_probe/UPSTREAM_MANIFEST.json").read_text())
    require(all(sha(LAB/"application_probe/upstream"/p) == h for p, h in upstream["sha256"].items()), "Upstream snapshot changed")
    before = protected(out)
    paths = list(ROOT.glob("*.py"))+list(ROOT.glob("*.md"))
    sources = {p.name: sha(p) for p in paths}
    out.mkdir(exist_ok=False); (out/"instrument").mkdir()
    for p in paths: shutil.copy2(p, out/"instrument"/p.name)
    save(out/"PLAN.json", {"frozen_at_utc": datetime.now(timezone.utc).isoformat(), "contract": plan(),
         "conditions": conditions, "source_hashes": sources, "protected_hashes": before,
         "runtime": runtime, "upstream_revision": upstream["revision"]})
    results = {}
    for c in conditions:
        name = condition_name(c); folder = out/name
        folder.mkdir(); (folder/"files").mkdir()
        cmd = [sys.executable, "-I", str(ROOT/"child_native.py"), str(folder), str(c["seed"]), c["arm"], c["order"], c["profile"], c["schedule"], c["admission_phase"]]
        env = prior.environment(); save(folder/"manifest.json", {"command": cmd, "environment": env})
        try:
            p = subprocess.run(cmd, cwd=folder, env=env, capture_output=True, text=True, timeout=270)
            process = {"exit_code": p.returncode, "timed_out": False, "child_reaped": True}
            stdout, stderr = p.stdout, p.stderr
        except subprocess.TimeoutExpired as exc:
            process = {"exit_code": None, "timed_out": True, "child_reaped": True}
            stdout = exc.stdout.decode() if isinstance(exc.stdout, bytes) else exc.stdout or ""
            stderr = exc.stderr.decode() if isinstance(exc.stderr, bytes) else exc.stderr or ""
        save(folder/"PROCESS.json", process)
        for filename, text in (("stdout.txt", stdout), ("stderr.txt", stderr)):
            with (folder/filename).open("x") as f: f.write(text)
        try: report = audit(folder)
        except Exception as exc: report = {"evidence_valid": False, "error_type": type(exc).__name__, "error": str(exc)}
        save(folder/"AUDIT.json", report); results[name] = report
        outcome = report.get("outcomes", {})
        print(json.dumps({"condition": name, "process": process,
                          "evidence_valid": report["evidence_valid"], "scoring_status": report.get("scoring_status"),
                          "error": report.get("error", report.get("scoring_error")),
                          "old_origin_post_policy_effects": outcome.get("old_origin_post_policy_effects"),
                          "checkpoint_content": outcome.get("queue", {}).get("checkpoint_content_status"),
                          "O_target_content": outcome.get("roles", {}).get("O", {}).get("target_artifact", {}).get("content", {}).get("class")}), flush=True)
        if not report["evidence_valid"] or report.get("scoring_status") != "complete": break
    summary = {"conditions": results, "all_planned_conditions_executed": len(results) == len(conditions),
               "all_evidence_valid": all(x["evidence_valid"] for x in results.values()),
               "all_scoring_complete": all(x.get("scoring_status") == "complete" for x in results.values()),
               "protected_files_unchanged": before == protected(out), "protected_file_count": len(before),
               "sources_unchanged": all(sha(ROOT/p) == h for p, h in sources.items()),
               "actual_provider_calls": 0, "external_slack_deliveries": 0, "automatic_retry": False,
               "catalogue_cases_certified": 0}
    save(out/"COMPLETION.json", summary)
    return 0 if all(summary[k] for k in ("all_planned_conditions_executed", "all_evidence_valid", "all_scoring_complete", "protected_files_unchanged", "sources_unchanged")) else 1


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--out", type=Path)
    p.add_argument("--seed", type=int, choices=SEEDS)
    p.add_argument("--arm", choices=ARMS)
    p.add_argument("--order", choices=ORDERS)
    p.add_argument("--profile", choices=PROFILES)
    p.add_argument("--schedule", choices=SCHEDULES)
    p.add_argument("--admission-phase", choices=ADMISSION_PHASES)
    args = p.parse_args()
    conditions = [c for c in matrix() if all(getattr(args, k) is None or c[k] == getattr(args, k) for k in ("seed", "arm", "order", "profile", "schedule", "admission_phase"))]
    require(conditions, "No declared conditions selected")
    if args.out is None: print(json.dumps(plan(), indent=2))
    else: raise SystemExit(run(args.out.resolve(), conditions))
