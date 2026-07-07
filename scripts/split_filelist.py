"""
Split a filelist.txt into N chunks and set up subdirectories for parallel inference.
Each subdirectory gets its own filelist.txt, split.json, and probe_counts.csv.

Usage:
    python scripts/split_filelist.py \
        --pkl_dir /scratch.global/huan2984/rocksalt_pkl \
        --n_chunks 6 \
        --out_base /scratch.global/huan2984/rocksalt_chunks
"""
import sys
sys.path.append('.')

import argparse
import shutil
from pathlib import Path
from scripts.write_dummy_split import main as write_split
from scripts.write_mp_probe_count_file import count_elements_in_numpy_files

parser = argparse.ArgumentParser()
parser.add_argument("--pkl_dir", required=True, help="Directory with filelist.txt, .npy, and _atoms.pkl files")
parser.add_argument("--n_chunks", type=int, default=6)
parser.add_argument("--out_base", required=True, help="Base directory for output chunks")


def main():
    args = parser.parse_args()
    pkl_dir = Path(args.pkl_dir)
    out_base = Path(args.out_base)

    with open(pkl_dir / "filelist.txt") as f:
        entries = [line.strip() for line in f if line.strip()]

    n = len(entries)
    chunk_size = (n + args.n_chunks - 1) // args.n_chunks
    print(f"{n} materials → {args.n_chunks} chunks of ~{chunk_size} each")

    for i in range(args.n_chunks):
        chunk = entries[i * chunk_size:(i + 1) * chunk_size]
        if not chunk:
            continue

        chunk_dir = out_base / f"chunk_{i}"
        chunk_dir.mkdir(parents=True, exist_ok=True)

        # symlink the actual .npy and _atoms.pkl files
        for name in chunk:
            for suffix in [".npy", "_atoms.pkl"]:
                src = pkl_dir / f"{name}{suffix}"
                dst = chunk_dir / f"{name}{suffix}"
                if src.exists() and not dst.exists():
                    dst.symlink_to(src)

        # write filelist.txt
        filelist = chunk_dir / "filelist.txt"
        with open(filelist, "w") as f:
            for name in chunk:
                f.write(f"{name}\n")

        # write probe_counts.csv and split.json
        count_elements_in_numpy_files(file_list_path=filelist, workers=1)
        write_split(filelist, output_file=chunk_dir / "split.json")

        print(f"  chunk_{i}: {len(chunk)} materials")

    print("Done. Submit one job per chunk directory.")


if __name__ == "__main__":
    main()
