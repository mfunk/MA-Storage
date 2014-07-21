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
##DATE: 2/12/2007 
##
##Usage: AddObserverFields_ma(<in_feature_class>)
##*********************************************************************************************************************"""


# import libraries
import os,sys,string, time
import arcgisscripting
import MAScriptUtils

# errors
msgTooFewArguments = "Incorrect number of arguments. \n Syntax should be as follows: \n AddObserverFields(<in_feature_class>)"
msgWrongInputType = "Input dataset must be a point or polyline featureclass."
msgCouldNotAddFields = "Could not add observer fields to %s"
msgFieldsAlreadyExist = "The following observer fields already exist: \n %s"
msgCouldNotObtainSchemaLock = "Could not obtain a schema lock on the input observers."
msgAddDefaultsFailed = "Could not add default values to observer fields: \n %s"
# messages
msgProcessingComplete = "Finished adding observer fields."

# create the Geoprocessor
gp = arcgisscripting.create(9.3)

# get script parameters
if (len(sys.argv) < 2):
    raise Exception, msgTooFewArguments
input_observers = gp.GetParameterAsText(0)


bDefaults = True
#if (len(sys.argv) > 3):
#    defaults = gp.GetParameterAsText(1)
#    if (str(defaults).upper() != "DEFAULTS"):
#        bDefaults = False
#    else:
#        bDefaults = True

try:
   
    # mfunk 2/4/2008 - now handled by tool validation
    # check that input feature class exists
    #if (gp.Exists(input_observers) != True):
    #    raise Exception, msgNoInputObservers % (str(input_observers))
    
    # mfunk 2/4/2008 - now handled by tool validation
    # check that input feature class is either POINT or POLYLINE
    #fcdescribe = gp.Describe(input_observers)
    #fctype = fcdescribe.DatasetType
    #fcshapetype = fcdescribe.ShapeType
    #if (fctype != "FeatureClass"):
    #    raise Exception, msgWrongInputType
    #elif (fcshapetype != "Point" and fcshapetype != "Polyline"):
    #    raise Exception, msgWrongInputType
    
    # check if observer fields already exist
    existing_fields = []
    missing_fields = MAScriptUtils.CheckObserverFields(gp,input_observers)
    #checkfields = ["SPOT","OFFSETA","OFFSETB","VERT1","VERT2","AZIMUTH1","AZIMUTH2","RADIUS1","RADIUS2"]
    checkfields = ["OFFSETA","OFFSETB","VERT1","VERT2","AZIMUTH1","AZIMUTH2","RADIUS1","RADIUS2"]
    for checkfield in checkfields:
        if (checkfield in missing_fields):
            pass
        else:
            existing_fields.append(checkfield)
            pass
        
    # if ANY of the observer fields already exist, exit with error
    if (len(existing_fields) > 0):
        raise Exception, msgFieldsAlreadyExist % (existing_fields)
    
    # check for schema lock
    #lock = MAScriptUtils.CheckForSchemaLock(gp,input_observers)
    #if (lock == False or lock == None):
    #    raise Exception, msgCouldNotObtainSchemaLock
    
    # Add observer fields to feature class
    success = MAScriptUtils.AddObserverFields(gp,input_observers)
    if (success == False):
        gpmessage = gp.GetMessages()
        raise Exception, msgCouldNotAddFields % (input_observers)

    # Add default values to observer modifiers in feature class
    #checkfields = ["OFFSETA","OFFSETB","VERT1","VERT2","AZIMUTH1","AZIMUTH2","RADIUS1","RADIUS2"]
    defaultvalues = [0.0,0.0,90.0,-90.0,0.0,360.0,0.0,1000.0]
    extension = input_observers[-4:]
    try:
        if (bDefaults == True):
            rows = gp.UpdateCursor(input_observers)
            row = rows.next()
            while (row != None and row != ""):
                #if (extension.upper() != ".SHP"):
                #    row.SetValue(checkfields[0],defaultvalues[0]) #SPOT
                #else:
                #    pass
                row.SetValue(checkfields[0],defaultvalues[0]) #OFFSETA
                row.SetValue(checkfields[1],defaultvalues[1]) #OFFSETB
                row.SetValue(checkfields[2],defaultvalues[2]) #VERT1
                row.SetValue(checkfields[3],defaultvalues[3]) #VERT2
                row.SetValue(checkfields[4],defaultvalues[4]) #AZIMUTH1
                row.SetValue(checkfields[5],defaultvalues[5]) #AZIMUTH2
                row.SetValue(checkfields[6],defaultvalues[6]) #RADIUS1
                row.SetValue(checkfields[7],defaultvalues[7]) #RADIUS2
                rows.UpdateRow(row)
                row = rows.next()
        # cleanup from update cursor
        del rows, row
    except:
        gpmessages = gp.GetMessages()
        raise Exception, msgAddDefaultsFailed % (gpmessages)

    # set output parameter
    gp.SetParameter(1,input_observers)

    # finished
    gp.AddMessage(msgProcessingComplete)
    print msgProcessingComplete

# Error handler
except Exception, ErrorMessage:
    print ErrorMessage
    gp.AddError(str(ErrorMessage))

del gp