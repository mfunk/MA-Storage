#!/usr/bin/env python
# -*- coding: latin-1 -*-

##""********************************************************************************************************************
##TOOL NAME: 
##SOURCE NAME: HiLoByPolygon.py
##VERSION: ArcGIS 9.3
##AUTHOR: Environmental Systems Research Institute Inc.
##REQUIRED ARGUMENTS: 
##
##TOOL DESCRIPTION: 
##
##DATE: 
##
##Usage: HiLoByPolygon(<input_polygons>,<input_surface>,<output_workspace>,<output_featureclass_name>,{HIGHEST | LOWEST},{ZONE | REGION},{zone_field})
##*********************************************************************************************************************"""

# messages
msgNoSpatialLicense = "This tool could not find and available Spatial Analyst license."
msgTooFewArguments = "Incorrect number of arguments. \n Syntax should be as follows: \n HiLoByPolygon(<input_polygons>,<input_surface>,<output_workspace>,<output_featureclass_name>,{HIGHEST | LOWEST},{ZONE | REGION},{zone_field})"
msgOutputFCExists = "Output feature class %s already exists."
msgPolysNoExist = "Input polygons %s do not exist."
msgBadPolyExtent = "Input polygons %s have bad extent values. The extent values must fall within the input surface."
msgSurfaceNoExist = "Input surface %s does not exist."
msgNoSchemaLock = "Could not obtain schema lock on output workspace %s."
msgCoordSysNotSame = "Coordinate system between polygons and surface do not match.\nThe coordinate systems must be exactly the same."
msgPolygonsOutsideSurface = "The polygon's extent is outside of the input surface."
msgConvertPolyToRaster = "Could not process input polygons for calculation:\n %s"
msgZonalFailed = "Calculation failed:\n %s"
msgPropsFailed = "Could not determine statistics for calculated dataset:\n %s"
msgSetNullFailed = "Could not isolate %s points in surface.\n %s"
msgConversionFailed = "Could not create output feature class:\n %s"

# import libraries
import os,sys,string,time
import arcgisscripting
import MAScriptUtils

debug = False

# create the Geoprocessor
gp = arcgisscripting.create(9.3)

if debug == True:
        gp.AddMessage("Got geoprocessor")
        print "Got geoprocessor"

# get script parameters
if (len(sys.argv) < 4):
    raise Exception, msgTooFewArguments
input_polygons = gp.GetParameterAsText(0)
input_surface = gp.GetParameterAsText(1)
output_workspace = gp.GetParameterAsText(2)
output_fc_name = gp.GetParameterAsText(3)

if (len(sys.argv) > 5):
    hi_lo = gp.GetParameterAsText(4)
else:
    hi_lo = "HIGHEST"

bZone = True # default value
if (len(sys.argv) > 6):
    zone_region = gp.GetParameterAsText(5) # should be ZONE or REGION
    if (zone_region == "#" or zone_region.upper() == "ZONE"):
        bZone = True
    elif (zone_region.upper() == "REGION"):
        bZone = False
    else:
        gp.AddMessage("Defaulting to ZONE calculation")
        bZone = True

if (bZone == True):
    if (len(sys.argv) > 7):
        zone_field = gp.GetParameterAsText(6)

if debug == True:
    gp.AddMessage("received parameters")
    print "received parameters"

try:
    
    # set temp workspace
    tempworkspace = MAScriptUtils.GetTempWorkspace(gp)
    gp.workspace = tempworkspace[1]
    
    # check for spatial analyst license
    if (MAScriptUtils.CheckForSpatialAnalystLicense(gp) != True):
        raise Exception, msgNoSpatialLicense
    else:
        # check out spatial license
        gp.CheckOutExtension("spatial")
    if debug == True:
        gp.AddMessage("checked out spatial analyst license")
        print "checked out spatial analyst license"
    
    # mfunk 2/6/2008 - this is handled by the ToolValidator
    # check that inputs exist
    #if (gp.Exists(input_polygons) == False):
    #    raise Exception, msgPolysNotExist % (input_polygons)
    #if (gp.Exists(input_surface) == False):
    #    raise Exception, msgSurfaceNoExist % (input_surface)
    #if debug == True:
    #    gp.AddMessage("checked for inputs")
    #    print "checked for inputs"
    
    # mfunk 2/6/2008 - this is handled by the ToolValidator
    # check that outputs do not exist
    output_fc = output_workspace + os.sep + output_fc_name
    #if (gp.Exists(output_fc) == True):
    #    raise Exception, msgOutputFCExists % (output_fc)
    #if debug == True:
    #    gp.AddMessage("checked for outputs")
    #    print "checked for outputs"
    
    # check that input poly & input surface have same coordinate system
    
    poly_desc = gp.Describe(input_polygons)
    poly_sr = poly_desc.spatialreference
    surf_desc = gp.Describe(input_surface)
    surf_sr = surf_desc.spatialreference
##    if (poly_sr.Name.upper() != surf_sr.Name.upper()):
##        raise Exception, msgCoordSysNotSame
    oidField = poly_desc.oidfieldname
    
    
    # mfunk 2/6/2008 - this is handled by the ToolValidator
    # check that input polys fall within input surface
    poly_extent = poly_desc.Extent
    surf_extent = surf_desc.Extent
    poly_extent = [poly_extent.Xmin,poly_extent.Ymin,poly_extent.Xmax,poly_extent.Ymax]
    surf_extent = [surf_extent.Xmin,surf_extent.Ymin,surf_extent.Xmax,surf_extent.Ymax]
    #poly_in_surface = MAScriptUtils.envelopeContainsEnvelope(poly_extent,surf_extent)
    #bExtOK = True
    #for splst in poly_extent:
    #    if (splst == '1.#QNAN'):
    #        bExtOK = False
    #if (bExtOK == False):
    #    raise Exception, msgBadPolyExtent % (input_polygons)
    #poly_in_surface = MAScriptUtils.EnvelopeRelation(gp,poly_extent,surf_extent)
    #if (poly_in_surface == 0):
    #    poly_in_surface = True
    #else:
    #    poly_in_surface = False
    #
    #if (poly_in_surface == False):
    #    raise Exception, msgPolygonsOutsideSurface
    #
    #if debug == True:
    #    gp.AddMessage("checked that extents are OK")
    #    print "checked that extents are OK"

    
    # Getting CONFIGKeyword causes errors,
    # get temp workspace parameters (if any)
    #temp_params = MAScriptUtils.DatabaseParams(gp,tempworkspace[1])
    DatabaseType = MAScriptUtils.DatabaseType(gp,tempworkspace[1])
    
    
    # if surface is catalog, mosaic to temp raster dataset
    # get props from input surface
    surf_desc = gp.Describe(input_surface)
    tempsurf = "0"
    if (surf_desc.DatasetType == "RasterCatalog"):
        # get temp raster name
        tempsurf = MAScriptUtils.GenerateTempFileName(gp,tempworkspace[1],"NoDataRasterDataset")
        
        #swap the input catalog for the temp surface raster
        input_surface = MAScriptUtils.MosaicAndClip(gp,input_surface,tempsurf,poly_extent)
    else:
        # get temp raster name
        tempsurf = MAScriptUtils.GenerateTempFileName(gp,tempworkspace[1],"NoDataRasterDataset")
        
        gp.CopyRaster(input_surface,tempsurf,"#","#","#","NONE","NONE","#")
        input_surface = tempsurf
    
    surf_desc = None
    
    if debug == True:
        gp.AddMessage("mosaicked input catalog: " + str(input_surface))
        print "mosaicked input catalog"
    
    # get props from input surface
    gp.AddMessage("Getting mean cell size: " + input_surface)
    surf_desc = gp.Describe(input_surface)

    try:
        surf_cell_size = surf_desc.MeanCellWidth
    except:
        gp.AddError("could not get mean cell size:\n %s" % gp.GetMessages())
        raise Exception, "could not get mean cell size:\n %s" % gp.GetMessages()

    if debug == True:
        gp.AddMessage("got mean cell size")
        print "got mean cell size" 
   
    # copy polys to temp feature class
    tempzonepoly = MAScriptUtils.GenerateTempFileName(gp,tempworkspace[1],"FeatureClass")
    
    if (DatabaseType == "FileSystem"):
        tempzonepoly = tempzonepoly + ".shp"
    
    try:
        #gp.Copy_management(input_polygons,tempzonepoly)  # THIS GUY NEVER WORKS!!!
        # 
        #FeatureclassToFeatureclass_conversion (in_Features, out_path, out_name, where_clause, field_mapping, config_keyword)
        gp.FeatureclassToFeatureclass_conversion(input_polygons,os.path.dirname(tempzonepoly),os.path.basename(tempzonepoly))
    except:
        gp.AddError("Could not copy polygons: \n %s" % (gp.GetMessages()))
        print "Could not copy polygons: \n %s" % (gp.GetMessages())
        
    if debug == True:
        gp.AddMessage("copied polys to temp featureclass")
        print "copied polys to temp featureclass"
    
    # check that zone field exists (if set)
    bField = False    
    if (bZone == True):
        if ((zone_field != "#") and (zone_field != None) and (zone_field != "")):
            fields = gp.ListFields(tempzonepoly)
            for field in fields:
                if (field.name.upper() == zone_field.upper()):
                    # found the field
                    bField = True


    if debug == True:
        gp.AddMessage("checked for zone field")
        print "checked for zone field"    

    # if we default to OID for zone field or we have single region
    if ((bZone == False) or (bZone == True and bField == False)):
        # - make new long field
        gp.AddField(tempzonepoly,"ZONE","LONG","8")
        # - calc OID to new long
        rows = gp.UpdateCursor(tempzonepoly)
        row = rows.next()
        while row:
            if (bZone == True):
                oid_val = row.GetValue(oidField)
                row.SetValue("ZONE",oid_val)
            else:
                row.SetValue("ZONE",0)
            rows.UpdateRow(row)
            row = rows.next()
            
        del rows
        zone_field = "ZONE"


    # set GP environment
    # - extent
    ###temp_extent = str(poly_extent).replace("[","").replace("]","").replace(","," ")
    temp_extent = MAScriptUtils.ListToString(poly_extent)
    gp.Extent = temp_extent
    gp.SnapRaster = input_surface
    # - cell size
    gp.CellSize = surf_cell_size

   
    ## convert polys to zones
    tempzoneraster = MAScriptUtils.GenerateTempFileName(gp,tempworkspace[1],"NoDataRasterDataset")
    
    try:
        
        gp.PolygonToRaster(tempzonepoly,zone_field,tempzoneraster,"CELL_CENTER","#",surf_cell_size)
    except:
        raise Exception, msgConvertPolyToRaster % (gp.GetMessages())

    if debug == True:
        gp.AddMessage("converted polys to zones")
        print "converted polys to zones"
    
    # set for Highest or Lowest calculation
    if (hi_lo.upper() == "HIGHEST"):
        bHigh = True
    elif (hi_lo.upper() == "LOWEST"):
        bHigh = False
    else:
        gp.AddWarning("Defaulting to HIGHEST calculation")
        bHigh = True

    
    # zonal statistics to figure out highest/lowest value
    tempzonestats = MAScriptUtils.GenerateTempFileName(gp,tempworkspace[1],"NoDataRasterDataset")
    
    if (bHigh == True):
        try:
            # get the maximum value within the extent
            #gp.ZonalStatistics(tempzoneraster,zone_field,input_surface,tempzonestats,"MAXIMUM","DATA")
            gp.ZonalStatistics(tempzonepoly,zone_field,input_surface,tempzonestats,"MAXIMUM","DATA")
        except:
            raise Exception, msgZonalFailed % (gp.GetMessages())
    else:
        try:
            # get the minimum value within the extent
            #gp.ZonalStatistics(tempzoneraster,zone_field,input_surface,tempzonestats,"MINIMUM","DATA")
            gp.ZonalStatistics(tempzonepoly,zone_field,input_surface,tempzonestats,"MINIMUM","DATA")
        except:
            raise Exception, msgZonalFailed % (gp.GetMessages())

    if debug == True:
        gp.AddMessage("found highest/lowest")
        print "found highest/lowest"

    # extract highest/lowest value cells from surface
    tempresult = MAScriptUtils.GenerateTempFileName(gp,tempworkspace[1],"NoDataRasterDataset")
    
    try:
        # pull the cells that contain the maximum value
        #
        # CON(<input_surface> == <tempzonestats>,<input_surface>)
        #
        expression = "CON(" + str(os.path.basename(input_surface)) + " == " + str(os.path.basename(tempzonestats)) + "," + str(os.path.basename(input_surface)) + ")"
        if debug == True:
            print "expression:" + expression
        gp.workspace = os.path.dirname(input_surface) #tempworkspace[1]
        
        gp.SingleOutputMapAlgebra(expression,tempresult)
        
    except:
        raise Exception, msgSetNullFailed % (hi_lo.upper(),gp.GetMessages())    
    
    if debug == True:
        gp.AddMessage("extracted highest/lowest")
        print "extracted highest/lowest"
    
    # convert to point feature class
    # ERROR:
    # for some reason the RasterToPoint tool is convering ALL of the cells
    # to points, not just the ones that have a VALUE.
    #
    try:
        gp.RasterToPoint_conversion(tempresult,output_fc,"VALUE")
    except:
        raise Exception, msgConversionFailed % (output_fc)

    if debug == True:
        gp.AddMessage("converted output to points")
        print "converted output to points"

    # set output properties
    gp.SetParameter(7,output_fc)
    
    # return spatial analyst license
    gp.CheckInExtension("spatial")

    
    # cleanup
    if (gp.Exists(tempsurf) == True): gp.Delete(tempsurf)
    if (gp.Exists(tempzonepoly) == True): gp.Delete(tempzonepoly)
    if (gp.Exists(tempzoneraster) == True): gp.Delete(tempzoneraster)
    if (gp.Exists(tempzonestats) == True): gp.Delete(tempzonestats)
    if (gp.Exists(tempresult) == True): gp.Delete(tempresult)
    # delete the tempworkspace
    if (tempworkspace[0] == True and gp.Exists(tempworkspace[1]) == True):
        gp.Delete(tempworkspace[1])

    
    
    if debug == True:
        gp.AddMessage("script is done.")
        print "script is done."

except Exception, ErrorMessage:
    # delete the tempworkspace
    if (tempworkspace[0] == True and gp.Exists(tempworkspace[1]) == True):
        gp.Delete(tempworkspace[1])
    # return spatial analyst license
    gp.CheckInExtension("spatial")
    gp.AddError(str(ErrorMessage))
    print ErrorMessage
   
del gp        