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

#for i in 0 1 2 3 4 5; do
#    sbatch --export=CHUNK_DIR=$SCRATCH_GLOBAL/$USER/rocksalt_chunks/chunk_$i \
#        scripts/submit_rocksalt_chunk.sh
#done

export MP_API_KEY="2Q5uDUi2nhLa9KZFK6FiVIqfw8UFJY2t"
source ~/.bashrc
cd ~/projects/charge_density/charge3net
source ~/.mp_credentials
conda activate dmc

python src/test_from_config.py \
    -cd configs/charge3net/ \
    -cn test_chgcar_inputs.yaml \
    input_dir=$CHUNK_DIR \
    nnodes=1 nprocs=1 \
    data.train_workers=0 data.val_workers=0 \
    hydra.run.dir=./data/rocksalt_results_$(basename $CHUNK_DIR)
