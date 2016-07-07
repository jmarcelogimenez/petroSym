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

To avoid an intrusive rendering during simulations, please comment (add a # at the beginning of) the line 300 of the file 
    
    PATH_TO_INSTALLATION/PyFoam/Applications/PVSnapshot.py

To check if PyFoam was succesfully installed, try:

    python check_PyFoam.py

Before installing or using petroSym, make sure the OpenFOAM environment variables are set by the following command:

    source /opt/openfoam240/etc/bashrc

After setting the OpenFOAM variables, run this script:

    ./install_extras.sh

Installation is based on setuptools. The --record option is important to uninstall files successfully:

    sudo python setup.py install --record installation_files.txt

If you want to install petroSym in a python virtual enviroment, you must create symbolic link of PyQt4 and sip:

    ln -s /usr/lib/python2.7/dist-packages/PyQt4/ ~/.virtualenvs/myEnv/lib/python2.7/site-packages/
    ln -s /usr/lib/python2.7/dist-packages/sip.so ~/.virtualenvs/myEnv/lib/python2.7/site-packages/

Then, you must run the setup.py without "sudo":

    python setup.py install --record installation_files.txt

Testing
-------

Try:

    petroSym

Cleaning
-------

To run the cleaner run:

    python setup.py clean
