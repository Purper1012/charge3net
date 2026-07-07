#!/bin/bash
#SBATCH --job-name=rocksalt_chunk
#SBATCH --time=23:59:00
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --mem=64gb
#SBATCH --gres=gpu:a40:1
#SBATCH --partition=interactive-gpu
#SBATCH -A cbartel
#SBATCH --mail-type=END,FAIL
#SBATCH --mail-user=huan2984@umn.edu
#SBATCH -o logs/rocksalt_chunk_%j.out
#SBATCH -e logs/rocksalt_chunk_%j.err

# Usage: sbatch --export=CHUNK_DIR=/path/to/chunk_0 scripts/submit_rocksalt_chunk.sh

cd ~/projects/charge_density/charge3net
source ~/anaconda3/etc/profile.d/conda.sh
conda activate dmc

python src/test_from_config.py \
    -cd configs/charge3net/ \
    -cn test_chgcar_inputs.yaml \
    input_dir=$CHUNK_DIR \
    nnodes=1 nprocs=1 \
    data.train_workers=0 data.val_workers=0 \
    hydra.run.dir=./data/rocksalt_results_$(basename $CHUNK_DIR)
