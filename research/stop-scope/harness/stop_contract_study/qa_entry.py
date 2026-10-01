"""No project modules inherited from the caller's working directory."""
from pathlib import Path
import argparse
import sys
import unittest
root=Path(__file__).resolve().parent
sys.dont_write_bytecode=True
sys.path.insert(0,str(root))
parser=argparse.ArgumentParser();parser.add_argument('--record',type=Path);parser.add_argument('--source-root',type=Path)
args=parser.parse_args()
import test_audit
test_audit.configure_record(args.record,args.source_root)
suite=unittest.defaultTestLoader.discover(str(root),pattern='test_*.py')
result=unittest.TextTestRunner(verbosity=2).run(suite)
raise SystemExit(0 if result.wasSuccessful() else 1)
