#!/bin/bash
#SBATCH --job-name=rocksalt_infer
#SBATCH --time=23:59:00
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --mem=64gb
#SBATCH --gres=gpu:a40:1
#SBATCH --partition=interactive-gpu
#SBATCH -A cbartel
#SBATCH --mail-type=END,FAIL
#SBATCH --mail-user=huan2984@umn.edu
#SBATCH -o logs/rocksalt_infer_%j.out
#SBATCH -e logs/rocksalt_infer_%j.err

cd ~/projects/charge_density/charge3net
source ~/anaconda3/etc/profile.d/conda.sh
conda activate dmc

SCRATCH=$SCRATCH_GLOBAL/$USER

python src/test_from_config.py \
    -cd configs/charge3net/ \
    -cn test_chgcar_inputs.yaml \
    input_dir=$SCRATCH/rocksalt_pkl \
    nnodes=1 nprocs=1 \
    data.train_workers=0 data.val_workers=0 \
    hydra.run.dir=./data/rocksalt_results
