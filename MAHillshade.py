#!/usr/bin/env python
# -*- coding: latin-1 -*-

##""********************************************************************************************************************
##TOOL NAME: Hillshade_ma
##SOURCE NAME: MAHillshade.py
##VERSION: ArcGIS 9.3
##AUTHOR: Environmental Systems Research Institute Inc.
##REQUIRED ARGUMENTS: <Input_Surface> <output workspace>,<output raster name> {clip_extent} {AUTO_CALC_Z | MANUAL_Z} {z-factor} {Azimuth} {Altitude} {NO_SHADOWS | SHADOWS}
##
##TOOL DESCRIPTION: Creates a hillshade of input surface raster.
##
##DATE: 
##
##Usage: Hillshade_ma(<Input_Surface_Raster>,<output workspace>,<output raster name>, {clip_extent} ,{AUTO_CALC_Z | MANUAL_Z},{z-factor},{Azimuth},{Altitude},{NO_SHADOWS | SHADOWS})
##*********************************************************************************************************************

## messages
msgNoLicense = "This tool could not find and available Spatial Analyst or 3D Analyst license."
msgTooFewArguments = "Incorrect number of arguments. \n Syntax should be as follows: \n Hillshade_ma <Input_Surface_Raster> <Output_Hillshade_Raster> {AUTO_CALC_Z | MANUAL_Z} {z-factor} {Azimuth} {Altitude} {NO_SHADOWS | SHADOWS}"
msgCatalogDoesNotExist = "Input dataset %s does not exist."
msgRasterExists = "Output raster %s already exists."
msgCouldNotMosaic = "Could not mosaic catalog for processing."
msgCouldNotCalcHillshade = "Could not calculate the hillshade:\n %s"
msgClipEnvDifferent = "clip_extent does not fall within extent of input_surface %s."
msgZFactorCalcWarning = "Correct z factor could not be calculated. Defaulting to 0.00003"
msgUseAutoCalcZ = "Could not read input z_factor. Defaulting to AUTO_CALC_Z"
msgZFactor = "z_factor calculated as: %s"
msgUsingEntireDataset = "Clip extent not defined. Using entire surface."

debug = False

# import libraries
import os, sys, math, time, string
import arcgisscripting
import MAScriptUtils

# create the Geoprocessor
gp = arcgisscripting.create(9.3)

# get script parameters and validate
if (len(sys.argv) < 3):
    raise Exception, msgTooFewArguments

input_raster = gp.GetParameterAsText(0)

# split to workspace and raster name
#target_raster = gp.GetParameterAsText(1)
output_workspace = gp.GetParameterAsText(1)
target_raster_name = gp.GetParameterAsText(2)
target_raster = output_workspace + os.sep + target_raster_name


clip_extent = "#"
if (len(sys.argv) > 4):
    clip_extent = gp.GetParameterAsText(3)
    if (clip_extent == "" or len(clip_extent) == 0 or clip_extent == None):
        clip_extent = "#"
else:
    pass

if (debug == True):
    gp.AddMessage("Clip extent: " + str(clip_extent))
    print "Clip extent: " + str(clip_extent)


if (len(sys.argv) > 5):
    z_calc_method = gp.GetParameterAsText(4)
else:
    z_calc_method = "AUTO_CALC_Z"

if (debug == True):
    gp.AddMessage("Calc Method: " + str(z_calc_method))
    print "Calc Method: " + str(z_calc_method)

if (len(sys.argv) > 6):
    manual_z_factor = gp.GetParameterAsText(5)

if (debug == True):
    gp.AddMessage("Manual ZFactor: " + str(manual_z_factor))
    print "Manual ZFactor: " + str(manual_z_factor)

if (len(sys.argv) > 7):
    manual_azimuth = gp.GetParameterAsText(6)
    if (manual_azimuth == "#" or manual_azimuth == None):
        manual_azimuth = 315.0
else:
    manual_azimuth = 315.0
manual_azimuth = float(manual_azimuth)

if (debug == True):
    gp.AddMessage("Manual azimuth: " + str(manual_azimuth))

if (len(sys.argv) > 8):
    manual_altitude = gp.GetParameterAsText(7)
    if (manual_altitude == "#" or manual_altitude == None):
        manual_altitude = 45.0
else:
    manual_altitude = 45.0
manual_altitude = float(manual_altitude)

if (debug == True):
    gp.AddMessage("Manual altitude: " + str(manual_altitude))
        
if (len(sys.argv) > 9): 
    shadow_option = gp.GetParameterAsText(8)
    if (shadow_option == "#" or shadow_option == None or shadow_option == "NO_SHADOWS"):
        shadow_option = "NO_SHADOWS"
    else:
        shadow_option = "SHADOWS"
else:
    shadow_option = "NO_SHADOWS"

if (debug == True):
    gp.AddMessage("Shadow option: " + str(shadow_option))
    print "Shadow option: " + str(shadow_option)



try:
    # set temp workspace
    work_path = MAScriptUtils.GetTempWorkspace(gp)
    gp.workspace = work_path[1]
    
    # check spatial or 3D license
    bUseSpatial = True
    if (MAScriptUtils.CheckForSpatialAnalystLicense(gp)):
        bUseSpatial = True
        gp.CheckOutExtension("spatial")
    elif (MAScriptUtils.CheckFor3DAnalystLicense(gp)):
        bUseSpatial = False
        gp.CheckOutExtension("3d")
    else:
        raise Exception, msgNoLicense
    
    # mfunk 2/6/2008 - now handled by ToolValidator
    # check that input exits
    #if (gp.Exists(input_raster) == False):
    #    raise Exception, msgCatalogDoesNotExist % (input_raster)
    
    # mfunk 2/6/2008 - now handled by ToolValidator
    # check that output does not exist
    #if (gp.Exists(target_raster) == True):
    #    raise Exception, msgRasterExists % (target_raster)

    # mfunk 2/6/2008 - now handled by ToolValidator
    # check azimuth between 0 and 360 (assume input is float)
    manual_azimuth = math.fabs(float(manual_azimuth))
    if (debug == True):
        msg = "manual_azimuth: " + str(manual_azimuth)
        print msg
    
    #if (manual_azimuth > 360.0):
    #    # if greater than 360 get mod and use instead
    #    manual_azimuth = math.fmod(manual_azimuth,360.0)
    
    # mfunk 2/6/2008 - now handled by ToolValidator
    # check altitude between 0 and 90 (assume input is float)
    manual_altitude = math.fabs(float(manual_altitude))
    if (debug == True):
        msg = "manual_altitude: " + str(manual_altitude)
        print msg
    
    #if (manual_altitude > 90.0):
    #    manual_altitude = 180.0 - manual_altitude
    
    # check z-factor
    if (z_calc_method == "MANUAL_Z"):
        if (manual_z_factor != None or manual_z_factor != "#"):
            # other checks we can do on it?
            z_factor = math.fabs(float(manual_z_factor))
        else:
            z_factor = float(MAScriptUtils.ZFactor(gp,input_raster))
            if (z_factor == None):
                gp.AddWarning(msgZFactorCalcWarning)
                print msgZFactorCalcWarning
                z_factor = float(0.00003)
            else:
                gp.AddWarning(msgUseAutoCalcZ)
                print msgUseAutoCalcZ
    else: # if it is other than "MANUAL_Z"
        z_factor = MAScriptUtils.ZFactor(gp,input_raster)
        if (z_factor == None):
            gp.AddWarning(msgZFactorCalcWarning)
            print msgZFactorCalcWarning
            z_factor = float(0.00003)
    
    if debug == True:
        print msgZFactor % (str(z_factor))
        gp.AddMessage(msgZFactor % (str(z_factor)))
    
    # mfunk 2/6/2008 - now handled by ToolValidator
    # check if the clip extent falls within the dataset
    if (clip_extent != None and clip_extent != "#"):
        clip_extent = clip_extent.split(" ")
    #    if (len(clip_extent) == 4):
    #        # Check that clip extent falls within extent of dataset
    #        in_surf_envelope = gp.Describe(input_raster).Extent.split(" ")
    #        if (MAScriptUtils.envelopeContainsEnvelope(clip_extent,in_surf_envelope) == False):
    #            #envelopes are different
    #            raise Exception, msgClipEnvDifferent % (input_raster)
    #else:
    #    gp.AddMessage(msgUsingEntireDataset)

    # if Raster Catalog mosaic to single surface
    tempsurf = MAScriptUtils.GenerateTempFileName(gp,work_path[1],"RasterDataset")
    surf_desc = gp.Describe(input_raster)
    if (str(surf_desc.DatasetType) == "RasterCatalog"):
        ## if clip_extent is empty, use extent of catalog
        # Mosaic all tiles that fall in extent and clip
        surf_mosaic = MAScriptUtils.MosaicAndClip(gp,input_raster,tempsurf,clip_extent)
        if (surf_mosaic == None):
            raise Exception, msgCouldNotMosaic
        # swap the input catalog with the mosaic
        input_raster = surf_mosaic

    # calculate the hillshade
    try:
        manual_azimuth = str(manual_azimuth)
        manual_altitude = str(manual_altitude)
        if (bUseSpatial == True):
            gp.hillshade_sa(input_raster,target_raster,manual_azimuth, manual_altitude,shadow_option,z_factor)
        else:
            gp.hillshade_3d(input_raster,target_raster,manual_azimuth, manual_altitude,shadow_option,z_factor)
    except:
        raise Exception, msgCouldNotCalcHillshade % (gp.GetMessages())
    
    #Set output parameters
    gp.SetParameter(8,target_raster)
    
    # cleanup
    if (gp.Exists(tempsurf)): gp.Delete(tempsurf)
    if (bUseSpatial == True):
        gp.CheckInExtension("spatial")
    else:
        gp.CheckInExtension("3d")
    
    # delete temp workspace
    if (work_path[0] == True and gp.Exists(work_path[1]) == True):
        gp.Delete(work_path[1])
    
except Exception, ErrorMessage:
    if (work_path[0] == True and gp.Exists(work_path[1]) == True):
        gp.Delete(work_path[1])
    
    if (bUseSpatial == True):
        gp.CheckInExtension("spatial")
    else:
        gp.CheckInExtension("3d")
        
    gp.AddError(str(ErrorMessage))
    print ErrorMessage

del gp
