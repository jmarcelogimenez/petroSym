/*---------------------------------------------------------------------------*\
  =========                 |
  \\      /  F ield         | OpenFOAM: The Open Source CFD Toolbox
   \\    /   O peration     |
    \\  /    A nd           | Copyright (C) 2012-2013 OpenFOAM Foundation
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
    Foam::particleTracking

Group
    grpUtilitiesFunctionObjects

Description
    This function object evolves a cloud of solid particles.
    The tracking strategy is one-way coupling

    - the field can be zeroed on start-up using the resetOnStartUp flag

SourceFiles
    particleTracking.C
    IOparticleTracking.H

\*---------------------------------------------------------------------------*/

#ifndef particleTracking_H
#define particleTracking_H

#include "fvMatricesFwd.H"
#include "UniformDimensionedField.H"
#include "myParticleCloud.H"

// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

namespace Foam
{

// Forward declaration of classes
class objectRegistry;
class dictionary;
class mapPolyMesh;

/*---------------------------------------------------------------------------*\
                       Class particleTracking Declaration
\*---------------------------------------------------------------------------*/

class particleTracking
{
    // Private data

        //- Name of this set of particleTracking objects
        word name_;

        //- Reference to the mesh database
        const fvMesh& mesh_;

        //- On/off switch
        bool active_;

        //- Flag to reset scalar field on start-up
        bool resetOnStartUp_;
        scalar tInjStart_;
        scalar tInjEnd_;
        label npByDt_;
        scalar d_;
        vector center_;
        vector r0_;
        vector vel_;
        scalar velprime_;
        scalar rho_;
        //Particle properties
        scalar rhop_;
        scalar e_;
        scalar mu_;

        //Particle Cloud
        myParticleCloud particles_;

        UniformDimensionedField<vector> g_;

        Random random_;


        // Private Member Functions

        //- Disallow default bitwise copy construct
        particleTracking(const particleTracking&);

        //- Disallow default bitwise assignment
        void operator=(const particleTracking&);

        void inject();


public:

    //- Runtime type information
    TypeName("particleTracking");


    // Constructors

        //- Construct for given objectRegistry and dictionary.
        //  Allow the possibility to load fields from files
        particleTracking
        (
            const word& name,
            const objectRegistry&,
            const dictionary&,
            const bool loadFromFiles = false
        );


    //- Destructor
    virtual ~particleTracking();


    // Member Functions

        //- Return name of the set of particleTracking
        virtual const word& name() const
        {
            return name_;
        }

        //- Read the particleTracking data
        virtual void read(const dictionary&);

        //- Execute, currently does nothing
        virtual void execute();

        //- Execute at the final time-loop, currently does nothing
        virtual void end();

        //- Called when time was set at the end of the Time::operator++
        virtual void timeSet();

        //- Calculate the particleTracking and write
        virtual void write();

        //- Update for changes of mesh
        virtual void updateMesh(const mapPolyMesh&)
        {}

        //- Update for changes of mesh
        virtual void movePoints(const polyMesh&)
        {}
};


// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

} // End namespace Foam

// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

#endif

// ************************************************************************* //
