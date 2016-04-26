# Amira Project 600
# Amira

proc load_vrml {fname} {
    # Loads a VRML file and converts it to the Amira Geometry Surface format.
    #
    # Input
    # -----
    # fname: File name of VRML file with .wrl extension
    #
    # Returns
    # -------
    # base: Basename of the file given by fname

    set base [file tail $fname]
    set base [string trimright $base ".wrl"]
    [load $fname] setLabel $base
    set module [appendn $base "-Open-Inventor-To-Surface"]
    create HxGeometryToSurface $module
    $module data connect $base
    $module action snap
    $module fire
    "GeometrySurface" setLabel [appendn $base "-Geometry-Surface"]
    return $base
}

proc remesh_surface {base nTriScaleFactor} {
    # Remeshes an Amira Geometry Surface module with best isotropic vertex
    # placement and contour smoothing enabled. The number of output triangles
    # is calculated by the number of input triangles scaled by the supplied
    # scaling factor (e.g. nTriScaleFactor = 2 will output 2x the number of
    # inputs triangles).
    #
    # Input
    # -----
    # base: Basename of Geometry Surface module
    # nTriScaleFactor: Scaling factor for number of triangles to output
    
    set module [appendn $base "-Remesh-Surface"]
    set nTriIn [[appendn $base "-Geometry-Surface"] getNumTriangles]
    set nTriOut [expr $nTriIn * $nTriScaleFactor]
    create HxRemeshSurface $module
    $module select
    $module data connect [appendn $base "-Geometry-Surface"]
    $module fire
    $module objective setIndex 0 1
    $module interpolateOrigSurface setValue 0
    $module desiredSize setValue 1 $nTriOut
    $module remeshOptions1 setValue 0 0
    $module remeshOptions1 setValue 1 1
    $module fire
    $module remesh snap
    $module fire
}

proc smooth_surface {base val1 val2} {
    # Smooths an Amira Geometry Surface with smoothing iterations and lambda
    # value given by val1 and val2, respectively. 
    #
    # Input
    # -----
    # base: Basename of Geometry Surface module
    # val1: Number of smoothing iterations to perform
    # val2: Lambda value for smoothing
    
    set module [appendn $base "-Smooth-Surface"]
    create HxSurfaceSmooth $module
    $module data connect [appendn $base "-Geometry-Surface.remeshed"]
    $module parameters setValue 0 $val1
    $module parameters setValue 1 $val2
    $module action snap
    $module fire
}

proc create_surface_view {base surfTrans surfColor} {
    # Creates a Surface View module to display an Amira Geometry Surface. 
    # The surface view is set to constant color mode and vertex normals
    # for drawing style.
    #
    # Input
    # -----
    # base: Basename of Geometry Surface module
    # surfTrans: Transparency of surface
    # surfColor: Color or surface, given as a comma-separated R,G,B string.
    #            (e.g.: "1,0,0")
                
    set module [appendn $base "-Surface-View"]
    create HxDisplaySurface $module
    $module data connect [appendn $base "-Geometry-Surface.smooth"]
    $module drawStyle setState 4 1 1 3 1 0 1
    $module fire
    $module baseTrans setValue $surfTrans
    $module colorMode setValue 5
    $module fire
    set surfColor [split $surfColor ","]
    $module colormap setDefaultColor [lindex $surfColor 0] [lindex $surfColor 1] [lindex $surfColor 2]
    $module fire 
}

proc appendn {str_in args} {
    # Appends numerous input strings to one output string.
    #
    # Input
    # -----
    # str_in: Starting string to append to
    # args: Strings to append
    #
    # Returns
    # -------
    # str_out: Output string consisting of all inputs appended

    set str_out $str_in
    foreach arg $args {
        set str_out ${str_out}$arg
    }
    return $str_out
}

proc isnan {x} {
    # Checks if the input is NaN.
    #
    # Input
    # -----
    # x: Variable to be tested
    #
    # Returns
    # -------
    # = 1 if x is NaN, else = 0
    
    if {![string is double $x] | $x != $x} {
        return 1
    } else {
        return 0
    }   
}

proc process_cell {fname color trans} {
    set base [load_vrml $fname]
    remesh_surface $base 1
    smooth_surface $base 10 0.6
    create_surface_view $base $trans $color
}

###
#####
# MAIN
#####
###

process_cell "out/cells/alpha_4_pm.wrl" "1,0,1" 0.7
