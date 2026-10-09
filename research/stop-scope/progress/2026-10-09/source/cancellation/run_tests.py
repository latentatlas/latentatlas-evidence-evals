"""Resolve this preflight's tests explicitly; keep preserved regressions separate."""
import importlib.util
import json
from pathlib import Path
import sys
import unittest
from contract import ROOT,require
from audit import sha


def main():
    suite=unittest.TestSuite();modules=[]
    for name in ("test_cancel_probe","test_audit","test_binding"):
        path=ROOT/(name+".py")
        spec=importlib.util.spec_from_file_location("f07_"+name,path)
        module=importlib.util.module_from_spec(spec);sys.modules[spec.name]=module;spec.loader.exec_module(module)
        require(Path(module.__file__).resolve()==path,"Foreign test module")
        suite.addTests(unittest.defaultTestLoader.loadTestsFromModule(module))
        modules.append(dict(file=name+".py",sha256=sha(path)))
    result=unittest.TextTestRunner(verbosity=1).run(suite)
    ok=result.wasSuccessful() and not result.skipped and result.testsRun==41
    print(json.dumps(dict(status="passed" if ok else "failed",tests_run=result.testsRun,skipped=len(result.skipped),test_modules=modules)))
    return 0 if ok else 1


if __name__=="__main__":raise SystemExit(main())
