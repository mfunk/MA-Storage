#!/usr/bin/env python
# -*- coding: latin-1 -*-

##""********************************************************************************************************************
##TOOL NAME: 
##SOURCE NAME: 
##VERSION: ArcGIS 9.3
##AUTHOR: Environmental Systems Research Institute Inc.
##REQUIRED ARGUMENTS: 
##
##TOOL DESCRIPTION: 
##
##DATE: 
##
##Usage: RadialLineOfSight(<observers>,<input_surface>,<output_workspace>,<fc_basename>,{METERS | FEET | KILOMETERS | US_SURVEY_FEET | MILES | NAUTICAL_MILES})
##*********************************************************************************************************************"""

# error messages
msgNoSpatialLicense = "This tool could not find and available Spatial Analyst license."
msgNoLicense = "This tool could not find and available Spatial Analyst or 3D Analyst license."
msgTooFewArguments = "Incorrect number of arguments. \n Syntax should be as follows: \n RLOS(observers,input_surface,output_workspace,fc_basename)"
msgNoInputObservers = "Input observers %s does not exist."
msgNoInputSurface = "Input surface %s does not exist."
msgObserversNotPoints = "Input observers must be a point featureclass."
msgSurfaceNotRaster = "Input surface must be a raster dataset or raster catalog"
msgOutputExists = "Output dataset %s already exists."
msgProjectObservers = "Could not project observers to Azimuthal Equidistant for processing: \n %s"
msgProjectRaster = "Could not project suface to Azimuthal Equidistant for processing: \n %s"
msgErrorDuringViewshed = "Error in creating viewshed.\n"
msgMissingObserverFields = "Input observers are missing the following required fields:\n %s"
msgNoMosaic = "Could not mosaic %s catalog for processing."
msgNoEnvelope = "Could not calculate envelope of observer points for processing."
msgNoCentroid = "Could not calculate centroid of observer points for processing."
msgCouldNotConvertVis = "Could not convert visibility to polygons: \n %s"
msgOutputParamsError = "Error in setting output parameters: \n %s"
msgLicenseCheckInError = "Error in checking in extension: \n %s" 

# status messages
msgProcessComplete = "Processing completed."
msgProjectingObservers = "Projecting observer points for processing."
msgProjectingSurface = "Projecting input surface for processing (This may take some time). "
msgRadialDistanceUnitsDefault = "Defaulting to radial distance units of meters"


# import libraries
import os,sys,string,time,re
import arcgisscripting
import MAScriptUtils, Observer

# create the Geoprocessor
gp = arcgisscripting.create(9.3)

# get script parameters
if (len(sys.argv) < 4):
    raise Exception, msgTooFewArguments
input_observers = gp.GetParameterAsText(0)
input_surface = gp.GetParameterAsText(1)
output_workspace = gp.GetParameterAsText(2)
output_basename = gp.GetParameterAsText(3)
radial_distance_units = gp.GetParameterAsText(4) #Optional

#
#THIS ONE IS HANDLED AS PART OF THE OBSERVER POINT.
#
#if (len(sys.argv) < 6 ):  
#    terrain_offset = gp.GetParameterAsText(5)
#else:
#    terrain_offset = 0.0
#

try:
    # tempworkspace
    workspace = MAScriptUtils.GetTempWorkspace(gp)
    gp.workspace = workspace[1]
    
    # mfunk 2/7/2008 - Error getting CONFIGKeyword
    # Get output params for output geodatabase
    #db_params = MAScriptUtils.DatabaseParams(gp,output_workspace)
    DatabaseType = MAScriptUtils.DatabaseType(gp,output_workspace)
    
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
    
    # Check input params exist and outputs do not exist
    if (gp.Exists(input_observers) != True):
        raise Exception, msgNoInputObservers % (str(input_observers))
    
    # mfunk 2/7/2008 - handled in ToolValidator
    # check that observers are a point featureclass
    #if (gp.Describe(input_observers).ShapeType != "Point"):
    #    raise Exception, msgObserversNotPoints
    
    # mfunk 2/7/2008 - handled in ToolValidator
    # if Raster Dataset check that it exists
    #if (gp.Exists(input_surface) != True):
    #    raise Exception, msgNoInputSurface % (str(input_surface))
    
    # mfunk 2/7/2008 - handled in ToolValidator
    # check that surface is a raster dataset or raster catalog
    #surf_describe = gp.Describe(input_surface)
    #surf_desc_DSType = surf_describe.DatasetType
    #if (surf_desc_DSType != "RasterDataset" and surf_desc_DSType != "RasterCatalog"):
    #    raise Exception, msgSurfaceNotRaster
    
    # check that output does NOT exist
    if (gp.Exists(output_workspace + os.sep + output_basename + "_vis") == True):
        raise Exception, msgOutputExists % (output_workspace + os.sep + output_basename + "_vis")
    if (gp.Exists(output_workspace + os.sep + output_basename + "_obs") == True):
        raise Exception, msgOutputExists % (output_workspace + os.sep + output_basename + "_obs")
    
    # mfunk 2/7/2008 - handled in ToolValidator
    # Check observers for proper fields
    #field_check = MAScriptUtils.CheckObserverFields(gp,input_observers)
    #if (len(field_check) > 0):
    #    raise Exception, msgMissingObserverFields % (field_check)

    # this is handled by the validator
    # Check the radial distance unit
    #if(radial_distance_units == "#" or radial_distance_units == "" or radial_distance_units == None):
    #    radial_distance_units == "meter"
    #    gp.AddWarning(str(msgRadialDistanceUnitsDefault))
    #else:
    #    linearPatterns = MAScriptUtils.RegExPatterns()['Linear']
    #    for linearPatternName in linearPatterns.keys():
    #        linearPatternExpression = linearPatterns[linearPatternName]
    #        patternSearch = re.search(linearPatternExpression,radial_distance_units)
    #        if (patternSearch != None):
    #            radial_distance_units = str(linearPatternName)
    #        else:
    #            radial_distance_units = "meter"
    #            gp.AddWarning(str(msgRadialDistanceUnitsDefault))

    # get envelope of observers
    # TODO: Need to make sure that the envelope includes the attributes for visibility
    #       - check projection units?, project before envelope?
    obs_extent = MAScriptUtils.GetObserverExtent(gp,input_observers,radial_distance_units)
    if ((obs_extent == None) or (len(obs_extent) == 0)):
        raise Exception, msgNoEnvelope


    # Get refractivity and curvature from Registry
    #
    #TODO: research error:
    # An error was encountered while executing Viewshed.
    # ("esriGeoAnalyst.GridEngine") Projections are incompatible for earth curvature corrections
    # - Must have Z coordinates defined????
    #
    #if (options.has_key("Terrain") == True):
    #    terrain_options = options["Terrain"]
    #    # if false use FLAT_EARTH, if true use CURVED_EARTH and coefficient
    #    if (terrain_options["TerrainUseCurveRefraction"] == 0):
    #        curvature = "FLAT_EARTH"
    #        refrac_coeff = "#"
    #    else:
    #        curvature = "CURVED_EARTH"
    #        # TODO: this guy is stored in some kind of hex or bin, need to convert to double
    #        refrac_coeff = terrain_options["TerrainRefraction"]
    #else:
    #    # if no registry for Terrain then use flat earth
    #    curvature = "FLAT_EARTH"
    #    refrac_coeff = "#"
    #

    curvature = "FLAT_EARTH"
    refrac_coeff = "#"
    
    
    # if Raster Catalog mosaic to single surface for RLOS computation
    tempsurf = MAScriptUtils.GenerateTempFileName(gp,workspace[1],"RasterDataset")

    surf_mosaic = None
    surf_desc = gp.Describe(input_surface)
    if (str(surf_desc.DatasetType) == "RasterCatalog"):
        # Mosaic all tiles that fall in extent and clip: MAScriptUtils.MosaicAndClip
        surf_mosaic = MAScriptUtils.MosaicAndClip(gp,input_surface,tempsurf,obs_extent)
        if (surf_mosaic == None):
            raise Exception, msgNoMosaic % (input_surface)
        # swap the input catalog with the mosaic
        input_surface = surf_mosaic
    else:
        # if single raster dataset
        pass

    # get centroid of observer envelope
    obs_centroid = MAScriptUtils.GetCentroidOfEnvelope(gp,obs_extent)
    if (obs_centroid == None or len(obs_centroid) != 2):
        raise Exception, msgNoCentroid

    # set AZED for the centroid of envelope
    spatial_ref_azed = MAScriptUtils.SetAZED(gp,0.0,0.0,obs_centroid[0],obs_centroid[1])
    
    
    # is observer fc in AZED, if not, project it.
    observers_azed = MAScriptUtils.GenerateTempFileName(gp,workspace[1],"FeatureClass")
    sr_obs = gp.Describe(input_observers).SpatialReference
    sr_obs_name = sr_obs.Name
    if (sr_obs_name != "Azimuthal Equidistant"):
        try:
            #if not project to AZED
            gp.AddMessage(msgProjectingObservers)
            print msgProjectingObservers
            gp.project_management(input_observers,observers_azed,spatial_ref_azed,"#",sr_obs)
        except:
            raise Exception, msgProjectObservers % (gp.GetMessages())
    else:
        observers_azed = input_observers


    # is surface in AZED, if not, project it.
    surface_azed = MAScriptUtils.GenerateTempFileName(gp,workspace[1],"RasterDataset")
    sr_surf = gp.Describe(input_surface).SpatialReference
    if (sr_surf.Name != "Azimuthal Equidistant"):
        try:
            #if not project to AZED
            gp.AddMessage(msgProjectingSurface)
            print msgProjectingSurface
            gp.ProjectRaster_management(input_surface,surface_azed,spatial_ref_azed,"BILINEAR")
        except:
            raise Exception, msgProjectRaster % (gp.GetMessages())
    else:
        surface_azed = input_surface


    # set GP environment
    gp.Extent = "MAXOF"

    # do the viewshed
    out_vis_raster = MAScriptUtils.GenerateTempFileName(gp,workspace[1],"RasterDataset")

    if (bUseSpatial == True):
        try:
            gp.viewshed_sa(surface_azed,observers_azed,out_vis_raster,str(1.0),curvature,refrac_coeff)
        except:
            raise Exception, msgErrorDuringViewshed + gp.GetMessages()
    else:
        try:
            gp.viewshed_3d(surface_azed,observers_azed,out_vis_raster,str(1.0),curvature,refrac_coeff)
        except:
            raise Exception, msgErrorDuringViewshed + gp.GetMessages()


    # convert output to feature classes in output workspace
    # - output observers
    final_observers = output_workspace + os.sep + output_basename + "_obs"
    if (DatabaseType == "FileSystem"):
        final_observers = final_observers + ".shp"
    #gp.Copy(observers_azed,final_observers) #gp.COPY always returns a Segment Violation with output FGDB
    gp.FeatureClassToFeatureClass_conversion(observers_azed,output_workspace,output_basename + "_obs","#","#","#") #db_params[1])
    # remove temp observers
    gp.Delete(observers_azed)

    # - output viewshed
    final_viewshed = output_workspace + os.sep + output_basename + "_vis"
    if (DatabaseType == "FileSystem"):
        final_viewshed = final_viewshed + ".shp"
    try:
        gp.RasterToPolygon_conversion(out_vis_raster,final_viewshed,"NO_SIMPLIFY","VALUE")
        if (gp.Exists(out_vis_raster) == True): gp.Delete(out_vis_raster)
        if (gp.Exists(surface_azed) == True): gp.Delete(surface_azed)
    except:
        raise Exception, msgCouldNotConvertVis % (gp.GetMessages())
    
    # delete mosaic surface
    if (surf_mosaic != None and gp.Exists(surf_mosaic) == True): gp.Delete(surf_mosaic)
      
    # set output script params
    try:
        gp.SetParameter(5,final_observers)
        gp.SetParameter(6,final_viewshed)
    except:
        raise Exception, msgOutputParamsError  % (gp.GetMessages())

    #if workspace is temporary, delete it
    if (workspace[0] == True):
        gp.Delete(workspace[1])

    # check license back in
    try:
        if (bUseSpatial == True):
            gp.CheckInExtension("spatial")
        else:
            gp.CheckInExtension("3d")
    except:
        raise Exception, msgLicenseCheckInError % (gp.GetMessages())
    pass

    # completed
    gp.AddMessage(msgProcessComplete)
    print msgProcessComplete

except Exception, ErrorMessage:
    
    if (bUseSpatial == True):
        gp.CheckInExtension("spatial")
    else:
        gp.CheckInExtension("3d")
        
    if (workspace[0] == True and gp.Exists(workspace[1]) == True):
        gp.Delete(workspace[1])
        
    gp.AddError(str(ErrorMessage))
    print ErrorMessage    #Python always crashes here.

del gp
