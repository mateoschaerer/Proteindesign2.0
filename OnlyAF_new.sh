#!/bin/bash
#SBATCH --time=72:00:00
#SBATCH --nodes=1
#SBATCH --ntasks=1
##SBATCH --cpus-per-task=20
#SBATCH --gres=gpu:4
#SBATCH --mem=90000

### NOTE
### This job script cannot be used without modification for your specific environment.


export ALPHAFOLD_DIR=/ssoft/spack/external/alphafold/v2.3.2-1
export ALPHAFOLD_DATADIR="/work/scitas-share/datasets/AlphaFold_Datasets/Databases"

export TMP=$(mktemp -d)

### Check values of some environment variables
echo INFO: SLURM_GPUS_ON_NODE=$SLURM_GPUS_ON_NODE
echo INFO: SLURM_JOB_GPUS=$SLURM_JOB_GPUS
echo INFO: SLURM_STEP_GPUS=$SLURM_STEP_GPUS
echo INFO: ALPHAFOLD_DIR=$ALPHAFOLD_DIR
echo INFO: ALPHAFOLD_DATADIR=$ALPHAFOLD_DATADIR
echo INFO: TMP=$TMP

###
### README This runs AlphaFold 2.3.2 on the T1050.fasta file
###

# AlphaFold should use all GPU devices available to the job by default.
#
# To run the CASP14 evaluation, use:
# --model_preset=monomer_casp14
# --db_preset=full_dbs (or delete the line; default is "full_dbs")
#
# On a test system with 4x Tesla V100-SXM2, this took about 50 minutes.
#
# To benchmark, running multiple JAX model evaluations (NB this
# significantly increases run time):
# --benchmark
#
# On a test system with 4x Tesla V100-SXM2, this took about 6 hours.

# Create output directory in $TMP (which is cleaned up by Slurm at end
# of job).
output_dir=$TMP/output
mkdir -p $output_dir


# get the fasta files
fasta_dir="AF_current_job"
fasta_paths=$(find "$fasta_dir" -name "*.fa" -type f -printf "%p," | sed 's/,$//')

echo INFO: output_dir=$output_dir

# Run AlphaFold; default is to use GPUs
python3 ${ALPHAFOLD_DIR}/run_singularity.py \
	--use_gpu \
	--data_dir=${ALPHAFOLD_DATADIR} \
	--fasta_paths="${fasta_paths[@]}" \
	--output_dir=$output_dir \
	--max_template_date=2020-05-14 \
	--model_preset=monomer \
	--db_preset=reduced_dbs

echo INFO: AlphaFold returned $?

### Copy Alphafold output back to directory where "sbatch" command was issued.
mkdir $SLURM_SUBMIT_DIR/Output-$SLURM_JOB_ID
cp -R $output_dir $SLURM_SUBMIT_DIR/Output-$SLURM_JOB_ID

rm -rf $TMP


#clear the AF_current job directory

rm -rf $fasta_dir/*
