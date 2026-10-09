"""Build the selected public sharing copy from retained local research records.

Never imports a runner, connects an account, or calls a provider. Original records
are read only. Run with --suite /path/to/stop_scope_suite; original records are
needed for exporting, but not for verify_snapshot.py in the published package.
"""
from __future__ import annotations

import argparse
from collections import Counter
import gzip
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
NATIVE = {
    "confirmation": "feasibility/role_queue_v05",
    "cancellation": "feasibility/f07_cancel_preflight_v01",
}
BATCH = "feasibility/development_batch_v01/live-2026-10-06-v01"
LIVE = {
    "initial-healthy-s17": "feasibility/live_exploration_v01/healthy-live-2026-10-06-v02",
    "initial-stop-s17": "feasibility/live_exploration_v01/stop-live-2026-10-06-v01",
    **{n: BATCH + "/" + n for n in (
        "01-healthy-s41", "02-stop-s41", "03-stop-s17", "04-healthy-s17",
        "05-stop-s17", "06-stop-s41")},
}
OMIT_EVENT_CONTENT = {"account_preflight", "batch_slot_claimed"}
OMIT_KEYS = {"raw_b64", "encrypted_content", "attribution"}


def digest(data):
    return hashlib.sha256(data).hexdigest()


def encoded(value):
    return (json.dumps(value, indent=2, ensure_ascii=False) + "\n").encode()


def safe_relative(value):
    p = Path(value)
    if p.is_absolute() or ".." in p.parts:
        raise ValueError("Unsafe export path")
    return p


class Exporter:
    def __init__(self, suite, out, refresh=False):
        self.suite = suite.resolve()
        self.lab = self.suite.parent
        self.out = out.resolve()
        self.refresh = refresh
        self.sources = {}
        self.exports = []
        self.omissions = Counter()

    def read(self, path):
        path = path.resolve()
        rel = path.relative_to(self.lab).as_posix()
        raw = path.read_bytes()
        if rel in self.sources and self.sources[rel] != digest(raw):
            raise ValueError("Source changed while exporting: " + rel)
        self.sources[rel] = digest(raw)
        return raw

    def clean(self, value):
        if isinstance(value, dict):
            if value.get("kind") in OMIT_EVENT_CONTENT:
                self.omissions[value["kind"]] += 1
                return {**{k: value[k] for k in ("seq", "monotonic_ns", "kind")},
                        "sharing_omission": "account_or_authorization_metadata"}
            if value.get("type") == "reasoning":
                self.omissions["reasoning_item"] += 1
                return {"type": "reasoning_omitted_in_sharing_copy",
                        "source_item_sha256": digest(encoded(value))}
            result = {}
            for k, v in value.items():
                if k in OMIT_KEYS:
                    self.omissions[k] += 1
                    continue
                result[k] = self.clean(v)
            return result
        if isinstance(value, list):
            return [self.clean(v) for v in value]
        if isinstance(value, str):
            value = value.replace(str(self.lab), "/workspace/stop-scope")
            if "/Users/" in value or "/private/var/" in value:
                raise ValueError("Unmapped personal path in selected source")
        return value

    def put(self, rel, raw, *, source=None, transform="generated"):
        path = self.out / safe_relative(rel)
        path.parent.mkdir(parents=True, exist_ok=True)
        if path.exists() and path.read_bytes() != raw and not self.refresh:
            raise ValueError("Refusing to overwrite differing export: " + rel)
        path.write_bytes(raw)
        item = {"path": rel, "sha256": digest(raw), "bytes": len(raw), "transform": transform}
        if source:
            source = source.resolve()
            item.update(source=source.relative_to(self.lab).as_posix(),
                        source_sha256=self.sources[source.relative_to(self.lab).as_posix()])
        self.exports.append(item)

    def copy(self, src, rel, *, json_file=False):
        raw = self.read(src)
        if json_file:
            public = encoded(self.clean(json.loads(raw)))
        else:
            public = self.clean(raw.decode()).encode()
        self.put(rel, public, source=src, transform="byte_copy" if public == raw else "privacy_sharing_copy")
        return public

    def events(self, src, rel):
        raw = self.read(src)
        rows = [self.clean(json.loads(line)) for line in raw.splitlines()]
        public = b"".join((json.dumps(r, ensure_ascii=False) + "\n").encode() for r in rows)
        self.put(rel, gzip.compress(public, mtime=0), source=src,
                 transform="privacy_sharing_copy_then_deterministic_gzip")
        self.exports[-1]["uncompressed_sha256"] = digest(public)
        self.exports[-1]["event_count"] = len(rows)
        return public

    def native(self, name, source):
        base = self.suite / source
        matrix = base / "local-matrix-v01"
        plan_path = matrix / "PLAN.json"
        plan = self.clean(json.loads(self.read(plan_path)))
        protected = plan.pop("protected_hashes", {})
        plan["sharing_note"] = "Protection inventory omitted; original source digest is in EXPORT_MANIFEST.json."
        plan["protected_inventory_count"] = len(protected)
        dest = f"data/{name}/local-matrix-v01"
        self.put(dest + "/PLAN.json", encoded(plan), source=plan_path, transform="privacy_and_protection_inventory_omission")
        completion_path = matrix / "COMPLETION.json"
        completion = self.clean(json.loads(self.read(completion_path)))
        for condition, stored in completion["conditions"].items():
            raw = self.events(matrix / condition / "events.jsonl", dest + "/" + condition + "/events.jsonl.gz")
            stored["events_sha256"] = digest(raw)
            for p in sorted((matrix / condition / "files").rglob("*")):
                if p.is_file():
                    self.copy(p, dest + "/" + condition + "/" + p.relative_to(matrix / condition).as_posix())
        self.put(dest + "/COMPLETION.json", encoded(completion), source=completion_path,
                 transform="privacy_copy_with_export_event_hashes")
        for p in sorted((matrix / "instrument").iterdir()):
            if p.suffix == ".py":
                self.copy(p, f"source/{name}/" + p.name)
        self.copy(matrix / "instrument/README.md", f"source/{name}/FROZEN_PROTOCOL.md")
        cross = "crosscheck_confirmation.py" if name == "confirmation" else "crosscheck_cancel.py"
        current = self.read(base / cross)
        frozen = self.read(matrix / "instrument" / cross)
        if current != frozen:
            raise ValueError("Crosscheck differs from frozen source")
        report = "RAW_CONFIRMATION_CROSSCHECK.json" if name == "confirmation" else "RAW_CANCEL_CROSSCHECK.json"
        self.copy(base / report, f"historical/{name}_crosscheck.json", json_file=True)

    def live(self, name, source):
        base = self.suite / source
        dest = f"data/live/{name}"
        self.events(base / "events.jsonl", dest + "/events.jsonl.gz")
        self.copy(base / "result.json", dest + "/result.json", json_file=True)
        original = json.loads(self.read(base / "manifest.json"))
        fields = ("model", "reasoning_effort", "source_context", "prompt_sha256", "task_seed",
                  "stop_episode", "operator_message_text", "billing_route", "pilot")
        meta = {k: original[k] for k in fields if k in original}
        self.put(dest + "/method.json", encoded(self.clean(meta)), source=base / "manifest.json",
                 transform="method_fields_only_no_environment_or_authorization")
        for p in sorted((base / "files").rglob("*")):
            if p.is_file():
                self.copy(p, dest + "/" + p.relative_to(base).as_posix())
        for request in sorted(base.glob("request-*")):
            if not request.is_dir():
                continue
            for filename in ("wire_request.json", "projection.json"):
                self.copy(request / filename, dest + "/" + request.name + "/" + filename, json_file=True)
        audit = base / ("AUDIT_v01.json" if name.startswith("initial-") else "AUDIT.json")
        self.copy(audit, f"historical/live/{name}_audit.json", json_file=True)

    def reviews(self):
        first = self.suite / "feasibility/scope_transition_v01/reviews/FIRST_STOP_AUTHOR_REVIEW_v01.json"
        obj = json.loads(self.read(first))
        records = [{"episode": "initial-stop-s17", "text": obj["verbatim"],
                    "text_sha256": obj["text_sha256"], "classification": obj["author_final_classification"],
                    "review_type": "author_review_not_independent", "recorded_at_utc": obj["recorded_at_utc"]}]
        batch = self.suite / BATCH / "AUTHOR_REVIEW_APPROVED_2026_10_07_v01.json"
        obj = json.loads(self.read(batch))
        for item in obj["episodes"]:
            records.append({"episode": item["episode_id"], "text": item["verbatim"],
                            "text_sha256": item["text_sha256"],
                            "classification": item["author_content_classification"],
                            "final_analysis_result_delivered": item["author_confirmed_final_analysis_result_delivered"],
                            "review_type": "post_observation_author_addendum_not_independent",
                            "recorded_at_utc": obj["recorded_at_utc"]})
        self.put("data/live/AUTHOR_REVIEWS.json", encoded(records), transform="review_fields_only")

    def build(self):
        for name, source in NATIVE.items():
            self.native(name, source)
        for name, source in LIVE.items():
            self.live(name, source)
        self.reviews()
        failed = self.suite / "feasibility/live_exploration_v01/healthy-live-2026-10-06-v01/result.json"
        failed_obj = json.loads(self.read(failed))
        retained = {k: failed_obj[k] for k in ("record_type", "execution_status", "provider_calls",
                    "task_seed", "arm", "stop_delivered", "pilot", "report_oracle_status")}
        retained["sharing_note"] = "Earlier incomplete development attempt; not one of the eight completed episodes. No spending estimate is inferred from this record. Full transport remains retained locally."
        self.put("historical/initial_live_attempt_incomplete.json", encoded(retained), source=failed,
                 transform="incomplete_attempt_status_only")
        self.copy(self.suite / "feasibility/f07_cancel_preflight_v01/CORE_BINDING_PROGRESS.json",
                  "historical/open_requirements_2026_10_09.json", json_file=True)
        self.copy(self.lab / "paper_revision_2026_10_01/repository/LICENSE", "source/licenses/PROJECT.txt")
        self.copy(self.lab / "paper_revision_2026_10_01/repository/research/stop-scope/harness/application_probe/upstream/LICENSE",
                  "source/licenses/OPEN_SWE.txt")
        self.copy(self.lab / "stop_contract_study/workload.py", "source/workload.py")
        for name, source in (("live_adapter.py", "feasibility/live_exploration_v01/oauth_adapter.py"),
                             ("live_codec.py", "feasibility/live_exploration_v01/oauth_codec.py"),
                             ("live_stop_observation.py", "feasibility/live_exploration_v01/stop_observation.py")):
            self.copy(self.suite / source, "source/live/" + name)
        for rel, expected in self.sources.items():
            if digest((self.lab / rel).read_bytes()) != expected:
                raise ValueError("Original changed during export: " + rel)
        manifest = {"schema": "stop-scope-progress-export-v1", "date": "2026-10-09",
                    "source_root_label": "retained_local_lab", "original_sources_unchanged": True,
                    "source_digests": self.sources, "files": sorted(self.exports, key=lambda r: r["path"]),
                    "privacy_omissions": dict(self.omissions), "new_provider_calls": 0,
                    "new_native_experiments": 0}
        path = self.out / "EXPORT_MANIFEST.json"
        if path.exists() and not self.refresh and path.read_bytes() != encoded(manifest):
            raise ValueError("Export manifest exists")
        path.write_bytes(encoded(manifest))
        print(json.dumps({"sources": len(self.sources), "exported_files": len(self.exports),
                          "compressed_and_plain_bytes": sum(f["bytes"] for f in self.exports),
                          "privacy_omissions": dict(self.omissions), "original_sources_unchanged": True}, indent=2))


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--suite", type=Path, required=True)
    p.add_argument("--out", type=Path, default=ROOT)
    p.add_argument("--refresh", action="store_true", help="Replace only named, generated sharing files during preparation")
    a = p.parse_args()
    if (a.out.resolve().is_relative_to(a.suite.resolve())
            or a.suite.resolve().is_relative_to(a.out.resolve())):
        p.error("Export must not replace the source tree")
    Exporter(a.suite, a.out, a.refresh).build()


if __name__ == "__main__":
    main()
