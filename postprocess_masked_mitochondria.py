#!/usr/bin/env python

"""
Performs post-processing of mitochondria automatic segmentation results after
they have been masked to individual cells. Pixel sizes are set according to the
bin2 N15 islet dataset:

/ccdbprod/ccdbprod8/home/CCDB_DATA_USER.portal/CCDB_DATA_USER/acquisition/
project_20340/microscopy_5261579/processed_data /3view-stack-final-bin2.mrc

The masked output is first remeshed, then sorted into different objects by 3D
connectivity. Then, small objects are removed (small objects are defined as
those having 3 contours or less). The kept objects are then merged into one,
and this object is named and remeshed. The model file is then saved to disk.
"""

import os
import glob
import pyimod

# Get list of directory names, following the output syntax from maskWholeCell
dirnames = sorted(glob.glob('output/cell_*'))

# Loop over each directory, each corresponding to one cellp
for diri in dirnames:

    # Load model 
    fname = os.path.join(diri, 'tmp', 'out.mod~')
    print 'Loading file {0}'.format(fname)
    mod = pyimod.ImodModel(fname)

    # Set pixel sizes
    mod.setPixelSizeXY(10.718)
    mod.setPixelSizeZ(70)
    mod.setUnits('nm')

    # Remesh and sort into spatially separate objects
    mod = pyimod.utils.ImodCmd(mod, 'imodmesh -e')
    mod = pyimod.utils.ImodCmd(mod, 'imodmesh -CTs -P 4')
    mod = pyimod.utils.ImodCmd(mod, 'imodsortsurf -s')

    # Remove all objects with less than 4 contours
    mod.filterByNContours('>', 3)

    # Move all objects to one
    mod.moveObjects(1, '2-{0}'.format(mod.nObjects))

    # Set object name and color
    mod.Objects[0].setName('Mitochondria')
    mod.Objects[0].setColor(0, 1, 0)

    # Remesh
    mod = pyimod.utils.ImodCmd(mod, 'imodmesh -e')
    mod = pyimod.utils.ImodCmd(mod, 'imodmesh -CTs -P 4')

    # Write model to disk
    fnameout = os.path.join(diri, 'tmp', 'proc.mod')
    pyimod.ImodWrite(mod, fnameout)
    print '{0} written to disk\n\n'.format(fnameout)
