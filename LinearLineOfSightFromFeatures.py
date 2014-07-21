#!/usr/bin/env python
# -*- coding: latin-1 -*-

##""********************************************************************************************************************
##TOOL NAME: Linear Line of Sight From Features
##SOURCE NAME: LinearLineOfSightFromFeatures.py
##VERSION: ArcGIS 9.3
##AUTHOR: Environmental Systems Research Institute Inc.
##REQUIRED ARGUMENTS:
##
##TOOL DESCRIPTION: Creates lines of sight from input observer and target point feature classes.
##
##DATE: 
##
##Usage: LinearLineOfSightFromFeatures_ma(<observer_points>,<target_points>,<input_surface>,<output_workspace>,<line_of_sight_name>,<obstruction_name>,{ALL | MATCH})
##*********************************************************************************************************************"""


# error messages
msgTooFewArguments = "Too few arguments to run LinearLineOfSightFromFeatures"
msgNo3DLicense = "This tool could not find and available 3D Analyst license."
msgNoInputSurface = "Input surface %s does not exist."
msgWrongSurfaceType = "Input surface must be a Raster Dataset or an Raster Catalog."
msgOutputExists = "Output dataset %s already exists."
msgMatchingAll = "Could not understand {match_method}, matching ALL observers and targets."
msgSpatialRefsDoNotMatch = "Spatial references between the observer/target points and input surface must be the same."
msgCreateTempFailed = "Could not create temporary line of sight file: \n %s"
msgDifferentInputNumbers = "The number of observer points is different than the number of target points. Not all points will have a match."
msgLOSFailed = "Calculation of LLOS failed: \n %s"
msgObserverPointsDoNotExist = "Input observer points %s do not exist."
msgTargetPointsDoNotExist = "Input target points %s do not exist."
msgObserversNotPoints = "Input observers are not points."
msgTargetsNotPoints = "Input targets are not points."
msgObserversOutsideSurface = "Observer's extent falls outside of surface extent."
msgTargetsOutsideSurface = "Target's extent falls outside of surface extent."

debug = False

# import libraries
import os,sys,string, time, traceback
import arcgisscripting
import MAScriptUtils

# create the Geoprocessor
gp = arcgisscripting.create(9.3)
if (debug == True): gp.AddMessage("Created Geoprocessor")

# get script parameters
if (len(sys.argv) < 1):
    raise Exception, msgTooFewArguments

observer_points = gp.GetParameterAsText(0)
target_points = gp.GetParameterAsText(1)
input_surface = gp.GetParameterAsText(2)
output_workspace = gp.GetParameterAsText(3)
line_of_sight_name = gp.GetParameterAsText(4)
obstruction_name = gp.GetParameterAsText(5)
if (len(sys.argv) > 7):
    match_method = gp.GetParameterAsText(6) # <ALL | MATCH>
else:
    match_method = "ALL"

try:
    
    # check for 3D license
    if (MAScriptUtils.CheckFor3DAnalystLicense(gp) != True):
        raise Exception, msgNo3DLicense
    else:
        gp.CheckOutExtension("3d")
    
    # set temp workspace
    tempworkspace = MAScriptUtils.GetTempWorkspace(gp)
    gp.workspace = tempworkspace[1] 
    
    # mfunk 2/7/2008 - handled in ToolValidator
    # check that input points exist
    #if (gp.Exists(observer_points) == False):
    #    raise Exception, msgObserverPointsDoNotExist % (observer_points)
    #if (gp.Exists(target_points) == False):
    #    raise Exception, msgTargetPointsDoNotExist % (target_points)
    
    # mfunk 2/7/2008 - handled in ToolValidator
    # check that inputs are points (not polylines, etc.)
    obs_desc = gp.describe(observer_points)
    tgt_desc = gp.describe(target_points)
    #if (obs_desc.shapetype != "Point"):
    #    raise Exception, msgObserversNotPoints
    #if (tgt_desc.shapetype != "Point"):
    #    raise Exception, msgTargetsNotPoints
    
    # mfunk 2/7/2008 - handled in ToolValidator
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
    
    # mfunk 2/7/2008 - handled in ToolValidator
    # check that outputs do not exist
    out_los = os.path.join(output_workspace,line_of_sight_name)
    out_obstructions = os.path.join(output_workspace,obstruction_name)
    
    # mfunk 2/7/2008 - make sure that we don't cause an error if the workspace is a folder
    DatabaseType = MAScriptUtils.DatabaseType(gp,output_workspace)
    if (DatabaseType == "FileSystem"):
        out_los = out_los + r".shp"
        out_obstructions = out_obstructions + r".shp"
    
    #if (gp.Exists(out_los) == True and gp.Exists(out_obstructions) == False):
    #    raise Exception, msgOutputExists % (out_los)
    #elif (gp.Exists(out_los) == False and gp.Exists(out_obstructions) == True):
    #    raise Exception, msgOutputExists % (out_obstructions)
    #elif (gp.Exists(out_los) == True and gp.Exists(out_obstructions) == True):
    #    raise Exception, msgOutputExists % (out_los + " and " + out_obstructions)
    
    # mfunk 2/7/2008 - handled in ToolValidator
    # check ALL | MATCH
    if debug == True:
        msg = " " + "match method:" + str(match_method)
        print msg
        gp.AddMessage(msg)
    #if (match_method == "ALL"):
    #    match_method = "ALL"
    #elif (match_method == "MATCH"):
    #    match_method = "MATCH"
    #elif (match_method == "#"):
    #    match_method = "ALL"
    #else:
    #    gp.AddWarning(msgMatchingAll)
    #    match_method = "ALL"
    
    
    # mfunk 2/7/2008 - handled in ToolValidator
    # check coordinate systems are the same
    #obs_spat_name = obs_desc.spatialreference.name
    #tgt_spat_name = tgt_desc.spatialreference.name
    surf_desc = gp.describe(input_surface)
    #surf_spat_name = surf_desc.spatialreference.name
    #if debug == True:
    #    print "obs spat: " + str(obs_spat_name)
    #    print "tgt spat: " + str(tgt_spat_name)
    #    print "surf spat: " + str(surf_spat_name)
    #if (obs_spat_name != tgt_spat_name and obs_spat_name != surf_spat_name and tgt_spat_name != surf_spat_name):
    #    raise Exception, msgSpatialRefsDoNotMatch
    #else:
    #    spatial_ref = obs_desc.spatialreference
    spatial_ref = obs_desc.spatialreference
    
    # mfunk 2/7/2008 - handled in ToolValidator
    # check that both points fall within surface
    obs_extent = obs_desc.Extent
    obs_extent = [obs_extent.xmin,obs_extent.ymin,obs_extent.xmax,obs_extent.ymax]
    tgt_extent = tgt_desc.Extent
    tgt_extent = [tgt_extent.xmin,tgt_extent.ymin,tgt_extent.xmax,tgt_extent.ymax]
    surf_extent = surf_desc.Extent
    surf_extent = [surf_extent.xmin,surf_extent.ymin,surf_extent.xmax,surf_extent.ymax]
    #obs_to_surf = MAScriptUtils.EnvelopeRelation(gp,obs_extent,surf_extent)
    #tgt_to_surf = MAScriptUtils.EnvelopeRelation(gp,tgt_extent,surf_extent)
    #if (obs_to_surf != 0):
    #    raise Exception, msgObserversOutsideSurface
    #if (tgt_to_surf != 0):
    #    raise Exception, msgTargetsOutsideSurface
    
    # Error getting CONFIGKeyword
    # get tempworkspace parameters
    #params = MAScriptUtils.DatabaseParams(gp,tempworkspace[1])
    #ConfigKeyword = params[1]
    #SpatialGrid1 = params[2]
    #SpatialGrid2 = params[3]
    #SpatialGrid3 = params[4]

    # get list of observer points (x,y,z for each)
    observers = []
    z_list = []
    obs_shape_field = obs_desc.ShapeFieldName
    bObsZEnabled = False
    if (obs_desc.hasz == True):
        bObsZEnabled = True
    else:
        bObsZEnabled = False
        
    # Create search cursor
    rows = gp.SearchCursor(observer_points)
    row = rows.Next()
    # Enter while loop for each feature/row
    while row:
        feat = row.GetValue(obs_shape_field)
        pnt = feat.GetPart()
        coords = []
        coords.append(pnt.x)
        coords.append(pnt.y)
        if bObsZEnabled == True:
            coords.append(pnt.z)
            z_list.append(pnt.z)
        observers.append(coords)
        row = rows.Next()
    del rows
    del row
    if debug == True:
        msg = " " + "observers: " + str(observers)
        #print msg
        gp.AddMessage(msg)
    
    # get list of target points (x,y,z for each)
    targets = []
    tgt_shape_field = tgt_desc.ShapeFieldName
    bTgtZEnabled = False
    if (tgt_desc.hasz == True):
        bTgtZEnabled = True
    else:
        bTgtZEnabled = False
    # Create search cursor
    rows = gp.SearchCursor(target_points)
    row = rows.Next()
    # Enter while loop for each feature/row
    while row:
        feat = row.GetValue(tgt_shape_field)
        pnt = feat.GetPart()
        coords = []
        coords.append(pnt.x)
        coords.append(pnt.y)
        if bTgtZEnabled == True:
            coords.append(pnt.z)
            z_list.append(pnt.z)
        targets.append(coords)
        row = rows.Next()
    del rows
    del row
    if debug == True:
        msg = " " + "targets: " + str(targets)
        #print msg
        gp.AddMessage(msg)
    
    # need to set the ZDomain for the spatial reference
    zmin = 0.0
    zmax = 0.0
    if len(z_list) > 0:
        zmin = min(z_list)
        zmax = max(z_list)
    if (zmin == zmax):
        zmin = -100.0
        zmax = 10000.0
    zexpand = ((zmax - zmin) * 0.5)
    zmin = float(zmin - zexpand)
    zmax = float(zmax + zexpand)
    
    # set analysis environment
    DatabaseType = "FileSystem"
    gp.Extent = "MAXOF"
    gp.OutputZFlag = "enabled"
    if (DatabaseType == "LocalDatabase"):
        gp.ZDomain = str(zmin) + " " + str(zmax) # only works on File GDB
    
    #create temp LOS
    templos = MAScriptUtils.GenerateTempFileName(gp,tempworkspace[1],"FeatureClass")
    try:
        result = gp.CreateFeatureClass(tempworkspace[1],os.path.basename(templos),"POLYLINE","#","#","DISABLED",spatial_ref,"#","#","#","#") #ConfigKeyword,SpatialGrid1,SpatialGrid2,SpatialGrid3)
        result_msg = result.GetMessages()
        if (debug == True):
            msg = " " + "writing to: " + str(templos)
            #print msg  -- Raj
            gp.AddMessage(msg)
    except:
        raise Exception, msgCreateTempFailed % (gp.GetMessages())
    
    # add make lines from the observers to the targets
    if (match_method == "ALL"):
        rows = gp.InsertCursor(templos)
        lineArray = gp.CreateObject("Array")
        obs_pnt = gp.CreateObject("Point")
        tgt_pnt = gp.CreateObject("Point")
        
        linecounter = 1
        o = 1
        for obspt in observers:
            t = 1
            for tgtpt in targets:
                
                if (debug == True):
                    msg = " " + "obs " + str(o) + " of " + str(len(observers)) + ", tgt " + str(t) + " of " + str(len(targets))
                    # print msg -- Raj

                # if observer and target are at same coordinates, skip the points
                if ((obspt[0] == tgtpt[0]) and (obspt[1] == tgtpt[1])):
                    msg = " " + str(linecounter) + " - skipping " + str(obspt) + " and " + str(tgtpt)
                    #print msg 
                    gp.AddMessage(msg)
                    
                else:
                    if debug == True:
                        msg = " " + str(linecounter) + " - matching " + str(obspt) + " to " + str(tgtpt)
                        #print msg   - Raj
                        gp.AddMessage(msg)
                    try:
                        
                        obs_pnt.X = obspt[0]
                        obs_pnt.Y = obspt[1]
                        if (bObsZEnabled == True):
                            obs_pnt.Z = obspt[2]
                        lineArray.add(obs_pnt)
                        
                        tgt_pnt.X = tgtpt[0]
                        tgt_pnt.Y = tgtpt[1]
                        if (bTgtZEnabled == True):
                            tgt_pnt.Z = tgtpt[2]
                        lineArray.add(tgt_pnt)
                        
                        row = rows.NewRow()
                        row.shape = lineArray
                        rows.InsertRow(row)
    
                        lineArray.RemoveAll()
                        
                    except:
                        raise Exception, msgCreateTempFailed % (gp.GetMessages())
                    
                linecounter += 1
                t += 1   
            o += 1
        del lineArray
        del obs_pnt
        del tgt_pnt
        del row
        del rows
        

    else: # match_method == "MATCH"
        if (len(observers) != len(targets)):
            gp.AddWarning(msgDifferentInputNumbers)
        counter = 0
        rows = gp.InsertCursor(templos)
        lineArray = gp.CreateObject("Array")
        obs_pnt = gp.CreateObject("Point")
        tgt_pnt = gp.CreateObject("Point")
        while counter <= (min(len(observers),len(targets)) - 1):
            obspt = observers[counter]
            tgtpt = targets[counter]
            if debug == True:
                msg = " " + "matching " + str(obspt) + " to " + str(tgtpt)
                # print msg -- Raj
                gp.AddMessage(msg)
                
            try:
                obs_pnt.X = obspt[0]
                obs_pnt.Y = obspt[1]
                #if (bObsZEnabled == True):
                #    obs_pnt.Z = obspt[2]
                lineArray.add(obs_pnt)
                
                tgt_pnt.X = tgtpt[0]
                tgt_pnt.Y = tgtpt[1]
                #if (bTgtZEnabled == True):
                #    tgt_pnt.Z = tgtpt[2]
                lineArray.add(tgt_pnt)
                
                #add the line to the temp file
                row = rows.NewRow()
                row.shape = lineArray
                rows.InsertRow(row)
                lineArray.RemoveAll()
                
            except:
                raise Exception, msgCreateTempFailed % (gp.GetMessages())
            counter += 1
            
        del lineArray
        del obs_pnt
        del tgt_pnt
        del row
        del rows
  
    # get temp surface
    tempsurface = ""
    if (bCatalog == True):
        # get the LOS extent
        los_extent = gp.describe(templos).Extent
        los_extent = [los_extent.xmin,los_extent.ymin,los_extent.xmax,los_extent.ymax]
        # TODO: check results of string return?
        tempsurface = MAScriptUtils.GenerateTempFileName(gp,tempworkspace[1],"RasterDataset")
        tempsurface = MAScriptUtils.MosaicAndClip(gp,input_surface,tempsurface,los_extent)
        if (tempsurface == None):
            raise Exception, "Internal Error: Could not mosaic catalog."
        input_surface = tempsurface
  
    # perhaps read these from Registry?
    bUseCurvature = False
    refraction_factor = 0.13
  
    # 3D - LOS
    try:
        gp.LineOfSight_3d(input_surface,templos,out_los,out_obstructions,bUseCurvature,bUseCurvature,refraction_factor)
    except:
        gpmessages = gp.GetMessages()
        raise Exception, (msgLOSFailed % (gpmessages))
  
    # return the 3D license.
    gp.CheckInExtension("3d")
    
    # set the output
    gp.SetParameter(7,out_los)
    gp.SetParameter(8,out_obstructions)
    
    # remove temp datasets
    if (gp.Exists(templos) == True):
        gp.Delete(templos)
    if (gp.Exists(tempsurface) == True):
        gp.Delete(tempsurface)
    if (tempworkspace[0] == True):
        gp.Delete(tempworkspace[1])
    
except Exception, ErrorMessage:
    # return the 3D license.
    gp.CheckInExtension("3d")
    # remove temp datasets
    if ("tempsurface" in globals()):
        gp.Delete(tempsurface)
    if ("templos" in globals()):
        gp.Delete(templos)
    if ("tempworkspace" in globals()):
        if (tempworkspace[0] == True):
            gp.Delete(tempworkspace[1])
    print ErrorMessage
    gp.AddError(str(ErrorMessage))

del gp
