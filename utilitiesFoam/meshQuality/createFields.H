    Info<< "Reading fields: nonOrth and skew\n" << endl;

    volScalarField nonOrth
    (
        IOobject
        (
            "nonOrth",
            runTime.timeName(),
            mesh,
            IOobject::NO_READ,
            IOobject::AUTO_WRITE
        ),
        mesh,
	dimensionedScalar("nonOrth",dimensionSet(0,0,0,0,0,0,0),0)
    );

    volScalarField skew
    (
        IOobject
        (
            "skew",
            runTime.timeName(),
            mesh,
            IOobject::NO_READ,
            IOobject::AUTO_WRITE
        ),
        mesh,
	dimensionedScalar("skew",dimensionSet(0,0,0,0,0,0,0),0)
    );



   
