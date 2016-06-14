/*---------------------------------------------------------------------------*\
  =========                 |
  \\      /  F ield         | OpenFOAM: The Open Source CFD Toolbox
   \\    /   O peration     |
    \\  /    A nd           | Copyright (C) 2011 OpenFOAM Foundation
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

#include "myParticleCloud.H"
#include "fvMesh.H"
#include "volFields.H"
#include "interpolationCellPoint.H"

// * * * * * * * * * * * * * * * * Constructors  * * * * * * * * * * * * * * //

Foam::myParticleCloud::myParticleCloud
(
    const fvMesh& mesh,
    const word& cloudName,
    bool readFields
)
:
    Cloud<myParticle>(mesh, cloudName, false),
    mesh_(mesh),
    particleProperties_
    (
        IOobject
        (
            "particleProperties",
            mesh_.time().constant(),
            mesh_,
            IOobject::MUST_READ_IF_MODIFIED,
            IOobject::NO_WRITE
        )
    ),
    rhop_(dimensionedScalar(particleProperties_.lookup("rhop")).value()),
    e_(dimensionedScalar(particleProperties_.lookup("e")).value()),
    mu_(dimensionedScalar(particleProperties_.lookup("mu")).value())
{
    if (readFields)
    {
        myParticle::readFields(*this);
    }
}

// * * * * * * * * * * * * * * * Member Functions  * * * * * * * * * * * * * //

bool Foam::myParticleCloud::hasWallImpactDistance() const
{
    return true;
}


void Foam::myParticleCloud::move(const dimensionedVector& g)
{
    const volScalarField& rho = mesh_.lookupObject<const volScalarField>("rho");
    const volVectorField& U = mesh_.lookupObject<const volVectorField>("U");
    const volScalarField& nu = mesh_.lookupObject<const volScalarField>("nu");

    interpolationCellPoint<scalar> rhoInterp(rho);
    interpolationCellPoint<vector> UInterp(U);
    interpolationCellPoint<scalar> nuInterp(nu);

    myParticle::trackingData
        td(*this, rhoInterp, UInterp, nuInterp, g.value());

    Cloud<myParticle>::move(td, mesh_.time().deltaTValue());
}

void Foam::myParticleCloud::writeFields()
{
    myParticle::writeFields(*this);
}

void Foam::myParticleCloud::set_rhop(scalar rhop){
    rhop_ = rhop;
}

void Foam::myParticleCloud::set_e(scalar e){
    e_ = e;
}

void Foam::myParticleCloud::set_mu(scalar mu){
    mu_ = mu;
}

// ************************************************************************* //
