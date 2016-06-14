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

#include "myParticle.H"
#include "IOstreams.H"

// * * * * * * * * * * * * * * * * Constructors  * * * * * * * * * * * * * * //

Foam::myParticle::myParticle
(
    const polyMesh& mesh,
    Istream& is,
    bool readFields
)
:
    particle(mesh, is, readFields)
{
    if (readFields)
    {
        if (is.format() == IOstream::ASCII)
        {
            d_ = readScalar(is);
            is >> U_;
            is >> Urold_;
        }
        else
        {
            is.read
            (
                reinterpret_cast<char*>(&d_),
                sizeof(d_) + sizeof(U_) + sizeof(Urold_)
            );
        }
    }

    // Check state of Istream
    is.check("myParticle::myParticle(Istream&)");
}


void Foam::myParticle::readFields(Cloud<myParticle>& c)
{
    if (!c.size())
    {
        return;
    }

    particle::readFields(c);

    IOField<scalar> d(c.fieldIOobject("d", IOobject::MUST_READ));
    c.checkFieldIOobject(c, d);

    IOField<vector> U(c.fieldIOobject("U", IOobject::MUST_READ));
    c.checkFieldIOobject(c, U);

    IOField<vector> Urold(c.fieldIOobject("Urold", IOobject::MUST_READ));
    c.checkFieldIOobject(c, Urold);

    label i = 0;
    forAllIter(Cloud<myParticle>, c, iter)
    {
        myParticle& p = iter();

        p.d_ = d[i];
        p.U_ = U[i];
        p.Urold_ = Urold[i];
        i++;
    }
}


void Foam::myParticle::writeFields(const Cloud<myParticle>& c)
{
    //Info<<"In Foam::myParticle::writeFields"<<endl;
    particle::writeFields(c);

    label np = c.size();

    IOField<scalar> d(c.fieldIOobject("d", IOobject::NO_READ), np);
    IOField<vector> U(c.fieldIOobject("U", IOobject::NO_READ), np);
    IOField<vector> Urold(c.fieldIOobject("Urold", IOobject::NO_READ), np);

    label i = 0;
    forAllConstIter(Cloud<myParticle>, c, iter)
    {
        const myParticle& p = iter();

        d[i] = p.d_;
        U[i] = p.U_;
        Urold[i] = p.Urold_;
        i++;
    }

    d.write();
    U.write();
    Urold.write();
}


// * * * * * * * * * * * * * * * IOstream Operators  * * * * * * * * * * * * //

Foam::Ostream& Foam::operator<<(Ostream& os, const myParticle& p)
{
    if (os.format() == IOstream::ASCII)
    {
        os  << static_cast<const particle&>(p)
            << token::SPACE << p.d_
            << token::SPACE << p.U_
            << token::SPACE << p.Urold_;
    }
    else
    {
        os  << static_cast<const particle&>(p);
        os.write
        (
            reinterpret_cast<const char*>(&p.d_),
            sizeof(p.d_) + sizeof(p.U_) + sizeof(p.Urold_)
        );
    }

    // Check state of Ostream
    os.check("Ostream& operator<<(Ostream&, const myParticle&)");

    return os;
}


// ************************************************************************* //
