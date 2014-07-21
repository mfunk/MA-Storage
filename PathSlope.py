#!/usr/bin/env python
# -*- coding: latin-1 -*-

##""********************************************************************************************************************
##TOOL NAME: Path Slope
##SOURCE NAME: PathSlope.py
##VERSION: ArcGIS 9.3
##AUTHOR: Environmental Systems Research Institute Inc.
##REQUIRED ARGUMENTS:
##
##TOOL DESCRIPTION: 
##
##DATE: 
##
##Usage: PathSlope_ma(<input_path>,<input_surface>,<output_workspace>,<output_pathslope_name>)
##
## <input_path> - polyline featureclass representing the path
## <input_surface> - raster surface (either a dataset or catalog) overwhich the path travels
## <output_workspace> - target workspace where the output will be stored
## <output_pathslope_name> - name for the resulting slope-paths
##
##*********************************************************************************************************************"""

# messages
msgTooFewArguments = "Incorrect number of arguments. \n Syntax should be as follows: \n PathSlope_ma(<input_path>,<input_surface>,<output_workspace>,<output_pathslope_name>)"
msgNoSpatialLicense = "This tool could not find and available Spatial Analyst license."
msgOutputExists = "Output feature class %s already exists."
msgInputNoExist = "Input features %s do not exist."
msgInputNotPolyline = "Input path features are not polylines."
msgNoInputSurface = "Input surface does not exist."
msgSpatialRefsDoNotMatch = "Spatial references between the path features and input surface must be the same."
msgPathOutsideSurface = "Path extent falls outside of surface extent."
msgWrongSurfaceType = "Input surface must be a Raster Dataset or an Raster Catalog."
msgSlopeFailed = "Calculating slope for input surface failed: \n %s"
msgReclassifyFailed = "Internal Error: Reclassify failed on tempslope: \n %s"
msgReclassConvFailed = "Internal Error: Failed to convert reclassified slope to polys: \n %s"
msgIntersectFailed = "Internal Error: Intersection of slope to path failed: \n %s"
msgAddFieldsFailed = "Internal Error: Could not add FACC slope fields to output path slope features: \n %s"
msgCalcFieldsFailed = "Internal Error: Could not add FACC slope values to output path slope features, values will be invalid: \n %s"
msgCalcSlope = "Calculating slope ..."
msgReclassifying = "Reclassifying slope values ..."
msgIntersecting = "Intersecting slope with path ..."
msgNeedArcInfoLicense = "Need ArcInfo Product License..."  #Raj

debug = False

# import libraries
import os,sys,string, time
import arcgisscripting
import MAScriptUtils

# create the Geoprocessor
gp = arcgisscripting.create(9.3)

# get script parameters
if (len(sys.argv) < 1):
    raise Exception, msgTooFewArguments
path_features = gp.GetParameterAsText(0)
input_surface = gp.GetParameterAsText(1)
output_workspace = gp.GetParameterAsText(2)
out_slope_name = gp.GetParameterAsText(3)


if(gp.ProductInfo() != "ArcInfo"):   #Raj
    raise Exception, msgNeedArcInfoLicense
 


try:
    
    # check for spatial analyst license
    if (MAScriptUtils.CheckForSpatialAnalystLicense(gp) != True):
        raise Exception, msgNoSpatialLicense
    else:
        gp.CheckOutExtension("spatial")
    
    # set temp workspace
    tempworkspace = MAScriptUtils.GetTempWorkspace(gp)
    gp.workspace = tempworkspace[1] 

    # mfunk 2/5/2008 - will be handled in the toolvalidator
    # check that input path exists
    #if (gp.Exists(path_features) != True):
    #    raise Exception, msgInputNoExist % (path_features)
    
    # mfunk 2/5/2008 - will be handled in the toolvalidator
    # check that input path is polyline
    path_desc = gp.Describe(path_features)
    #if (path_desc.shapetype != "Polyline"):
    #    raise Exception, msgInputNotPolyline
    
    # mfunk 2/5/2008 - will be handled in the toolvalidator
    # check that input surface exists
    #if (gp.Exists(input_surface) != True):
    #    raise Exception, msgNoInputSurface
    
    # mfunk 2/5/2008 - will be handled in the toolvalidator
    # check that surface is Raster Dataset or Raster Catalog
    surf_desc = gp.describe(input_surface)
    bCatalog = False # assume dataset for now
    #if (debug == True): print "surface type: " + str(surf_desc.DatasetType)
    if (surf_desc.DatasetType == "RasterCatalog"):
        bCatalog = True
    elif (surf_desc.DatasetType == "RasterDataset"):
        bCatalog = False
    else:
        raise Exception, msgWrongSurfaceType
    
    # mfunk 2/5/2008 - will be handled in the toolvalidator
    # check that inputs have same coordinate system
    #path_spat_name = path_desc.spatialreference.name
    #surf_spat_name = surf_desc.spatialreference.name
    #if debug == True:
    #    print "path spat: " + str(path_spat_name)
    #    print "surf spat: " + str(surf_spat_name)
    #if (path_spat_name != surf_spat_name):
    #    raise Exception, msgSpatialRefsDoNotMatch
    #else:
    #    spatial_ref = path_desc.spatialreference

    # mfunk 2/5/2008 - will be handled in the toolvalidator
    # check that path extent falls within surface extent
    path_extent = path_desc.Extent
    path_extent = [path_extent.xmin,path_extent.ymin,path_extent.xmax,path_extent.ymax]
    #path_extent = MAScriptUtils.StringToList(path_extent)
    surf_extent = surf_desc.Extent
    surf_extent = [surf_extent.xmin,surf_extent.ymin,surf_extent.xmax,surf_extent.ymax]
    #surf_extent = MAScriptUtils.StringToList(surf_extent)
    
    #path_to_surf = MAScriptUtils.EnvelopeRelation(gp,path_extent,surf_extent)
    #if (path_to_surf != 0):
    #    raise Exception, msgPathOutsideSurface
    
    # mfunk 2/5/2008 - will be handled in the toolvalidator
    # check that output does not exist
    if (MAScriptUtils.DatabaseType(gp,output_workspace) == "FileSystem"):
        out_slope_path = output_workspace + os.sep + out_slope_name + ".shp"
    else:
        out_slope_path = output_workspace + os.sep + out_slope_name
    #if (gp.Exists(out_slope_path) == True):
    #    raise Exception, msgOutputExists % (out_slope_path)
    
    # mosaic catalog if necessary
    if (bCatalog == True):
        tempsurface = MAScriptUtils.GenerateTempFileName(gp,tempworkspace[1],"RasterDataset")
        tempsurface = MAScriptUtils.MosaicAndClip(gp,input_surface,tempsurface,path_extent)
        input_surface = tempsurface
    
    # measurement type and z_factor
    measurement_type = "DEGREE"
    z_factor = MAScriptUtils.ZFactor(gp,input_surface)
    
    # get slope raster from surface
    #Slope_sa (in_raster, out_raster, output_measurement, z_factor)
    try:
        gp.addmessage(msgCalcSlope)
        tempslope = MAScriptUtils.GenerateTempFileName(gp,tempworkspace[1],"NoDataRasterDataset")
        gp.slope_sa(input_surface,tempslope,measurement_type,z_factor)
    except:
        gpmessages = gp.GetMessages()
        raise Exception, msgSlopeFailed % (gpmessages)
    
    # calc stats on the slope raster
    try:
        # CalculateStatistics_management (in_raster_dataset, x_skip_factor, y_skip_factor, ignore_values) 
        gp.calculatestatistics_management(tempslope)
    except:
        pass
    
    # reclassify slope dataset to FACC_2.1 - SPR att.
    #ATT_CODE    ATT_VAL	        ATT_VAL_DESCRIPTION
    #SPR	        000		Unknown
    #SPR	        001		<= 3%
    #SPR	        002		> 3% and <= 10%
    #SPR	        003		> 10% and <= 15%
    #SPR	        004		> 15% and <= 20%
    #SPR	        005		> 20% and <= 30%
    #SPR	        006		> 30% and <= 45%
    #SPR	        007		> 45% and <= 60%
    #SPR	        008		> 60% and <= 85%
    #SPR	        009		> 85%
    remap_list = []
    remap_list.append([0,"SPR","000","Unknown"])
    remap_list.append([1,"SPR","001","<= 3"])
    remap_list.append([2,"SPR","002","> 3 and <= 10"])
    remap_list.append([3,"SPR","003","> 10 and <= 15"])
    remap_list.append([4,"SPR","004","> 15 and <= 20"])
    remap_list.append([5,"SPR","005","> 20 and <= 30"])
    remap_list.append([6,"SPR","006","> 30 and <= 45"])
    remap_list.append([7,"SPR","007","> 45 and <= 60"])
    remap_list.append([8,"SPR","008","> 60 and <= 85"])
    remap_list.append([9,"SPR","009","> 85"])
    
    # create ASCII remap table
    remap = r"0 3 1;3 10 2;10 15 3;15 20 4;20 30 5;30 45 6;45 60 7;60 85 8;85 90 9"
    
    # reclassify slope values
    missing_values = "NODATA"
    try:
        tempreclass = MAScriptUtils.GenerateTempFileName(gp,tempworkspace[1],"NoDataRasterDataset")
        gp.addmessage(msgReclassifying)
        # Reclassify_sa (in_raster, reclass_field, remap, out_raster, missing_values)
        gp.Reclassify_sa(tempslope,"VALUE",remap,tempreclass,missing_values)        
    except:
        gpmessages = gp.GetMessages()
        raise Exception, msgReclassifyFailed % (gpmessages)
    
    # Convert reclass raster to polys
    try:
        temppoly = MAScriptUtils.GenerateTempFileName(gp,tempworkspace[1],"FeatureClass")
        simplify = "NO_SIMPLIFY"
        # RasterToPolygon_conversion (in_raster, out_polygon_features, simplify, raster_field)
        gp.RasterToPolygon_conversion(tempreclass,temppoly,simplify,"VALUE")
    except:
        gpmessages = gp.GetMessages()
        raise Exception, msgReclassConvFailed % (gpmessages)
    
    # split path into slope classifications.
    try:
        attrib_xfer = "NO_FID"
        cluster_tol = "#"
        output_type = "LINE"
        rel_xfer = "NO_RELATIONSHIPS"
        gp.addmessage(" " + msgIntersecting)
        # Identity_analysis (in_features, identity_features, out_feature_class, join_attributes, cluster_tolerance, relationship)
        gp.Identity_analysis(path_features,temppoly,out_slope_path,attrib_xfer,cluster_tol,rel_xfer)
    except:
        gpmessages = gp.GetMessages()
        raise Exception, msgIntersectFailed % (gpmessages)

    # add fields (text,len=20)
    try:
        # check for schema lock?
        # AddField_management (in_table, field_name, field_type, field_precision, field_scale, field_length, field_alias, field_is_nullable, field_is_required, field_domain)
        gp.AddField_management(out_slope_path,"ATT_CODE", "TEXT", "", "", "5", "", "#", "#", "")
        gp.AddField_management(out_slope_path,"ATT_VAL", "TEXT", "", "", "5", "", "#", "#", "")
        gp.AddField_management(out_slope_path,"ATT_DESC", "TEXT", "", "", "20", "", "#", "#", "")
        if debug == True: print "added fields to slope fc"

    except:
        gpmessages = gp.GetMessages()
        warning = msgAddFieldsFailed % (gpmessages)
        gp.AddWarning(" " + str(warning))
        raise Exception, warning
    else:
        # calc values using remap_list
        try:
            #count = 0
            rows = gp.UpdateCursor(out_slope_path)
            row = rows.next()
            while row:
                slope_class = row.GetValue("GRIDCODE")
                slope_class = int(slope_class)
                
                remap_vals = remap_list[slope_class]
                
                row.SetValue("ATT_CODE",remap_vals[1])
                row.SetValue("ATT_VAL",remap_vals[2])
                row.SetValue("ATT_DESC",remap_vals[3])
                #if debug == True: print "assigning values:" + str(remap_vals)  -- Raj
                #count = count + 1
                #gp.addmessage("assigning values:" + str(remap_vals)+ "ROW:" + str(count))
                rows.UpdateRow(row)
                row = rows.next()
            del rows
            del row
        except:
            gpmessages = gp.GetMessages()
            warning = msgCalcFieldsFailed % (gpmessages)
            gp.AddWarning(" " + str(warning))
            pass

    # return spatial analyst license
    gp.CheckInExtension("spatial")
    
    # cleanup temp stuff
    if debug == False:
        removelist = ["tempslope","tempsurface","tempreclass","temppoly"]
        for remove in removelist:
            if (remove in globals()):
                if (gp.Exists(remove) == True): gp.Delete(remove)
        if (tempworkspace[0] == True and gp.Exists(tempworkspace[1]) == True): gp.Delete(tempworkspace[1])
    
    # set output params
    gp.SetParameter(4,out_slope_path)


except Exception, ErrorMessage:
    # return spatial analyst license
    gp.CheckInExtension("spatial")
    # cleanup
    if debug == False:
        removelist = ["tempslope","tempsurface","tempreclass","temppoly"]
        for remove in removelist:
            if (remove in globals()):
                if (gp.Exists(remove) == True):
                    gp.Delete(remove)
        if ("tempworkspace" in globals()):
            if (tempworkspace[0] == True):
                gp.Delete(tempworkspace[1])
    print ErrorMessage
    gp.AddError(" " + str(ErrorMessage))

del gp
