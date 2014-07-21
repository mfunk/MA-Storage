#!/usr/bin/env python
# -*- coding: latin-1 -*-

##""********************************************************************************************************************
##TOOL NAME: Create Observers From Table
##SOURCE NAME: CreateObserversFromTable.py
##VERSION: ArcGIS 9.3
##AUTHOR: Environmental Systems Research Institute Inc.
##REQUIRED ARGUMENTS: Input_Table, Target_Workspace, Output_Name, {spatial_ref}
##
##TOOL DESCRIPTION: Creates Observer Points from a table of parameters
##
##DATE: 
##
##Usage: CreateObserversFromTable_ma(<Input_Table>,<Target_Workspace>,<Output_Observers_Name>,{spatial_reference})
##*********************************************************************************************************************"""

# error messages
msgTooFewArguments = "Incorrect number of arguments. \n Syntax should be as follows: \n CreateObserversFromTable <Input_Table> <Target_Workspace> <Output_Observers_Name> {spatial_reference}"
msgTableDoesNotExist = "Input table %s does not exist."
msgAddFields = "Could not add fields to observer features."
msgFeatureClassExists = "Feature class %s already exists."
msgSchemaLock = "Could not obtain a schema lock for %s"
msgDetermineGeodatabaseType = "Could not determine geodatabase type"
msgNoGPSettings = "Could not determine GP environment settings"
msgCouldNotCreateFC = "Could not create Feature Class %s"
msgCouldNotAddFields = "Could not add required fields to %s"
msgCouldNotAddPoint = "Could not add point to %s"
msgSchemaLock = "Could not obtain schema lock to create %s. \n Check %s for schema lock"
msgCouldNotSetObserver = "Could not set observer point"
msgMissingObserverFields = "Missing fields from input table %s: %s"
msgMissingBothXYField = "Input table is missing both the X coordinate field and Y coordinate field."
msgMissingXField = "Input table is missing the X coordinate field."
msgMissingYField = "Input table is missing the Y coordinate field."
# status messages
msgReadingInputTable = "Reading input table ..."
msgAddingObserver = "Adding observer at %s , %s"
msgProcessComplete = "Processing completed."


# import libraries
import os,sys,string
import arcgisscripting
import MAScriptUtils, Observer

debug = False

# create the Geoprocessor
gp = arcgisscripting.create(9.3)
if debug == True: print "created geoprocessor"
# get script parameters
if (len(sys.argv) < 4):
    raise Exception, msgTooFewArguments
    
input_table = gp.GetParameterAsText(0)
target_workspace = gp.GetParameterAsText(1)
fc_name = gp.GetParameterAsText(2)

if (len(sys.argv) > 4):
    spatial_ref = gp.GetParameterAsText(3)
    

# local variables
DatabaseType = "RemoteDatabase"
ConfigKeyword = "Defaults"
SpatialGrid1 = "0.0"
SpatialGrid2 = "0.0"
SpatialGrid3 = "0.0"
target_workspace = string.replace(target_workspace,"/","\\")
gp.workspace = target_workspace
 

try:
    # set temp workspace
    tempworkspace = MAScriptUtils.GetTempWorkspace(gp)
    gp.workspace = tempworkspace[1]
    
    # mfunk 2/5/2008 - Input parameters in toolbox checks this
    # check that the input table exists (and it is a table)
    #if (gp.Exists(input_table) == False):
    #    raise Exception, msgTableDoesNotExist % (input_table)
    
    # mfunk2/5/2008 - moved to tool validator
    # check that required fields exist.
    #missing_fields = MAScriptUtils.CheckMissingObserverFields(gp,input_table)
    #if (len(missing_fields) != 0):
    #    raise Exception, msgMissingObserverFields % (input_table,missing_fields)
    
    # check for X and Y fields
    bFindX = False
    bFindY = False
    fields = gp.ListFields(input_table)
    #field = fields.next()
    #while field:
    for field in fields:
        fieldname = field.Name
        if debug == True:
            gp.AddMessage("Input field: " + str(field.Name))
        if (fieldname.upper() == "X".upper()):
            bFindX = True
        if (fieldname.upper() == "Y".upper()):
            bFindY = True
        #field = fields.next()
        
    if (bFindX == False and bFindY == False):
        gp.AddError(msgMissingBothXYField)
        raise Exception, msgMissingBothXYField
    elif (bFindX == False and bFindY == True):
        gp.AddError(msgMissingXField)
        raise Exception, msgMissingXField
    elif (bFindX == True and bFindY == False):
        gp.AddError(msgMissingYField)
        raise Exception, msgMissingYField
    
    if debug == True:
        gp.AddMessage("checked for missing fields in table")
        print "checked for missing fields in table"

    # set spatial reference    
    if (spatial_ref == "#" or spatial_ref == None or spatial_ref == ""):
        spatial_ref = MAScriptUtils.SetGeographicWGS84(gp)
    elif (str(type(spatial_ref)) == "<type 'str'>"):
        spatial_ref = MAScriptUtils.CreateSpatialReferenceFromString(gp,spatial_ref)
    else:
        spatial_ref = MAScriptUtils.SetGeographicWGS84(gp)
    
    # mfunk 2/5/2008 - Always get error trying to read CONFIGKeyword
    # Database type
    #db_params = MAScriptUtils.DatabaseParams(gp,target_workspace)
    #if (len(db_params) != 5):
    #    raise Exception, msgNoGPSettings
    #else:
    DatabaseType = MAScriptUtils.DatabaseType(gp,target_workspace)#str(db_params[0])
    #    ConfigKeyword = str(db_params[1])
    #    SpatialGrid1 = str(db_params[2])
    #    SpatialGrid2 = str(db_params[3])
    #    SpatialGrid3 = str(db_params[4])

    if debug == True:
        gp.AddMessage("checked database params")
        print "checked database params"

    # check workspace type and fc name for .shp
    if (DatabaseType == "FileSystem"):
        if (fc_name[-4:].upper() != ".SHP"):
            fc_name = fc_name + ".shp"
    
    # mfunk 2/5/2008 - check is peformed in tool validation
    # check if the output FC exists already
    target_fc = os.path.join(target_workspace,fc_name)
    #if gp.Exists(target_fc):
    #    raise Exception, msgFeatureClassExists %  (target_fc)                                                               
    
    ## check for schema lock on output workspace
    #schema_lock = MAScriptUtils.CheckForSchemaLock(gp,target_workspace)
    #if (schema_lock == False):
    #    raise Exception, msgSchemaLock % (target_workspace)
    #
    #if debug == True:
    #    gp.AddMessage("checked schema lock")
    #    print "checked schema lock"

    # create feature class
    if debug == True: print "Creating output Feature Class"
    try:
        if debug == True:
            gp.AddMessage(target_workspace + "\n" + fc_name + "\n" + str(spatial_ref))# + "\n" + ConfigKeyword + "\n" + SpatialGrid1 + "\n" + SpatialGrid2 + "\n" + SpatialGrid3)
            
        gp.CreateFeatureClass(str(target_workspace),str(fc_name),"POINT","#","#","#",spatial_ref,"#","#","#","#")#ConfigKeyword,SpatialGrid1,SpatialGrid2,SpatialGrid3)
    except:
        raise Exception, msgCouldNotCreateFC % target_fc + "\n" + gp.GetMessages()
    
    if debug == True:
        gp.AddMessage("created feature class")
        print "created feature class"
    
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
    
    if debug == True:
        gp.AddMessage("Added observer fields")
        print "Added observer fields"
    
    try:
        # Reading table input ...
        gp.AddMessage(msgReadingInputTable)
        print msgReadingInputTable
        
        # start a search cursor on input table      
        search_rows = gp.SearchCursor(input_table)
        current_row = search_rows.next()
        while current_row:
        #for current_row in search_rows:
            # get values from current row
            #X,Y,SPOT,OFFSETA,OFFSETB,VERT1,VERT2,AZIMUTH1,AZIMUTH2,RADIUS1,RADIUS2
            cr_x = current_row.X
            cr_y = current_row.Y
            #cr_spot = current_row.SPOT
            cr_spot = None

            if (len(str(current_row.OFFSETA)) > 0 and str(current_row.OFFSETA) != " "):
                cr_offseta = float(current_row.OFFSETA)
            else:
                cr_offseta = None
                
            if (len(str(current_row.OFFSETB)) > 0 and str(current_row.OFFSETB) != " "):
                cr_offsetb = float(current_row.OFFSETB)
            else:
                cr_offsetb = None
                
            if (len(str(current_row.VERT1)) > 0 and str(current_row.VERT1) != " "):
                cr_vert1 = float(current_row.VERT1)
            else:
                cr_vert1 = None
                
            if (len(str(current_row.VERT2)) > 0 and str(current_row.VERT2) != " "):
                cr_vert2 = float(current_row.VERT2)
            else:
                cr_vert2 = None
                
            if (len(str(current_row.AZIMUTH1)) > 0 and str(current_row.AZIMUTH1) != " "):
                cr_azimuth1 = float(current_row.AZIMUTH1)
            else:
                cr_azimuth1 = None
                
            if (len(str(current_row.AZIMUTH2)) > 0 and str(current_row.AZIMUTH2) != " "):
                cr_azimuth2 = float(current_row.AZIMUTH2)
            else:
                cr_azimuth2 = None
                
            if (len(str(current_row.RADIUS1)) > 0 and str(current_row.RADIUS1) != " "):
                cr_radius1 = float(current_row.RADIUS1)
            else:
                cr_radius1 = None
                
            if (len(str(current_row.RADIUS2)) > 0 and str(current_row.RADIUS2) != " "):
                cr_radius2 = float(current_row.RADIUS2)
            else:
                cr_radius2 = None
            
            try:
                # create a new observer object
                observer = Observer.Observer(gp)
                # set observer properties
                success = observer.SetObserver(cr_x,cr_y,cr_spot,cr_offseta,cr_offsetb,cr_radius1,cr_radius2,cr_azimuth1,cr_azimuth2,cr_vert1,cr_vert2,spatial_ref)
                if (success == False):
                    raise Exception, msgCouldNotSetObserver
                # add observer to FC
                print msgAddingObserver % (cr_x,cr_y)
                gp.AddMessage(msgAddingObserver % (cr_x,cr_y))
                success = observer.AddObserver(gp,target_fc)
                if (success == False):
                    raise Exception, msgCouldNotAddPoint % (target_fc)
                observer = None
                
            except Exception, ErrorMessage:
                observer = None
                # delete the feature class
                gp.Delete(target_fc)
                raise Exception, ErrorMessage
            
            current_row = search_rows.next()
            
        del search_rows
    except:
        gp.Delete(target_fc)
        # raise error
        raise Exception, msgCouldNotAddPoint % (target_fc)

    # remove temp workspace
    if (tempworkspace[0] == True and gp.Exists(tempworkspace[1]) == True):
        gp.Delete(tempworkspace[1])

    #Set output parameters
    gp.SetParameterAsText(4,target_fc)
    
    # Processing completed.
    gp.AddMessage(msgProcessComplete)
    print msgProcessComplete
    
except Exception, ErrorMessage:
    # raise error
    print ErrorMessage
    gp.AddError(str(ErrorMessage))
    
del gp
