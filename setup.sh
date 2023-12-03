#!/bin/bash

user="${1}"
if [[ "$user" == "" ]]; then
	    echo -e "\e[93;1mMust specify username\e[0m"
	        exit 1
fi

pip install --upgrade pip

#move into code directory

cd pipeline_code

# Miniconda3---------------------------------------------------------------------------------------------------------


wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
echo -e "\e[91;1m│ Install conda to /home/$user/miniconda3 │\e[0m"
bash Miniconda3-latest-Linux-x86_64.sh -b
source ~/.bashrc

# remove the install script
rm -rf Miniconda3-latest-Linux-x86_64.sh

conda init
conda update conda



#RFdiffusion---------------------------------------------------------------------------------------------

#clone the git
git clone https://github.com/RosettaCommons/RFdiffusion.git

cd RFdiffusion
mkdir models && cd models
wget http://files.ipd.uw.edu/pub/RFdiffusion/6f5902ac237024bdd0c176cb93063dc4/Base_ckpt.pt
wget http://files.ipd.uw.edu/pub/RFdiffusion/e29311f6f1bf1af907f9ef9f44b8328b/Complex_base_ckpt.pt
wget http://files.ipd.uw.edu/pub/RFdiffusion/60f09a193fb5e5ccdc4980417708dbab/Complex_Fold_base_ckpt.pt
wget http://files.ipd.uw.edu/pub/RFdiffusion/74f51cfb8b440f50d70878e05361d8f0/InpaintSeq_ckpt.pt
wget http://files.ipd.uw.edu/pub/RFdiffusion/76d00716416567174cdb7ca96e208296/InpaintSeq_Fold_ckpt.pt
wget http://files.ipd.uw.edu/pub/RFdiffusion/5532d2e1f3a4738decd58b19d633b3c3/ActiveSite_ckpt.pt
wget http://files.ipd.uw.edu/pub/RFdiffusion/12fc204edeae5b57713c5ad7dcb97d39/Base_epoch8_ckpt.pt
wget http://files.ipd.uw.edu/pub/RFdiffusion/f572d396fae9206628714fb2ce00f72e/Complex_beta_ckpt.pt

# original structure prediction weights
wget http://files.ipd.uw.edu/pub/RFdiffusion/1befcb9b28e2f778f53d47f18b7597fa/RF_structure_prediction_weights.pt

cd /home/$user/Proteindesign2.0/pipeline_code

#install the SE3 enviroment
conda env create -f SE3nv-cuda11.7.yml
conda activate SE3nv2.0


# add modules for the rest of the script to the env 
pip install spython
pip install yaml
pip install absl-py

cd RFdiffusion/env/SE3Transformer
pip install --no-cache-dir -r requirements.txt
python setup.py install
cd ../.. # change into the root directory of the repository
pip install -e . # install the rfdiffusion module from the root of the repository

cd /home/$user/Proteindesign2.0/pipeline_code
#Protein MPNN -----------------------------------------------------------------------------------------
git clone https://github.com/dauparas/ProteinMPNN.git

#prepare output folders
cd ..
mkdir Results
mkdir AF_current_job

echo "FINISHED"
