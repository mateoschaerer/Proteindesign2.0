import subprocess
import yaml
import os
import shutil
import subprocess
from main_tools import extract_residues_from_PDB, index_contigs_in_generated_sequence, extract_contig_from_residue_table


def RunRFdiffusion(config_path):
    script_path = 'RFdiffusion/scripts/run_inference.py'

    command = [script_path]

    def add_to_command(key, value):
        if value is not None:
            command.append(f"{key}={value}")

    # Load YAML configuration
    with open(config_path, 'r') as yaml_file:
        config = yaml.safe_load(yaml_file)

    add_to_command('inference.input_pdb', config["inference"]["input_pdb"])
    add_to_command('inference.num_designs', config["inference"]["num_designs"])
    add_to_command('inference.output_prefix', "RFdiffusion_tmp_output/"+config["inference"]["design_name"])
    add_to_command('contigmap.contigs', config["contigmap"]["contigs"])
    add_to_command('ppi.hotspot_res', config["ppi"]["hotspot_res"])

    # Run the subprocess
    subprocess.call(command)


    



def RunProteinMPNN(config_path):
    

    # get stuff needed for MPNN
    with open(config_path, "r") as stream:
        try:
            config = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print("Could not parse yaml file")
            print(exc)

    num_seq_per_target = num_seq_per_target = int(config["for_rest_of_script"]["num_seq_per_target"])
    design_name = config["inference"]["design_name"]
    contigs = config["for_rest_of_script"]["contigs_AS"][0]
    input_pdb = config["inference"]["input_pdb"]
    binder_mode = bool(config["for_rest_of_script"]["binder_mode"])


    os.mkdir("Sequences")
    cur_res_dir = "Sequences"


    # get 
    if contigs is not None:
         path_for_parsed_chains   = os.path.join(cur_res_dir, "parsed_pdbs.jsonl")
         path_for_assigned_chains = os.path.join(cur_res_dir, "assigned_pdbs.jsonl")
         path_for_fixed_positions = os.path.join(cur_res_dir, "fixed_pdbs.jsonl")

        # get contigs as list of strings
         all_residues = extract_residues_from_PDB(input_pdb)
         contigs_as_list_of_strings = extract_contig_from_residue_table(all_residues,contigs)[2]

        # ProteinMPNN: parse the chains
         subprocess.run(["python",
                         "ProteinMPNN/helper_scripts/parse_multiple_chains.py",
                         "--input_path=RFdiffusion_tmp_output" ,
                         "--output_path=" + path_for_parsed_chains,])



         # ProteinMPNN: assign the fixed chains (we only have a single chain A)
         subprocess.run(["python",
                         "ProteinMPNN/helper_scripts/assign_fixed_chains.py",
                          "--input_path=" + path_for_parsed_chains,
                          "--output_path=" + path_for_assigned_chains,
                          "--chain_list=A",])

    # iterate through all .pdb files in the RFdiffusion_tmp output directory this will create sequenecs in Sequences/seqs directory
    for pdb in [os.path.join("RFdiffusion_tmp_output", file) for file in os.listdir("RFdiffusion_tmp_output") if file.endswith(".pdb")]:
        if contigs is None:  # for Unconditional rus
            subprocess.run([
                "python",
                "ProteinMPNN/protein_mpnn_run.py",
                "--pdb_path", pdb,
                "--pdb_path_chains", "A",
                "--out_folder", cur_res_dir,
                "--num_seq_per_target", str(num_seq_per_target),
                "--sampling_temp", "0.1",
                "--seed", "37",
                "--batch_size", "1",
            ])
        else:
            all_residues_of_design = extract_residues_from_PDB(pdb)
            not_contig_indices = index_contigs_in_generated_sequence(all_residues_of_design, contigs_as_list_of_strings)[1]
            variable_positions = ' '.join([str(num) for num in not_contig_indices])
            # ProteinMPNN: produce dict (jsonl) with non fixed positions
            # (these residues will be changed by ProteinMPNN)
            subprocess.run(["python",
                            "ProteinMPNN/helper_scripts/make_fixed_positions_dict.py",
                            "--input_path=" + path_for_parsed_chains,
                            "--output_path=" + path_for_fixed_positions,
                            "--chain_list=A",
                            "--position_list=" + variable_positions,
                            "--specify_non_fixed",])
            


            # Run ProteinMPNN using all the previously generated files
            subprocess.run(["python",
                            "ProteinMPNN/protein_mpnn_run.py",
                            "--pdb_path=" + pdb,
                            "--jsonl_path=" + path_for_parsed_chains,
                            "--chain_id_jsonl=" + path_for_assigned_chains,
                            "--fixed_positions_jsonl=" + path_for_fixed_positions,
                            "--out_folder=" + cur_res_dir,
                            "--num_seq_per_target=" + str(num_seq_per_target),
                            "--sampling_temp=0.1",
                            "--seed=37",
                            "--batch_size=1",])


             

    print("no issues up to here")
    # parse the sequences to avoid recognition as a multimer
    for fasta_path in [os.path.join("Sequences/seqs", file) for file in os.listdir("Sequences/seqs")]:

        # get the design name + design num
        file_name = os.path.basename(fasta_path)
        design_name = os.path.splitext(file_name)[0]

        with open(fasta_path, 'r') as fasta_file:
            sequences = fasta_file.read().split('>')[1:]

            for num_seq, seq in enumerate(sequences):
                seq_lines = seq.strip().split('\n')
                header = seq_lines[0]
                sequence = ''.join(seq_lines[1:])


                #for binder mode need to take the first part after the split
                sequence = sequence.split("/")[0]
                

                if num_seq != 0:
                    # Create a new file for each sequence in the AF_job directory
                    output_file_path = os.path.join("../AF_current_job", f"{design_name}_sample={num_seq}.fa")
                    with open(output_file_path, 'w') as output_file:

                        # ignore the first fasta file as this comes from RF and is garbage
                        output_file.write(f">{header}\n{sequence}\n")
                        print(f"Sequence written to {output_file_path}")
   


