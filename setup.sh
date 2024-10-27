#!/bin/bash

# Check if a user is provided
user="${1}"
if [[ "$user" == "" ]]; then
    echo -e "\e[93;1mMust specify username\e[0m"
    exit 1
fi

# Move to the project directory
cd /home/$user/Protein-design-rcp

# Update pip
pip install --upgrade pip

# Download and install Miniconda for the user in /home/$user
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
echo -e "\e[91;1m│ Install conda to /home/$user/miniconda3 │\e[0m"
bash Miniconda3-latest-Linux-x86_64.sh -b -p /home/$user/miniconda3
rm -f Miniconda3-latest-Linux-x86_64.sh

# Set up the environment variables for Miniconda
export PATH="/home/$user/miniconda3/bin:$PATH"
source /home/$user/miniconda3/etc/profile.d/conda.sh

# Initialize conda and update
conda init
conda update -y conda

# Install the SE3 environment using the YAML file
cd /home/$user/Protein-design-rcp/pipeline_code
conda env create -f SE3nv-cuda11.7.yml
source activate SE3nv2.0

# Install additional modules required
pip install spython yaml absl-py

# RFdiffusion setup
git clone https://github.com/RosettaCommons/RFdiffusion.git
cd RFdiffusion
mkdir models && cd models

# Download model weights for RFdiffusion
wget http://files.ipd.uw.edu/pub/RFdiffusion/6f5902ac237024bdd0c176cb93063dc4/Base_ckpt.pt
wget http://files.ipd.uw.edu/pub/RFdiffusion/e29311f6f1bf1af907f9ef9f44b8328b/Complex_base_ckpt.pt
wget http://files.ipd.uw.edu/pub/RFdiffusion/60f09a193fb5e5ccdc4980417708dbab/Complex_Fold_base_ckpt.pt
wget http://files.ipd.uw.edu/pub/RFdiffusion/74f51cfb8b440f50d70878e05361d8f0/InpaintSeq_ckpt.pt
wget http://files.ipd.uw.edu/pub/RFdiffusion/76d00716416567174cdb7ca96e208296/InpaintSeq_Fold_ckpt.pt
wget http://files.ipd.uw.edu/pub/RFdiffusion/5532d2e1f3a4738decd58b19d633b3c3/ActiveSite_ckpt.pt
wget http://files.ipd.uw.edu/pub/RFdiffusion/12fc204edeae5b57713c5ad7dcb97d39/Base_epoch8_ckpt.pt
wget http://files.ipd.uw.edu/pub/RFdiffusion/f572d396fae9206628714fb2ce00f72e/Complex_beta_ckpt.pt
wget http://files.ipd.uw.edu/pub/RFdiffusion/1befcb9b28e2f778f53d47f18b7597fa/RF_structure_prediction_weights.pt

# Install RFdiffusion and SE(3)-Transformer
cd ..
pip install -e .

cd env/SE3Transformer
pip install --no-cache-dir -r requirements.txt
python setup.py install
cd ../.. # Go back to the RFdiffusion root directory
pip install -e .

# Clone and set up ProteinMPNN
cd /home/$user/Protein-design-rcp/pipeline_code
git clone https://github.com/dauparas/ProteinMPNN.git
cd ProteinMPNN
pip install -r requirements.txt

# Clone and set up AlphaFold
cd /home/$user/Protein-design-rcp
git clone https://github.com/deepmind/alphafold.git
cd alphafold
pip install -r requirements.txt

# Prepare output directories
cd /home/$user/Protein-design-rcp
mkdir -p Results AF_current_job

# Final message
echo "Setup complete. Miniconda installed, environments created, and dependencies installed."
