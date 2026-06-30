#!/bin/bash
#SBATCH --job-name=zincblende_pipeline
#SBATCH --time=23:59:00
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --mem=64gb
#SBATCH --gres=gpu:a40:1
#SBATCH --partition=interactive-gpu
#SBATCH -A cbartel
#SBATCH --mail-type=END,FAIL
#SBATCH --mail-user=huan2984@umn.edu
#SBATCH -o logs/zincblende_%j.out
#SBATCH -e logs/zincblende_%j.err

export MP_API_KEY="2Q5uDUi2nhLa9KZFK6FiVIqfw8UFJY2t"
cd ~/projects/charge_density/charge3net
source ~/.mp_credentials
conda activate dmc

mkdir -p logs

# Step 1: download CHGCARs from MP
PYTHONPATH=. python scripts/download_by_spacegroup.py \
    --mp_api_key $MP_API_KEY \
    --spacegroup 216 \
    --label zincblende \
    --task_id_file ./data/mpid_to_task_id_map.json \
    --workers 1

# Step 2: convert to charge3net format
PYTHONPATH=. python scripts/convert_chgcar_dir_to_pkl_dir.py \
    --input ./data/zincblende_raw \
    --output ./data/zincblende_pkl \
    --workers 4

# Step 3: run charge3net inference
python src/test_from_config.py \
    -cd configs/charge3net/ \
    -cn test_chgcar_inputs.yaml \
    input_dir=./data/zincblende_pkl \
    nnodes=1 nprocs=1 \
    data.train_workers=0 data.val_workers=0 \
    hydra.run.dir=./data/zincblende_results
