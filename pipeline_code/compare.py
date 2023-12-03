from main_tools import CompareTwoPDBs, CompareTwoPDBs_binder, extract_contig_from_residue_table, extract_residues_from_PDB
import os
import glob
import yaml
import re



def CompareAFtoOriginal(contigs, original_pdb_file, AF_pdb, slurmID, output_dir):
    with open(f"{output_dir}/summary.txt", "a") as summary_file:            
        rmsd, mean_conf_AF, min_conf_AF, max_conf_AF = CompareTwoPDBs(contigs, original_pdb_file, AF_pdb)

        summary_file.write(f"{design}    {rmsd} A    {mean_conf_AF}  {min_conf_AF}   {max_conf_AF}\n")

 
def CompareAFtoBinder(design, AF_pdb, slurmID, output_dir):
    print(design)

    # get the RFdiffusion PDB for the binder
    RF_design_name = re.sub(r'_sample=\d+', '', design)
    
    RF_pdb = f"{output_dir}/RFdiffusion_pdbs/{RF_design_name}.pdb"
    
    # compare the binders
    rmsd =CompareTwoPDBs_binder(AF_pdb, RF_pdb)

    #save the rmsd to summary file
    with open(f"{output_dir}/summary.txt", "a") as summary_file:
        summary_file.write(f"{design}    {rmsd} A\n")

if __name__ == "__main__":
    with open("../config.yaml", "r") as stream:
        try:
            config = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print("Could not parse custom.yaml file :")
            print(exc)

    
    #get the jobID
    slurmID = os.environ.get('SLURM_JOB_ID')
    #slurmID = 1513145
    output_dir = f"../Results/output_PID-{slurmID}"

    # Get input file name
    original_pdb_file = config["inference"]["input_pdb"]
    binder_mode = bool(config["for_rest_of_script"]["binder_mode"])
    contigs = config["for_rest_of_script"]["contigs_AS"][0]

    #create the summary file
    summary_file=f"{output_dir}/summary.txt"
    

    # make the file header
    with open(f"{output_dir}/summary.txt", "w") as summary_file:
        summary_file.write("Filename\t RMSD\t mean_conf_AF\t min_conf_AF\t max_conf_AF\n")

    

    for design in os.listdir(f"{output_dir}/AF_output"):
        if design != 'ld.so.cache':
            AF_pdb = f"{output_dir}/AF_output/{design}/ranked_0.pdb"
            if binder_mode:
                CompareAFtoBinder(design, AF_pdb,slurmID, output_dir)
            else:
                CompareAFtoOriginal(contigs, original_pdb_file, AF_pdb,slurmID, output_dir)













