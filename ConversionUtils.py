"""********************************************************************************************************************
ConversionUtils.py

Description: This module provides functions and the geoprocessor which is used by both the FeatureclassConversion.py
and TableConversion.py modules.

Requirements: Python 2.4.1

Author: ESRI, Redlands

Date: Jan 28 2004
*********************************************************************************************************************"""

#Importing standard library modules
import os, arcgisscripting

#Create the geoprocessing objectf
gp = arcgisscripting.create()

#Define message constants so they may be translated easily
msgErrorGenOutput = "Problem generating Output Name"
msgErrorGenOutputRaster = "Problem generating Output Raster Name"
msgErrorSplittingInput = "Problem encountered parse input list"
msgErrorValidateInputRaster ="Problem encountered validate input raster"

#Generates a valid output feature class or table name based on the input and destination
def GenerateOutputName(inName, outWorkspace):
    try:
        #Extract the basename for the input fc from the path (ie. the input feature class or table name)
        outName = os.path.basename(inName)

        #Describe the FeatureClass to determine it's type (shp, cov fc, gdb fc, etc...)
        dsc = gp.Describe(inName)

        #Get the path to the input feature class (basically the fc container). This could be a dataset, coverage, geodatabase, etc...
        inContainer = os.path.dirname(inName)   #Full path excluding the featureclass. D:\Data\redlands.mdb\city

        if inContainer:
            #Extract the basename for the fc container (ie. the geodatabase name, or feature dataset name)
            #This will be used in certain cases to generate the output name
            inContainerName = os.path.basename(inContainer)   #Full path excluding the featureclass. D:\Data\redlands.mdb\city

            #Describe the type of the Feature class container (cov, gdb, vpf, etc...)
            dscInContainer = gp.Describe(inContainer)

            #If the input fc is a feature dataset (Coverage, CAD or VPF), then set the output name to be a
            # combination of the input feature dataset and feature class name. For example if the input
            # is "c:\gdb.mdb\fds\fc" the name for the output feature class would be "fds_fc"
            if (dsc.DataType == "CoverageFeatureClass" or dscInContainer.DataType == "VPFCoverage"
                or dscInContainer.DataType == "CadDrawingDataset" or dscInContainer.DataType == "RasterDataset"):
                outName = inContainerName + "_" + outName

            #If the input is a shapefile, txt or dbf, do not include the extention (".shp", ".dbf", ".txt") as part of the output name
            # Do this everytime since the output could may or may not be a geodatabase feature class or table
            elif (dsc.DataType == "DbaseTable") or (dsc.DataType == "ShapeFile") or (dsc.DataType == "TextFile"):
                outName = outName[:outName.find(".")]

        #The next 3 steps (get rid of invalid chars, add extention (if the output will have one), and generate a unique name)
       
        # If output workspace is a folder, the output is either a shp file or a dbase table, so determine
        # if the output name need to add .shp or .dbf extention to the output
        desOutWorkspace = gp.Describe(outWorkspace)
        if desOutWorkspace.DataType == "Folder":
            if (dsc.DatasetType == "FeatureClass") and (not outName.lower().endswith(".shp")):
                outName = outName.replace(":","_").replace(".","_") + ".shp"
            elif (dsc.DatasetType == "Table") and (not outName.lower().endswith(".dbf")):
                outName = outName.replace(":","_").replace(".","_") + ".dbf"

        # If the output location is a Geodatabase (SDE or Personal) we can use gp.ValidateTableName to generate
        # a valid name for the output table or feature class.
        elif desOutWorkspace.DataType == "Workspace" :
            try:
                outName = gp.ValidateTableName(outName, outWorkspace)
            except:
                pass

        elif desOutWorkspace.DataType == "FeatureDataset":
            try:
                outName = gp.ValidateTableName(outName, os.path.dirname(outWorkspace))
            except:
                pass
            
        # Check if the name which has been generated so far already exist, if yes, create a unique one
        # ValidateTableName will return something unique for that workspace (not yet though) so
        # this (eventully) should move into the >if desOutWorkspace.DataType == "Folder"< block
        outName = GenerateUniqueName(outName, outWorkspace)

        #Return the name full path to the name which was generated 
        return outWorkspace + os.sep + outName

    except Exception, ErrorDesc:
        raise Exception, "%s (%s)" % (msgErrorGenOutput, str(ErrorDesc))

#Generate a valid output raster dataset name with extension
def GenerateRasterName(inName, outWorkspace, ext):
    try:

        #Extract the basename for the input raster dataset
        outName = os.path.basename(inName)
        
        #Get the path to the input dataset. This could be a raster catalog or workspace.
        inContainer = os.path.dirname(inName)   #Full path excluding the raster dataset
        des=gp.Describe(inContainer)
        if (des.DataType == "RasterCatalog"): #rastercatalog
            outName=os.path.basename(inContainer) #use raster catalog name as basename
        elif (des.WorkspaceType =="FileSystem"): #file with extension
            ids = outName.find(".")
            if (ids > -1):
                outName = outName[:ids]

        # for ArcSDE
        outName.replace(":",".")
        ids = outName.rfind(".")
        if (ids > -1):
            outName = outName[(ids+1):]          

        desOutWorkspace = gp.Describe(outWorkspace) #workspace
        if (desOutWorkspace.DataType == "RasterCatalog"):
            return outWorkspace

        # If the output location is a Geodatabase (SDE or Personal) we can use gp.ValidateTableName to generate
        # a valid name for the output table or feature class.
        if desOutWorkspace.DataType == "Workspace":
            try:
                outName = gp.ValidateTableName(outName, outWorkspace)
            except:
                pass
        
        if (desOutWorkspace.WorkspaceType == "FileSystem"): #filesystem
            outName = outName + ext
            if (ext == ""): #Grid format, make sure the filename is 8.3 standard
                grdlen = len(outName)
                if (grdlen > 12):
                    outName = outName[:8]
        else:
            outName = gp.QualifyTableName(outName,outWorkspace)

        outName = GenerateUniqueName(outName, outWorkspace)
        
        return outWorkspace + os.sep + outName
    
    except Exception, ErrorDesc:
        raise Exception, "%s (%s)" % (msgErrorGenOutputRaster, str(ErrorDesc))

#Generates a unique name. If the name already exists, adds "_1" at the end, if that exists, adds "_2", and so on...
def GenerateUniqueName(name, workspace):
    if gp.exists(workspace + os.sep + name):

        # If there is an extention, figure out what it is 
        extention = ""
        if (name.find(".shp") != -1) or (name.find(".dbf") != -1) or (name.find(".img") != -1) or (name.find(".tif") != -1):
            name,extention = name.split(".")
            extention = "." + extention
        i = 1
        name2 = name + "_" + str(i) + extention
        while gp.exists(workspace + os.sep + name2):
            #While the output exists, add 1 to it. So if "tab_1" exists, try "tab_2", then "tab_3", ...
            i += 1
            name2 = name + "_" + str(i) + extention
        name = name2
    return name

#Split the semi-colon (;) delimited input string (tables or feature classes) into a list
def SplitMultiInputs(multiInputs):
    try:
        #Remove the single quotes and parathesis around each input featureclass
        multiInputs = multiInputs.replace("(","").replace(")","").replace("'","")

        #split input tables by semicolon ";"
        return multiInputs.split(";")
    except:
        raise Exception, msgErrorSplittingInput

#Copy the contents (features) of the input feature class to the output feature class
def CopyFeatures(inFeatures, outFeatureClass):
    try:
        gp.CopyFeatures_management(inFeatures, outFeatureClass)
    except:
        raise Exception, gp.GetMessages(2).replace("\n"," ")

#Copy the contents (rasters) of the input raster dataset to the output raster dataset
def CopyRasters(inRasters, outRasters, keyword):
    try:
        gp.CopyRaster_management(inRasters, outRasters, keyword)
    except:
        raise Exception, gp.GetMessages(2).replace("\n"," ")

#Copy the contents (rows) of the input table to the output table
def CopyRows(inTable, outTable):
    try:
        gp.CopyRows_management(inTable, outTable)
    except:
        raise Exception, gp.GetMessages(2).replace("\n"," ")

def ValidateInputRaster(inName):
    try:
        if inName.startswith("'") and inName.endswith("'"):
            inName = inName[1:-1]
        return inName
    
    except:
        raise Exception, msgErrorValidateInputRaster
