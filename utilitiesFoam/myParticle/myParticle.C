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

// * * * * * * * * * * * * * * Static Data Members * * * * * * * * * * * * * //

namespace Foam
{
    defineTemplateTypeNameAndDebug(Cloud<myParticle>, 0);
}

// * * * * * * * * * * * * * * * Member Functions  * * * * * * * * * * * * * //

bool Foam::myParticle::move
(
    trackingData& td,
    const scalar trackTime
)
{
    td.switchProcessor = false;
    td.keepParticle = true;

    const polyBoundaryMesh& pbMesh = mesh_.boundaryMesh();

    scalar tEnd = (1.0 - stepFraction())*trackTime;
    scalar dtMax = tEnd;

    while (td.keepParticle && !td.switchProcessor && tEnd > SMALL)
    {
        if (debug)
        {
            Info<< "Time = " << mesh_.time().timeName()
                << " trackTime = " << trackTime
                << " tEnd = " << tEnd
                << " stepFraction() = " << stepFraction() << endl;
        }

        // remember which cell the parcel is in
        // since this will change if a face is hit
        label cellI = cell();

        cellPointWeight cpw(mesh_, position(), cellI, face());
        scalar rhoc = td.rhoInterp().interpolate(cpw);
        vector Uc = td.UInterp().interpolate(cpw);
        scalar nuc = td.nuInterp().interpolate(cpw);
        vector Ucold = td.UoldInterp().interpolate(cpw);

        scalar rhop = td.cloud().rhop();

        vector Ur = Uc-U_;
        scalar magUr = mag(Ur);

        vector dUr = Ur-Urold_;
        vector dU = Uc-Ucold;

        scalar Re = magUr*d_/nuc;

        scalar ReFunc = 1.0;
        if (Re > 0.01)
        {
            ReFunc += 0.15*pow(Re, 0.687);
        }
        scalar Dc = (24.0*nuc/d_)*ReFunc*(3.0/4.0)*(rhoc/(d_*rhop));

        //implemento mi modelo de particula
        scalar Cd = 0;
        Cd = 24/Re + (2.6*Re/5.0)/(1+pow(Re/5.0,1.52));
        Cd += 0.411*pow(Re/263000.0,-7.94)/(1+pow(Re/263000.0,-8.0));
        Cd += pow(Re,0.8)/461000.0;

        // set the lagrangian time-step
        //mejorar la estimacion del paso de tiempo para el tracking
        //scalar tRelax = (rhop*d_*d_/(18*rhoc*nuc+1e-12))/(1+0.15*pow(Re,0.687));
        //scalar dt = min(dtMax, min(tEnd,tRelax));
        scalar dt = min(dtMax, tEnd);

        dt *= trackToFace(position() + dt*U_, td);

        tEnd -= dt;
        stepFraction() = 1.0 - tEnd/trackTime;

        if(0){
            //Modelo basico de Foam            
            U_ = (U_ + dt*(Dc*Uc + (1.0 - rhoc/rhop)*td.g()))/(1.0 + dt*Dc);
        }else{
            //Cd = Dc;
            //Fuerza de Drag
            //vector Fd = (3.0/4.0)*rhoc/d_*Cd*Ur*magUr;
            //Fuerza de Drag en Fluent
            vector Fd = (18.0*rhoc*nuc/(rhop*d_*d_))*Cd*Re/24.0*Ur;
            //Fuerza de inercia
            vector Fi = rhoc*dU/(1e-10+trackTime);
            //Fuerza de boyancia
            vector Fb = (rhop-rhoc)*td.g();
            //Fuerza de masa agregada
            vector Fm = rhoc/2.0*dUr/(1e-10+dt);

            Urold_ = Ur;

            //Info<<"Fi: "<<Fi<<endl;
            //Info<<"Fd: "<<Fd<<endl;
            //Info<<"Fb: "<<Fb<<endl;
            //Info<<"Fm: "<<Fm<<endl;
            U_ = (U_ + dt/rhop*(Fd+Fi+Fb+Fm));



        }



        if (onBoundary() && td.keepParticle)
        {
            if (isA<processorPolyPatch>(pbMesh[patch(face())]))
            {
                td.switchProcessor = true;
            }
        }
    }

    return td.keepParticle;
}


bool Foam::myParticle::hitPatch
(
    const polyPatch&,
    trackingData&,
    const label,
    const scalar,
    const tetIndices&
)
{
    return false;
}


void Foam::myParticle::hitProcessorPatch
(
    const processorPolyPatch&,
    trackingData& td
)
{
    td.switchProcessor = true;
}


void Foam::myParticle::hitWallPatch
(
    const wallPolyPatch& wpp,
    trackingData& td,
    const tetIndices& tetIs
)
{
    vector nw = tetIs.faceTri(mesh_).normal();
    nw /= mag(nw);

    //Info<<"hiting wall in "<<position()<<" enter with U: "<<U_<<endl;
    scalar Un = U_ & nw;
    vector Ut = U_ - Un*nw;

    if (Un > 0)
    {
        U_ -= (1.0 + td.cloud().e())*Un*nw;
    }

    U_ -= td.cloud().mu()*Ut;
    //Info<<"hiting wall leave with U: "<<U_<<endl;
}


void Foam::myParticle::hitPatch
(
    const polyPatch&,
    trackingData& td
)
{
    td.keepParticle = false;
}


void Foam::myParticle::transformProperties (const tensor& T)
{
    particle::transformProperties(T);
    U_ = transform(T, U_);
}


void Foam::myParticle::transformProperties(const vector& separation)
{
    particle::transformProperties(separation);
}


Foam::scalar Foam::myParticle::wallImpactDistance(const vector&) const
{
    return 0.5*d_;
}


// ************************************************************************* //
