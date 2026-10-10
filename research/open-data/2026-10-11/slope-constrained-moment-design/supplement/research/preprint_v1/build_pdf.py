#!/usr/bin/env python3
"""Compile the paper in a disposable directory and record source hashes."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--tectonic",default="tectonic")
    ap.add_argument("--output-dir",type=Path,required=True)
    args=ap.parse_args()
    out=args.output_dir.resolve()
    if out.exists():raise SystemExit("Choose a fresh output directory.")
    exe=shutil.which(args.tectonic)
    if not exe:raise SystemExit("Tectonic not found.")
    exe=str(Path(exe).resolve())
    version=subprocess.check_output([exe,"--version"],text=True).strip()
    with tempfile.TemporaryDirectory(prefix="moment-preprint-") as td:
        work=Path(td)
        for p in HERE.glob("*.tex"):shutil.copyfile(p,work/p.name)
        shutil.copytree(HERE/"figures",work/"figures")
        run=subprocess.run([exe,"--keep-logs","--keep-intermediates","manuscript.tex"],
                           cwd=work,text=True,capture_output=True,
                           env={**os.environ,"SOURCE_DATE_EPOCH":"1790121600"})
        if run.returncode:
            print(run.stdout+run.stderr);raise SystemExit(run.returncode)
        log=(work/"manuscript.log").read_text(errors="replace")
        bad=[s for s in ["Overfull \\hbox","Overfull \\vbox","Undefined control sequence",
                         "There were undefined references","There were undefined citations",
                         "Missing character:"] if s in log]
        out.mkdir(parents=True)
        for name in ["manuscript.pdf","manuscript.log","manuscript.aux"]:
            shutil.copyfile(work/name,out/name)
        (out/"compiler_output.txt").write_text(run.stdout+run.stderr)
        report={"compiler":version,"compiler_sha256":sha(Path(exe)),
                "pdf_sha256":sha(out/"manuscript.pdf"),"layout_or_reference_errors":bad,
                "sources":{p.name:sha(p) for p in sorted(HERE.glob("*.tex"))},
                "figures":{p.name:sha(p) for p in sorted((HERE/"figures").glob("*.pdf"))}}
        (out/"build.json").write_text(json.dumps(report,indent=2)+"\n")
        print(json.dumps({"output":str(out),"errors":bad}))
        if bad:raise SystemExit(2)
if __name__=="__main__":main()
