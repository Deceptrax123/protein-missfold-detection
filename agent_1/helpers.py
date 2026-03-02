import shutil
import subprocess
from pathlib import Path
from Bio.Seq import Seq


def find_foldseek() -> str:
    for name in ("foldseek", "foldseek.exe"):
        path = shutil.which(name)
        if path:
            return path
    # Check project foldseek folder (e.g. protein-missfold-detection/foldseek/bin/foldseek)
    project_root = Path(__file__).resolve().parent.parent
    local_bin = project_root / "foldseek" / "bin" / "foldseek"
    if local_bin.exists():
        return str(local_bin)
    raise FileNotFoundError("Foldseek executable not found in PATH or project foldseek/bin/.")


def run_foldseek_pdb_to_3di(pdb_paths: list[Path], foldseek_bin: str, work_dir: Path) -> dict:
    print(f"\n[DEBUG-FOLDSEEK] Starting 3Di conversion...")
    if not pdb_paths:
        return {}

    input_dir = work_dir / "input"
    input_dir.mkdir(parents=True, exist_ok=True)

    for src in pdb_paths:
        dst = input_dir / src.name
        shutil.copy2(src, dst)

    db_base = work_dir / "db"
    result_base = work_dir / "result"
    tmp_dir = work_dir / "tmp"
    tmp_dir.mkdir(exist_ok=True)

    r1 = subprocess.run([foldseek_bin, "createdb", str(input_dir), str(db_base)],
                        capture_output=True, text=True)
    if r1.returncode != 0:
        raise RuntimeError(f"createdb failed: {r1.stderr}")

    cmd_search = [
        foldseek_bin, "easy-search", str(input_dir), str(
            db_base), str(result_base), str(tmp_dir),
        "--format-output", "query,target,qaln,taln,fident",
        "-e", "inf",
        "--exhaustive-search", "1",
        "--min-aln-len", "10"
    ]

    print(f"[DEBUG-FOLDSEEK] Running search with exhaustive flags...")
    r2 = subprocess.run(cmd_search, capture_output=True, text=True)
    if r2.returncode != 0:
        raise RuntimeError(f"easy-search failed: {r2.stderr}")

    out = {}
    result_tsv = result_base

    if not result_tsv.exists() or result_tsv.stat().st_size == 0:
        print(
            "[DEBUG-FOLDSEEK] ERROR: Result file is empty! Foldseek rejected the sequence.")
        return out

    with open(result_tsv, encoding="utf-8", errors="replace") as f:
        for line in f:
            parts = line.rstrip().split("\t")
            if len(parts) < 5:
                continue

            query, target, qaln, taln, fident = parts[:5]
            qid = Path(query).stem

            if qid not in out and (query == target or float(fident or 0) >= 0.99):
                seq = (qaln or taln or "").replace("-", "").lower()
                if seq:
                    out[qid] = seq

    return out
