#!/usr/bin/env python3
"""
Convert PDB files to 3Di structural sequences using Foldseek.

Foldseek (https://github.com/steineggerlab/foldseek) encodes protein structures
as 3Di sequences—a 20-letter structural alphabet that captures local backbone
conformations. This script uses Foldseek's createdb and easy-search to extract
3Di strings from PDB/mmCIF files.

Requirements:
    - Foldseek must be installed and in PATH
    - Install: conda install -c bioconda foldseek
    - Or download from: https://mmseqs.com/foldseek/
    - For GPU: use foldseek-linux-gpu.tar.gz (NVIDIA Ampere+ recommended)

Usage:
    python pdb_to_3di.py <pdb_file_or_dir> [--output out.json]
    python pdb_to_3di.py AlphaFold_model_PDBs/ --output 3di_sequences.json
    python pdb_to_3di.py structures/ -o 3di.json --gpu
"""

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


def find_foldseek() -> str | None:
    """Locate foldseek executable (foldseek or foldseek.exe on Windows)."""
    for name in ("foldseek", "foldseek.exe"):
        path = shutil.which(name)
        if path:
            return path
    return None


def get_pdb_files(path: str | Path) -> list[Path]:
    """Collect PDB/mmCIF files from a file or directory."""
    p = Path(path).resolve()
    if not p.exists():
        raise FileNotFoundError(f"Path not found: {path}")

    if p.is_file():
        suf = p.suffix.lower()
        if suf in (".pdb", ".cif", ".mmcif", ".ent"):
            return [p]
        raise ValueError(f"Not a structure file: {path} (expected .pdb, .cif)")

    files = []
    for suf in (".pdb", ".cif", ".mmcif", ".ent", ".pdb.gz", ".cif.gz"):
        files.extend(p.glob(f"*{suf}"))
    files = sorted(set(files))
    if not files:
        raise FileNotFoundError(f"No PDB/mmCIF files found in: {path}")
    return files


def run_foldseek_pdb_to_3di(
    pdb_paths: list[Path],
    foldseek_bin: str,
    work_dir: Path,
    *,
    use_gpu: bool = False,
) -> dict[str, str]:
    """
    Use Foldseek to convert PDB files to 3Di sequences.

    Workflow:
    1. foldseek createdb <input_dir> db
    2. foldseek easy-search <input_dir> db result tmp --format-output query,target,qaln,taln
    3. Parse result: for each query self-hit, qaln (with gaps removed) = 3Di sequence
    """
    if not pdb_paths:
        return {}

    input_dir = work_dir / "input"
    input_dir.mkdir(parents=True, exist_ok=True)

    for src in pdb_paths:
        dst = input_dir / src.name
        if src.resolve() != dst.resolve():
            if dst.exists():
                dst.unlink()
            try:
                os.symlink(src, dst)
            except OSError:
                shutil.copy2(src, dst)

    db_base = work_dir / "db"
    result_base = work_dir / "result"
    tmp_dir = work_dir / "tmp"
    tmp_dir.mkdir(exist_ok=True)

    # 1. Create Foldseek database from structures
    cmd_createdb = [
        foldseek_bin,
        "createdb",
        str(input_dir),
        str(db_base),
    ]
    r1 = subprocess.run(
        cmd_createdb,
        capture_output=True,
        text=True,
        cwd=str(work_dir),
    )
    if r1.returncode != 0:
        raise RuntimeError(
            f"Foldseek createdb failed:\n{r1.stderr}\n{r1.stdout}"
        )

    cmd_search = [
        foldseek_bin,
        "easy-search",
        str(input_dir),
        str(db_base),
        str(result_base),
        str(tmp_dir),
        "--format-output", "query,target,qaln,taln,fident",
        "-e", "10000",
        "--max-seqs", "10000",
    ]
    if use_gpu:
        cmd_search.extend(["--gpu", "1", "--prefilter-mode", "1"])
    r2 = subprocess.run(
        cmd_search,
        capture_output=True,
        text=True,
        cwd=str(work_dir),
    )
    if r2.returncode != 0:
        raise RuntimeError(
            f"Foldseek easy-search failed:\n{r2.stderr}\n{r2.stdout}"
        )

    candidates = list(work_dir.glob("result*")) + [result_base]
    result_tsv = next(
        (f for f in candidates if f.is_file() and f.stat().st_size > 0),
        None,
    )

    out: dict[str, str] = {}
    seen: set[str] = set()

    if not result_tsv or not result_tsv.exists():
        return out

    with open(result_tsv, encoding="utf-8", errors="replace") as f:
        for line in f:
            line = line.rstrip()
            if not line:
                continue
            parts = line.split("\t")
            if len(parts) < 5:
                continue
            query, target, qaln, taln, fident = parts[:5]
            # Normalize query id (strip path, extension)
            qid = Path(query).stem
            if qid in seen:
                continue
            # Prefer self-hit; otherwise take best hit
            if query == target or float(fident or 0) >= 0.99:
                # qaln/taln in 3Di+AA mode: alignment string; remove gaps for full 3Di
                seq = (qaln or taln or "").replace("-", "").lower()
                if seq:
                    out[qid] = seq
                    seen.add(qid)

    if len(out) < len(pdb_paths):
        seen.clear()
        with open(result_tsv, encoding="utf-8", errors="replace") as f:
            for line in f:
                line = line.rstrip()
                if not line:
                    continue
                parts = line.split("\t")
                if len(parts) < 5:
                    continue
                query, target, qaln, taln, _ = parts[:5]
                qid = Path(query).stem
                if qid in seen:
                    continue
                seq = (qaln or taln or "").replace("-", "").lower()
                if seq:
                    out[qid] = seq
                    seen.add(qid)

    return out


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Convert PDB/mmCIF files to 3Di structural sequences using Foldseek.",
    )
    parser.add_argument(
        "input",
        type=str,
        help="PDB/mmCIF file or directory containing structure files",
    )
    parser.add_argument(
        "-o", "--output",
        type=str,
        default=None,
        help="Output JSON file (default: print to stdout)",
    )
    parser.add_argument(
        "--keep-temp",
        action="store_true",
        help="Keep temporary working directory for debugging",
    )
    parser.add_argument(
        "--foldseek",
        type=str,
        default=None,
        help="Path to foldseek executable (default: search PATH)",
    )
    parser.add_argument(
        "--gpu",
        action="store_true",
        help="Use GPU acceleration for search (requires foldseek-linux-gpu build)",
    )

    args = parser.parse_args()

    foldseek_bin = args.foldseek or find_foldseek()
    if not foldseek_bin:
        print(
            "Error: Foldseek not found. Install with:\n"
            "  conda install -c bioconda foldseek\n"
            "Or download from https://mmseqs.com/foldseek/",
            file=sys.stderr,
        )
        return 1

    try:
        pdb_files = get_pdb_files(args.input)
    except (FileNotFoundError, ValueError) as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

    print(f"Found {len(pdb_files)} structure file(s). Running Foldseek...", file=sys.stderr)

    with tempfile.TemporaryDirectory(prefix="pdb23di_") as tmp:
        work_dir = Path(tmp)
        try:
            results = run_foldseek_pdb_to_3di(
                pdb_files, foldseek_bin, work_dir, use_gpu=args.gpu
            )
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
            if args.keep_temp:
                keep = Path("pdb23di_temp")
                if keep.exists():
                    shutil.rmtree(keep)
                shutil.copytree(work_dir, keep)
                print(f"Kept temp dir: {keep}", file=sys.stderr)
            return 1

        if args.keep_temp:
            keep = Path("pdb23di_temp")
            if keep.exists():
                shutil.rmtree(keep)
            shutil.copytree(work_dir, keep)
            print(f"Kept temp dir: {keep}", file=sys.stderr)

    if not results:
        print("Warning: No 3Di sequences extracted. Check Foldseek output.", file=sys.stderr)
        return 1

    out_json = json.dumps(results, indent=2)
    if args.output:
        Path(args.output).write_text(out_json, encoding="utf-8")
        print(f"Wrote {len(results)} 3Di sequences to {args.output}", file=sys.stderr)
    else:
        print(out_json)

    return 0


if __name__ == "__main__":
    sys.exit(main())

