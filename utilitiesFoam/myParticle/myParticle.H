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
    Foam::myParticle

Description
    Simple solid spherical particle class with one-way coupling with the
    continuous phase.

SourceFiles
    myParticleI.H
    myParticle.C
    myParticleIO.C

\*---------------------------------------------------------------------------*/

#ifndef myParticle_H
#define myParticle_H

#include "particle.H"
#include "IOstream.H"
#include "autoPtr.H"
#include "interpolationCellPoint.H"
#include "contiguous.H"

// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

namespace Foam
{

class myParticleCloud;

/*---------------------------------------------------------------------------*\
                           Class myParticle Declaration
\*---------------------------------------------------------------------------*/

class myParticle
:
    public particle
{
    // Private member data

        //- Diameter
        scalar d_;

        //- Velocity of parcel
        vector U_;

        //- Previous relative velocity
        vector Urold_;


public:

    friend class Cloud<myParticle>;

    //- Class used to pass tracking data to the trackToFace function
    class trackingData
    :
        public particle::TrackingData<myParticleCloud>
    {
        // Interpolators for continuous phase fields

            const interpolationCellPoint<scalar>& rhoInterp_;
            const interpolationCellPoint<vector>& UInterp_;
            const interpolationCellPoint<scalar>& nuInterp_;

        //- Local gravitational or other body-force acceleration
        const vector& g_;


    public:

        // Constructors

            inline trackingData
            (
                myParticleCloud& spc,
                const interpolationCellPoint<scalar>& rhoInterp,
                const interpolationCellPoint<vector>& UInterp,
                const interpolationCellPoint<scalar>& nuInterp,
                const vector& g
            );


        // Member functions

            inline const interpolationCellPoint<scalar>& rhoInterp() const;

            inline const interpolationCellPoint<vector>& UInterp() const;

            inline const interpolationCellPoint<scalar>& nuInterp() const;

            inline const vector& g() const;
    };


    // Constructors

        //- Construct from components
        inline myParticle
        (
            const polyMesh& mesh,
            const vector& position,
            const label cellI,
            const label tetFaceI,
            const label tetPtI,
            const scalar d,
            const vector& U
        );

        //- Construct from Istream
        myParticle
        (
            const polyMesh& mesh,
            Istream& is,
            bool readFields = true
        );

        //- Construct and return a clone
        virtual autoPtr<particle> clone() const
        {
            return autoPtr<particle>(new myParticle(*this));
        }

        //- Factory class to read-construct particles used for
        //  parallel transfer
        class iNew
        {
            const polyMesh& mesh_;

        public:

            iNew(const polyMesh& mesh)
            :
                mesh_(mesh)
            {}

            autoPtr<myParticle> operator()(Istream& is) const
            {
                return autoPtr<myParticle>
                (
                    new myParticle(mesh_, is, true)
                );
            }
        };


    // Member Functions

        // Access

            //- Return diameter
            inline scalar d() const;

            //- Return velocity
            inline const vector& U() const;


        // Tracking

            //- Move
            bool move(trackingData&, const scalar);


        // Patch interactions

            //- Overridable function to handle the particle hitting a patch
            //  Executed before other patch-hitting functions
            bool hitPatch
            (
                const polyPatch&,
                trackingData& td,
                const label patchI,
                const scalar trackFraction,
                const tetIndices& tetIs
            );

            //- Overridable function to handle the particle hitting a
            //  processorPatch
            void hitProcessorPatch
            (
                const processorPolyPatch&,
                trackingData& td
            );

            //- Overridable function to handle the particle hitting a wallPatch
            void hitWallPatch
            (
                const wallPolyPatch&,
                trackingData& td,
                const tetIndices&
            );

            //- Overridable function to handle the particle hitting a polyPatch
            void hitPatch
            (
                const polyPatch&,
                trackingData& td
            );

            //- Transform the physical properties of the particle
            //  according to the given transformation tensor
            virtual void transformProperties(const tensor& T);

            //- Transform the physical properties of the particle
            //  according to the given separation vector
            virtual void transformProperties(const vector& separation);

            //- The nearest distance to a wall that
            //  the particle can be in the n direction
            virtual scalar wallImpactDistance(const vector& n) const;


    // I-O

        static void readFields(Cloud<myParticle>& c);

        static void writeFields(const Cloud<myParticle>& c);


    // Ostream Operator

        friend Ostream& operator<<(Ostream&, const myParticle&);
};


template<>
inline bool contiguous<myParticle>()
{
    return true;
}


// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

} // End namespace Foam

// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

#include "myParticleI.H"

// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

#endif

// ************************************************************************* //
