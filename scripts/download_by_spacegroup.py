import sys
sys.path.append('.')

import argparse
import json
from pathlib import Path
from mp_api.client import MPRester
from emmet.core.summary import HasProps
from download.download_materials_project import _read_in_write_out_task, write_filelist

parser = argparse.ArgumentParser()
parser.add_argument("--mp_api_key", required=True)
parser.add_argument("--spacegroup", type=int, required=True, help="Space group number (e.g. 225=rocksalt, 221=perovskite, 216=zincblende)")
parser.add_argument("--label", type=str, required=True, help="Label for output directory (e.g. rocksalt, perovskite, zincblende)")
parser.add_argument("--out_dir", type=str, default=None, help="Output directory (default: ./data/{label}_raw)")
parser.add_argument("--task_id_file", default="./data/mpid_to_task_id_map.json")
parser.add_argument("--workers", type=int, default=1)
parser.add_argument("--limit", type=int, default=0)


def get_mpids(api_key, spacegroup):
    with MPRester(api_key) as mpr:
        docs = mpr.materials.summary.search(
            has_props=[HasProps.charge_density],
            spacegroup_number=spacegroup,
            fields=["material_id"]
        )
    return {doc.material_id for doc in docs}


def main():
    args = parser.parse_args()
    out_dir = Path(args.out_dir) if args.out_dir else Path(f"./data/{args.label}_raw")
    out_dir.mkdir(parents=True, exist_ok=True)

    print(f"Querying MP for spacegroup {args.spacegroup} ({args.label}) materials...")
    mpids = get_mpids(args.mp_api_key, args.spacegroup)
    print(f"Found {len(mpids)} materials")

    with open(args.task_id_file) as f:
        task_id_map = json.load(f)

    pairs = [(mpid, task_id_map[mpid]) for mpid in mpids if mpid in task_id_map]
    print(f"{len(pairs)} have task IDs in map")

    if args.limit > 0:
        pairs = pairs[:args.limit]
        print(f"Limiting to {args.limit}")

    write_filelist([mpid for mpid, _ in pairs], out_dir / "filelist.txt")

    print("Downloading CHGCARs...")
    for i, (mpid, task_id) in enumerate(pairs):
        print(f"  {i+1}/{len(pairs)}: {mpid}")
        _read_in_write_out_task(args.mp_api_key, mpid, task_id, out_dir)

    print("Done.")


if __name__ == "__main__":
    main()
