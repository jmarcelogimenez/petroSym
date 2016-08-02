#!/bin/bash

echo "Updating petroSym"
cd ..
sudo rm -r petroSym
git clone https://github.com/jmarcelogimenez/petroSym.git
cd petroSym
sudo pip install -r requirements.txt
source /opt/openfoam240/etc/bashrc
./install_extras.sh
sudo python setup.py install --record installation_files.txt
echo "Finished"
