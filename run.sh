#!/bin/bash

#SBATCH --time=72:00:00
#SBATCH --nodes=1
#SBATCH --gres=gpu:4
##SBATCH --partition=debug
#SBATCH --mem=90000
#SBATCH --ntasks=1


#make folder with job ID
mkdir Results/output_PID-$SLURM_JOB_ID


cd pipeline_code


echo STARTING AT $(date)
source ~/.bashrc

# Activate Conda environment
conda activate SE3nv2.0

# Print GPU information
nvidia-smi





# RFdiffusion and ProteinMPNN
srun python3 main.py



#Alphafold
cd ..


chmod +x OnlyAF_new.sh
./OnlyAF_new.sh




mv pipeline_code/RFdiffusion_tmp_output Results/output_PID-$SLURM_JOB_ID/RFdiffusion_pdbs #move the RFdiffusion output
mv pipeline_code/Sequences/seqs Results/output_PID-$SLURM_JOB_ID/sequences #move the sequences
mv Output-$SLURM_JOB_ID/* Results/output_PID-$SLURM_JOB_ID/AF_output


rm -rf pipeline_code/Sequences #remove empty file:
rm -rf Output-$SLURM_JOB_ID

cd pipeline_code

srun python3 compare.py
