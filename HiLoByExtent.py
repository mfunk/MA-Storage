#!/usr/bin/env python
# -*- coding: latin-1 -*-

##""********************************************************************************************************************
##TOOL NAME: 
##SOURCE NAME: HiLoByExtent.py
##VERSION: ArcGIS 9.3
##AUTHOR: Environmental Systems Research Institute Inc.
##REQUIRED ARGUMENTS: 
##
##TOOL DESCRIPTION: 
##
##DATE: 
##
##Usage: HiLoByExtent(<input_surface>,<input_extent>,<output_workspace>,<output_featureclass_name>,{HIGHEST | LOWEST})
##*********************************************************************************************************************"""

# messages
msgNoSpatialLicense = "This tool could not find and available Spatial Analyst license."
msgTooFewArguments = "Incorrect number of arguments. \n Syntax should be as follows: \n HiLoByExtent(<input_surface>,<input_extent>,<output_workspace>,<output_featureclass_name>,{HIGHEST | LOWEST})"
msgOutputFCExists = "Output feature class %s already exists."
msgInputNoExist = "Input surface %s does not exist."
msgNoSchemaLock = "Could not obtain schema lock on output workspace %s."
msgExtentOutsideSurface = "The extent specified is outside of the input surface."
msgExtentWrongSize = "The input extent must contain coordinates for Left, Bottom, Right and Top of the bounding box."
msgCreateConstantError = "Could not create temp zone dataset:\n %s"
msgZonalFailed = "Calculation failed:\n %s"
msgPropsFailed = "Could not determine statistics for calculated dataset:\n %s"
msgSetNullFailed = "Could not isolate %s points in surface.\n %s"
msgConversionFailed = "Could not create output feature class:\n %s"

# import libraries
import os,sys,string,time
import arcgisscripting
import MAScriptUtils

# create the Geoprocessor
gp = arcgisscripting.create(9.3)
debug = False

DatabaseType = "RemoteDatabase"
ConfigKeyword = "Defaults"
SpatialGrid1 = "0.0"
SpatialGrid2 = "0.0"
SpatialGrid3 = "0.0"

# get script parameters
arg_len = len(sys.argv)
if (arg_len < 4):
    if debug: print sys.argv
    raise Exception, msgTooFewArguments
    
input_surface = gp.GetParameterAsText(0)
input_extent = gp.GetParameterAsText(1) # Left, Bottom, Right, Top
output_workspace = gp.GetParameterAsText(2)
output_fc_name = gp.GetParameterAsText(3)

if (len(sys.argv) >= 6):
    hi_lo = gp.GetParameterAsText(4)
else:
    hi_lo = "HIGHEST"

try:
    
    # set temp workspace
    tempworkspace = MAScriptUtils.GetTempWorkspace(gp)
    gp.workspace = tempworkspace[1]
    
    # mfunk 2/6/2008 - Getting CONFIGKeyword fails
    # Database type
    #db_params = MAScriptUtils.DatabaseParams(gp,output_workspace)
    #if (len(db_params) != 5): raise Exception, msgNoGPSettings
    #else:
    #    DatabaseType = db_params[0]
    DatabaseType = MAScriptUtils.DatabaseType(gp,output_workspace)
    #    ConfigKeyword = db_params[1]
    #    SpatialGrid1 = db_params[2]
    #    SpatialGrid2 = db_params[3]
    #    SpatialGrid3 = db_params[4]
    
    # check workspace type and fc name for .shp
    if (DatabaseType == "FileSystem"):
        if (output_fc_name[-4:].upper() != ".SHP"):
            output_fc_name = output_fc_name + ".shp"
    
    # mfunk 2/8/2008 - handled in ToolValidator
    # check that inputs exist and outputs do not
    #if (gp.Exists(input_surface) == False):
    #    raise Exception, msgInputNoExist % (input_surface)
    #
    output_fc = output_workspace + os.sep + output_fc_name
    #if (gp.Exists(output_fc) == True):
    #    raise Exception, msgOutputFCExists % (output_fc)
        
    # check for spatial analyst license
    if (MAScriptUtils.CheckForSpatialAnalystLicense(gp) != True):
        raise Exception, msgNoSpatialLicense
    
    # check out spatial license
    gp.CheckOutExtension("spatial")
    
    # check input extent has 4 coord values
    input_extent = input_extent.split(" ")
    if (len(input_extent) != 4):
        raise Exception, msgExtentWrongSize
    
    # mfunk 2/8/2008 - handled in ToolValidator
    # check that extent envelope falls within surface extent
    surf_desc = gp.Describe(input_surface)
    surf_extent_obj = surf_desc.Extent
    surf_extent = [surf_extent_obj.xmin,surf_extent_obj.ymin,surf_extent_obj.xmax,surf_extent_obj.ymax]
    
    if (debug == True):
        msg = "surf_extent: " + str(surf_extent)
        print msg
        gp.AddMessage(msg)
    
    #if (MAScriptUtils.envelopeContainsEnvelope(input_extent,surf_extent) == False):
    #    raise Exception, msgExtentOutsideSurface 
    #poly_in_surface = MAScriptUtils.EnvelopeRelation(gp,input_extent,surf_extent)
    #if (poly_in_surface == 0):
    #    poly_in_surface = True
    #else:
    #    poly_in_surface = False
    #
    #if (poly_in_surface == False):
    #    raise Exception, msgExtentOutsideSurface
    
    # if surface is catalog, mosaic to temp raster dataset
    tempsurf = "0"
    if (surf_desc.DatasetType == "RasterCatalog"):
        # get temp raster name
        tempsurf = MAScriptUtils.GenerateTempFileName(gp,tempworkspace[1],"NoDataRasterDataset")
        input_surface = MAScriptUtils.MosaicAndClip(gp,input_surface,tempsurf,input_extent)
    else:
        # copy to temp workspace
        tempsurf = MAScriptUtils.GenerateTempFileName(gp,tempworkspace[1],"NoDataRasterDataset")
        gp.CopyRaster(input_surface,tempsurf,"#","#","#","NONE","NONE","#")
    
    if (debug == True):
        msg = "tempsurf: " + str(tempsurf)
        print msg
        gp.AddMessage(msg)
        
    # get cellsize and projection of surface
    insurf_desc = gp.Describe(input_surface)
    surf_sr = insurf_desc.SpatialReference
    surf_cellsize = insurf_desc.MeanCellWidth
    
    # set GP environment for analysis
    # - extent
    temp_extent = MAScriptUtils.ListToString(input_extent)       
    gp.Extent = temp_extent
    # - snapraster
    gp.SnapRaster = tempsurf
    # - cell size
    gp.CellSize = surf_cellsize
    
    # convert extent to raster for zone grid
    tempzone = MAScriptUtils.GenerateTempFileName(gp,tempworkspace[1],"NoDataRasterDataset")
    zone_ext = MAScriptUtils.ListToString(input_extent)
    try:
        gp.CreateConstantRaster(tempzone,1,"INTEGER",surf_cellsize,zone_ext)
    except:
        raise Exception, msgCreateConstantError % (gp.GetMessages())
    
    # Do ZONAL op
    if (hi_lo.upper() == "HIGHEST"):
        bHigh = True
    elif (hi_lo.upper() == "LOWEST"):
        bHigh = False
    else:
        gp.AddWarning("Defaulting to HIGHEST calculation")
        print "Defaulting to HIGHEST  calculation"
        bHigh = True

    # Get a temp NoData raster
    tempzstat = MAScriptUtils.GenerateTempFileName(gp,tempworkspace[1],"NoDataRasterDataset")
    
    # If HIGHEST, else LOWEST
    if (bHigh == True):
        try:
            # get the maximum value within the extent
            gp.ZonalStatistics(tempzone,"Value",tempsurf,tempzstat,"MAXIMUM","DATA")
        except:
            raise Exception, msgZonalFailed % (gp.GetMessages())
        
        try:
            # what is the maximum value?
            max_val = gp.GetRasterProperties(tempzstat,"MAXIMUM").GetOutPut(0)
        except:
            raise Exception, msgPropsFailed % (gp.GetMessages())
        
        try:
            # pull the cells that contain the maximum value
            # SETNULL(<input_surface> lt <min_val>,<input_surface>)
            gp.workspace = os.path.dirname(tempsurf)
            expression = "setnull(" + str(os.path.basename(tempsurf)) + " lt " + str(max_val) + "," + str(os.path.basename(tempsurf)) + ")"
            if debug == True:
                print expression
                gp.AddMessage(expression)
            # temp NoData raster
            tempresult = MAScriptUtils.GenerateTempFileName(gp,tempworkspace[1],"NoDataRasterDataset")
            # do the SETNULL as a SOMA expression
            gp.SingleOutputMapAlgebra(expression,tempresult)
            gp.workspace = tempworkspace[1]
        except:
            raise Exception, msgSetNullFailed % (hi_lo.upper(),gp.GetMessages())
    else:
        # here we're going to do LOWEST
        try:
            # get the minimum value within the extent
            gp.ZonalStatistics(tempzone,"Value",tempsurf,tempzstat,"MINIMUM","DATA")
        except:
            raise Exception, msgZonalFailed % (gp.GetMessages())
        
        try:
            # what is the minimum value?
            min_val = gp.GetRasterProperties(tempzstat,"MINIMUM").GetOutPut(0)
        except:
            raise Exception, msgPropsFailed % (gp.GetMessages())
        
        try:
            # pull the cells that contain the minimum value
            # SETNULL(<input_surface> lt <min_val>,<input_surface>)
            gp.workspace = os.path.dirname(tempsurf)
            expression = "SETNULL(" + str(os.path.basename(tempsurf)) + " gt " + str(min_val) + "," + str(os.path.basename(tempsurf)) + ")"
            if debug == True:
                print expression
                gp.AddMessage(expression)
            tempresult = MAScriptUtils.GenerateTempFileName(gp,tempworkspace[1],"NoDataRasterDataset")
            # run SETNULL as s SOMA expression
            gp.SingleOutputMapAlgebra(expression,tempresult)
            gp.workspace = tempworkspace[1]
        except:
            raise Exception, msgSetNullFailed % (hi_lo.upper(),gp.GetMessages())
    
    # Take the resulting highest/lowest cell locations make them into a point using RasterToPoint
    try:
        output_fc = output_fc.replace("\\",os.sep)
        gp.RasterToPoint_conversion(tempresult,output_fc,"VALUE")
    except:
        raise Exception, msgConversionFailed % (gp.GetMessages())
    
    # remove temp raster dataset
    if (gp.Exists(tempsurf) == True): gp.Delete(tempsurf)
    if (gp.Exists(tempzone) == True): gp.Delete(tempzone)
    if (gp.Exists(tempzstat) == True): gp.Delete(tempzstat)
    if (gp.Exists(tempresult) == True): gp.Delete(tempresult)
    
    # set return parameters
    gp.SetParameter(5,output_fc)
    
    # remove temp workspace
    if (tempworkspace[0] == True):
        gp.Delete(tempworkspace[1])
    
    # return spatial analyst license
    gp.CheckInExtension("spatial")

    
except Exception, ErrorMessage:
    # remove temp workspace
    if (tempworkspace[0] == True):
        gp.Delete(tempworkspace[1])
    gp.CheckInExtension("spatial")
    print ErrorMessage
    gp.AddError(str(ErrorMessage))

del gp

