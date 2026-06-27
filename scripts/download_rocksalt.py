import sys
sys.path.append('.')

import argparse
from pathlib import Path
from mp_api.client import MPRester
from emmet.core.summary import HasProps
from download.download_materials_project import write_chgcar, write_filelist
from multiprocessing import pool as mp_pool

parser = argparse.ArgumentParser()
parser.add_argument("--mp_api_key", required=True)
parser.add_argument("--out_dir", default="./data/rocksalt_raw")
parser.add_argument("--workers", type=int, default=1)
parser.add_argument("--limit", type=int, default=0)


def get_rocksalt_mpids(api_key):
    with MPRester(api_key) as mpr:
        docs = mpr.materials.summary.search(
            has_props=[HasProps.charge_density],
            spacegroup_number=225,
            fields=["material_id"]
        )
    return [doc.material_id for doc in docs]


def download_one(mp_api_key, mpid, outpath):
    try:
        with MPRester(mp_api_key) as mpr:
            chgcar = mpr.get_charge_density_from_material_id(mpid)
        if chgcar is not None:
            write_chgcar(chgcar, outpath, mpid)
        else:
            print(f"No charge density for {mpid}")
    except Exception as e:
        print(f"{mpid}: {e}")


def main():
    args = parser.parse_args()
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    print("Querying MP for rocksalt materials with charge density...")
    mpids = get_rocksalt_mpids(args.mp_api_key)
    print(f"Found {len(mpids)} rocksalt materials")

    if args.limit > 0:
        mpids = mpids[:args.limit]
        print(f"Limiting to {args.limit} materials")

    write_filelist(mpids, out_dir / "filelist.txt")

    print("Downloading CHGCARs...")
    if args.workers > 1:
        mp_pool.Pool(args.workers).starmap(
            download_one,
            [(args.mp_api_key, mpid, out_dir) for mpid in mpids]
        )
    else:
        for i, mpid in enumerate(mpids):
            print(f"  {i+1}/{len(mpids)}: {mpid}")
            download_one(args.mp_api_key, mpid, out_dir)

    print("Done.")


if __name__ == "__main__":
    main()
