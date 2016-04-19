#!/bin/bash

#---Eliminar lo compilado por ./install_foam_utilities
export FOAM_MPI_INCLUDE=$WM_THIRD_PARTY_DIR/platforms/$WM_ARCH$WM_COMPILER/$FOAM_MPI/include
rm -rf dist build petroSym.egg-info #Borra la carpeta build y egg.info (de la carpeta de instalacion, no del sistema)
pushd .
cd utilitiesFoam
cd dirFeaturesFoam
wclean
rm -rf build
cd ../meshQuality
wclean
rm -rf build
cd ../meshQualityFaceSet
wclean
rm -rf build
cd ../meshQualitySubSet
wclean
rm -rf build
popd

#---Borrar cosas varias 

find . -iname "*~" | xargs rm -f #Busca y remueve ~
find . -iname "*log" | xargs rm -f #Busca y remueve logs
find . -iname "*pyc" | xargs rm -f #Busca y remueve .pyc

#---Desinstalar paquetes instalados

cat installation_files.txt | sudo xargs rm -rf #Desinstala todo, quedan las carpetas vacias. Para borrar las carpetas hay que hacerlo manualmente
cat dirtoremove.txt | sudo xargs rm -rf
rm installation_files.txt
rm dirtoremove.txt
