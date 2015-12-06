#!/bin/bash
set -e

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
popd
