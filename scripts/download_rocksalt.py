import sys
sys.path.append('.')

import argparse
from pathlib import Path
from mp_api.client import MPRester
from emmet.core.summary import HasProps
from download.download_materials_project import _read_in_write_out, write_filelist
from multiprocessing import pool as mp_pool

parser = argparse.ArgumentParser()
parser.add_argument("--mp_api_key", required=True)
parser.add_argument("--out_dir", default="./data/rocksalt_raw")
parser.add_argument("--workers", type=int, default=1)


def get_rocksalt_mpids(api_key):
    with MPRester(api_key) as mpr:
        docs = mpr.materials.summary.search(
            has_props=[HasProps.charge_density],
            spacegroup_number=225,
            fields=["material_id"]
        )
    return [doc.material_id for doc in docs]


def main():
    args = parser.parse_args()
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    print("Querying MP for rocksalt materials with charge density...")
    mpids = get_rocksalt_mpids(args.mp_api_key)
    print(f"Found {len(mpids)} materials")

    write_filelist(mpids, out_dir / "filelist.txt")

    print("Downloading CHGCARs...")
    if args.workers > 1:
        mp_pool.Pool(args.workers).starmap(
            _read_in_write_out,
            [(args.mp_api_key, mpid, out_dir) for mpid in mpids]
        )
    else:
        for i, mpid in enumerate(mpids):
            print(f"  {i+1}/{len(mpids)}: {mpid}")
            _read_in_write_out(args.mp_api_key, mpid, out_dir)

    print(f"\nDone. Next steps:")
    print(f"  1. PYTHONPATH=. python scripts/convert_chgcar_dir_to_pkl_dir.py --input {out_dir} --output ./data/rocksalt_pkl --workers 4")
    print(f"  2. python src/test_from_config.py -cd configs/charge3net/ -cn test_chgcar_inputs.yaml input_dir=./data/rocksalt_pkl nnodes=1 nprocs=1 data.train_workers=0 data.val_workers=0")


if __name__ == "__main__":
    main()
