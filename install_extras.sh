#!/bin/bash
set -e
echo "Installing Foam Utilities"
export FOAM_MPI_INCLUDE=$WM_THIRD_PARTY_DIR/platforms/$WM_ARCH$WM_COMPILER/$FOAM_MPI/include

pushd .
cd utilitiesFoam
cd dirFeaturesFoam
wmake
cd ../meshQuality
wmake
cd ../meshQualityFaceSet
wmake
cd ../meshQualitySubSet
wmake
cd ../myParticle
wmake
cd ../particleTracking
wmake
cd ../snapshots
wmake
popd
echo "Finished"

echo "Compiling GUI Widgets"
pyrcc4 -o petroSym/resources_rc.py petroSym/resources.qrc
pyuic4 -w petroSym/petroSym.ui -o petroSym/petroSym_ui.py
pyuic4 -w petroSym/popUpNew.ui -o petroSym/popUpNew_ui.py
pyuic4 -w petroSym/popUpNewFigure.ui -o petroSym/popUpNewFigure_ui.py
pyuic4 -w petroSym/figureResiduals.ui -o petroSym/figureResiduals_ui.py
pyuic4 -w petroSym/figureTracers.ui -o petroSym/figureTracers_ui.py
pyuic4 -w petroSym/figureSampledLine.ui -o petroSym/figureSampledLine_ui.py
pyuic4 petroSym/runTimeControls.ui -o petroSym/runTimeControls_ui.py
pyuic4 petroSym/numericalSchemes.ui -o petroSym/numericalSchemes_ui.py
pyuic4 petroSym/solverSettings.ui -o petroSym/solverSettings_ui.py
pyuic4 petroSym/solutionModelingNew.ui -o petroSym/solutionModeling_ui.py
pyuic4 petroSym/materials.ui -o petroSym/materials_ui.py
pyuic4 -w petroSym/materialsABM.ui -o petroSym/materialsABM_ui.py
pyuic4 petroSym/mesh.ui -o petroSym/mesh_ui.py
pyuic4 -w petroSym/tracers.ui -o petroSym/tracers_ui.py
pyuic4 petroSym/run.ui -o petroSym/run_ui.py
pyuic4 petroSym/postpro.ui -o petroSym/postpro_ui.py
pyuic4 -w petroSym/bc.ui -o petroSym/bc_ui.py
pyuic4 petroSym/initialConditions.ui -o petroSym/initialConditions_ui.py
pyuic4 -w petroSym/reset.ui -o petroSym/reset_ui.py
pyuic4 -w petroSym/bcPatch.ui -o petroSym/bcPatch_ui.py
pyuic4 -w petroSym/blockmesh.ui -o petroSym/blockmesh_ui.py
pyuic4 -w petroSym/loading.ui -o petroSym/loading_ui.py
pyuic4 -w petroSym/solvers_info.ui -o petroSym/solvers_info_ui.py
pyuic4 -w petroSym/turbulence.ui -o petroSym/turbulence_ui.py
pyuic4 -w petroSym/gravity.ui -o petroSym/gravity_ui.py
pyuic4 -w petroSym/particleTracking.ui -o petroSym/particleTracking_ui.py

#Esto lo puse para que no se queje travis, pero supuestamente estos directorios a esta altura ya esta creados
#if [ ! -d ~/.config/ ]; then
#   mkdir ~/.config/ 
#fi
if [ ! -d ~/.config/matplotlib/ ]; then
   mkdir -p ~/.config/matplotlib/
fi
cp petroSym/matplotlibrc ~/.config/matplotlib/.

echo "Finished"
