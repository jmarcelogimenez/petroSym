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

// * * * * * * * * * * * * * * * * Constructors  * * * * * * * * * * * * * * //

inline Foam::myParticle::trackingData::trackingData
(
    myParticleCloud& spc,
    const interpolationCellPoint<scalar>& rhoInterp,
    const interpolationCellPoint<vector>& UInterp,
    const interpolationCellPoint<scalar>& nuInterp,
    const vector& g
)
:
    particle::TrackingData<myParticleCloud>(spc),
    rhoInterp_(rhoInterp),
    UInterp_(UInterp),
    nuInterp_(nuInterp),
    UoldInterp_(UInterp),
    g_(g)
{}


inline Foam::myParticle::trackingData::trackingData
(
    myParticleCloud& spc,
    const interpolationCellPoint<scalar>& rhoInterp,
    const interpolationCellPoint<vector>& UInterp,
    const interpolationCellPoint<scalar>& nuInterp,
    const interpolationCellPoint<vector>& UoldInterp,
    const vector& g
)
:
    particle::TrackingData<myParticleCloud>(spc),
    rhoInterp_(rhoInterp),
    UInterp_(UInterp),
    nuInterp_(nuInterp),
    UoldInterp_(UoldInterp),
    g_(g)
{}


inline Foam::myParticle::myParticle
(
    const polyMesh& mesh,
    const vector& position,
    const label cellI,
    const label tetFaceI,
    const label tetPtI,
    const scalar d,
    const vector& U
)
:
    particle(mesh, position, cellI, tetFaceI, tetPtI),
    d_(d),
    U_(U)
{
    Urold_ = vector(0,0,0);
}


// * * * * * * * * * * * * * * * Member Functions  * * * * * * * * * * * * * //

inline const Foam::interpolationCellPoint<Foam::scalar>&
Foam::myParticle::trackingData::rhoInterp() const
{
    return rhoInterp_;
}


inline const Foam::interpolationCellPoint<Foam::vector>&
Foam::myParticle::trackingData::UInterp() const
{
    return UInterp_;
}


inline const Foam::interpolationCellPoint<Foam::scalar>&
Foam::myParticle::trackingData::nuInterp() const
{
    return nuInterp_;
}

inline const Foam::interpolationCellPoint<Foam::vector>&
Foam::myParticle::trackingData::UoldInterp() const
{
    return UoldInterp_;
}

inline const Foam::vector& Foam::myParticle::trackingData::g() const
{
    return g_;
}


inline Foam::scalar Foam::myParticle::d() const
{
    return d_;
}


inline const Foam::vector& Foam::myParticle::U() const
{
    return U_;
}


// ************************************************************************* //
