/*---------------------------------------------------------------------------*\
  =========                 |
  \\      /  F ield         | OpenFOAM: The Open Source CFD Toolbox
   \\    /   O peration     |
    \\  /    A nd           | Copyright (C) 2011-2013 OpenFOAM Foundation
     \\/     M anipulation  |
-------------------------------------------------------------------------------
License
    This file is derivated from OpenFOAM.

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

Application
    meshQuality

Description
    Creates two volScalarFields: nonOrth y Skew and a results raw data

\*---------------------------------------------------------------------------*/

#include "fvCFD.H"
#include "fvIOoptionList.H"
#include "faceSet.H"
#include "primitiveMesh.H"
#include "primitiveMeshTools.H"


// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

int main(int argc, char *argv[])
{

    timeSelector::addOptions();
    #include "addRegionOption.H"
    //argList::validArgs.append("fieldName");
    #include "setRootCase.H"
    #include "createTime.H"
    instantList timeDirs = timeSelector::select0(runTime, args);
    #include "createNamedMesh.H"
    #include "createFields.H"
	
    // * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

    forAll(timeDirs, timeI)
    {
        runTime.setTime(timeDirs[timeI], timeI);
        Info<< "Time = " << runTime.timeName() << endl;

        mesh.readUpdate();
		

	    const vectorField& fAreas = mesh.faceAreas();
	    const vectorField& fCentres = mesh.faceCentres();
		const vectorField& cCentres = mesh.cellCentres();
		const primitiveMesh& meshh = mesh;
        const pointField& points = mesh.points();

        // Start of non orthogonality calculation
		tmp<scalarField> tortho = primitiveMeshTools::faceOrthogonality
		(
		    meshh,
		    fAreas,
		    cCentres
		);

		scalarField ortho = tortho();
		scalarField orthogonality = ortho;
		
		forAll(ortho, faceI)
		{
			if (ortho[faceI] > 1)
			{
				ortho[faceI] = 1;
			}
			else if (ortho[faceI] < -1)
			{
				ortho[faceI] = -1;
			}
		
			orthogonality[faceI] = radToDeg(::acos(ortho[faceI]));
		}

		forAll(orthogonality, faceI)
		{
			label cellI = mesh.faceOwner()[faceI];
			
			if (orthogonality[faceI] >= nonOrth[cellI])
			{
				nonOrth.internalField()[cellI] = orthogonality[faceI];
			}
		}

        // Start of skewness calculation
        tmp<scalarField> tFaceSkew = primitiveMeshTools::faceSkewness
        (
            meshh,
            points,
            fCentres,
            fAreas,
            cCentres
        );

        scalarField faceSkew = tFaceSkew();

		forAll(faceSkew, faceI)
		{
			label cellI = mesh.faceOwner()[faceI];
			
			if (faceSkew[faceI] > skew[cellI])
			{
				skew.internalField()[cellI] = faceSkew[faceI];
			}
		}
			
		nonOrth.write();
		skew.write();
			
		//Postprocessing to histograms
		List<int> histo_nonOrth(10,0);
		List<int> histo_skew(10,0);
		List<int> histo_vol(10,0);
		List<int> zero(10,0);

		scalar maxV = Foam::max(mesh.V()).value();
		scalar minV = Foam::min(mesh.V()).value();
		bool calc_vol = true;
		if (maxV-minV < 1e-12)
			calc_vol = false;

		forAll(mesh.cells(), cellI){
			label index = nonOrth.internalField()[cellI]/9;
			index = (index>9) ? label(9) : (index<0) ? label(0) : index;
			histo_nonOrth[index]++;

			index = skew.internalField()[cellI]/0.5;
			index = (index>9) ? label(9) : (index<0) ? label(0) : index;
			histo_skew[index]++;

			if(calc_vol){
				index = int((10.0/(maxV-minV))*mesh.V()[cellI]-(10.0/(maxV-minV))*minV);
				index = (index>9) ? label(9) : (index<0) ? label(0) : index;
				histo_vol[index]++;
			}else histo_vol[0]++;
		}

		//Parallel allgathering

    	// Create lists of the lists of the above variables, with size equal to the
	    // number of processors.
    	List< List<int> > histo_nonOrth_global(Pstream::nProcs());
   		List< List<int> > histo_skew_global(Pstream::nProcs());
    	List< List<int> > histo_vol_global(Pstream::nProcs());

		//  Populate and gather the stuff onto the master processor.
		histo_nonOrth_global[Pstream::myProcNo()] = histo_nonOrth;
		histo_skew_global[Pstream::myProcNo()] = histo_skew;
		histo_vol_global[Pstream::myProcNo()] = histo_vol;

	    Pstream::gatherList(histo_nonOrth_global);
	    Pstream::gatherList(histo_skew_global);
	    Pstream::gatherList(histo_vol_global);

		if(!Pstream::myProcNo()){
			forAll(histo_nonOrth, ii){
				histo_nonOrth[ii] = 0;
				histo_skew[ii] = 0;
				histo_vol[ii] = 0;
				for (int ip = 0; ip < Pstream::nProcs(); ip++)
				{
					histo_nonOrth[ii] += histo_nonOrth_global[ip][ii];
					histo_skew[ii] += histo_skew_global[ip][ii];
					histo_vol[ii] += histo_vol_global[ip][ii];
				}
			}

			Info<<endl;
			Info<<" nonOrth: ";
			forAll(histo_nonOrth, ih){Info<<histo_nonOrth[ih]<<" ";}
			Info<<endl;
			Info<<" skew: ";
			forAll(histo_skew, ii) Info<<histo_skew[ii]<<" ";
			Info<<endl;
			Info<<" maxVol: "<<maxV<<endl;
			Info<<" minVol: "<<minV<<endl;
			Info<<" vol: ";
			forAll(histo_vol, ii) Info<<histo_vol[ii]<<" ";
			Info<<endl;
			Info<<endl;
		}
		


		Info<< "ExecutionTime = " << runTime.elapsedCpuTime() << " s"
		        << "  ClockTime = " << runTime.elapsedClockTime() << " s"
		        << nl << endl;


    }

    Info<< "End\n" << endl;

    return 0;
}


// ************************************************************************* //
