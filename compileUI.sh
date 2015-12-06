# Pasarlo al setup.py
# https://pypi.python.org/pypi/pyqt-distutils/
# https://gist.github.com/geeksunny/3174947
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
cp petroSym/matplotlibrc ~/.config/matplotlib/.
