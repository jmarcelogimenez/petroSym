import PyFoam
import PyFoam.FoamInformation
assert len(PyFoam.FoamInformation.foamTutorials()) > 0
print 'OpenFoam tutorials detected'
print PyFoam.FoamInformation.foamTutorials()
