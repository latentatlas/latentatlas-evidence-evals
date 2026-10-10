#!/usr/bin/env python3
"""Build the public figure/table pack for the action-time publication package.

The pack adds publication-safe support artifacts for fail-closed required-field
validation, synthetic negative-control assertions, and local baseline replay. It
supports a bounded technical report, not independent benchmark evidence.
"""

from __future__ import annotations

import argparse
import csv
import html
import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


DEFAULT_PUBLICATION_SUMMARY = Path(
    "outputs/latentatlas/action_time_p0_publication_package_v3/publication_package_summary.json"
)
DEFAULT_CLOSURE_SUMMARY = Path(
    "outputs/latentatlas/concurrency_closure_pack_20260718/concurrency_closure_summary.json"
)
DEFAULT_REQUIRED_FIELDS_VALIDATION = Path(
    "outputs/latentatlas/concurrency_closure_pack_20260718/concurrency_required_fields_validation.csv"
)
DEFAULT_NEGATIVE_CONTROL_ASSERTIONS = Path(
    "outputs/latentatlas/concurrency_closure_pack_20260718/concurrency_negative_control_assertions.csv"
)
DEFAULT_BASELINE_REPLAY = Path(
    "outputs/latentatlas/concurrency_closure_pack_20260718/concurrency_baseline_replay.csv"
)
DEFAULT_FAMILY_OVERLAP_MATRIX = Path(
    "outputs/latentatlas/concurrency_closure_pack_20260718/concurrency_family_overlap_matrix.csv"
)
DEFAULT_OUT_DIR = Path("outputs/latentatlas/action_time_p0_figure_table_pack_v3")

SCHEMA_VERSION = "latentatlas_action_time_p0_figure_table_pack_v3"

FAMILY_PUBLIC_NAMES = {
    "stale_read": "Stale evidence read",
    "identity_time_split": "Identity and timing split",
    "authority_expiry": "Expired or missing authority",
    "materialization_race": "State changed before execution",
    "visibility_truth_confusion": "Visibility mistaken for truth",
    "context_contamination": "Outside-context contamination",
}

VALUE_PUBLIC_NAMES = {
    "correct_block": "packet-supported block",
    "false_block": "packet-unsupported block",
    "needs_more_evidence": "insufficient evidence",
    "fail_closed_until_schema_upgrade": "fail closed until schema upgrade",
    "missing_exact": "missing exact field",
    "missing_in_p0_freeze": "missing in high-priority freeze",
    "available_exact": "available exact field",
    "derivable_from_masked_field": "derivable from masked field",
    "missing_until_response": "missing until response",
    "do_not_detect": "do not detect",
}


def utc_now() -> str:
    return datetime.now(UTC).isoformat()


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def write_csv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fieldnames})


def pct(value: Any) -> str:
    try:
        return f"{float(value) * 100:.1f}%"
    except (TypeError, ValueError):
        return str(value)


def metric_by_id(metrics: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    return {row.get("metric_id", ""): row for row in metrics}


def public_text(value: Any) -> str:
    text = str(value)
    replacements = {
        "P0": "high-priority",
        "PDP": "product-detail-page",
        "correct-block": "packet-supported block",
        "false-block": "packet-unsupported block",
        "needs-more-evidence": "insufficient evidence",
        "correct_block": "packet-supported block",
        "false_block": "packet-unsupported block",
        "needs_more_evidence": "insufficient evidence",
        "packet-visible evidence": "evidence visible in the review packet",
        "Packet-visible evidence": "Evidence visible in the review packet",
        "packet-visible": "review-packet",
        "Packet-visible": "Review-packet",
        "identity-guard": "identity guard",
    }
    for needle, replacement in replacements.items():
        text = text.replace(needle, replacement)
    return text


def public_family_name(family_id: Any) -> str:
    return FAMILY_PUBLIC_NAMES.get(str(family_id), public_text(str(family_id).replace("_", " ")).title())


def public_relationship(value: Any) -> str:
    relationships = {
        "same_set": "same set",
        "subset_of_family_b": "inside Family B",
        "superset_of_family_b": "contains Family B",
        "partial_overlap": "partial overlap",
        "disjoint": "no overlap",
    }
    return relationships.get(str(value), public_text(str(value).replace("_", " ")))


def public_field_name(value: Any) -> str:
    text = str(value)
    if text in VALUE_PUBLIC_NAMES:
        return VALUE_PUBLIC_NAMES[text]
    return public_text(text.replace("_", " "))


def public_fixture_name(value: Any) -> str:
    text = str(value)
    for family_id, family_name in FAMILY_PUBLIC_NAMES.items():
        text = text.replace(family_id, family_name.lower())
    return public_field_name(text)


def public_table_rows(rows: list[dict[str, str]], row_type: str) -> list[dict[str, str]]:
    public_rows: list[dict[str, str]] = []
    if row_type == "required_fields":
        for row in rows:
            public_rows.append(
                {
                    "family": public_family_name(row.get("family_id", "")),
                    "required_field": public_field_name(row.get("required_field", "")),
                    "reviewed_rows_checked": row.get("current_p0_rows_checked", ""),
                    "present_or_derivable_count": row.get("present_or_derivable_count", ""),
                    "missing_count": row.get("missing_count", ""),
                    "coverage_rate": row.get("coverage_rate", ""),
                    "field_status": public_field_name(row.get("field_status", "")),
                    "validation_state": public_field_name(row.get("validation_state", "")),
                }
            )
    elif row_type == "assertions":
        for row in rows:
            public_rows.append(
                {
                    "fixture": public_fixture_name(row.get("fixture_id", "")),
                    "family": public_family_name(row.get("family_id", "")),
                    "fixture_type": public_field_name(row.get("fixture_type", "")),
                    "expected_result": public_fixture_name(row.get("expected_result", "")),
                    "assertion_state": public_field_name(row.get("assertion_state", "")),
                    "claim_boundary": public_text(row.get("claim_boundary", "")),
                }
            )
    elif row_type == "replay":
        for row in rows:
            public_rows.append(
                {
                    "family": public_family_name(row.get("family_id", "")),
                    "rows_replayed": row.get("rows_replayed", ""),
                    "decision_time_only_block_count": row.get("decision_time_only_block_count", ""),
                    "action_time_policy_block_count": row.get("action_time_policy_block_count", ""),
                    "action_time_policy_hold_or_revalidate_count": row.get(
                        "action_time_policy_hold_or_revalidate_count", ""
                    ),
                    "local_avoidable_overblock_or_hold_rate": row.get("local_avoidable_overblock_or_hold_rate", ""),
                    "claim_boundary": public_text(row.get("claim_boundary", "")),
                }
            )
    elif row_type == "overlap":
        for row in rows:
            public_rows.append(
                {
                    "family_a": public_family_name(row.get("family_a", "")),
                    "family_b": public_family_name(row.get("family_b", "")),
                    "family_a_count": row.get("family_a_count", ""),
                    "family_b_count": row.get("family_b_count", ""),
                    "overlap_count": row.get("overlap_count", ""),
                    "overlap_rate_of_a": row.get("overlap_rate_of_a", ""),
                    "overlap_rate_of_b": row.get("overlap_rate_of_b", ""),
                    "relationship": public_relationship(row.get("relationship", "")),
                    "claim_boundary": public_text(row.get("claim_boundary", "")),
                }
            )
    return public_rows


def blocked_summary(reason: str, paths: dict[str, Path], inputs: dict[str, Path]) -> dict[str, Any]:
    return {
        "generated_at_utc": utc_now(),
        "mode": "latentatlas_action_time_p0_figure_table_pack",
        "schema_version": SCHEMA_VERSION,
        "status": "blocked",
        "failure_reasons": [reason],
        "figure_count": 0,
        "table_count": 0,
        "level4_probability_claim_allowed": False,
        "contains_customer_data": False,
        "contains_personal_data": False,
        "raw_source_rows_read": False,
        "external_calls_used_by_builder": False,
        "production_truth_mutation": False,
        "inputs": {key: str(value) for key, value in inputs.items()},
        "outputs": {key: str(value) for key, value in paths.items()},
    }


def build_claim_ladder_rows(publication: dict[str, Any]) -> list[dict[str, str]]:
    return [
        {
            "claim_tier": "Conceptual boundary",
            "claim_state": "conceptual contribution",
            "allowed_public_claim": "Evidence can be true but still fail action-time authority.",
            "blocked_public_claim": "All AI execution failures are concurrency failures.",
            "evidence_needed_to_upgrade": "None for conceptual framing; keep scope bounded.",
        },
        {
            "claim_tier": "Protocol proposal",
            "claim_state": "protocol proposal",
            "allowed_public_claim": "Authority leases define actor, action, target, evidence, permission, policy, expiry, and impact checks.",
            "blocked_public_claim": "The protocol is production-validated across deployments.",
            "evidence_needed_to_upgrade": "Independent implementation and production-side audit logs.",
        },
        {
            "claim_tier": "Frozen-set descriptive evidence",
            "claim_state": "frozen-set descriptive evidence",
            "allowed_public_claim": f"{publication.get('denominators', {}).get('frozen_reviewed_rows', '')} masked high-priority cases were reviewed with explicit labels.",
            "blocked_public_claim": "The frozen-set rates generalize to a broader population.",
            "evidence_needed_to_upgrade": "Larger stratified sample with independent review.",
        },
        {
            "claim_tier": "Closure checks plus local proxy replay",
            "claim_state": "closure artifact plus local proxy replay",
            "allowed_public_claim": "Fail-closed fields, negative controls, and local replay improve auditability.",
            "blocked_public_claim": "Live causal reduction in unsupported blocks.",
            "evidence_needed_to_upgrade": "Prospective benchmark or production A/B evidence.",
        },
        {
            "claim_tier": "Independent benchmark validation",
            "claim_state": "not claimed",
            "allowed_public_claim": "Not claimed.",
            "blocked_public_claim": "Population-level probability, reviewer reliability, or benchmark effectiveness.",
            "evidence_needed_to_upgrade": "Independent reviewers, power plan, stratified holdout, and reproducible benchmark run.",
        },
    ]


def build_outcome_rows(publication: dict[str, Any]) -> list[dict[str, Any]]:
    denominators = publication.get("denominators", {})
    outcomes = publication.get("outcome_counts", {})
    metrics = metric_by_id(publication.get("metrics", []))
    return [
        {
            "measure": "High-priority rows",
            "count": denominators.get("p0_rows", ""),
            "denominator": "",
            "rate": "",
            "claim_boundary": "Freeze size only.",
        },
        {
            "measure": "Reviewed review-eligible high-priority rows",
            "count": denominators.get("frozen_reviewed_rows", ""),
            "denominator": denominators.get("outcome_ready_p0_rows", ""),
            "rate": pct(metrics.get("review_completion", {}).get("rate", "")),
            "claim_boundary": "Freeze completeness, not population coverage.",
        },
        {
            "measure": "Packet-supported block",
            "count": outcomes.get("correct_block", ""),
            "denominator": denominators.get("frozen_reviewed_rows", ""),
            "rate": pct(metrics.get("correct_block_all_reviewed", {}).get("rate", "")),
            "claim_boundary": "Frozen reviewed set only; packet evidence supported the conservative block.",
        },
        {
            "measure": "Packet-unsupported block",
            "count": outcomes.get("false_block", ""),
            "denominator": denominators.get("frozen_reviewed_rows", ""),
            "rate": pct(metrics.get("false_block_all_reviewed", {}).get("rate", "")),
            "claim_boundary": "Frozen reviewed set only; not model-wide false-positive rate and not direct proof the real-world action was safe.",
        },
        {
            "measure": "Insufficient evidence",
            "count": outcomes.get("needs_more_evidence", ""),
            "denominator": denominators.get("frozen_reviewed_rows", ""),
            "rate": pct(metrics.get("needs_more_evidence_all_reviewed", {}).get("rate", "")),
            "claim_boundary": "Evidence insufficiency, not success or failure.",
        },
    ]


def build_family_rows(publication: dict[str, Any]) -> list[dict[str, Any]]:
    rows = []
    for family in publication.get("concurrent_evidence_failure", {}).get("failure_families", []):
        rows.append(
            {
                "family": public_family_name(family.get("family_id", "")),
                "definition": public_text(family.get("definition", "")),
                "local_numerator": family.get("numerator", ""),
                "local_denominator": family.get("denominator", ""),
                "local_rate": pct(family.get("local_rate", "")) if family.get("local_rate", "") != "" else "",
                "claim_boundary": public_text(family.get("claim_boundary", "")),
            }
        )
    return rows


def trim_rows(rows: list[dict[str, str]], fields: list[str]) -> list[dict[str, str]]:
    return [{field: row.get(field, "") for field in fields} for row in rows]


def build_figures() -> dict[str, str]:
    return {
        "figure_1_authority_lease_timeline.mmd": """flowchart LR
    A["Decision evidence"] --> B["Authority lease"]
    B --> C["Action-time lease check"]
    C --> D["Execute"]
    C --> E["Revalidate"]
    C --> F["Block"]
    C --> G["Human review"]
""",
        "figure_2_evidence_boundary_ladder.mmd": """flowchart TB
    A["Observation"] --> B["Evidence packet"]
    B --> C["Decision evidence"]
    C --> D["Action authority"]
    D --> E["Execution"]
    C -. "not automatically" .-> E
""",
        "figure_3_concurrent_evidence_validity_gate.mmd": """flowchart LR
    A["Identity"] --> G["Lease gate"]
    B["Freshness"] --> G
    C["Permission"] --> G
    D["Visibility"] --> G
    E["Materialization"] --> G
    F["Impact ceiling"] --> G
    G --> H["action permitted / hold / block"]
""",
        "figure_4_decision_time_vs_action_time_replay.mmd": """flowchart LR
    A["Frozen reviewed rows"] --> B["Decision-time-only policy"]
    B --> C["Block from prior signal"]
    A --> D["Action-time authority policy"]
    D --> E["Block packet-supported blocks only"]
    D --> F["Hold or revalidate unsupported or insufficient-evidence cases"]
    F --> G["Local avoidable overblock/hold delta"]
""",
        "figure_5_fail_closed_measurement_gate.mmd": """flowchart TB
    A["Required authority field"] --> B{"Present or derivable?"}
    B -- "yes" --> C["Eligible for family-specific test"]
    B -- "no" --> D["fail closed until schema upgrade"]
    C --> E{"Negative control assertion passes?"}
    E -- "yes" --> F["bounded measurement artifact"]
    E -- "no" --> G["blocked: detector not publish-safe"]
""",
    }


def figure_specs() -> list[dict[str, Any]]:
    return [
        {
            "slug": "figure_1_authority_lease_timeline",
            "title": "Authority Lease Timeline",
            "caption": "A prior decision becomes action-valid only if the authority lease still holds at execution time.",
            "nodes": [
                "Decision evidence",
                "Authority lease",
                "Action-time lease check",
                "Execute",
                "Revalidate",
                "Block",
                "Human review",
            ],
        },
        {
            "slug": "figure_2_evidence_boundary_ladder",
            "title": "Evidence Boundary Ladder",
            "caption": "Observation, evidence, decision, action authority, and execution are separate boundary states.",
            "nodes": [
                "Observation",
                "Evidence packet",
                "Decision evidence",
                "Action authority",
                "Execution",
            ],
        },
        {
            "slug": "figure_3_concurrent_evidence_validity_gate",
            "title": "Concurrent Evidence Validity Gate",
            "caption": "Identity, freshness, permission, visibility, materialization, and impact ceiling must remain aligned.",
            "nodes": [
                "Identity",
                "Freshness",
                "Permission",
                "Visibility",
                "Materialization",
                "Impact ceiling",
                "Lease gate",
            ],
        },
        {
            "slug": "figure_4_decision_time_vs_action_time_replay",
            "title": "Decision-Time vs Action-Time Replay",
            "caption": "The local proxy replay compares a decision-time-only policy with an action-time authority policy.",
            "nodes": [
                "Frozen reviewed rows",
                "Decision-time-only policy",
                "Block from prior signal",
                "Action-time authority policy",
                "Block packet-supported blocks only",
                "Hold or revalidate unsupported or insufficient-evidence cases",
            ],
        },
        {
            "slug": "figure_5_fail_closed_measurement_gate",
            "title": "Fail-Closed Measurement Gate",
            "caption": "Missing required fields fail closed until schema upgrade; negative controls guard detector promotion.",
            "nodes": [
                "Required field",
                "Present or derivable?",
                "Eligible for family test",
                "Fail closed",
                "Negative control passes?",
                "Bounded artifact",
                "Blocked detector",
            ],
        },
    ]


def wrap_svg_text(text: str, max_chars: int = 24) -> list[str]:
    words = text.split()
    lines: list[str] = []
    current: list[str] = []
    for word in words:
        candidate = " ".join([*current, word])
        if len(candidate) > max_chars and current:
            lines.append(" ".join(current))
            current = [word]
        else:
            current.append(word)
    if current:
        lines.append(" ".join(current))
    return lines[:3]


def build_svg(spec: dict[str, Any]) -> str:
    width = 980
    height = 360
    nodes = spec["nodes"]
    box_w = 180
    box_h = 78
    gap = 32
    x0 = 44
    y = 150
    title = html.escape(spec["title"])
    caption = html.escape(spec["caption"])
    node_blocks = []
    edge_blocks = []
    for idx, node in enumerate(nodes):
        x = x0 + (idx % 5) * (box_w + gap)
        row = idx // 5
        yy = y + row * 105
        fill = "#eef4f9" if idx % 2 == 0 else "#f7f3df"
        node_blocks.append(
            f'<rect x="{x}" y="{yy}" width="{box_w}" height="{box_h}" rx="7" fill="{fill}" stroke="#9aa8b5" />'
        )
        for line_idx, line in enumerate(wrap_svg_text(node)):
            tx = x + box_w / 2
            ty = yy + 30 + line_idx * 17
            node_blocks.append(
                f'<text x="{tx}" y="{ty}" text-anchor="middle" font-size="14" fill="#17202a">{html.escape(line)}</text>'
            )
        if idx > 0 and idx % 5 != 0:
            prev_x = x - gap
            edge_blocks.append(
                f'<line x1="{prev_x}" y1="{yy + box_h / 2}" x2="{x}" y2="{yy + box_h / 2}" stroke="#52616f" stroke-width="2" marker-end="url(#arrow)" />'
            )
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-label="{title}">
  <defs>
    <marker id="arrow" markerWidth="10" markerHeight="10" refX="9" refY="3" orient="auto" markerUnits="strokeWidth">
      <path d="M0,0 L0,6 L9,3 z" fill="#52616f" />
    </marker>
  </defs>
  <rect x="0" y="0" width="{width}" height="{height}" fill="#fbfaf7" />
  <text x="44" y="42" font-size="24" font-family="Arial, Helvetica, sans-serif" font-weight="700" fill="#17202a">{title}</text>
  <text x="44" y="72" font-size="14" font-family="Arial, Helvetica, sans-serif" fill="#5d6670">{caption}</text>
  <g font-family="Arial, Helvetica, sans-serif">
    {''.join(edge_blocks)}
    {''.join(node_blocks)}
  </g>
</svg>
"""


def render_png_if_available(svg_path: Path, png_path: Path, spec: dict[str, Any]) -> bool:
    try:
        from PIL import Image, ImageDraw, ImageFont
    except ImportError:
        return False

    width, height = 980, 360
    image = Image.new("RGB", (width, height), "#fbfaf7")
    draw = ImageDraw.Draw(image)
    try:
        title_font = ImageFont.truetype("Arial.ttf", 24)
        body_font = ImageFont.truetype("Arial.ttf", 14)
    except OSError:
        title_font = ImageFont.load_default()
        body_font = ImageFont.load_default()
    draw.text((44, 28), spec["title"], fill="#17202a", font=title_font)
    draw.text((44, 60), spec["caption"], fill="#5d6670", font=body_font)

    box_w, box_h, gap, x0, y = 180, 78, 32, 44, 150
    for idx, node in enumerate(spec["nodes"]):
        x = x0 + (idx % 5) * (box_w + gap)
        row = idx // 5
        yy = y + row * 105
        fill = "#eef4f9" if idx % 2 == 0 else "#f7f3df"
        if idx > 0 and idx % 5 != 0:
            draw.line((x - gap, yy + box_h / 2, x, yy + box_h / 2), fill="#52616f", width=2)
            draw.polygon(
                [
                    (x - 8, yy + box_h / 2 - 4),
                    (x, yy + box_h / 2),
                    (x - 8, yy + box_h / 2 + 4),
                ],
                fill="#52616f",
            )
        draw.rounded_rectangle((x, yy, x + box_w, yy + box_h), radius=7, fill=fill, outline="#9aa8b5", width=1)
        for line_idx, line in enumerate(wrap_svg_text(node)):
            bbox = draw.textbbox((0, 0), line, font=body_font)
            tx = x + (box_w - (bbox[2] - bbox[0])) / 2
            ty = yy + 24 + line_idx * 17
            draw.text((tx, ty), line, fill="#17202a", font=body_font)
    png_path.parent.mkdir(parents=True, exist_ok=True)
    image.save(png_path)
    return svg_path.exists() and png_path.exists()


def build_figure_captions() -> list[dict[str, str]]:
    return [
        {
            "figure_id": spec["slug"],
            "title": spec["title"],
            "caption": spec["caption"],
            "claim_boundary": "Conceptual or local-proxy illustration only; not independent benchmark evidence.",
        }
        for spec in figure_specs()
    ]


def build_report(summary: dict[str, Any]) -> str:
    if summary["status"] != "pass":
        return "\n".join(["# Action-Time Figure/Table Pack", "", "Status: blocked", *summary.get("failure_reasons", [])])

    return f"""# Action-Time Figure/Table Pack

Status: pass

This pack supports the current public technical report. It adds publication-safe
visuals and tables for fail-closed measurement, synthetic negative controls,
and local decision-time vs action-time replay.

## Counts

- Figures: {summary["figure_count"]}
- Tables: {summary["table_count"]}
- Evidence maturity: bounded descriptive evidence with local proxy replay
- Population-level validation claimed: False

## Added Support

- Decision-time vs action-time replay figure
- Fail-closed measurement-gate figure
- rendered SVG figure assets and captions
- Required-field validation table
- Negative-control assertion table
- Local baseline replay table
- Failure-family overlap matrix

## Boundary

These artifacts support a bounded technical report. They do not establish
population rates, reviewer reliability, production performance, or independent
benchmark evidence.
"""


def run(
    publication_summary_path: Path = DEFAULT_PUBLICATION_SUMMARY,
    closure_summary_path: Path = DEFAULT_CLOSURE_SUMMARY,
    required_fields_validation_path: Path = DEFAULT_REQUIRED_FIELDS_VALIDATION,
    negative_control_assertions_path: Path = DEFAULT_NEGATIVE_CONTROL_ASSERTIONS,
    baseline_replay_path: Path = DEFAULT_BASELINE_REPLAY,
    out_dir: Path = DEFAULT_OUT_DIR,
    family_overlap_matrix_path: Path = DEFAULT_FAMILY_OVERLAP_MATRIX,
) -> dict[str, Any]:
    inputs = {
        "publication_summary": publication_summary_path,
        "closure_summary": closure_summary_path,
        "required_fields_validation": required_fields_validation_path,
        "negative_control_assertions": negative_control_assertions_path,
        "baseline_replay": baseline_replay_path,
        "family_overlap_matrix": family_overlap_matrix_path,
    }
    paths = {
        "summary": out_dir / "action_time_p0_figure_table_pack_summary.json",
        "manifest": out_dir / "action_time_p0_figure_table_pack_manifest.json",
        "report": out_dir / "action_time_p0_figure_table_pack.md",
    }

    publication = read_json(publication_summary_path)
    closure = read_json(closure_summary_path)
    required_fields = read_csv(required_fields_validation_path)
    assertions = read_csv(negative_control_assertions_path)
    replay = read_csv(baseline_replay_path)
    overlap = read_csv(family_overlap_matrix_path)

    if publication.get("status") != "pass":
        summary = blocked_summary("publication package is not pass", paths, inputs)
    elif closure.get("status") != "pass":
        summary = blocked_summary("concurrency closure package is not pass", paths, inputs)
    elif publication.get("level4_probability_claim_allowed") is not False:
        summary = blocked_summary("publication package does not keep independent benchmark / population-level boundary blocked", paths, inputs)
    elif closure.get("negative_assertion_fail_count") != 0:
        summary = blocked_summary("negative control assertions include failures", paths, inputs)
    elif any(row.get("assertion_state") != "pass" for row in assertions):
        summary = blocked_summary("negative control assertion table includes non-pass rows", paths, inputs)
    else:
        figure_paths = {}
        for filename, body in build_figures().items():
            path = out_dir / filename
            write_text(path, body)
            figure_paths[filename.removesuffix(".mmd")] = path
        rendered_figure_paths = {}
        rendered_png_paths = {}
        for spec in figure_specs():
            svg_path = out_dir / f"{spec['slug']}.svg"
            write_text(svg_path, build_svg(spec))
            rendered_figure_paths[f"{spec['slug']}_svg"] = svg_path
            png_path = out_dir / f"{spec['slug']}.png"
            if render_png_if_available(svg_path, png_path, spec):
                rendered_png_paths[f"{spec['slug']}_png"] = png_path

        table_1 = build_claim_ladder_rows(publication)
        table_2 = build_outcome_rows(publication)
        table_3 = build_family_rows(publication)
        figure_captions = build_figure_captions()
        table_4_fields = [
            "family",
            "required_field",
            "reviewed_rows_checked",
            "present_or_derivable_count",
            "missing_count",
            "coverage_rate",
            "field_status",
            "validation_state",
        ]
        table_5_fields = [
            "fixture",
            "family",
            "fixture_type",
            "expected_result",
            "assertion_state",
            "claim_boundary",
        ]
        table_6_fields = [
            "family",
            "rows_replayed",
            "decision_time_only_block_count",
            "action_time_policy_block_count",
            "action_time_policy_hold_or_revalidate_count",
            "local_avoidable_overblock_or_hold_rate",
            "claim_boundary",
        ]
        table_7_fields = [
            "family_a",
            "family_b",
            "family_a_count",
            "family_b_count",
            "overlap_count",
            "overlap_rate_of_a",
            "overlap_rate_of_b",
            "relationship",
            "claim_boundary",
        ]
        table_8 = [
            {
                "gate": "Second reviewer",
                "current_state": "not available",
                "publication_effect": "No reviewer reliability claim.",
                "next_upgrade": "Independent reviewer with packet-grounded labels.",
            },
            {
                "gate": "Independent benchmark or population validation",
                "current_state": "not claimed",
                "publication_effect": "No population or benchmark-effectiveness claim.",
                "next_upgrade": "Power plan, stratified holdout, and reproducible run.",
            },
            {
                "gate": "Production validation",
                "current_state": "not used",
                "publication_effect": "No customer or production truth mutation.",
                "next_upgrade": "Governed deployment evidence, if future scope requires it.",
            },
        ]

        table_specs: dict[str, tuple[list[dict[str, Any]], list[str]]] = {
            "table_1_claim_ladder.csv": (
                table_1,
                [
                    "claim_tier",
                    "claim_state",
                    "allowed_public_claim",
                    "blocked_public_claim",
                    "evidence_needed_to_upgrade",
                ],
            ),
            "table_2_frozen_p0_outcomes.csv": (
                table_2,
                ["measure", "count", "denominator", "rate", "claim_boundary"],
            ),
            "table_3_concurrent_failure_families.csv": (
                table_3,
                ["family", "definition", "local_numerator", "local_denominator", "local_rate", "claim_boundary"],
            ),
            "table_4_required_fields_validation.csv": (
                public_table_rows(required_fields, "required_fields"),
                table_4_fields,
            ),
            "table_5_negative_control_assertions.csv": (
                public_table_rows(assertions, "assertions"),
                table_5_fields,
            ),
            "table_6_local_baseline_replay.csv": (
                public_table_rows(replay, "replay"),
                table_6_fields,
            ),
            "table_7_family_overlap_matrix.csv": (
                public_table_rows(overlap, "overlap"),
                table_7_fields,
            ),
            "table_8_preprint_readiness_gates.csv": (
                table_8,
                ["gate", "current_state", "publication_effect", "next_upgrade"],
            ),
        }

        table_paths = {}
        table_row_counts = {}
        for filename, (rows, fieldnames) in table_specs.items():
            path = out_dir / filename
            write_csv(path, rows, fieldnames)
            table_paths[filename.removesuffix(".csv")] = path
            table_row_counts[filename.removesuffix(".csv")] = len(rows)

        paths.update(figure_paths)
        paths.update(rendered_figure_paths)
        paths.update(rendered_png_paths)
        paths.update(table_paths)
        caption_csv = out_dir / "figure_captions.csv"
        public_captions = [
            {
                "figure": row["title"],
                "title": row["title"],
                "caption": row["caption"],
                "claim_boundary": row["claim_boundary"],
            }
            for row in figure_captions
        ]
        write_csv(caption_csv, public_captions, ["figure", "title", "caption", "claim_boundary"])
        paths["figure_captions_csv"] = caption_csv
        caption_index = out_dir / "figure_captions.md"
        caption_lines = ["# Figure Captions", ""]
        for row in figure_captions:
            caption_lines.extend(
                [
                    f"## {row['title']}",
                    "",
                    row["caption"],
                    "",
                    f"Boundary: {row['claim_boundary']}",
                    "",
                ]
            )
        write_text(caption_index, "\n".join(caption_lines))
        paths["figure_captions_markdown"] = caption_index
        summary = {
            "generated_at_utc": utc_now(),
            "mode": "latentatlas_action_time_p0_figure_table_pack",
            "schema_version": SCHEMA_VERSION,
            "status": "pass",
            "research_level": publication.get("research_level"),
            "publication_readiness": publication.get("publication_readiness"),
            "figure_count": len(figure_paths),
            "rendered_figure_count": len(rendered_figure_paths),
            "rendered_png_count": len(rendered_png_paths),
            "caption_count": len(figure_captions),
            "table_count": len(table_paths),
            "table_row_counts": table_row_counts,
            "v3_quality_upgrade": {
                "fail_closed_required_fields": closure.get("required_field_fail_closed_rows", 0),
                "negative_fixture_count": closure.get("negative_fixture_count", 0),
                "negative_assertion_fail_count": closure.get("negative_assertion_fail_count", 0),
                "baseline_replay_family_count": closure.get("baseline_replay_family_count", 0),
            },
            "level4_probability_claim_allowed": False,
            "contains_customer_data": False,
            "contains_personal_data": False,
            "raw_source_rows_read": False,
            "external_calls_used_by_builder": False,
            "production_truth_mutation": False,
            "inputs": {key: str(value) for key, value in inputs.items()},
            "outputs": {key: str(value) for key, value in paths.items()},
        }

    write_text(paths["report"], build_report(summary))
    write_json(paths["summary"], summary)
    manifest = {
        "schema_version": SCHEMA_VERSION,
        "generated_at_utc": utc_now(),
        "status": summary["status"],
        "outputs": summary["outputs"],
        "inputs": summary["inputs"],
    }
    write_json(paths["manifest"], manifest)
    return summary


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--publication-summary", type=Path, default=DEFAULT_PUBLICATION_SUMMARY)
    parser.add_argument("--closure-summary", type=Path, default=DEFAULT_CLOSURE_SUMMARY)
    parser.add_argument("--required-fields-validation", type=Path, default=DEFAULT_REQUIRED_FIELDS_VALIDATION)
    parser.add_argument("--negative-control-assertions", type=Path, default=DEFAULT_NEGATIVE_CONTROL_ASSERTIONS)
    parser.add_argument("--baseline-replay", type=Path, default=DEFAULT_BASELINE_REPLAY)
    parser.add_argument("--family-overlap-matrix", type=Path, default=DEFAULT_FAMILY_OVERLAP_MATRIX)
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT_DIR)
    args = parser.parse_args()
    summary = run(
        args.publication_summary,
        args.closure_summary,
        args.required_fields_validation,
        args.negative_control_assertions,
        args.baseline_replay,
        args.out_dir,
        args.family_overlap_matrix,
    )
    print(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if summary["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
