#!/bin/bash


echo -n "Do you want to update petroSym (y/n)? "
read answer
if echo "$answer" | grep -iq "^y" ;then
	echo "Updating petroSym..."
	sleep 2
	echo "Downloading the latest updates..."
	sleep 1
	git pull > LOG
	if cat LOG | grep 'Already up-to-date';then
		exit
		rm LOG
	fi
	rm LOG
	echo "Installing the new requirements..."
	sleep 1
	sudo pip install -r requirements.txt
	source /opt/openfoam240/etc/bashrc
	echo "Compiling the new widgets..."
	sleep 1
	./install_extras.sh
	echo "Installing the program..."
	sleep 1
	sudo python setup.py install --record installation_files.txt
	echo "Finished"  
else
	exit
fi
