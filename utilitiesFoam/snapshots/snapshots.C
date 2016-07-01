/*---------------------------------------------------------------------------*\
  =========                 |
  \\      /  F ield         | OpenFOAM: The Open Source CFD Toolbox
   \\    /   O peration     |
    \\  /    A nd           | Copyright (C) 2012-2014 OpenFOAM Foundation
     \\/     M anipulation  |
-------------------------------------------------------------------------------
License
    This file is part of OpenFOAM.

    OpenFOAM is free software: you can redistribute it and/or modify it
    under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    OpenFOAM is distributed in the hope that it will be useful, but WITHOUT
    ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
    FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License
    for more details.

    You should have received a copy of the GNU General Public License
    along with OpenFOAM.  If not, see <http://www.gnu.org/licenses/>.

\*---------------------------------------------------------------------------*/

#include "snapshots.H"
#include "surfaceFields.H"
#include "dictionary.H"
#include "fixedValueFvPatchFields.H"
#include "zeroGradientFvPatchFields.H"
#include "fvScalarMatrix.H"
#include "fvmDdt.H"
#include "fvmDiv.H"
#include "fvcDiv.H"
#include "fvmLaplacian.H"
#include "fvmSup.H"
#include "incompressible/turbulenceModel/turbulenceModel.H"
#include "compressible/turbulenceModel/turbulenceModel.H"

// * * * * * * * * * * * * * * Static Data Members * * * * * * * * * * * * * //

namespace Foam
{
defineTypeNameAndDebug(snapshots, 0);
}


// * * * * * * * * * * * * * Private Member Functions  * * * * * * * * * * * //


// * * * * * * * * * * * * * * * * Constructors  * * * * * * * * * * * * * * //

Foam::snapshots::snapshots
(
    const word& name,
    const objectRegistry& obr,
    const dictionary& dict,
    const bool loadFromFiles
)
:
    name_(name),
    mesh_(refCast<const fvMesh>(obr))
{
    read(dict);

}


// * * * * * * * * * * * * * * * * Destructor  * * * * * * * * * * * * * * * //

Foam::snapshots::~snapshots()
{}


// * * * * * * * * * * * * * * * Member Functions  * * * * * * * * * * * * * //

void Foam::snapshots::read(const dictionary& dict)
{
    
}


void Foam::snapshots::execute()
{
        Info<< "Doing nothing in "<< type() <<". snapshots: "<<this->name_<< endl;
}


void Foam::snapshots::end()
{
        execute();
}


void Foam::snapshots::timeSet()
{
    // Do nothing
}


void Foam::snapshots::write()
{
    fileName vtkPath
    (
        Pstream::parRun()
      ? mesh_.time().path()/".."/"postProcessing"/"snapshots"/name()
      : mesh_.time().path()/"postProcessing"/"snapshots"/name()
    );
    if (mesh_.name() != fvMesh::defaultRegion)
    {
        vtkPath = vtkPath/mesh_.name();
    }
    vtkPath = vtkPath/mesh_.time().timeName();

    mkDir(vtkPath);
}


// ************************************************************************* //
