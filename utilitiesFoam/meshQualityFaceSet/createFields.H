    Info<< "Creating scalar fields: nonOrth and skew\n" << endl;

    scalarField nonOrth(mesh.nCells(), 0);

    /*volScalarField nonOrth
    (
        IOobject
        (
            "nonOrth",
            runTime.timeName(),
            mesh,
            IOobject::NO_READ,
            IOobject::AUTO_WRITE
        ),
        mesh
    );*/

    scalarField skew(mesh.nCells(), 0);

    /*volScalarField skew
    (
        IOobject
        (
            "skew",
            runTime.timeName(),
            mesh,
            IOobject::NO_READ,
            IOobject::AUTO_WRITE
        ),
        mesh
    );*/



   
