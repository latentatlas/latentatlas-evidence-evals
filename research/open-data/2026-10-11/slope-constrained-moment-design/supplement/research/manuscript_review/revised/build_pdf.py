#!/usr/bin/env python3
"""Build the review manuscript in a disposable directory, never over frozen bytes."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--tectonic', default='tectonic')
    ap.add_argument('--output-dir', type=Path, required=True)
    args = ap.parse_args()
    out = args.output_dir.absolute()
    if out.exists():
        raise SystemExit('Output directory already exists; choose a fresh directory.')
    executable = shutil.which(args.tectonic)
    if not executable:
        raise SystemExit('Tectonic executable not found.')
    executable = str(Path(executable).absolute())
    version = subprocess.check_output([executable, '--version'], text=True).strip()
    with tempfile.TemporaryDirectory(prefix='slope-paper-') as temp:
        work = Path(temp)
        for name in ['manuscript.tex', 'certified_constants.tex']:
            shutil.copyfile(HERE/name, work/name)
        shutil.copytree(HERE/'figures', work/'figures')
        command = [executable, '--keep-logs', '--keep-intermediates', 'manuscript.tex']
        run = subprocess.run(command, cwd=work, text=True, capture_output=True)
        if run.returncode:
            print(run.stdout + run.stderr)
            raise SystemExit(run.returncode)
        log = (work/'manuscript.log').read_text(errors='replace')
        forbidden = ['Overfull \\hbox', 'Overfull \\vbox', 'Undefined control sequence',
                     'There were undefined references', 'There were undefined citations',
                     'Missing character:']
        warnings = [s for s in forbidden if s in log]
        out.mkdir(parents=True)
        for name in ['manuscript.pdf', 'manuscript.log', 'manuscript.aux']:
            shutil.copyfile(work/name, out/name)
        (out/'compiler_output.txt').write_text(run.stdout + run.stderr)
        (out/'build.json').write_text(json.dumps({
            'compiler_version': version,
            'command': command,
            'compiler_sha256': hashlib.sha256(Path(executable).read_bytes()).hexdigest(),
            'pdf_sha256': hashlib.sha256((out/'manuscript.pdf').read_bytes()).hexdigest(),
            'tex_sha256': hashlib.sha256((HERE/'manuscript.tex').read_bytes()).hexdigest(),
            'layout_or_reference_errors': warnings,
            'source_date_epoch': os.environ.get('SOURCE_DATE_EPOCH'),
            'external_upload_of_manuscript': False,
        }, indent=2)+'\n')
        print(json.dumps({'output_dir': str(out), 'layout_or_reference_errors': warnings}))
        if warnings:
            raise SystemExit(2)

if __name__ == '__main__':
    main()
