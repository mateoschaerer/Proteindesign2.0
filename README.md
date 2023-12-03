# Table of Contents
1. [Installation](#installation)
2. [Usage](#usage)
   - [Upload a PDB file from the local computer](#1-upload-a-pdb-file-from-local-computer)
   - [Modify the config.yaml file](#2-modify-the-configyaml-file)
   - [Submit a job to IZAR](#3-submit-a-job-to-izar)
   - [Download results to the local computer](#4-download-results-to-local-computer)
3. [Only Alphafold runs](#only-alphafold-runs)
4. [Results](#results)
   - [Interpreting results](#interpreting-results)

# Installation
## 0. Connect to EPFL WIFI
If you're not on an EPFl network you must use a VPN

More info can be found here: https://www.epfl.ch/schools/sb/research/iphys/wp-content/uploads/2019/06/Welcome_IPHYS-IT.pdf

## 1. Setup

1. Make sure you have an account on izar. Contact Sahand. Throughout, I will be refering to your username when I write <gaspar username>

2. ssh into izar
```bash
ssh <gaspar username>@izar.epfl.ch
```

3. Clone this repository

```bash
git clone https://github.com/mateoschaerer/Proteindesign2.0.git
```

Note that downloading the repository from the command line requires a different authentication method than logging into the github web site. Your regular password should not work for downloading the repository. You have to create a token through the github password (or find another way to authenticate). The process is described on this web site:

https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens#creating-a-personal-access-token-classic

## 2. Download models

```bash
cd Proteindesign2.0
source setup.sh gasparusername
```
When prompted to contiue type y/yes

# Usage
## 1. Upload a pdb file from local computer
If you are connected to izar, close the connection:
```bash
exit
```
Then run the following command:
```bash
scp "path/to/pdb/file" gasparusername@izar.epfl.ch:/home/gasparusername/Proteindesign2.0/RFdiffusion_input
```
replace "path\to\pdb\location" with the path to the pdb file on your local computer. Make sure to keep the quotation marks! In windows this can be obtained by right clicking on the pdb file and selecting "copy as path" 

## 2.Modify the config.yaml file:
```bash
vi config.yaml
```
Once in the config.yaml file, press I until --insert-- apears on the bottom lefthand side of the window. Now you can edit the file, which should contain these lines:

```bash
for_rest_of_script:
  binder_mode: True
  num_seq_per_target: 1
  contigs_AS: [A20-100] # for binders this is the target residues
inference:
  design_name: "test_binder_final"
  input_pdb: "RFdiffusion_input/4n5t.pdb"
  num_designs: 1

contigmap:
  contigs: [A20-100/0 100-100]

ppi:
  hotspot_res: null
```
1. Insert the name of the pdb file in the input_pdb variable. (replace only the 4n5t.pdb with your input pdb)
2. specify design name
3. Change the binder_mode variable to "True" for binder design. For all other application set this to "False"
5. Add active cite contigs and RFdiffusion contigs.
6. Specify the number of designs to create aswell as the number of sequences per design by modifing num_designs and num_seq_per_target variables.
7. Once this is done press esc key till --insert-- disappears from bottom left hand side of the screen.
8. Type :wq to save and exit.

For binder design make sure to also:
1. Set the binder design variable to "True"
2. Set the AS_contig variable to the target of the pdb onto which you're designing binders
3. If you want specific residues to interact with the binder this can be specified as a list given in the hotspot_residues variable

## 3. Submit a job to IZAR
 ```bash
sbatch run.sh
```
You can check up on it's progress using this command:
 ```bash
squeue -u gasparusername
```

## 4. Download results to local computer
If you are connected to izar run the following command:
```bash
exit
```
Then run:
```bash
scp -r gasparusername@izar.epfl.ch:/home/gasparusername/Proteindesign2.0/Results "path\to\local\storage_file"

```
To get the path, similar to pdb file right click on folder where you want the results to be downloaded and select "copy as path".

# Only Alphafold runs
To only use Alphafold upload your fasta files the AF_current_job directory. Make sure they **end with .fa and contain only 1 sequence** then submit the job as follows:

```bash
sbatch OnlyAF_new.sh

```
The results will appear in a directory labeld Output-jobID.

 
# Results
## Interpreting results
**AF_output:**

This directory encapsulates the outcomes of a specific computational job, uniquely identified by its SlurmID (e.g., output_PID-1513444).
for example  test_binder_final_0_sample=1, corresponding to design 0 and sequence 1. Inside the test_binder_final_0_sample=1 directory, various PDB files are present (ranked_0.pdb, ranked_1.pdb, ..., ranked_4.pdb). If you need the AF output you'll need to use the ranked_0.pdb 

**RFdiffusion_pdbs:**

This directory holds PDB-related files for the RFdiffusion model. Use the .pdb files not the .traj files.

**Sequences:**

Located in the sequences directory you'll find a fasta file for every RFdiffusion design. In this fasta you'll have all the sequences that belong to the design.

**Summary.txt:**

This file contains RMSD values of every sequence created for the project.




Results file tree for reference:
```
Results
└── output_PID-1513444
    ├── AF_output
    │   ├── ld.so.cache
    │   └── test_binder_final_0_sample=1
    │       ├── features.pkl
    │       ├── msas
    │       │   ├── mgnify_hits.sto
    │       │   ├── pdb_hits.hhr
    │       │   ├── small_bfd_hits.sto
    │       │   └── uniref90_hits.sto
    │       ├── ranked_0.pdb
    │       ├── ranked_1.pdb
    │       ├── ranked_2.pdb
    │       ├── ranked_3.pdb
    │       ├── ranked_4.pdb
    │       ├── ranking_debug.json
    │       ├── relaxed_model_1_pred_0.pdb
    │       ├── relax_metrics.json
    │       ├── result_model_1_pred_0.pkl
    │       ├── result_model_2_pred_0.pkl
    │       ├── result_model_3_pred_0.pkl
    │       ├── result_model_4_pred_0.pkl
    │       ├── result_model_5_pred_0.pkl
    │       ├── timings.json
    │       ├── unrelaxed_model_1_pred_0.pdb
    │       ├── unrelaxed_model_2_pred_0.pdb
    │       ├── unrelaxed_model_3_pred_0.pdb
    │       ├── unrelaxed_model_4_pred_0.pdb
    │       └── unrelaxed_model_5_pred_0.pdb
    ├── RFdiffusion_pdbs
    │   ├── test_binder_final_0.pdb
    │   ├── test_binder_final_0.trb
    │   └── traj
    │       ├── test_binder_final_0_pX0_traj.pdb
    │       └── test_binder_final_0_Xt-1_traj.pdb
    ├── sequences
    │   └── test_binder_final_0.fa
    └── summary.txt


```


