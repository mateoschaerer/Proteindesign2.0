# 0. Connect to EPFL WIFI
If you're not on an EPFl network you must use a VPN

More info can be found here: https://www.epfl.ch/schools/sb/research/iphys/wp-content/uploads/2019/06/Welcome_IPHYS-IT.pdf

# 1. Setup

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

#2. Install

```bash
cd Proteindesign2.0
source setup.sh gasparusername
```
When prompted to contiue type y/yes


# 2. Upload a pdb file from local computer
If you are connected to izar, close the connection:
```bash
exit
```
Then run the following command:
```bash
scp "path/to/pdb/file" gasparusername@izar.epfl.ch:/home/gasparusername/Proteindesign2.0/RFdiffusion_input
```
replace "path\to\pdb\location" with the path to the pdb file on your local computer. Make sure to keep the quotation marks! In windows this can be obtained by right clicking on the pdb file and selecting "copy as path" 

# 3.Modify the config.yaml file:
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




# 4. Submit a job to IZAR
 ```bash
sbatch run.sh
```
You can check up on it's progress using this command:
 ```bash
squeue -u gasparusername
```

# 5. Downloading results to local computer
If you are connected to izar run the following command:
```bash
exit
```
Then run:
```bash
scp -r gasparusername@izar.epfl.ch:/home/gasparusername/Proteindesign2.0/Results "path\to\local\storage_file"

```
To get the path, similar to pdb file right click on folder where you want the results to be downloaded and select "copy as path".



