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

Installation in the system (Option 1)
-------------------------------------

If you want to install PetroSym in your system, please follow this steps.

1.0) First of all, clone the repository in your system:

    git clone https://github.com/jmarcelogimenez/petroSym.git
    cd petroSym

1.1) Package petroSym requires python 2.7, matplotlib>=1.5.0, PyQt and pyFoam 0.6.4:

    sudo pip install -r requirements.txt

1.2) Before installing or using petroSym, make sure the OpenFOAM environment variables are set by the following command:

    source /opt/openfoam240/etc/bashrc

1.3) After setting the OpenFOAM variables, run this script:

    ./install_extras.sh

1.4) Installation is based on setuptools. The --record option is important to uninstall files successfully:

    sudo python setup.py install --record installation_files.txt

Installation in a virtual environment (Option 2)
------------------------------------------------

2.0) To install the virtualenv packages, run the following script:
    
    sudo apt-get install python-virtualenv

2.1) Then, to create the virtual environment, run:

    virtualenv "Myvirtualenv"

2.2) To activate the virtual environment, run:

    cd "Myvirtualenv"
    source bin/activate

2.3) Then, follow the steps 1.0 to 1.3 (In step 1.1, run the command without sudo)

2.4) In order to make it work, you must create symbolic link of PyQt4 and sip:

    ln -s /usr/lib/python2.7/dist-packages/PyQt4/ PATH_OF_THE_VIRTUALENV/lib/python2.7/site-packages/
    ln -s /usr/lib/python2.7/dist-packages/sip.so PATH_OF_THE_VIRTUALENV/lib/python2.7/site-packages/

2.5) Then, you must run the setup.py without "sudo":

    python setup.py install --record installation_files.txt

Testing
-------

Try:

    petroSym

Updating
--------

In order to update petroSym, run the following script:

    ./update_petroSym.sh

Cleaning
-------

To run the cleaner run:

    python setup.py clean
