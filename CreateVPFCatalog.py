# ---------------------------------------------------------------------------
# CreateVPFCatalog.py
# Usage: CreateVPFCatalog <Output_Location> <FeatureClassName>
# Description: 
# This tool will create the geodatabase schema for an MA VPF Catalog.
# ---------------------------------------------------------------------------

# Import system modules
import sys, string, os
import arcgisscripting, MAScriptUtils

# Error Messages
msgAlreadyExists = "Catalog %s already exists."
msgCreateCatalogFeaturesFailed = "Could not create catalog's feature class: \n %s"
msgCreateCatalogTableFailed = "Could not create catalog's table: \n %s"
msgAddFeatureFieldFailed = "Could not add required fields to catalog feature class: \n %s"
msgAddTableFieldFailed = "Could not add required fields to catalog table: \n %s"
# Progress Messages
msgProcessComplete = "Catalog created successfully."

# Create the Geoprocessor object
#gp = win32com.client.Dispatch("esriGeoprocessing.GpDispatch.1")
gp = arcgisscripting.create(9.3)

# Script arguments
Input_Geodatabase = gp.GetParameterAsText(0)
FeatureClassName = gp.GetParameterAsText(1)


# Local variables
FeatureClassPath = Input_Geodatabase + os.sep + FeatureClassName
TableName = FeatureClassName + "_features"
TablePath = Input_Geodatabase + os.sep + TableName
GCS_WGS84 = "GEOGCS['GCS_WGS_1984',DATUM['D_WGS_1984',SPHEROID['WGS_1984',6378137.0,298.257223563]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]];-10000 -10000 100000;0 100000;0 100000;0.00002;0.00002;0.00002;IsHighPrecision"
#GCS_WGS84 = MAScriptUtils.SetGeographicWGS84 + ";-10000 -10000 100000;0 100000;0 100000;0.00002;0.00002;0.00002;IsHighPrecision"

# Set Workspace
gp.Workspace = Input_Geodatabase


try:
    
    # mfunk 2/11/2008 - Handled in ToolValidator
    # Check that output does not exist
    #if (gp.Exists(FeatureClassPath) == True):
    #    raise Exception, msgAlreadyExists % (FeatureClassPath)
    #
    #if (gp.Exists(TablePath) == True):
    #    raise Exception, msgAlreadyExists % (TablePath)
    
    # mfunk 2/11/2008 - Error in getting CONFIGKeyword
    # Database parameters
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

    # Create Feature Class
    try:
        gp.CreateFeatureclass_management(Input_Geodatabase, FeatureClassName, "POLYGON", "", "DISABLED", "DISABLED",GCS_WGS84,"#","#","#","#") # ConfigKeyword, SpatialGrid1, SpatialGrid2, SpatialGrid3)
    except:
        gpmessages = gp.GetMessages()
        gp.AddError(msgCreateCatalogFeaturesFailed)
        raise Exception, msgCreateCatalogFeaturesFailed
    
    # Add Fields to featureclass
    try:
        gp.AddField_management(FeatureClassPath, "PRODUCT", "TEXT", "", "", "25", "", "NULLABLE", "NON_REQUIRED", "")
        gp.AddField_management(FeatureClassPath, "LIBRARY", "TEXT", "", "", "20", "", "NULLABLE", "NON_REQUIRED", "")
        gp.AddField_management(FeatureClassPath, "SCALE", "LONG", "", "", "", "", "NULLABLE", "NON_REQUIRED", "")
        gp.AddField_management(FeatureClassPath, "TILE_ID", "LONG", "", "", "", "", "NULLABLE", "NON_REQUIRED", "")
    except:
        gpmessages = gp.GetMessages()
        #delete Feature Class
        try:
            gp.delete_management(FeatureClassPath)
        except:
            raise Exception, gp.GetMessages()
        gp.AddError(msgAddFeatureFieldFailed % (gpmessages))
        raise Exception, msgAddFeatureFieldFailed % (gpmessages)

    # Create Table
    try:        
        gp.CreateTable_management(Input_Geodatabase, TableName, "","#") #ConfigKeyword)
    except:
        gpmessages = gp.GetMessages()
        #delete Feature Class
        try:
            gp.delete_management(TablePath)
        except:
            raise Exception, gp.GetMessages()
        gp.AddError(msgCreateCatalogTableFailed % (gpmessages))
        raise Exception, msgCreateCatalogTableFailed % (gpmessages)
    
    # Add Fields to table
    try:
        gp.AddField_management(TablePath, "PRODUCT", "TEXT", "", "", "25", "", "NULLABLE", "NON_REQUIRED", "")
        gp.AddField_management(TablePath, "PATH", "TEXT", "", "", "255", "", "NULLABLE", "NON_REQUIRED", "")
        gp.AddField_management(TablePath, "LIBRARY", "TEXT", "", "", "20", "", "NULLABLE", "NON_REQUIRED", "")
        gp.AddField_management(TablePath, "COVERAGE", "TEXT", "", "", "15", "", "NULLABLE", "NON_REQUIRED", "")
        gp.AddField_management(TablePath, "FEAT_CLS", "TEXT", "", "", "10", "", "NULLABLE", "NON_REQUIRED", "")
        gp.AddField_management(TablePath, "COV_DESC", "TEXT", "", "", "100", "", "NULLABLE", "NON_REQUIRED", "")
        gp.AddField_management(TablePath, "FC_DESC", "TEXT", "", "", "100", "", "NULLABLE", "NON_REQUIRED", "")
        gp.AddField_management(TablePath, "FC_TYPE", "TEXT", "", "", "1", "", "NULLABLE", "NON_REQUIRED", "")
        gp.AddField_management(TablePath, "GEOSYM_PID", "LONG", "", "", "", "", "NULLABLE", "NON_REQUIRED", "")
        gp.AddField_management(TablePath, "FAC_CODES", "TEXT", "", "", "100", "", "NULLABLE", "NON_REQUIRED", "")
    except:
        gpmessages = gp.GetMessages()
        #delete Feature Class
        try:
            gp.delete_management(FeatureClassPath)
        except:
            raise Exception, gp.GetMessages()
        # delete table
        try:
            gp.delete_management(TablePath)
        except:
            raise Exception, gp.GetMessages()
        gp.AddError(msgAddTableFieldFailed % (gpmessages))
        raise Exception, msgAddTableFieldFailed % (gpmessages)
    
    # Set output
    gp.SetParameter(2,FeatureClassPath)
    
    # finished
    gp.AddMessage(msgProcessComplete)
    print msgProcessComplete 


except Exception, ErrorMessage:
    gp.AddError(ErrorMessage)
    print ErrorMessage
    
