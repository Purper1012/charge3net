#!/bin/bash
#SBATCH -N 1
#SBATCH -n 4
#SBATCH --gres=gpu:a40:1
#SBATCH --mem=64G
#SBATCH --time=24:00:00
#SBATCH -p interactive-gpu
#SBATCH -A cbartel
#SBATCH --job-name=rocksalt_pipeline
#SBATCH -o logs/rocksalt_%j.out
#SBATCH -e logs/rocksalt_%j.err

cd ~/projects/charge_density/charge3net
conda activate dmc

mkdir -p logs

# Step 1: download CHGCARs from MP
PYTHONPATH=. python scripts/download_rocksalt.py \
    --mp_api_key $MP_API_KEY \
    --out_dir ./data/rocksalt_raw \
    --workers 3

# Step 2: convert to charge3net format
PYTHONPATH=. python scripts/convert_chgcar_dir_to_pkl_dir.py \
    --input ./data/rocksalt_raw \
    --output ./data/rocksalt_pkl \
    --workers 4

# Step 3: run charge3net inference
python src/test_from_config.py \
    -cd configs/charge3net/ \
    -cn test_chgcar_inputs.yaml \
    input_dir=./data/rocksalt_pkl \
    nnodes=1 nprocs=1 \
    data.train_workers=0 data.val_workers=0 \
    hydra.run.dir=./data/rocksalt_results
