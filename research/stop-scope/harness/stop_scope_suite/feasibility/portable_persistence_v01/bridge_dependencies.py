"""Explicit local dependencies; no account, old run directory, or import fallback."""
import hashlib
import importlib.util
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
FEAS = HERE.parent
LAB = FEAS.parent.parent
ROOT = LAB.parent
MANIFEST = HERE / "SOURCE_MANIFEST.json"
PATHS = {
    "common": FEAS/"f07_receiver_process_v01/common.py",
    "path_policy": FEAS/"shared_queue_v05/path_policy.py",
    "persistent_prior_receiver": FEAS/"f07_live_receiver_v02/receiver_worker.py",
    "persistent_observer": FEAS/"f07_receiver_process_v01/observer.py",
    "persistent_workload": LAB/"stop_contract_study/workload.py",
    "bridge_durable_receiver": FEAS/"f07_persistent_receiver_v01/durable_receiver.py",
    "bridge_prior_adapter": FEAS/"f07_live_receiver_v02/adapter_bridge.py",
}
def pinned(path):
    return json_manifest()[str(path.relative_to(ROOT))]
def json_manifest():
    import json
    return json.loads(MANIFEST.read_text())["files"]
PINS = {name: (path, pinned(path)) for name, path in PATHS.items()}
NATIVE_ADAPTER = FEAS/"f07_direct_after_v01/native_adapter.py"
def load(name):
    path, expected = PINS[name]
    if hashlib.sha256(path.read_bytes()).hexdigest() != expected:
        raise ValueError("Pinned dependency changed: " + name)
    if name in sys.modules:
        module = sys.modules[name]
        if Path(module.__file__).resolve() != path.resolve():
            raise ValueError("Module identity conflict: " + name)
        return module
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    try: spec.loader.exec_module(module)
    except BaseException:
        sys.modules.pop(name, None)
        raise
    return module
common = load("common")
path_policy = load("path_policy")
prior_receiver = load("persistent_prior_receiver")
observer = load("persistent_observer")
workload = load("persistent_workload")
# The retained receiver imports the narrow 'dependencies' facade below.
import dependencies
durable = load("bridge_durable_receiver")
def verify_adapter(module):
    common.require(Path(module.__file__).resolve() == NATIVE_ADAPTER.resolve()
                   and common.sha(NATIVE_ADAPTER.read_bytes()) == pinned(NATIVE_ADAPTER),
                   "Native adapter binding changed")
def dependency_hashes():
    return {str(p.relative_to(ROOT)): h for p,h in PINS.values()}
