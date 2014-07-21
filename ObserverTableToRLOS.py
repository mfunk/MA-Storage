#!/usr/bin/env python

# ---------------------------------------------------------------------------
# ObserverTableToRLOS.py
# Usage: 
# ---------------------------------------------------------------------------

# Import system modules
import sys, string, os
import arcgisscripting, MAScriptUtils

#Create geoprocessor
gp = arcgisscripting.create()

#Input Arguments
Input_Geodatabase = gp.GetParameters(0)
Input_Observer_Table = gp.GetParameters(1)
Output_Basename = gp.GetParameters(2)
DTED_Folder = gp.GetParameters(3)

#Locals
Observer_Name = Output_Basename + "_observers"
Observer_Path = Input_Geodatabase + os.sep + Observer_Name
Surface_Catalog_Name = Output_Basename + "_surfcat"
Surface_Catalog_Path = Input_Geodatabase + os.sep + Surface_Catalog_Name

try:
    
    #Create observers: <Input_Table>,<Target_Workspace>,<Output_Observers_Name>,{spatial_reference}
    try:
        gp.CreateObserversFromTable_ma(Input_Observer_Table,Input_Geodatabase,Observer_Name)
    except:
        gpmessages = gp.GetMessages()
        errormsg = "Could not create observer points from table: \n %s" % (gpmessages)
        gp.AddError(errormsg)
        raise Exception, errormsg
    
    #Create DTED catalog
    try:
        gp.CreateDTEDCatalog_ma(Input_Geodatabase,Surface_Catalog_Name)
    except:
        gpmessages = gp.GetMessages()
        errormsg = "Could not create surface catalog: \n %s" % (gpmessages)
        gp.AddError(errormsg)
        raise Exception, errormsg
    
    #Load DTED catalog
    try:
        gp.LoadMaCatalog_ma(Surface_Catalog_Path,DTED_Folder)
    except:
        gpmessages = gp.GetMessages()
        errormsg = "Could not load surface catalog: \n %s" % (gpmessages)
        gp.AddError(errormsg)
        raise Exception, errormsg
    
    #Run Radial Line of Sight: <observers>,<input_surface>,<output_workspace>,<fc_basename>
    try:
        gp.RadialLineOfSight_ma(Observer_Path,Surface_Catalog_Path,Input_Geodatabase,Output_Basename)
    except:
        gpmessages = gp.GetMessages()
        errormsg = "Could perform Radial Line of Sight: \n %s" % (gpmessages)
        gp.AddError(errormsg)
        raise Exception, errormsg
    
    #Finish message
    gp.AddMessage("Processing complete.")
    

except Exception, ErrorMessage:
    gp.AddError(ErrorMessage)
    print ErrorMessage