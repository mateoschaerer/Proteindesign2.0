import yaml
from run_models import RunRFdiffusion, RunProteinMPNN
from main_tools import extract_residues_from_PDB, extract_contig_from_residue_table
import os


if __name__ == "__main__":
    RunRFdiffusion("../config.yaml")
    RunProteinMPNN("../config.yaml")
