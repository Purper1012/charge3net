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
parser.add_argument("--out_dir", default="./data/rocksalt_raw")
parser.add_argument("--task_id_file", default="./data/mpid_to_task_id_map.json")
parser.add_argument("--workers", type=int, default=1)
parser.add_argument("--limit", type=int, default=0)


def get_rocksalt_mpids(api_key):
    with MPRester(api_key) as mpr:
        docs = mpr.materials.summary.search(
            has_props=[HasProps.charge_density],
            spacegroup_number=225,
            fields=["material_id"]
        )
    return {doc.material_id for doc in docs}


def main():
    args = parser.parse_args()
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    print("Querying MP for rocksalt materials with charge density...")
    rocksalt_mpids = get_rocksalt_mpids(args.mp_api_key)
    print(f"Found {len(rocksalt_mpids)} rocksalt materials")

    with open(args.task_id_file) as f:
        task_id_map = json.load(f)

    pairs = [(mpid, task_id_map[mpid]) for mpid in rocksalt_mpids if mpid in task_id_map]
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
