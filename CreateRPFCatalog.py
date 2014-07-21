# ---------------------------------------------------------------------------
# CreateRPFCatalog.py
# Usage: CreateRPFCatalog <Input_Geodatabase> <Catalog_Name>
# Description: 
# This tool will create the geodatabase schema for an MA RPF Catalog.
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
#gp = win32com.client.Dispatch("esriGeoprocessing.GPDispatch.1")
gp = arcgisscripting.create(9.3)

# Script arguments
Input_Geodatabase = gp.GetParameterAsText(0)
Catalog_Name = gp.GetParameterAsText(1)
Table_name = Catalog_Name + "_uids"   #Defect 30537
Param_Input_Catalog = Input_Geodatabase + os.sep + Catalog_Name


# Local variables
RasterCoordSystem = "GEOGCS['GCS_WGS_1984',DATUM['D_WGS_1984',SPHEROID['WGS_1984',6378137.0,298.257223563]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]]"
#RasterCoordSystem = MAScriptUtils.SetGeographicWGS84(gp)
#WireframeCoordSystem = "GEOGCS['GCS_WGS_1984',DATUM['D_WGS_1984',SPHEROID['WGS_1984',6378137.0,298.257223563]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]]
WireframeCoordSystem = RasterCoordSystem + ";-10000 -10000 100000;0 100000;0 100000;0.00002;0.00002;0.00002;IsHighPrecision"

try:
    
    # Set workspace
    gp.Workspace = Input_Geodatabase
    
    # mfunk 2/8/2008 - now handled in ToolValidator
    # Check that catalog exists
    #if (gp.Exists(Param_Input_Catalog) == True):
    #    gp.AddError(msgAlreadyExists % (Param_Input_Catalog))
    #    raise Exception, msgAlreadyExists % (Param_Input_Catalog)
    
    # Error getting CONFIGKeyword
    #params = MAScriptUtils.DatabaseParams(gp,Input_Geodatabase)
    #DatabaseType = params[0]
    DatabaseType = MAScriptUtils.DatabaseType(gp,Input_Geodatabase)
    #ConfigKeyword = params[1]
    #SpatialGrid1 = params[2]
    #SpatialGrid2 = params[3]
    #SpatialGrid3 = params[4]
    
    if (DatabaseType == "LocalDatabase"):
        ManagementType = "Unmanaged" #For PGDB and FileGDB
    else:
        ManagementType = "Managed"   #For ArcSDE

    #Create Raster Catalog
    try:        
        #gp.CreateRasterCatalog_management(Input_Geodatabase, Catalog_Name, RasterCoordSystem,WireframeCoordSystem , ConfigKeyword, SpatialGrid1, SpatialGrid2, SpatialGrid3, ManagementType)
        gp.CreateRasterCatalog_management(Input_Geodatabase, Catalog_Name, RasterCoordSystem,WireframeCoordSystem ,"#","#","#","#", ManagementType)
    except:
        gpmessages = gp.GetMessages()
        gp.AddError(msgCreateCatalogFailed % (gpmessages))
        raise Exception, msgCreateCatalogFailed % (gpmessages)


    # Add fields to catalog      
    try:
        gp.AddField_management(Param_Input_Catalog, "FULL_NAME", "TEXT", "", "", "260", "", "NULLABLE", "NON_REQUIRED", "")
        gp.AddField_management(Param_Input_Catalog, "PRODUCT", "TEXT", "", "", "25", "", "NULLABLE", "NON_REQUIRED", "")
        gp.AddField_management(Param_Input_Catalog, "SERIES", "TEXT", "", "", "5", "", "NULLABLE", "NON_REQUIRED", "")
        gp.AddField_management(Param_Input_Catalog, "SCALE", "LONG", "", "", "", "", "NULLABLE", "NON_REQUIRED", "")
    except:
        gpmessages = gp.GetMessages()
        # Remove the catalog
        try:
            gp.Delete(Param_Input_Catalog)
        except:
            raise Exception, gp.GetMessages()
        gp.AddError(msgAddFieldFailed % (gpmessages))
        raise Exception, msgAddFieldFailed % (gpmessages)

    #set the output
    gp.SetParameter(2,Param_Input_Catalog)

    #Create the uid table -- Defect 30537
    try:
        gp.CreateTable(Input_Geodatabase,Table_name)
        gp.AddMessage("Created uid table successfully...")
    
    except:
        messages = gp.GetMessages()
        gp.AddError("Create uid table failed: \n %s" % (messages))

    #Add the PRODUCT and SCALE fields -- Defect 30537
    try:
        Input = Input_Geodatabase + os.sep + Table_name 
        gp.AddField_management(Input, "PRODUCT", "TEXT", "", "", "25", "", "NULLABLE", "NON_REQUIRED", "")
        gp.AddField_management(Input, "SCALE", "LONG", "", "", "", "", "NULLABLE", "NON_REQUIRED", "")

    except:
        gpmessages = gp.GetMessages()
        gp.AddError("Failed to add Field" % (gpmessages))
        # Remove the table
        try:
            gp.Delete(Input)
        except:
            raise Exception, gp.GetMessages()
        gp.AddError(msgAddFieldFailed % (gpmessages))
        raise Exception, msgAddFieldFailed % (gpmessages)
    
    
    # finished
    gp.AddMessage(msgProcessComplete)
    print msgProcessComplete

except Exception, ErrorMessage:
    #raise error
    gp.AddError(ErrorMessage)
    print ErrorMessage
