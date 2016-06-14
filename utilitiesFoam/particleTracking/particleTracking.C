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

#include "particleTracking.H"
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
defineTypeNameAndDebug(particleTracking, 0);
}


// * * * * * * * * * * * * * Private Member Functions  * * * * * * * * * * * //


// * * * * * * * * * * * * * * * * Constructors  * * * * * * * * * * * * * * //

Foam::particleTracking::particleTracking
(
    const word& name,
    const objectRegistry& obr,
    const dictionary& dict,
    const bool loadFromFiles
)
:
    name_(name),
    mesh_(refCast<const fvMesh>(obr)),
    active_(true),
    resetOnStartUp_(false),
    tInjStart_(0),
    tInjEnd_(-1),
    npByDt_(10),
    d_(0.001),
    center_(0,0,0),
    r0_(0,0,0),
    vel_(0,0,0),
    velprime_(0),
    rho_(1.0),
    rhop_(1.0),
    e_(0.0),
    mu_(1.0),
    particles_
    (
        mesh_,
        name
    ),
    g_
    (
        IOobject
        (
            "g",
            "constant",
            mesh_,
            IOobject::MUST_READ,
            IOobject::NO_WRITE
        )
    ),
    random_(time(NULL))
{
    read(dict);

    //Falta chequear si esta en el path el archivo de particulas, levantarlo
    if (resetOnStartUp_)
    {
        //parcels_.cloudReset(parcels_);
    }

    if(!mesh_.foundObject<volScalarField>("rho")){
        new volScalarField
        (
            IOobject
            (
                "rho",
                mesh_.time().timeName(),
                mesh_,
                IOobject::NO_READ,
                IOobject::NO_WRITE
            ),
            mesh_,
            dimensionedScalar("rho", dimDensity, rho_)
        );
    }

    if(!mesh_.foundObject<volScalarField>("nu")){
        word tpName = "transportProperties";
        dimensionedScalar nu_;
        //Info<<"mesh_.lookupObject<IOdictionary>(tpName).lookup(nu): "<<mesh_.lookupObject<IOdictionary>(tpName).lookup("nu")<<endl;
        mesh_.lookupObject<IOdictionary>(tpName).lookup("nu") >> nu_;
        new volScalarField
        (
            IOobject
            (
                "nu",
                mesh_.time().timeName(),
                mesh_,
                IOobject::NO_READ,
                IOobject::NO_WRITE
            ),
            mesh_,
            dimensionedScalar("nu", dimViscosity, nu_.value())
        );
    }
}


// * * * * * * * * * * * * * * * * Destructor  * * * * * * * * * * * * * * * //

Foam::particleTracking::~particleTracking()
{}


// * * * * * * * * * * * * * * * Member Functions  * * * * * * * * * * * * * //

void Foam::particleTracking::read(const dictionary& dict)
{
    if (active_)
    {
        Info<< type() << ":" << nl;

        dict.lookup("resetOnStartUp") >> resetOnStartUp_;
        dict.lookup("tInjStart") >> tInjStart_;
        dict.lookup("tInjEnd") >> tInjEnd_;
        dict.lookup("npByDt") >> npByDt_;
        dict.lookup("d") >> d_;
        dict.lookup("r0") >> r0_;
        dict.lookup("center") >> center_;
        vel_ = dict.lookupOrDefault<vector>("vel", vector(0,0,0));
        velprime_ = dict.lookupOrDefault<scalar>("velprime", 0.0);
        rho_ = dict.lookupOrDefault<scalar>("rho", 1.0);
        dict.lookup("rhop") >> rhop_;
        dict.lookup("e") >> e_;
        dict.lookup("mu") >> mu_;

        particles_.set_rhop(rhop_);
        particles_.set_e(e_);
        particles_.set_mu(mu_);

    }
}


void Foam::particleTracking::execute()
{
    if (active_)
    {
        Info<< "In "<< type() <<". Moving cloud: "<<this->name_<< endl;

        //Info<<mesh_.names()<<endl;

        if (mesh_.time().timeOutputValue() >= tInjStart_  && mesh_.time().timeOutputValue()<= tInjEnd_)
            inject();

        particles_.move(g_);

        //Info<< endl;
    }
}


void Foam::particleTracking::end()
{
    if (active_)
    {
        execute();
    }
}


void Foam::particleTracking::inject()
{
    for(label ip=0; ip<npByDt_;ip++){
        vector tmp = (random_.vector01()-vector(0.5,0.5,0.5))*2;
        scalar posx = tmp.x()*r0_.x();
        scalar posy = tmp.y()*r0_.y();
        scalar posz = tmp.z()*r0_.z();
        vector pos = center_+vector(posx,posy,posz);
        //Info<<"pos random "<<vector(posx,posy,posz)<<endl;
        vector tmpv = vector(random_.GaussNormal(),random_.GaussNormal(),random_.GaussNormal())/Foam::sqrt(3.0);
        vector vel = tmpv*velprime_+vel_;
        label cellI = mesh_.findCell(pos);
        if(cellI>=0){
            Info<<"injected in "<<pos<<" - cellI:"<<cellI<<endl;
            myParticle* ptr = new myParticle(mesh_,pos,cellI,0,0,d_,vel);
            ptr->initCellFacePt();
            particles_.addParticle(ptr);
        }
    }
    //Info<<"Finish injection"<<endl;

}


void Foam::particleTracking::timeSet()
{
    // Do nothing
}


void Foam::particleTracking::write()
{
    //Info<<"In Foam::particleTracking::write()"<<endl;
    particles_.writeFields();
    // Do nothing
}


// ************************************************************************* //
