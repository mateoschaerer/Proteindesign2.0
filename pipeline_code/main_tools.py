import numpy as np

def extract_residues_from_PDB(pdb_file):

    # A dictionary mapping three-letter amino acid codes to one-letter codes
    three_to_one = {
        'ALA': 'A', 'CYS': 'C', 'ASP': 'D', 'GLU': 'E', 'PHE': 'F',
        'GLY': 'G', 'HIS': 'H', 'ILE': 'I', 'LYS': 'K', 'LEU': 'L',
        'MET': 'M', 'ASN': 'N', 'PRO': 'P', 'GLN': 'Q', 'ARG': 'R',
        'SER': 'S', 'THR': 'T', 'VAL': 'V', 'TRP': 'W', 'TYR': 'Y'
    }

    # Initialize an empty list to store the amino acid positions
    amino_acids = []

    # Read the PDB file and extract the amino acid positions
    with open(pdb_file, 'r') as file:
        for line in file:
            if line.startswith('ATOM'):
                amino_acid = line[17:20].strip()
                strand_letter = line[21]
                if amino_acid in three_to_one:
                    amino_acid = three_to_one[amino_acid]
                    position = int(line[22:26])
                    confidence = int(float(line[60:66]))
                    amino_acids.append((amino_acid, strand_letter, position, confidence))

    # Remove consecutive duplicate entries from the amino acids list
    residue_table = [] # filtered amino_acids
    for i, entry in enumerate(amino_acids):
        if i == 0 or entry[0:3] != amino_acids[i - 1][0:3]: # this caused a huge bug. In experimental PDB structures, the "confidence" varies from atom to atom
            residue_table.append(entry)
            
    # Print the table of unique amino acid codes, strand letter, and positions
    return residue_table



def extract_contig_from_residue_table(residue_table,contigs):

    contigs_as_list_of_strings = []

    # Process the entries in the input string
    in_contig_amino_acids = []
    for entry in contigs.split('/'):
        if entry[0].isalpha():
            letter = entry[0]
            start, end = map(int, entry[1:].split('-'))
            contig_string = ""
            for amino_acid, strand_letter, position, confidence in residue_table:
                if strand_letter == letter and start <= position <= end:
                    in_contig_amino_acids.append((amino_acid, strand_letter, position, confidence))
                    contig_string = contig_string + amino_acid
            contigs_as_list_of_strings.append(contig_string)
                    
    # Remove in_contig_amino_acids from residue_table
    variable_amino_acids = [row for row in residue_table if row not in in_contig_amino_acids]
                    

    return in_contig_amino_acids, variable_amino_acids, contigs_as_list_of_strings
    
    

def index_contigs_in_generated_sequence(residue_table, contigs_as_list_of_strings):
    # Extract the amino acid sequence from residue_table
    sequence = "".join(row[0] for row in residue_table)

    # Find positions and matching characters of consecutive strings in the sequence
    positions = []
    all_matching_positions = []
    all_matching_positions_resIDs = []
    confidences_of_residues = [] # snuck the list of confidences in here because would otherwise have to write exact same code all over again
    for string in contigs_as_list_of_strings:
        start = 0
        while True:
            position = sequence.find(string, start)
            if position == -1:
                break
            positions.append(position + 1)  # Add 1 to match position in protein
            matching_positions = range(position + 1, position + len(string) + 1)
            all_matching_positions.extend(matching_positions)
            for i_position in range(position,position+len(string)):
                all_matching_positions_resIDs.append(residue_table[i_position][2])
                confidences_of_residues.append(residue_table[i_position][3])
            start = position + 1

    # Find indices of characters not in all_matching_positions
    not_matching_indices = [i + 1 for i, char in enumerate(sequence) if i + 1 not in all_matching_positions]

    return all_matching_positions, not_matching_indices, all_matching_positions_resIDs, confidences_of_residues



# residue_table = extract_residues_from_PDB(pdb_file)

# in_contig_amino_acids, variable_amino_acids, contigs_as_list_of_strings = extract_contig_from_residue_table(residue_table,contigs)

# all_matching_positions, not_matching_indices = index_contigs_in_generated_sequence(residue_table, contigs_as_list_of_strings)



def parse_pdb_file(file_path):
    # Parse the PDB file and extract atom coordinates and residue IDs
    atom_coords = []
    residue_ids = []
    with open(file_path, 'r') as pdb_file:
        for line in pdb_file:
            if line.startswith('ATOM'):
                x = float(line[30:38])
                y = float(line[38:46])
                z = float(line[46:54])
                residue_id = int(line[22:26]) # only number, no chain ID
                atom_coords.append([x, y, z])
                residue_ids.append(residue_id)
    return np.array(atom_coords), residue_ids



def compute_centroid(coords):
    # Compute the centroid of a set of coordinates
    return np.mean(coords, axis=0)



def compute_rmsd(coords1, coords2):
    # Compute the RMSD between two sets of coordinates
    diff = coords1 - coords2
    rmsd = np.sqrt(np.mean(np.sum(diff**2, axis=1)))
    return rmsd


    
def sort_atoms_by_type(pdb_file):
    # Open the PDB file
    with open(pdb_file, 'r') as file:
        lines = file.readlines()

    # Filter and sort the atoms for each residue
    residues = {}
    current_residue = None
    for line in lines:
        if line.startswith('ATOM'):
            residue_pos = int(line[22:26].strip())
            atom_type = line[12:16].strip()

            # Skip hydrogen atoms
            if atom_type.startswith('H'):
                continue

            # Create a new residue entry
            if residue_pos not in residues:
                residues[residue_pos] = []

            residues[residue_pos].append(line)

    # Sort the atoms by atom type within each residue
    sorted_lines = []
    for residue_pos, atoms in sorted(residues.items()):
        sorted_atoms = sorted(atoms, key=lambda x: x[12:16])
        sorted_lines.extend(sorted_atoms)

    # Save the sorted PDB file
    output_file = pdb_file.split('.pdb')[0] + '_sorted.pdb'
    with open(output_file, 'w') as file:
        file.writelines(sorted_lines)

    print(f"Sorted PDB file saved as: {output_file}")



def rigid_alignment(ref_file, mov_file, ref_aa_names, mov_aa_names):

    # Sort atoms in PDB files and delete hydrogens
    sort_atoms_by_type(ref_file)
    sort_atoms_by_type(mov_file)

    # Parse the reference and mobile PDB files
    ref_coords, ref_residues = parse_pdb_file(ref_file.split('.pdb')[0] + '_sorted.pdb')
    mov_coords, mov_residues = parse_pdb_file(mov_file.split('.pdb')[0] + '_sorted.pdb')

    # Select the specified amino acids for alignment
    ref_indices = [i for i, res_id in enumerate(ref_residues) if res_id in ref_aa_names]
    mov_indices = [i for i, res_id in enumerate(mov_residues) if res_id in mov_aa_names]

    # Select the coordinates for the selected amino acids
    ref_selected_coords = ref_coords[ref_indices]
    mov_selected_coords = mov_coords[mov_indices]

    # Compute the centroids of the selected sets
    ref_centroid = compute_centroid(ref_selected_coords)
    mov_centroid = compute_centroid(mov_selected_coords)

    # Center the selected sets by subtracting the centroids
    ref_centered_coords = ref_selected_coords - ref_centroid
    mov_centered_coords = mov_selected_coords - mov_centroid
     
    # Compute the rotation matrix using singular value decomposition (SVD)
    H = np.dot(ref_centered_coords.T, mov_centered_coords)
    U, S, Vt = np.linalg.svd(H)
    R = np.dot(Vt.T, U.T)

    # Apply the rotation and translation to the mobile coordinates
    rotated_mov_coords = np.dot(mov_coords - mov_centroid, R) + ref_centroid
    
    # Compute the RMSD between the specified sets of amino acids
    rmsd = compute_rmsd(ref_selected_coords, rotated_mov_coords[mov_indices])

    return rotated_mov_coords, rmsd



def update_pdb_coordinates(input_file, output_file, new_coords):
    # Update the coordinates in the PDB file while preserving the rest of the information
    with open(input_file, 'r') as input_pdb, open(output_file, 'w') as output_pdb:
        for i, line in enumerate(input_pdb):
            if line.startswith('ATOM'):
                atom_line = line[:30] + f"{new_coords[i, 0]:8.3f}{new_coords[i, 1]:8.3f}{new_coords[i, 2]:8.3f}" + line[54:]
                output_pdb.write(atom_line)
            else:
                output_pdb.write(line)



def CompareTwoPDBs(contigs, ref_pdb_file, mov_pdb_file):

    res_table1 = extract_residues_from_PDB(ref_pdb_file)
    contigs_as_list_of_strings = extract_contig_from_residue_table(res_table1,contigs)[2]
    all_matching_positions_resIDs1 = index_contigs_in_generated_sequence(res_table1, contigs_as_list_of_strings)[2]

    res_table2 = extract_residues_from_PDB(mov_pdb_file)
    all_matching_positions_resIDs2 = index_contigs_in_generated_sequence(res_table2, contigs_as_list_of_strings)[2]
    confidences_of_residues        = index_contigs_in_generated_sequence(res_table2, contigs_as_list_of_strings)[3]

    # Perform rigid alignment and compute RMSD
    rotated_coords, rmsd = rigid_alignment(ref_pdb_file, mov_pdb_file, all_matching_positions_resIDs1, all_matching_positions_resIDs2)

    ## Update the coordinates in the mobile PDB file
    update_pdb_coordinates(mov_pdb_file.split('.pdb')[0] + '_sorted.pdb', mov_pdb_file.split('.pdb')[0] + '_sorted-aligned.pdb', rotated_coords)

    return rmsd, sum(confidences_of_residues)/len(confidences_of_residues), min(confidences_of_residues), max(confidences_of_residues)
#    print(f"RMSD: {rmsd:.3f}")


def parse_pdb_backbone_binders(pdb_file, chain_id='A'):
    backbone_atoms = []
    with open(pdb_file, "r") as file:
        for line in file:
            if line.startswith("ATOM"):
                atom_name = line[12:16].strip()
                chain = line[21]
                if atom_name in ("N", "CA", "C") and chain == chain_id:
                    x = float(line[30:38])
                    y = float(line[38:46])
                    z = float(line[46:54])
                    backbone_atoms.append((atom_name, (x, y, z)))
    return backbone_atoms


def align_pdb_backbones(reference_atoms, moving_atoms):
    if len(reference_atoms) != len(moving_atoms):
        raise ValueError("The two structures have different numbers of backbone atoms.")

    # Convert atom coordinates to NumPy arrays
    ref_coords = np.array([atom[1] for atom in reference_atoms])
    mov_coords = np.array([atom[1] for atom in moving_atoms])

    # Calculate the centroids for both structures
    ref_centroid = np.mean(ref_coords, axis=0)
    mov_centroid = np.mean(mov_coords, axis=0)

    # Translate both structures to align centroids
    ref_aligned = ref_coords - ref_centroid
    mov_aligned = mov_coords - mov_centroid

    # Calculate the rotation matrix
    H = np.dot(ref_aligned.T, mov_aligned)
    U, _, Vt = np.linalg.svd(H)
    rotation_matrix = np.dot(Vt.T, U.T)

    # Apply the rotation matrix to the aligned moving atoms
    mov_rotated = np.dot(mov_aligned, rotation_matrix)

    # Translate the rotated moving atoms back to the reference centroid
    mov_final = mov_rotated + ref_centroid

    # Convert back to list of tuples for output
    aligned_atoms = [(atom[0], tuple(coord)) for atom, coord in zip(moving_atoms, mov_final)]

    return aligned_atoms

def calculate_rmsd_binders(reference_atoms, aligned_atoms):
    if len(reference_atoms) != len(aligned_atoms):
        raise ValueError("The two structures have different numbers of backbone atoms.")

    squared_sum = sum(
        np.sum((np.array(ref_coord) - np.array(aligned_coord)) ** 2) for (atom, ref_coord), (_, aligned_coord) in
        zip(reference_atoms, aligned_atoms))
    rmsd = np.sqrt(squared_sum / len(reference_atoms))

    return rmsd

def CompareTwoPDBs_binder(ref_pdb_file_path, mov_pdb_file_path):
    reference_atoms = parse_pdb_backbone_binders(ref_pdb_file_path)
    moving_atoms = parse_pdb_backbone_binders(mov_pdb_file_path)

    if len(reference_atoms) != len(moving_atoms):
        raise ValueError("The two structures have different numbers of backbone atoms.")

    # perform alignment only via the backbone
    aligned_atoms = align_pdb_backbones(reference_atoms, moving_atoms)

    # calculate RMSD of backbones
    rmsd = calculate_rmsd_binders(reference_atoms, aligned_atoms)
    print(f"RMSD of backbones: {rmsd:.2f} Å")

    return rmsd
