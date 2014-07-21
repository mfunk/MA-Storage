# ---------------------------------------------------------------------------
# CreateDTEDCatalog.py
# Usage: CreateDTEDCatalog <Input_Geodatabase> <Catalog_Name>
# Description: 
# This tool will create the geodatabase schema for an MA DTED Catalog.
# ---------------------------------------------------------------------------

# Import system modules
import sys, string, os
import arcgisscripting, MAScriptUtils

# Error Messages
msgAlreadyExists = "Catalog %s already exists."
msgCreateCatalogFailed = "Could not create catalog: \n %s"
msgAddFieldFailed = "Could not add required fields to catalog: \n %s"
# Progress Messages
msgProcessComplete = "Catalog created successfully."


# Create the Geoprocessor object
#gp = win32com.client.Dispatch("esriGeoprocessing.GPDispatch.1") #superceeded by arcgisscripting
gp = arcgisscripting.create(9.3)

debug = False

# Script arguments
#   Single Output Parameter
#Param_Input_Catalog = gp.GetParameterAsText(0)
#Input_Geodatabase = os.path.dirname(Param_Input_Catalog)
#Catalog_Name = os.path.basename(Param_Input_Catalog)

#   Two Input Parameters, One Output Parameter
Input_Geodatabase = gp.GetParameterAsText(0)
Catalog_Name = gp.GetParameterAsText(1)
Param_Input_Catalog = Input_Geodatabase + os.sep + Catalog_Name


if debug == True:
    gp.AddMessage("Input_Geodatabase: " + Input_Geodatabase)
    gp.AddMessage("Catalog_Name: " + Catalog_Name)

try:
    
    # Local variables
    RasterCoordSystem = "GEOGCS['GCS_WGS_1984',DATUM['D_WGS_1984',SPHEROID['WGS_1984',6378137.0,298.257223563]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]]"
    #RasterCoordSystem = str(MAScriptUtils.SetGeographicWGS84(gp))
    #WireframeCoordSystem = "GEOGCS['GCS_WGS_1984',DATUM['D_WGS_1984',SPHEROID['WGS_1984',6378137.0,298.257223563]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]];-10000 -10000 100000;0 100000;0 100000;0.00002;0.00002;0.00002;IsHighPrecision"
    WireframeCoordSystem = RasterCoordSystem + ";-10000 -10000 100000;0 100000;0 100000;0.00002;0.00002;0.00002;IsHighPrecision"
    
    # mfunk 2/8/2008 - this is now handled in the ToolValidator
    # Check for exisitng catalog    
    #if (gp.Exists(Input_Geodatabase + os.sep + Catalog_Name) == True):
    #    gp.AddError(msgAlreadyExists % (Param_Input_Catalog))
    #    raise Exception, msgAlreadyExists % (Param_Input_Catalog)
    
    # Set Workspace & parameters
    gp.Workspace = Input_Geodatabase
    
    if debug == True:
        gp.AddMessage("Set workspace: " + gp.Workspace)
    
    # Error getting CONFIGKeyword
    # Database type
    #params = MAScriptUtils.DatabaseParams(gp, Input_Geodatabase)
    #DatabaseType = params[0]
    DatabaseType = MAScriptUtils.DatabaseType(gp,Input_Geodatabase)
    #ConfigKeyword = params[1]
    #SpatialGrid1 = params[2]
    #SpatialGrid2 = params[3]
    #SpatialGrid3 = params[4]

    # Set Management type for catalog
    if (DatabaseType == "LocalDatabase"):
        ManagementType = "Unmanaged" #For PGDB and FileGDB
    else:
        ManagementType = "Managed"   #For ArcSDE
    if debug == True:
        gp.AddMessage("Catalog management type is " + ManagementType)


    # Create base raster catalog
    try:
        #Create Raster Catalog
        #gp.CreateRasterCatalog_management(Input_Geodatabase, Catalog_Name, RasterCoordSystem, WireframeCoordSystem, ConfigKeyword, SpatialGrid1, SpatialGrid2, SpatialGrid3, ManagementType)
        gp.CreateRasterCatalog_management(Input_Geodatabase, Catalog_Name, RasterCoordSystem, WireframeCoordSystem,"#","#","#","#", ManagementType)
        if debug == True:
            gp.AddMessage("Created catalog")
    except:
        gpmessages = gp.GetMessages()     
        gp.AddError(msgCreateCatalogFailed % (gpmessages))
        raise Exception, msgCreateCatalogFailed % (gpmessages)

    
    # Add fields to catalog        
    try:
        if debug == True: gp.AddMessage("Adding FULL_NAME")
        gp.AddField_management(Param_Input_Catalog, "FULL_NAME", "TEXT", "", "", "260", "", "NULLABLE", "NON_REQUIRED", "")
        if debug == True: gp.AddMessage("Added FULL_NAME, Adding DTED_TYPE")
        gp.AddField_management(Param_Input_Catalog, "DTED_TYPE", "TEXT", "", "", "15", "", "NULLABLE", "NON_REQUIRED", "")
        if debug == True: gp.AddMessage("Added DTED_TYPE")
    except:
        if debug == True: gp.AddMessage("Error adding fields: " + gp.GetMessages())
        gpmessages = gp.GetMessages()
        # Remove the catalog
        try:
            gp.Delete(Param_Input_Catalog)
        except:
            raise Exception, gp.GetMessages()
        # raise error
        gp.AddError(msgAddFieldFailed % (gpmessages))
        raise Exception, msgAddFieldFailed % (gpmessages)

    # finished
    gp.SetParameter(2,Param_Input_Catalog)
    gp.AddMessage(msgProcessComplete)
    print msgProcessComplete

except Exception, ErrorMessage:
    gp.AddError(ErrorMessage)
    print ErrorMessage
