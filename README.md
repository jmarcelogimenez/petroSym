# petroSym
Graphical User Interface for OpenFOAM oriented to petroleum simulations

Repository
----------

petroSym is hosted on github: https://github.com/jmarcelogimenez/petroSym

Requirements
------------

- OpenFOAM 2.4
- Paraview

run:

    sudo add-apt-repository http://www.openfoam.org/download/ubuntu
    sudo apt-get update -qq
    sudo apt-get install -y --force-yes openfoam240
    sudo apt-get install paraviewopenfoam410
    sudo apt-get install libfreetype6-dev libpng12-dev
    sudo apt-get install python-pip python2.7-dev libxext-dev python-qt4 pyqt4-dev-tools build-essential

Installation
------------

Package petroSym requires python 2.7, matplotlib>=1.5.0, PyQt and pyFoam 0.6.4:

    pip install -r requirements.txt
    ./install_foam_utilities.sh

Before installing or using petroSym, make sure the OpenFOAM environment variables are set by the following command:

    source /opt/openfoam240/etc/bashrc

Installation is based on setuptools. The --record option is important to uninstall files successfully:

    sudo python setup.py install --record installation_files.txt


Testing
-------

Try:

    petroSym

Cleaning
-------

To run the cleaner run:

    python setup.py clean
