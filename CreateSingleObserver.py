#!/usr/bin/env python
# -*- coding: latin-1 -*-

##""********************************************************************************************************************
##TOOL NAME: Create Single Observer
##SOURCE NAME: CreateSingleObserver.py
##VERSION: ArcGIS 9.3
##AUTHOR: Environmental Systems Research Institute Inc.
##REQUIRED ARGUMENTS: Input_Geodatabase,fc_name,longitude,latitude
##
##TOOL DESCRIPTION: Creates an observer point feature class from a set of input parameters
##
##DATE: 
##
##Usage: CreateSingleObserver(target_workspace,fc_name,longitude,latitude,{z},{offseta},{offsetb},{radius1},{radius2},{azimuth1},{azimuth2},{vert1},{vert2},{spatial_ref})
##*********************************************************************************************************************"""

# messages
msgAddFields = "Could not add fields to observer features."
msgFeatureClassExists = "Feature class %s already exists."
msgDetermineGeodatabaseType = "Could not determine geodatabase type"
msgNoGPSettings = "Could not determine GP environment settings"
msgCouldNotCreateFC = "Could not create Feature Class %s"
msgCouldNotAddFields = "Could not add required fields to %s"
msgCouldNotAddPoint = "Could not add point to %s"
msgSchemaLock = "Could not obtain schema lock to create %s. \n Check %s for schema lock"
msgCouldNotSetObserver = "Could not set observer point"

# import libraries
import os,sys,string
import arcgisscripting
import MAScriptUtils, Observer

# create the Geoprocessor
gp = arcgisscripting.create(9.3)

# local variables
## TODO: How should we handle units for the linear distances?
DatabaseType = "RemoteDatabase"
ConfigKeyword = "Defaults"
SpatialGrid1 = "0.0"
SpatialGrid2 = "0.0"
SpatialGrid3 = "0.0"
lon_coord = 0.0
lat_coord = 0.0
z_coord = 0.0
offset_a = 0.0
offset_b = 0.0
radius_1 = 1.0
radius_2 = 0.0
azimuth_1 = 0.0
azimuth_2 = 360.0
vert_1 = 90.0
vert_2 = -90.0


# get script arguments

# mfunk 2/4/2008 - perhaps we need to modify params 0 and 1 to be one single argument
target_workspace = gp.GetParameterAsText(0)
fc_name = gp.GetParameterAsText(1)

lon_coord = gp.GetParameterAsText(2)
lat_coord = gp.GetParameterAsText(3)
if (len(sys.argv) > 5): z_coord = gp.GetParameterAsText(4) # Z coordinate is same as SPOT
if (z_coord == ""):
     z_coord = "#"
if (len(sys.argv) > 6): offset_a = gp.GetParameterAsText(5)
if (len(sys.argv) > 7): offset_b = gp.GetParameterAsText(6)
if (len(sys.argv) > 8): radius_1 = gp.GetParameterAsText(7)
if (len(sys.argv) > 9): radius_2 = gp.GetParameterAsText(8)
if (len(sys.argv) > 10): azimuth_1 = gp.GetParameterAsText(9)
if (len(sys.argv) > 11): azimuth_2 = gp.GetParameterAsText(10)
if (len(sys.argv) > 12): vert_1 = gp.GetParameterAsText(11)
if (len(sys.argv) > 13): vert_2 = gp.GetParameterAsText(12)
if (len(sys.argv) > 14):
    spatial_ref = gp.GetParameterAsText(13)


try:
    
    # mfunk 2/4/2008 - ERROR getting gp.CONFIGKeyword causes the script to fail
    # Database type
    #db_params = MAScriptUtils.DatabaseParams(gp,target_workspace)
    #if (len(db_params) != 5): raise Exception, msgNoGPSettings
    #else:
    DatabaseType = MAScriptUtils.DatabaseType(gp,target_workspace)
    #    ConfigKeyword = db_params[1]
    #    SpatialGrid1 = db_params[2]
    #    SpatialGrid2 = db_params[3]
    #    SpatialGrid3 = db_params[4]

    # check workspace type and fc name for .shp
    if (DatabaseType == "FileSystem"):
        if (fc_name[-4:].upper() != ".SHP"):
            fc_name = fc_name + ".shp"
            
    
    # set workspace
    target_fc = os.path.join(target_workspace,fc_name)
    gp.Workspace = target_workspace
    
    # set coordinate system
    spatial_ref_WGS84 = MAScriptUtils.SetGeographicWGS84(gp)
    if (spatial_ref == "#"):
        spatial_ref = spatial_ref_WGS84
    elif (str(type(spatial_ref)) == "<type 'str'>"):
        spatial_ref = MAScriptUtils.CreateSpatialReferenceFromString(gp,spatial_ref)
    else:
        spatial_ref = spatial_ref_WGS84

    ## check workspace type and fc name for .shp
    #if (DatabaseType == "FileSystem"):
    #    if (fc_name[-4:].upper() != ".SHP"):
    #        fc_name = fc_name + ".shp"
    
    # mfunk 2/4/2008 - Tool validation handles this now
    # check if target FC exists.
    #if gp.Exists(target_fc):
    #    raise Exception, msgFeatureClassExists % target_fc
    
    ## check workspace for schema lock
    #locked_workspace = MAScriptUtils.CheckForSchemaLock(gp,target_workspace)
    #if (locked_workspace != True):
    #    raise Exception, msgSchemaLock % (str(fc_name),str(target_workspace))
        
    # set environment
    #gp.OutputZFlag = "enabled"
    #if (DatabaseType != "FileSystem"):  #Need to set ZDomain for all geodatabases, nothing else
        #if (z_coord == "#") or (z_coord == None):
            #z_domain = "-5000 5000"    
        #else:
            #z_domain = str(float(z_coord) - 5000) + " " + str(float(z_coord) + 5000)
        #gp.ZDomain = z_domain
    
    
    # create feature class    
    try:
        gp.CreateFeatureClass(str(target_workspace),str(fc_name),"POINT","#","DISABLED","ENABLED",spatial_ref,"#","#","#","#")#ConfigKeyword,SpatialGrid1,SpatialGrid2,SpatialGrid3)
        gp.RefreshCatalog(target_workspace)
    except:
        raise Exception, msgCouldNotCreateFC % target_fc + "\n" + gp.GetMessages()

    # add fields to observer FC
    try:
        success = MAScriptUtils.AddObserverFields(gp,target_fc)
        if (success == False):
            gp.Delete(target_fc)
            raise Exception, msgAddFields
    except:
        # delete the feature class
        gp.Delete(target_fc)
        raise Exception, msgCouldNotAddFields % target_fc
    
    try:
        # create a new observer object
        observer = Observer.Observer(gp)
        # set observer properties
        success = observer.SetObserver(lon_coord,lat_coord,z_coord,offset_a,offset_b,radius_1,radius_2,azimuth_1,azimuth_2,vert_1,vert_2,spatial_ref)
        if (success == False):
            raise Exception, msgCouldNotSetObserver
        # add observer to FC
        success = observer.AddObserver(gp,target_fc)
        if (success == False):
            raise Exception, msgCouldNotAddPoint % target_fc
    except Exception, ErrorMessage:
        # delete the feature class
        gp.Delete(target_fc)
        raise Exception, ErrorMessage
    
    #Set output parameters
    gp.SetParameter(14,target_fc)
        
except Exception, ErrorMessage:
    #raise error
    print ErrorMessage
    gp.AddError(str(ErrorMessage))
    

del gp
