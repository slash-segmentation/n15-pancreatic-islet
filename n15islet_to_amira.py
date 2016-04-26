#!/usr/bin/env python

import os
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

def preprocess_cell(obj, name, path_out_cells):
    # Process ImodObject name to be consistent
    name = name.split('_')
    name = ' '.join(name)
    name = name.split()
    name = '_'.join(name)
    fnameout = os.path.join(path_out_cells, name)

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
    pyimod.ImodExport(modtmp, fnameout + '.wrl')

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
   
    # Loop over all objects
    for iObj in range(mod.nObjects):
        obj = mod.Objects[iObj]
        name = obj.name.lower()
        path_out_cells = os.path.join(path_out, 'cells')
        print 'Object {0}'.format(iObj+1)
        print 'Name: {0}'.format(obj.name)
        print 'Color: {0}, {1}, {2}'.format(obj.red, obj.green, obj.blue)

        if name == 'vessels':
            print 'Type: Blood vessels'

        if name.startswith('connective tissue'):
            print 'Type: Connective tissue' 

        if name.endswith('pm'):
            if not os.path.isdir(path_out_cells):
                os.mkdir(path_out_cells)
            if name.startswith('alpha'):
                print 'Type: Alpha cell'
                preprocess_cell(obj, name, path_out_cells)
            elif name.startswith('young_alpha'):
                print 'Type: Young Alpha cell'
            elif name.startswith('old_alpha'):
                print 'Type: Old Alpha cell'
            elif name.startswith('beta'):
                print 'Type: Beta cell'
            elif name.startswith('young_beta'):
                print 'Type: Young Beta cell'
            elif name.startswith('old_beta'):
                print 'Type: Old Beta cell'
            elif name.startswith('delta'):
                print 'Type: Delta cell'
            elif name.startswith('young_delta'):
                print 'Type: Young Delta cell'
            elif name.startswith('old_delta'):
                print 'Type: Old Delta cell'
            elif name.startswith('perycyte') or name.startswith('pericyte'):
                print 'Type: Pericyte'
            elif name.startswith('unknown'):
                print 'Type: Unknown cell'
            elif 'fibroblast' in name:
                print 'Type: Fibroblast'
        print '\n'
