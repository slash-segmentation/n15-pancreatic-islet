#!/usr/bin/env python

import os
import shutil
import pyimod
from optparse import OptionParser

def parse_args():
    global p
    p = OptionParser(usage = "%prog [options] file.mod output_path")
    (opts, args) = p.parse_args()
    file_mod, path_out = check_args(args)
    return opts, file_mod, path_out

def check_args(args):
    if len(args) is not 2:
        usage('Improper number of arguments.')
    file_mod = args[0]
    path_out = args[1]
    if not os.path.isfile(file_mod):
        usage('{0} is not a valid file.'.format(file_mod))
    return file_mod, path_out

def usage(errstr):
    print ""
    print "ERROR: %s" % errstr
    print ""
    p.print_help()
    print ""
    exit(1)

def preprocess_cell(obj, path_out):
    """
    Runs preprocessing for a cell object. First, creates a temporary PyIMOD
    ImodObject instance for the current object. Then, removes meshes from the
    object and remeshes with a skip parameter of 10. Finally, exports the 
    object to a VRML file.

    Inputs
    ------
    obj:      PyIMOD ImodObject instance for the given cell.
    path_out: Output path for storing cell data.

    Returns
    -------
    fnameout: Filename of output VRML file, with output path prepended.
    """
    # Process ImodObject name to be consistent
    name = obj.name.lower()
    name = name.split('_')
    name = ' '.join(name)
    name = name.split()
    name = '_'.join(name)
    fnameout = os.path.join(path_out, name + '.wrl')

    # Create a new ImodModel with just the object to be processed
    modtmp = pyimod.ImodModel(mod)
    modtmp.Objects = []
    modtmp.Objects.append(obj)
    modtmp.nObjects = 1
    modtmp.view_objvsize = 1

    # Mesh object 
    modtmp = pyimod.utils.ImodCmd(modtmp, 'imodmesh -e')
    modtmp = pyimod.utils.ImodCmd(modtmp, 'imodmesh -CTs -P 10')

    # Convert to VRML
    pyimod.ImodExport(modtmp, fnameout)
    return fnameout

def process_cell(celltype, obj, path_out, fid):
    """
    Processes a cell object. First, performs preprocessing by remeshing and
    exporting to the VRML format. Then, writes a line to the growing Amira
    project file (.hx) to process the given cell object in Amira. Object color
    is read from the IMOD object and supplied to Amira.

    Inputs
    ------
    celltype: String specifying the type of cell. If this string is empty, the
              cell is interpreted as being unrecognized, and a warning message
              is printed and no further steps are made.
    obj:      PyIMOD ImodObject object for the given cell.
    path_out: Output path for storing cell data.
    fid:      File ID of the growing .hx file to be appended to.
    """
    if celltype:
        print 'Type: {0}'.format(celltype)
        name = obj.name.lower()
        fnamecell = preprocess_cell(obj, path_out)
        fid.write('process_cell "{0}" "{1},{2},{3}" 0 $path_out_cells\n'.format(
            fnamecell, obj.red, obj.green, obj.blue))
    else:
        print 'WARNING: UNRECOGNIZED CELL TYPE. SKIPPING.'

def process_vessel(obj, path_out, fid):
    """
    Processes a vessel object. First performs the same preprocessing done for
    cells, and exports to the VRML format. Then writes a line to the Amira
    project file (.hx) to process the vessel in Amira. Object color is read from
    the IMOD object and supplied to Amira.

    Inputs
    ------
    obj:      PyIMOD ImodObject instance for the given vessel.
    path_out: Output path for storing vessel data and files.
    fid:      File ID of the growing .hx file to be appended to.
    """
    print 'Type: Blood Vessel'
    name = obj.name.lower()
    fnamevessel = preprocess_cell(obj, path_out)
    fid.write('process_vessel "{0}" "{1},{2},{3}" 0 $path_out_vessels\n'.format(
        fnamevessel, obj.red, obj.green, obj.blue))

def process_nerve(obj, path_out, fid):
    """
    Processes a nerve object. First performs the same preprocessing done for
    cells, and exports to the VRML format. Then writes a line to the Amira
    project file (.hx) to process the nerve in Amira. Object color is read from
    the IMOD object and supplied to Amira.

    Inputs
    ------
    obj:      PyIMOD ImodObject instance for the given vessel.
    path_out: Output path for storing nerve data and files.
    fid:      File ID of the growing .hx file to be appended to.
    """ 
    print 'Type: Nerve'
    name = obj.name.lower()
    fnamenerve = preprocess_cell(obj, path_out)
    fid.write('process_nerve "{0}" "{1},{2},{3}" 0 $path_out_nerves\n'.format(
        fnamenerve, obj.red, obj.green, obj.blue))

if __name__ == "__main__":
    global mod

    opts, file_mod, path_out = parse_args()

    # Make output path if necessary
    if not os.path.isdir(path_out):
        os.mkdir(path_out)

    # Load file_mod
    print 'Loading IMOD model file {0}'.format(file_mod)
    mod = pyimod.ImodModel(file_mod)
    print '# Objects: {0}\n'.format(mod.nObjects)
    if mod.minx_set:
        print 'MINX Scale: {0}'.format(mod.minx_cscale)
        print 'MINX Trans: {0}'.format(mod.minx_ctrans)
    else:
        print 'WARNING: NO MINX DATA!'
  
    # Make a copy of the Amira .hx file and open it in append mode
    bnamemod = os.path.basename(os.path.split(file_mod)[1])
    fnamehx = os.path.join(path_out, bnamemod + '.hx')
    shutil.copyfile(os.path.join('n15-pancreatic-islet', 
        'n15islet_to_amira.hx'), fnamehx)
    print 'Amira project file initialized at: {0}'.format(fnamehx)
    fid = open(fnamehx, 'a+')

    # Append object-specific output paths to the Amira .hx file 
    path_out_cells = os.path.join(path_out, 'cells')
    path_out_vessels = os.path.join(path_out, 'vessels')
    path_out_nerves = os.path.join(path_out, 'nerves')
    fid.write('set path_out_cells "{0}"\n'.format(path_out_cells))
    fid.write('set path_out_vessels "{0}"\n'.format(path_out_vessels))
    fid.write('set path_out_nerves "{0}"\n'.format(path_out_nerves))

    # Loop over all objects
    for iObj in range(mod.nObjects):
        obj = mod.Objects[iObj]
        name = obj.name.lower()

        print 'Object {0}'.format(iObj+1)
        print 'Name: {0}'.format(obj.name)
        print 'Color: {0}, {1}, {2}'.format(obj.red, obj.green, obj.blue)

        # Detect blood vessel objects.
        if name.startswith('vessels'):
            if not os.path.isdir(path_out_vessels):
                os.mkdir(path_out_vessels)
            process_vessel(obj, path_out_vessels, fid)

        # Detect nerve objects.
        if name.startswith('nerve'):
            if not os.path.isdir(path_out_nerves):
                os.mkdir(path_out_nerves)
            process_nerve(obj, path_out_nerves, fid)

        # Detect cell objects (a.k.a. plasma membrane, or pm, objects).
        if name.endswith('pm'):
            if not os.path.isdir(path_out_cells):
                os.mkdir(path_out_cells)
            if name.startswith('alpha'):
                celltype = 'Alpha cell'
            elif name.startswith('young_alpha'):
                celltype = 'Young Alpha Cell'
            elif name.startswith('old_alpha'):
                celltype = 'Old Alpha Cell'
            elif name.startswith('beta'):
                celltype = 'Beta cell'
            elif name.startswith('young_beta'):
                celltype = 'Young Beta Cell'
            elif name.startswith('old_beta'):
                celltype = 'Old Beta Cell'
            elif name.startswith('delta'):
                celltype = 'Delta Cell'
            elif name.startswith('young_delta'):
                celltype = 'Young Delta Cell'
            elif name.startswith('old_delta'):
                celltype = 'Old Delta Cell'
            elif name.startswith('perycyte') or name.startswith('pericyte'):
                celltype = 'Pericyte'
            elif name.startswith('unknown'):
                celltype = 'Unknown Cell'
            else:
                celltype = ''
 
            # Run cell processing
            process_cell(celltype, obj, path_out_cells, fid)
    fid.close()
