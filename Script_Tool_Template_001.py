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
##Usage: 
##*********************************************************************************************************************"""


# import libraries
import os,sys,string, time
import arcgisscripting
import MAScriptUtils

# create the Geoprocessor
gp = arcgisscripting.create()

# get script parameters
if (len(sys.argv) < 1):
    raise Exception, msgTooFewArguments

try:
    
    # check for spatial analyst license
    if (MAScriptUtils.CheckForSpatialAnalystLicense != True):
        raise Exception, msgNoSpatialLicense
    
    # set temp workspace
    options = MAScriptUtils.GetMAOptions(gp)
    if (len(options) == 0 or options == None):
        tempworkspace = gp.workspace
    elif (len(options) != 0):
        gen_opt = options["General"]
        tempworkspace = gen_opt["GeneralWorkspacePathName"]
    else:
        tempworkspace = os.path.curdir
    
    
    
    
except Exception, ErrorMessage:
    print ErrorMessage
    gp.AddError(ErrorMessage)