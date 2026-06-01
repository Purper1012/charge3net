#!/bin/bash
#SBATCH -N 1
#SBATCH -n 4
#SBATCH --mem=32G
#SBATCH --time=12:00:00
#SBATCH -p amdsmall
#SBATCH -A cbartel
#SBATCH --job-name=rocksalt_download
#SBATCH -o logs/rocksalt_%j.out
#SBATCH -e logs/rocksalt_%j.err

cd ~/projects/charge_density/charge3net
conda activate dmc

mkdir -p logs

# Step 1: download CHGCARs
PYTHONPATH=. python scripts/download_rocksalt.py \
    --mp_api_key $MP_API_KEY \
    --out_dir ./data/rocksalt_raw \
    --workers 3

# Step 2: convert to charge3net format
PYTHONPATH=. python scripts/convert_chgcar_dir_to_pkl_dir.py \
    --input ./data/rocksalt_raw \
    --output ./data/rocksalt_pkl \
    --workers 4
