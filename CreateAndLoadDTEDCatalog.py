#!/usr/bin/env python

# ---------------------------------------------------------------------------
# CreateAndLoadDTEDCatalog.py
# Usage: CreateAndLoadDTEDCatalog <Input_Geodatabase> <Catalog_Name> <Input_Folder>
# ---------------------------------------------------------------------------

# Import system modules
import sys, string, os
import arcgisscripting, MAScriptUtils

gp = arcgisscripting.create(9.3)

Input_Geodatabase = gp.GetParameterAsText(0)
Catalog_Name = gp.GetParameterAsText(1)
Input_Folder = gp.GetParameterAsText(2)
Out_Catalog_Name = Input_Geodatabase + os.sep + Catalog_Name
gp.SetParameter(3,Out_Catalog_Name)


try:
    gp.CreateDTEDCatalog_ma(Input_Geodatabase,Catalog_Name)
except:
    messages = gp.GetMessages()
    gp.AddError("Create DTED catalog failed: \n %s" % (messages))

try:
    gp.LoadMaCatalog(Out_Catalog_Name,Input_Folder)
except:
    messages = gp.GetMessages()
    gp.AddError("Load DTED catalog failed: \n %s" % (messages))
    
gp.AddMessage("Completed")

