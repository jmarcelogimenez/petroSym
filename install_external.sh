#!/bin/bash
set -e
# install pyFoam
mkdir -p pyfoam_install
wget https://openfoamwiki.net/images/3/3b/PyFoam-0.6.4.tar.gz -O pyfoam_install/pyfoam.tgz --no-check-certificate
tar -xzf pyfoam_install/pyfoam.tgz -C pyfoam_install
pip install --upgrade pyfoam_install/PyFoam-0.6.4
rm -fr pyfoam_install
source /opt/openfoam240/etc/bashrc
python check_PyFoam.py
