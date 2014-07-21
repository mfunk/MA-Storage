#!/usr/bin/env python
# -*- coding: latin-1 -*-

##""********************************************************************************************************************
##TOOL NAME: Linear Line of Sight
##SOURCE NAME: LinearLineOfSight.py
##VERSION: ArcGIS 9.3
##AUTHOR: Environmental Systems Research Institute Inc.
##REQUIRED ARGUMENTS: <observer x>,<observer y>,<observer offset>,<target x>,<target y>,<target z>,<input surface>,<output workspace>,<line of sight name>,<obstruction name>
##
##TOOL DESCRIPTION: From an input observer point and target point this tool produces a line of sight and obstruction points for a surface.
##
##DATE: 2/27/2007 - orignial coding.
##
##Usage: LinearLineOfSight(<observer x>,<observer y>,<observer offset>,<target x>,<target y>,<target z>,<input surface>,<METERS | FEET>,<output workspace>,<line of sight name>,<obstruction name>,{spatial reference},{TRUE | FALSE})
##*********************************************************************************************************************"""


# error messages
msgTooFewArguments = "Too few arguments to run LinearLineOfSight: \n LinearLineOfSight(<observer x>,<observer y>,<observer offset>,<target x>,<target y>,<target z>,<input surface>,<output workspace>,<line of sight name>,<obstruction name>)"
msgNo3DLicense = "This tool could not find and available 3D Analyst license."
msgNoInputSurface = "Input surface %s does not exist."
msgWrongSurfaceType = "Input surface must be a Raster Dataset or an Raster Catalog."
msgOutputExists = "Output dataset %s already exists."
msgSpatialRefsDoNotMatch = "Spatial references between the observer/target points and input surface must be the same."
msgAddObserverFailed = "Could not create observer point"
msgAddTargetFailed = "Could not create target point"
msgCreateTempFailed = "Could not create temporary line of sight file: \n %s"
msgLOSFailed = "Calculation of LLOS failed: \n %s"
msgCouldNotSetZDomain = "Internal Error: Could not set ZDomain for temporary surface."
msgCouldNotInterpolateZ = "Could not interpolate Z falue on surface."
msgPlotLibSources = "\n Install the NUMPY and MATPLOTLIB libraries from source organizations:\n NUMPY: http://www.scipy.org/ \n MATPLOTLIB: http://matplotlib.sourceforge.net/"
msgNUMPYNotAvailable = "The NUMPY library is not avaliable to LLOS." + msgPlotLibSources
msgPYLABNotAvailable = "The PYLAB (MATPLOTLIB) library is not available to LLOS." + msgPlotLibSources
msgPlotCloseWindowMessage = "The Linear Line of Sight tool will complete after the plot window is closed."

# status messages
msgAddingObserver = "Creating observer point at: %s, %s, %s"
msgAddingTarget = "Creating target point at: %s, %s, %s"

# import libraries
import os,sys,string, time, types
import arcgisscripting
import MAScriptUtils, Observer

# create the Geoprocessor
gp = arcgisscripting.create(9.3)

debug = False
plot = True

# get script parameters
if (len(sys.argv) < 11):
    raise Exception, msgTooFewArguments

observer_x = gp.GetParameterAsText(0) #<observer x>
observer_y = gp.GetParameterAsText(1) #<observer y>
observer_offset = gp.GetParameterAsText(2) #<observer offset>
if (observer_offset == None or observer_offset == "#"):
    observer_offset = 0.0
target_x = gp.GetParameterAsText(3) #<target x>
target_y = gp.GetParameterAsText(4) #<target y>
target_offset = gp.GetParameterAsText(5) #<target offset>
if (target_offset == None or target_offset == "#"):
    target_offset = 0.0
input_surface = gp.GetParameterAsText(6) #<input surface>
z_units = gp.GetParameterAsText(7) # z_units of surface
output_workspace = gp.GetParameterAsText(8) #<output workspace>
line_of_sight_name = gp.GetParameterAsText(9) #<line of sight name>
obstruction_name = gp.GetParameterAsText(10) #<obstruction name>
spatial_ref = gp.GetParameterAsText(11) #{spatial reference}


try:
    
    if debug == True:
        print "Starting LLOS"
        gp.AddMessage("Starting LLOS")
    
    # set temp workspace
    tempworkspace = MAScriptUtils.GetTempWorkspace(gp)
    gp.workspace = tempworkspace[1]    

    # ERROR getting CONFIGKeyword
    # get tempworkspace parameters
    #params = MAScriptUtils.DatabaseParams(gp,tempworkspace[1])
    #ConfigKeyword = params[1]
    #SpatialGrid1 = params[2]
    #SpatialGrid2 = params[3]
    #SpatialGrid3 = params[4]

    # if spatial ref is empty
    if (spatial_ref == None or spatial_ref == "#"):
        spatial_ref = MAScriptUtils.SetGeographicWGS84(gp)

    # check for 3D license
    if (MAScriptUtils.CheckFor3DAnalystLicense(gp) != True):
        raise Exception, msgNo3DLicense
    else:
        gp.CheckOutExtension("3d")
    
    # mfunk 2/6/2008 - Now handled in ToolValidator
    # check that input surface exists
    #if (gp.Exists(input_surface) == False):
    #    raise Exception, msgNoInputSurface % (input_surface)
    
    # is surface a catalog or dataset?
    bCatalog = False # assume dataset for now
    describe_input_surface = gp.describe(input_surface)
    if (debug == True): print "surface type: " + str(describe_input_surface.DatasetType)
    if (describe_input_surface.DatasetType == "RasterCatalog"):
        bCatalog = True
    elif (describe_input_surface.DatasetType == "RasterDataset"):
        bCatalog = False
    else:
        raise Exception, msgWrongSurfaceType
    
    # mfunk 2/6/2008 - Now handled in ToolValidator
    # check that outputs do not exist
    out_los = output_workspace + os.sep + line_of_sight_name
    out_obstructions = output_workspace + os.sep + obstruction_name
    #if (gp.Exists(out_los) == True and gp.Exists(out_obstructions) == False):
    #    raise Exception, msgOutputExists % (out_los)
    #elif (gp.Exists(out_los) == False and gp.Exists(out_obstructions) == True):
    #    raise Exception, msgOutputExists % (out_obstructions)
    #elif (gp.Exists(out_los) == True and gp.Exists(out_obstructions) == True):
    #    raise Exception, msgOutputExists % (out_los + " and " + out_obstructions)
    
    # mfunk 2/7/2008 - make sure that we don't cause an error if the workspace is a folder
    DatabaseType = MAScriptUtils.DatabaseType(gp,output_workspace)
    if (DatabaseType == "FileSystem"):
        out_los = out_los + r".shp"
        out_obstructions = out_obstructions + r".shp"
    
    
    # spatial ref into an object
    if (type(spatial_ref) is types.StringType):
        spatial_ref = MAScriptUtils.CreateSpatialReferenceFromString(gp,spatial_ref)
    
    # mfunk 2/6/2008 - Now handled in ToolValidator
    # check that coordinate systems are the same
    surf_sr = gp.describe(input_surface).SpatialReference
    surf_sr_name = surf_sr.Name
    #spatial_ref_name = spatial_ref.Name.replace("'","") # cheap workaround: try and trim the single quotes
    #if (debug == True): print "surf sr: " + str(surf_sr_name) + "\nObs sr: " + str(spatial_ref_name)
    #if (surf_sr_name != spatial_ref_name):
    #    raise Exception, msgSpatialRefsDoNotMatch
    
    if debug == True:
        print "Finished initial checks"
        gp.AddMessage("Finished initial checks")
    
    # perhaps read these from Registry?
    bUseCurvature = False
    refraction_factor = 0.13
    
    # define XY exent of the observer and target points
    x_min = min(float(observer_x),float(target_x))
    x_max = max(float(observer_x),float(target_x))
    x_diff = float(x_max) - float(x_min)
    y_min = min(float(observer_y),float(target_y))
    y_max = max(float(observer_y),float(target_y))
    y_diff = float(y_max) - float(y_min)
    # expand the extent by 50%
    x_min -= (x_diff * 0.5)
    x_max += (x_diff * 0.5)
    y_min -= (y_diff * 0.5)
    y_max += (y_diff * 0.5)
    input_ext = [x_min,y_min,x_max,y_max]
    # if catalog, mosaic and clip to temp LOS
    if (bCatalog == True):
        tempsurface = MAScriptUtils.GenerateTempFileName(gp,tempworkspace[1],"RasterDataset")
        tempsurface = MAScriptUtils.MosaicAndClip(gp,input_surface,tempsurface,input_ext)
        input_surface = tempsurface
    if (debug == True):
        print "clipped surface"
        gp.AddMessage("clipped surface")
    
    # Create observer point
    try:
        observer_point = Observer.Observer(gp)
        observer_point.X = observer_x
        observer_point.Y = observer_y
        observer_spot = observer_point.InterpolateZ(gp,input_surface,"BILINEAR")
        if (observer_spot == None):
            raise Exception, msgCouldNotInterpolateZ
        observer_point.Z = float(observer_spot) + float(observer_offset)
        
        gp.AddMessage(msgAddingObserver % (observer_point.X,observer_point.Y,observer_point.Z))
        print msgAddingObserver % (observer_point.X,observer_point.Y,observer_point.Z)
    except:
        raise Exception, msgAddObserverFailed
    
    if (debug == True):
        print "Created observer point: " + str(observer_point.X) + "," + str(observer_point.Y)
        gp.AddMessage("Created observer point: " + str(observer_point.X) + "," + str(observer_point.Y))
    
    # Create target point
    try:
        target_point = Observer.Observer(gp)
        target_point.X = target_x
        target_point.Y = target_y
        
        target_spot = target_point.InterpolateZ(gp,input_surface,"BILINEAR")
        
        if (target_spot == None):
            raise Exception, msgCouldNotInterpolateZ
        target_point.Z = float(target_spot) + float(target_offset)
        
        gp.AddMessage(msgAddingTarget % (target_point.X,target_point.Y,target_point.Z))
        print msgAddingTarget % (target_point.X,target_point.Y,target_point.Z)
    except:
        raise Exception, msgAddTargetFailed
    
    if debug == True:
        print "Created target point: " + str(target_point.X) + "," + str(target_point.Y)
        gp.AddMessage("Created target point: " + str(target_point.X) + "," + str(target_point.Y))
    
    # need to set the ZDomain for the spatial reference
    zmin = min(target_point.Z,observer_point.Z)
    zmax = max(target_point.Z,observer_point.Z)
    zexpand = ((zmax - zmin) * 0.5)
    zmin = float(zmin - zexpand)
    zmax = float(zmax + zexpand)
    
    #set analysis environment
    gp.Extent = "MAXOF"
    gp.OutputZFlag = "enabled"
    if (DatabaseType == "LocalDatabase"):
    #if (params[0] == "LocalDatabase"): # removed params because of CONFIGKeyword errors
        gp.ZDomain = str(zmin) + " " + str(zmax)

    if debug == True:
        gp.AddMessage("setting zdomain: %s to %s" % (str(zmin),str(zmax)))
        print "setting zdomain: %s to %s" % (str(zmin),str(zmax))
        #setting zdomain: 1402.67881391 to 1951.75694464
    
    # Can we set the z domain directly in the SR?
    #spatial_ref.SetZDomain(zmin,zmax) #ERROR in ArcCatalog: 'unicode' object has no attribute 'SetZDomain'
    #spatial_ref.ZDomain = str(zmin) + " " + str(zmax) #ERROR in ArcCatalog: 'unicode' object has no attribute 'ZDomain'

    
    if debug == True:
        print "Set zdomain"
        gp.AddMessage("Set zdomain")
    
    #create temp LOS
    templos = MAScriptUtils.GenerateTempFileName(gp,tempworkspace[1],"FeatureClass")
    try:
        gp.CreateFeatureClass(tempworkspace[1],os.path.basename(templos),"POLYLINE","#","#","ENABLED",spatial_ref,"#","#","#","#") #ConfigKeyword,SpatialGrid1,SpatialGrid2,SpatialGrid3)
    except:
        raise Exception, msgCreateTempFailed % (gp.GetMessages())
    
    #create the line geometry from observer and target
    try:
        lineArray = gp.CreateObject("Array")
        obs_pnt = gp.CreateObject("Point")
        obs_pnt.X = observer_point.X
        obs_pnt.Y = observer_point.Y
        obs_pnt.Z = observer_point.Z
        lineArray.add(obs_pnt)
        tgt_pnt = gp.CreateObject("Point")
        tgt_pnt.X = target_point.X
        tgt_pnt.Y = target_point.Y
        tgt_pnt.Z = target_point.Z
        lineArray.add(tgt_pnt)
        #add the line to the temp file
        rows = gp.InsertCursor(templos)
        row = rows.NewRow()
        row.shape = lineArray
        rows.InsertRow(row)
        lineArray.RemoveAll()
    except:
        raise Exception, msgCreateTempFailed % (gp.GetMessages())
    
    if debug == True:
        print "Created temp 2D los"
        gp.AddMessage("Created temp 2D los")

    
    try:
        gp.LineOfSight_3d(input_surface,templos,out_los,out_obstructions,bUseCurvature,bUseCurvature,refraction_factor)
    except:
        gpmessages = gp.GetMessages()
        raise Exception, (msgLOSFailed % (gpmessages))
    
    if debug == True:
        print "Ran llos"
        gp.AddMessage("Ran llos")
    
    # Check output LOS for visibility
    out_isvisible = False # default is False, it is not visible
    vis_rows = gp.SearchCursor(out_los)
    vis_row = vis_rows.next()
    vis_val = vis_row.GetValue("TarIsVis")
    if (vis_val == 0):
        out_isvisible = False
        gp.AddMessage("Target is NOT VISIBLE.")
    else:
        out_isvisible = True
        gp.AddMessage("Target is VISIBLE.")
    del vis_row, vis_rows
    
    # mfunk 2/6/2008 - drop this guy
    #if (plot == True):
    #    # check that numpy and pylab (matplotlib) libraries have been installed.
    #    try:
    #        import numpy # can we import it?
    #    except ImportError:
    #        gp.AddWarning(msgNUMPYNotAvailable)
    #        print msgNUMPYNotAvailable
    #    else:
    #        try:
    #            import pylab
    #        except ImportError:
    #            gp.AddWarning(msgPYLABNotAvailable)
    #            print msgPYLABNotAvailable
    #        else:
    #            
    #            del numpy #remove ref to libarary (it will be called later)
    #            del pylab 
    #            # Generate list of coords for profile graph and plot them
    #            print msgPlotCloseWindowMessage
    #            gp.AddMessage(msgPlotCloseWindowMessage)
    #            profile = MAScriptUtils.GenerateProfileLine(gp,out_los,z_units)
    
    # remove temp datasets
    try:
        gp.Delete(templos) # remove temp LOS
        if (bCatalog == True):
            gp.Delete(tempsurface) # remove temp surface
        if (tempworkspace[0] == True):
            gp.Delete(tempworkspace[1])
    except:
        raise Exception, gp.GetMessages()
    
    # return the 3D license.
    gp.CheckInExtension("3d")
    
    # set the output
    gp.SetParameter(12,out_los)
    gp.SetParameter(13,out_obstructions)
    gp.SetParameter(14,out_isvisible)
    
except Exception, ErrorMessage:

    if ("tempsurface" in globals()): gp.Delete(tempsurface)
    if ("templos" in globals()): gp.Delete(templos)
    if (tempworkspace[0] == True): gp.Delete(tempworkspace[1])
    
    # return the 3D license.
    gp.CheckInExtension("3d")
    
    gp.AddError(str(ErrorMessage))
    print ErrorMessage
    

del gp
    
