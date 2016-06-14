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

Class
    Foam::myParticleCloud

Description
    A Cloud of solid particles

SourceFiles
    myParticleCloudI.H
    myParticleCloud.C
    myParticleCloudIO.C

\*---------------------------------------------------------------------------*/

#ifndef myParticleCloud_H
#define myParticleCloud_H

#include "Cloud.H"
#include "myParticle.H"
#include "IOdictionary.H"

// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

namespace Foam
{

// Forward declaration of classes
class fvMesh;

/*---------------------------------------------------------------------------*\
                           Class myParticleCloud Declaration
\*---------------------------------------------------------------------------*/

class myParticleCloud
:
    public Cloud<myParticle>
{
    // Private data

        const fvMesh& mesh_;

        IOdictionary particleProperties_;

        scalar rhop_;
        scalar e_;
        scalar mu_;


    // Private Member Functions

        //- Disallow default bitwise copy construct
        myParticleCloud(const myParticleCloud&);

        //- Disallow default bitwise assignment
        void operator=(const myParticleCloud&);


public:

    // Constructors

        //- Construct given mesh
        myParticleCloud
        (
            const fvMesh&,
            const word& cloudName = "defaultCloud",
            bool readFields = true
        );


    // Member Functions

        // Access

            virtual bool hasWallImpactDistance() const;

            inline const fvMesh& mesh() const;

            inline scalar rhop() const;
            inline scalar e() const;
            inline scalar mu() const;

            void set_rhop(scalar rhop);
            void set_e(scalar e);
            void set_mu(scalar mu);


        // Edit

            //- Move the particles under the influence of the given
            //  gravitational acceleration
            void move(const dimensionedVector& g);

            void writeFields();
};


// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

} // End namespace Foam

// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

#include "myParticleCloudI.H"

// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

#endif

// ************************************************************************* //
