#!/usr/bin/env python
# -*- coding: latin-1 -*-

#
# MAScriptUtils.py
#
# Military Analyst Scripting Utilities
#

# import libraries
import os,sys,string,time
import math,decimal,re
import ConversionUtils
import MAScriptUtils


# locals
debug = False

#def __main__(patternDictionary,patternKeys):
#    patternDictionary = MAScriptUtils.RegExPatterns()
#    patternKeys = patternDictionary.keys()
#    return

def RegExPatterns():

    # --- Linear Units ---
    linearDictionary = {}
    metersPattern = re.compile(r"\b(m|M)(e|E)?(t|T)?(e|E)?(r|R)?(s|S)?\b",re.VERBOSE)
    linearDictionary['meters'] = metersPattern
    
    kilometerPattern = re.compile(r"\b[k|K][i|I]?[l|L]?[o|O]?(m|M)(e|E)?(t|T)?(e|E)?(r|R)?(s|S)?\b",re.VERBOSE)
    linearDictionary['kilometer'] = kilometerPattern
    
    feetPattern = re.compile(r"(f|F)((e|E){2})?(t|T)",re.VERBOSE)
    linearDictionary['feet'] = feetPattern
    
    surveyFeetPattern = re.compile(r"\b[U|u][S|s][ _]?[s|S][u|U][r|R][v|V][e|E][y|Y][ _]?[f|F][e|E]?[e|E]?[t|T]\b",re.VERBOSE)
    linearDictionary['US Survey feet'] = surveyFeetPattern
    
    milesPattern = re.compile(r"\b[^A-Za-z0-9 ][m|M][i|I][l|L]?[e|E]?[s|S]?\b",re.VERBOSE)
    linearDictionary['miles'] = milesPattern
    
    nauticalMilesPattern = re.compile(r"\b[n|N][a|A]?[u|U]?[t|T]?[i|I]?[c|C]?[a|A]?[l|L]?[ _]?(m|M)(i|I)?(l|L)?(e|E)?(s|S)?\b",re.VERBOSE)
    linearDictionary['nautical miles'] = nauticalMilesPattern
    
    # --- Angular Units ---
    angularDictionary = {}
    degreesPattern = re.compile(r"\b[d|D][e|E][g|G][.]?[r|R]?[e|E]?[e|E]?[s|S]?\b",re.VERBOSE)
    angularDictionary['degrees'] = degreesPattern
    
    radiansPattern = re.compile(r"\b[r|R][a|A][d|D][i|I]?[a|A]?[n|N]?[s|S]?\b",re.VERBOSE)
    angularDictionary['rads'] = radiansPattern
    
    gradiansPattern = re.compile(r"\b[g|G][r|R][a|A][d|D][i|I]?[a|A]?[n|N]?[s|S]?\b",re.VERBOSE)
    angularDictionary['grads'] = gradiansPattern
    
    milsPattern = re.compile(r"\b[m|M][i|I][l|L][s|S]?\b",re.VERBOSE)
    angularDictionary['mils'] = milsPattern
    
    # --- Area Units ---
    areaDictionary = {}
    squareMetersPattern = re.compile(r"\b[s|S][q|Q][.]?[u|U]?[a|A]?[r|R]?[e|E]?[ _]?[m|M][e|E]?[t|T]?[e|E]?[r|R]?[s|S]?\b",re.VERBOSE)
    areaDictionary['square meters'] = squareMetersPattern
    
    squareFeetPattern = re.compile(r"\b[s|S][q|Q][.]?[u|U]?[a|A]?[r|R]?[e|E]?[ _]?[f|F][e|E]?[e|E]?[t|T]\b",re.VERBOSE)
    areaDictionary['square feet'] = squareFeetPattern
    
    squareKilometersPattern = re.compile(r"\b[s|S][q|Q][.]?[u|U]?[a|A]?[r|R]?[e|E]?[ _]?[k|K][i|I]?[l|L]?[o|O]?(m|M)(e|E)?(t|T)?(e|E)?(r|R)?(s|S)?\b",re.VERBOSE)
    areaDictionary['square kilometers'] = squareKilometersPattern
    
    squareMilesPattern = re.compile(r"\b[s|S][q|Q][.]?[u|U]?[a|A]?[r|R]?[e|E]?[ _]?[m|M][i|I][l|L]?[e|E]?[s|S]?\b",re.VERBOSE)
    areaDictionary['square miles'] = squareMilesPattern
    
    acresPattern = re.compile(r"\b[a|A][c|C][r|R]?[e|E]?[s|S]?\b",re.VERBOSE)
    areaDictionary['acres'] = acresPattern
    
    hectaresPattern = re.compile(r"\b[h|H][e|E]?[c|C]?[t|T]?[a|A][r|R]?[e|E]?[s|S]?\b",re.VERBOSE)
    areaDictionary['hectares'] = hectaresPattern
    
    # Combine dictionaries together
    patternDictionary = {"Linear":linearDictionary,"Angular":angularDictionary,"Area":areaDictionary}
    return patternDictionary


def SetGeographicWGS84(gp):
    spatial_ref_WGS84 = "GEOGCS['GCS_WGS_1984',DATUM['D_WGS_1984',SPHEROID['WGS_1984',6378137.0,298.257223563]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]];-10000 -10000 100000;0 100000;0 100000;0.00002;0.00002;0.00002;IsHighPrecision"
    sr_object = MAScriptUtils.CreateSpatialReferenceFromString(gp,spatial_ref_WGS84)
    return sr_object

def SetAZED(gp,false_easting,false_northing,central_meridian,latitude_of_origin):
    ## TODO: Need to fix domain info for AZED projection
    if (false_easting == None or false_easting == "#"): false_easting = 0.0
    if (false_northing == None or false_northing == "#"): false_northing = 0.0
    if (central_meridian == None or central_meridian == "#"): central_meridian = -155.6063229999909
    if (latitude_of_origin == None or latitude_of_origin == "#"): latitude_of_origin = 19.47635120038616
    
    # here's the string for the PRJ file
    # DO NOT SPLIT this string for 'readability', this will introduce
    # spacing in the string that will cause the PRJ creation to fail!
    spatial_ref_AZED = 'PROJCS["Azimuthal Equidistant",GEOGCS["GCS_WGS_1984",DATUM["D_WGS_1984",SPHEROID["WGS_1984",6378137.0,298.257223563]],PRIMEM["Greenwich",0.0],UNIT["Degree",0.0174532925199433]],PROJECTION["Azimuthal_Equidistant"],PARAMETER["False_Easting",' + str(false_easting) + '],PARAMETER["False_Northing",' + str(false_northing) + '],PARAMETER["Central_Meridian",' + str(central_meridian) + '],PARAMETER["Latitude_Of_Origin",' + str(latitude_of_origin) + '],UNIT["Meter",1.0]]'
    # domain stuff we don't need for the PRJ file
    #;-10000 -10000 100000;0 100000;0 100000;0.00002;0.00002;0.00002;IsHighPrecision
    
    sr_object = MAScriptUtils.CreateSpatialReferenceFromString(gp,spatial_ref_AZED)
    return sr_object

def IsGeographicSR(gp,dataset):
    ## Check if dataset has spatial reference that is Geographic
    IsGeographic = False
    spatial_reference = gp.Describe(dataset).SpatialReference
    s_r_type = spatial_reference.Type
    if (s_r_type == "Geographic"):
        IsGeographic = True
    return IsGeographic
    
def IsProjectedSR(gp,dataset):
    ## Check if dataset has spatial reference that is Geographic
    IsProjected = False
    spatial_reference = gp.Describe(dataset).SpatialReference
    s_r_type = spatial_reference.Type
    if (s_r_type == "Projected"):
        IsProjected = True
    return IsProjected

def IsGeographicWGS84SR(gp,dataset):
    ## Check if dataset has spatial reference that is Geographic WGS 1984
    IsGeographicWGS84 = False
    if (IsGeographicSR == True):
        spatial_reference = gp.Describe(dataset).SpatialReference
        datum_name = spatial_reference.DatumName
        if (datum_name == "D_WGS_1984"):
            IsGeographicWGS84 = True
    return IsGeographicWGS84


def CanEditSDE(gp,ws):
    ## Returns True or False if user can edit or create SDE tables depending on license and schema locks.
    product_info = gp.ProductInfo()

    if (product_info == "ArcInfo" or product_info == "ArcEditor" or product_info == "EngineGeoDB"):
        # True:    
        # ArcEditor
        # ArcInfo
        # EngineGeoDB
        if (CheckForSchemaLock(ws) == True):
            return True
        else:
            return False
    else:
        # False:
        # NotInitialized (no license set)    
        # Engine
        # ArcView
        # ArcServer ????
        return False


def CheckExists(gp,dataset):
    exists = gp.exists(dataset)
    if (exists == 0 or exists == "False" or exists == False):
        return False
    else:
        return True
    
def CheckForSchemaLock(gp,ds):
    ## Checks input workspace for a schema lock
    ## If 'True'then a schema lock can be applied.
    ## If 'False' then a schema lock cannot be applied.
    msgErrorGettingSchemaLock = "Error obtaining a schema lock: \n %s"
    msgSchemaLockNotSupported = "Specified dataset does not support schema lock"
    lock_result = False

    # check for lock
    lock_result = gp.TestSchemaLock(ds)
    # True—A schema lock can be applied to the dataset.
    if (lock_result == "TRUE"): lock_result = True
    # False—A schema lock cannot be obtained on the dataset.
    elif (lock_result == "False"): lock_result = False
    # ERROR—Returned if the specified dataset does not support schema locks, such as a folder
    elif (lock_result == "ERROR"):
        lock_result = None
        gp.AddMessage(msgErrorGettingSchemaLock % (gp.GetMessages()))
    return lock_result

def GetWorkspaceOfDataset(dataset):
    ## Returns the workspace (as string) of a dataset
    path_sep_index = dataset.rfind(os.sep)
    path = dataset[:path_sep_index]
    if (os.path.exists(path) == True):
        return str(path)
    else:
        return ""

def CheckForSpatialAnalystLicense(gp):
    ## Checks if there is an available Spatial Analyst license
    license_result = False
    if gp.CheckExtension("spatial") == "Available":
        license_result = True
    return license_result

def CheckFor3DAnalystLicense(gp):
    ## Checks if there is an available 3D Analyst license
    license_result = False
    if gp.CheckExtension("3d") == "Available":
        license_result = True
    return license_result

def CheckForNetworkLicense(gp):
    ## Checks if there is an available Network Analyst license
    license_result = False
    if gp.CheckExtension("network") == "Available":
        license_result = True
    return license_result

def GetMAOptions(gp):
    ## returns MA options as a list
    ## this is only available for ArcGIS Desktop users.
    options = {}
    if (os.name != "nt"): # possible results: 'posix', 'nt', 'mac', 'os2', 'ce', 'java', 'riscos'
        if (debug == True): print "OS: " + os.name    
        return options
    
    # we don't install options for Engine or Server
    if (gp.ProductInfo() != "ArcInfo" and gp.ProductInfo() != "ArcEditor"  and gp.ProductInfo() != "ArcView"):
        if (debug == True): print "ProductInfo: " + str(gp.ProductInfo())
        return options
    
    try:
        import _winreg
        import struct
        
        # HKEY_CURRENT_USER
        key = _winreg.HKEY_CURRENT_USER
        ma_sub_key = "Software\ESRI\MilitaryAnalyst\9.0.0.0"
        ma_key_handle = _winreg.OpenKey(key,ma_sub_key)
        
        # Enumerate thorugh all subkeys
        num_subs = _winreg.QueryInfoKey(ma_key_handle)[0]
        idx = 0
        while idx <= (num_subs - 1):
            subkeyname = _winreg.EnumKey(ma_key_handle,idx)
            newkey = _winreg.OpenKey(ma_key_handle,subkeyname)
            num_vals = _winreg.QueryInfoKey(newkey)[1]
            ndx = 0
            subops = {}
            while ndx <= (num_vals - 1):
                valname = _winreg.EnumValue(newkey,ndx)[0]
                valstor = _winreg.EnumValue(newkey,ndx)[1]
                valtype = _winreg.EnumValue(newkey,ndx)[2]
                
                if (valtype == 1):
                    struct_format = str(len(str(valstor))) + "s"
                    valstor = struct.unpack(struct_format,valstor)[0]
                    valstor = valstor.replace("\x00","")
                    subops[valname] = str(valstor)
                
                elif (valtype == 3):  # C++ double
                    # DOUBLE: 8
                    if (len(valstor) == struct.calcsize("d")):
                        valstor = struct.unpack("d",valstor)[0]
                    subops[valname] = str(valstor)
                    
                elif (valtype == 4): # True/False
                    if (valstor == 1):
                        valstor = "True"
                    else:
                        valstor = "False"
                    subops[valname] = valstor
                    
                elif (valtype == 7): # raw symbology
                    valstor = "<symbology>"
                    subops[valname] = valstor
                    
                else:
                    subops[valname] = str(valstor)
                
                ndx = ndx + 1
            options[subkeyname] = subops
            _winreg.CloseKey(newkey)
            idx = idx + 1
        
    except:
        message = "Could not read MA Options from registry."
        gp.AddWarning(message)
        print message
        
    if (debug == True): print "Leaving GetMAOptions"
    return options

def ZFactor(gp,in_dataset):
    ## returns the Z-Factor of the input GCS dataset
    zfactor = None
    try:
        # get the dataset extent    
        extent = gp.Describe(in_dataset).Extent
        
        #Check that dataset is geographic
        s_r_type = MAScriptUtils.IsGeographicSR(gp,in_dataset)
        
        if (s_r_type != True):
            raise Exception, "The dataset %s is not in geographic coordinates." % (str(in_dataset))
        else:
            #get the top and bottom of the extent
            top = extent.YMax
            bottom = extent.YMin
            
            if (top > bottom):
                height = (top - bottom)
                mid = (height/2) + bottom
            elif (top < bottom):
                height = bottom - top
                mid = (height/2) + top
            else: # top == bottom
                mid = top
                
            #
            # function:
            # ? Z-Factor = 1.0/(113200 * cos(mid-latitude in radians))
            # this is the correct one: Z-Factor = 1.0/(111320 * cos(mid-latitude in radians))
            decimal.getcontext().prec = 28
            decimal.getcontext().rounding = decimal.ROUND_UP
            a = decimal.Decimal("1.0")
            b = decimal.Decimal("111320.0")
            c = decimal.Decimal(str(math.cos(mid)))
            # here's the actual calculation
            zfactor = a/(b * c)
            # return the correct format
            zfactor = "%06f" % (zfactor.__abs__())
            # make sure it returns a postive number

    
    except Exception, ErrorMessage:
        gp.AddError(ErrorMessage)
        print ErrorMessage
    
    # send it back
    return zfactor     
    
def AddObserverFields (gp,target_fc):
    success = False
    #X,Y,SPOT,OFFSETA,OFFSETB,VERT1,VERT2,AZIMUTH1,AZIMUTH2,RADIUS1,RADIUS2
    try:
        # refresh workspace
        gp.RefreshCatalog(os.path.dirname(target_fc))
        
        #Add observer fields
        #AddField_management (in_table, field_name, field_type, field_precision, field_scale, field_length, field_alias, field_is_nullable, field_is_required, field_domain) 
        #gp.AddField_management(target_fc, "SPOT", "TEXT", "", "", "12", "", "NULLABLE", "NON_REQUIRED", "")
        
        # we won't add SPOT now because it will override surface interp for some functions
        #gp.AddField_management(target_fc, "SPOT", "DOUBLE", "8", "4", "12", "", "NULLABLE", "NON_REQUIRED", "")
        gp.AddField_management(target_fc, "OFFSETA", "DOUBLE", "8", "4", "12", "", "NULLABLE", "NON_REQUIRED", "")
        gp.AddField_management(target_fc, "OFFSETB", "DOUBLE", "8", "4", "12", "", "NULLABLE", "NON_REQUIRED", "")
        gp.AddField_management(target_fc, "VERT1", "DOUBLE", "8", "4", "12", "", "NULLABLE", "NON_REQUIRED", "")
        gp.AddField_management(target_fc, "VERT2", "DOUBLE", "8", "4", "12", "", "NULLABLE", "NON_REQUIRED", "")
        gp.AddField_management(target_fc, "AZIMUTH1", "DOUBLE", "8", "4", "12", "", "NULLABLE", "NON_REQUIRED", "")
        gp.AddField_management(target_fc, "AZIMUTH2", "DOUBLE", "8", "4", "12", "", "NULLABLE", "NON_REQUIRED", "")
        gp.AddField_management(target_fc, "RADIUS1", "DOUBLE", "8", "4", "12", "", "NULLABLE", "NON_REQUIRED", "")
        gp.AddField_management(target_fc, "RADIUS2", "DOUBLE", "8", "4", "12", "", "NULLABLE", "NON_REQUIRED", "")
        success = True
    except:
        message = "Could not add fields to observer feature class: \n %s" % (gp.GetMessages())
        gp.AddError(message)
        print message
        success = False
    return success

def GetFieldNames(gp,input_table):
    '''Get a Python list of field names from the input table.'''
    
    # get table description
    table_desc = gp.describe(input_table)
    # get fields in table
    fields = gp.listfields(input_table)
    # add field names to a list
    field_names = []
    #fields.reset()
    #field = fields.next()
    #while field:
    for field in fields:
        field_names.append(field.NAME)
        #field = fields.next()
    
    return field_names

def CheckMissingObserverFields(gp,input_table):
    #X,Y,SPOT,OFFSETA,OFFSETB,VERT1,VERT2,AZIMUTH1,AZIMUTH2,RADIUS1,RADIUS2
    
    # check for missing fields
    field_names = GetFieldNames(gp,input_table)
    missing_fields = []
    if not ("X" in field_names): missing_fields.append("X")
    if not ("Y" in field_names): missing_fields.append("Y")
    #if not ("SPOT" in field_names): missing_fields.append("SPOT")
    if not ("OFFSETA" in field_names): missing_fields.append("OFFSETA")
    if not ("OFFSETB" in field_names): missing_fields.append("OFFSETB")
    if not ("VERT1" in field_names): missing_fields.append("VERT1")
    if not ("VERT2" in field_names): missing_fields.append("VERT2")
    if not ("AZIMUTH1" in field_names): missing_fields.append("AZIMUTH1")
    if not ("AZIMUTH2" in field_names): missing_fields.append("AZIMUTH2")
    if not ("RADIUS1" in field_names): missing_fields.append("RADIUS1")
    if not ("RADIUS2" in field_names): missing_fields.append("RADIUS2")

    return missing_fields

def CheckObserverFields (gp,dataset):
    msgNoDataset = "Dataset %s does not exist."
    missingfields = []
    #checkfields = ["SPOT","OFFSETA","OFFSETB","VERT1","VERT2","AZIMUTH1","AZIMUTH2","RADIUS1","RADIUS2"]
    checkfields = ["OFFSETA","OFFSETB","VERT1","VERT2","AZIMUTH1","AZIMUTH2","RADIUS1","RADIUS2"]
    try:
        # check that dataset exists
        if (CheckExists(gp,dataset) == False): raise Exception, msgNoDataset % (str(dataset))
        
        # get list of fields in dataset
        fieldnamelist = []
        desc = gp.Describe(dataset)
        fields = gp.ListFields(dataset)

        #field = fields.next()
        for field in fields:
        #while field:
            fieldname = field.Name
            fieldnamelist.append(fieldname)
            #field = fields.next()
            
        #print fieldnamelist
        for check in checkfields:
            if not (check in fieldnamelist):
                missingfields.append(str(check))
                
        return missingfields
        
    except Exception, ErrorMessage:
        print ErrorMessage
        gp.AddError(ErrorMessage)
        return None
    

def DatabaseParams(gp, Input_Geodatabase):
    # returns geodatabase environment info for a workspace (Input_Geodatabase)
    params = []
    
    ## dtype = gp.Describe(Input_Geodatabase).WorkspaceType # Known issue with PGDB
    
    # for SDE geodatabase
    if string.upper(Input_Geodatabase[-4:]) == string.upper(".sde"):
        DatabaseType = "RemoteDatabase"
        ConfigKeyword = str(gp.CONFIGKeyword)
        if (ConfigKeyword == "None" or ConfigKeyword == ""): ConfigKeyword = "DEFAULTS"
        SpatialGrid1 = str(gp.SpatialGrid1)
        if (SpatialGrid1 == "" or SpatialGrid1 == "0" or SpatialGrid1 == "0.0"): SpatialGrid1 = "0.0"
        SpatialGrid2 = str(gp.SpatialGrid2)
        if (SpatialGrid2 == "" or SpatialGrid2 == "0" or SpatialGrid2 == "0.0"): SpatialGrid2 = "0.0"
        SpatialGrid3 = str(gp.SpatialGrid3)
        if (SpatialGrid3 == "" or SpatialGrid3 == "0" or SpatialGrid3 == "0.0"): SpatialGrid3 = "0.0"
        
    # for File Geodatabase
    elif string.upper(Input_Geodatabase[-4:]) == string.upper(".gdb"):
        DatabaseType = "LocalDatabase"
        ConfigKeyword = str(gp.CONFIGKeyword)
        if (ConfigKeyword == "None" or ConfigKeyword == ""): ConfigKeyword = "DEFAULTS"
        SpatialGrid1 = str(gp.SpatialGrid1)
        if (SpatialGrid1 == "" or SpatialGrid1 == "0" or SpatialGrid1 == "0.0"): SpatialGrid1 = "0.0"
        SpatialGrid2 = str(gp.SpatialGrid2)
        if (SpatialGrid2 == "" or SpatialGrid2 == "0" or SpatialGrid2 == "0.0"): SpatialGrid2 = "0.0"
        SpatialGrid3 = str(gp.SpatialGrid3)
        if (SpatialGrid3 == "" or SpatialGrid3 == "0" or SpatialGrid3 == "0.0"): SpatialGrid3 = "0.0"
        
    # for Personal Geodatabase
    elif string.upper(Input_Geodatabase[-4:]) == string.upper(".mdb"):
        DatabaseType = "LocalDatabase"
        ConfigKeyword = ""
        SpatialGrid1 = str(gp.SpatialGrid1)
        SpatialGrid2 = ""
        SpatialGrid3 = ""
        
    # for folder
    else:
        DatabaseType = "FileSystem"
        ConfigKeyword = ""
        SpatialGrid1 = ""
        SpatialGrid2 = ""
        SpatialGrid3 = ""
        
    params = [DatabaseType,ConfigKeyword,SpatialGrid1,SpatialGrid2,SpatialGrid3]
    return params

def MosaicAndClip(gp,inMACatalog,outRaster,clip_extent):

    ## Mosaics and clips for GP operations on DTED Catalogs
    ##
    ## gp - (object) existing gp processor 
    ## inMACatalog (string) - path to an existing MA DTED
    ## outRaster (string) - path to a non-existant raster dataset
    ## clip_extent (list) -  X-Minimum (left), Y-Minimum (bottom), X-Maximum (right), Y-Maximum (top)
    ##                      coordinates for a clipping box
    
    msgNoCatalog = "Catalog %s does not exist."
    msgOutRasterExists = "Raster %s already exists."
    msgBadEnvelope = "Envelope values have wrong number of parameters.\
                     \n Envelope list must be in the following format:\n\
                     <left>,<bottom>,<right>,<top>"
    msgCouldNotCreateOutputRaster = "Could not create output mosaic: \n %s"
    msgCouldNotMosaicRasters = "Could not mosaic rasters:\n %s"
    msgCouldNotClipRasters = "Could not clip mosaic raster to specified extent:\n %s"
    msgBadRasterInCatalog = "Skipping bad raster in catalog: %s"
    msgClippingMosaic = "Clipping mosaic to: %s"
    
    try:
        # check input values
        if not(gp.exists(inMACatalog) == True): raise Exception, msgNoCatalog % (str(inMACatalog))
        if (gp.exists(outRaster) == True): raise Exception, msgOutRasterExists % (str(outRaster))
        
        # check if we need to clip the catalog or not
        bDoNotClip = False
        if (clip_extent != "#" and clip_extent != None):
            if (len(clip_extent) != 4):
                raise Exception, msgBadEnvelope
        else:
            bDoNotClip = True
        
        # get highest and lowest DTED level available - GP error messages are handled internally - filters for MA catalog
        dtedTypes = MAScriptUtils.ReturnDTEDTypes(gp,inMACatalog)
        if (dtedTypes == None or len(dtedTypes) < 1):  return None
        
        # determine the minimum and maximum DTED level
        maxLevel = -1
        minLevel = 100
        for level in dtedTypes:
            #trim characters from string, return number only
            ilevel = int(level[11:])
            if (ilevel > maxLevel):
                maxLevel = ilevel
            pass
            if (ilevel < minLevel):
                minLevel = ilevel
            pass
        DTEDLevel = "DTED Level " + str(minLevel)
        gp.AddMessage("Using %s for processing." % (DTEDLevel)) 
        
        # make where clause string for search cursor
        whereclausestring = "DTED_TYPE = \'" + DTEDLevel + "\'"
        
        
        # Get the Field names for the Geometry and OID fields    
        objectIdField = GetOIDField(inMACatalog, gp)
        geometryField = GetGeometryField(inMACatalog, gp)
        nameField = "NAME"
        productField = "PRODUCT"
        
        
        startlist = []
        # Get an search cursor for the input catalog
        rows = gp.SearchCursor(inMACatalog,whereclausestring)
        row = rows.next()
        recordCount = 0
        listCount = 0
        while row :
            recordCount += 1
            # Get row attributes
            objectId = row.GetValue(objectIdField)
            geometry = row.GetValue(geometryField)
            name = row.GetValue(nameField)

            # get envelope of the row
            featureEnvelope = geometry.Extent
            featureEnvelope = str(featureEnvelope).split(" ")
            featureEnvelope = [featureEnvelope[0],featureEnvelope[1],featureEnvelope[2],featureEnvelope[3]]

            # does this raster fall within the desired extents?
            #@@envelopeInExtent = envelopeContainsEnvelope(featureEnvelope, clip_extent)
            if (bDoNotClip == False and len(clip_extent) != 0):
                envelopeInExtent = EnvelopeRelation(gp,featureEnvelope,clip_extent)
            else:
                envelopeInExtent = 256
            
            # if it does, add it to the list
            #@@if envelopeInExtent :
            if (envelopeInExtent != -1):
                copySource = str(inMACatalog) + "\RASTER.ObjectID=" + str(objectId)
                startlist.append(copySource)

                # FATAL ERROR Segment Violation if raster missing in from cat
                ras_desc = gp.Describe(copySource)
                
                # ensure that the clipping extent is not too small WRT to the resolution of the raster
                if (len(clip_extent) > 3):
                    minWidth = float(ras_desc.MeanCellWidth) * 4.0
                    if minWidth > (float(clip_extent[2]) - float(clip_extent[0])):
                         clip_extent[0] = float(clip_extent[0]) - 0.5 * minWidth
                         clip_extent[2] = float(clip_extent[2]) + 0.5 * minWidth
                    minHeight = float(ras_desc.MeanCellHeight) * 4.0
                    if minHeight > (float(clip_extent[3]) - float(clip_extent[1])):
                         clip_extent[1] = float(clip_extent[1]) - 0.5 * minHeight
                         clip_extent[3] = float(clip_extent[3]) + 0.5 * minHeight
                
                #print copySource
                
                if (listCount == 0):
                    try:
                        # need cell size to create the output raster later on
                        cellsize = ras_desc.MeanCellWidth
                        # convert pixel type
                        if (ras_desc.PixelType == "U1"): pixel_type = "1_BIT"
                        if (ras_desc.PixelType == "U2"): pixel_type = "2_BIT"
                        if (ras_desc.PixelType == "U4"): pixel_type = "4_BIT"
                        if (ras_desc.PixelType == "U8"): pixel_type = "8_BIT_UNSIGNED"
                        if (ras_desc.PixelType == "S8"): pixel_type = "8_BIT_SIGNED"
                        if (ras_desc.PixelType == "U16"): pixel_type = "16_BIT_UNSIGNED"
                        if (ras_desc.PixelType == "S16"): pixel_type = "16_BIT_SIGNED"
                        if (ras_desc.PixelType == "U32"): pixel_type = "32_BIT_UNSIGNED"
                        if (ras_desc.PixelType == "S32"): pixel_type = "32_BIT_SIGNED"
                        if (ras_desc.PixelType == "F32"): pixel_type = "32_BIT_FLOAT"
                        # raster spatial reference
                        ras_sr = ras_desc.SpatialReference
                        listCount += 1
                    except:
                        gp.AddWarning(msgBadRasterInCatalog % (copySource))
                  
            row = rows.next()

        # cleanup
        del row, rows
        
        # format the list for mosaic
        idx = 0
        for ras in startlist:
            if (idx == 0):
                rasterlist = ras
            else:
                rasterlist = rasterlist + ";" + ras
            idx += 1
            
        # make a temp dataset for mosaic
        tempworkspace = gp.workspace
        temppath = MAScriptUtils.GenerateTempFileName(gp,tempworkspace,"RasterDataset")
        try:
            gp.CreateRasterDataset(os.path.dirname(temppath),os.path.basename(temppath),cellsize,pixel_type,ras_sr,1,"#","#","#","#","#")
        except:
            raise Exception, msgCouldNotCreateOutputRaster % (gp.GetMessages())
        # Do the mosaic here from raster list to the temp dataset
        try:
            #Mosaic_management (inputs, target, mosaic_type, colormap, background_value,
            #                   nodata_value, onebit_to_eightbit, mosaicking_tolerance)
            gp.mosaic_management(rasterlist,temppath,"BLEND","#","#","#","#","#")
        except:
            raise Exception, msgCouldNotMosaicRasters % (gp.GetMessages())

        
        # should we clip the mosaic?
        if (len(clip_extent) != 0 and bDoNotClip == False):
            try:
                
                if (debug == True):
                    msg1 = " " + outRaster + " exists?: " + str(gp.Exists(outRaster))
                    msg2 = " " + temppath + " exists?: " + str(gp.Exists(temppath))
                    #print msg2
                    #print msg1
                    gp.AddMessage(msg2)
                    print msg2
                    gp.AddMessage(msg1)
                    print msg1
                                
                # clip the mosaic
                clip_extent = MAScriptUtils.ListToString(clip_extent)                
                #gp.Clip_management(temppath,clip_extent,outRaster,"#")
                gp.Clip_management(temppath,clip_extent,outRaster,temppath) #not sure why a template raster is needed
                
                # delete the mosaic
                gp.Delete_management(temppath)
            except:
                msg = gp.GetMessages()
                print msg
                raise Exception, msgCouldNotClipRasters % (msg)
        else:
            #if there is nothing to clip
            try:
                gp.copy(temppath,outRaster)
                gp.delete(temppath)
            except:
                raise Exception, gp.GetMessages()



        # return the resulting raster
        return outRaster
        
    except Exception, ErrorMessage:
        print str(ErrorMessage)
        gp.AddError(str(ErrorMessage))
        return None
    


def GetObserverExtent(gp,dataset,distance_units):
    
    msgNoDataset = "Dataset %s does not exist."
    msgUnknownCoordinateSystem = "Cannot properly convert distance units because coordinate system is Unknown"

    try:
        # X-Minimum (left), Y-Minimum (bottom), X-Maximum (right), Y-Maximum (top)
        output_extent = []
        
        if (CheckExists(gp,dataset) == False): raise Exception, msgNoDataset % (str(dataset))
        
        # get extent of observer feature class
        extent = gp.Describe(dataset).Extent
        fc_extent = [extent.xmin,extent.ymin,extent.xmax,extent.ymax]
        
        # get datasets spatial reference
        spatial_ref = gp.Describe(dataset).SpatialReference
        
        # find the largest radius in radius1 or radius2 fields
        maxrad = 0.0
        rows = gp.SearchCursor(dataset)
        row = rows.next()
        while row:
            r1 = float(row.GetValue("RADIUS1"))
            r2 = float(row.GetValue("RADIUS2"))
            if (r1 > maxrad): maxrad = r1
            if (r2 > maxrad): maxrad = r2
            row = rows.next()
        
        # we'll give it a bit of a buffer first
        maxrad = maxrad * 1.5
        

        if (spatial_ref.type == "Geographic"):
            # convert from input units to meters
            maxrad = MAScriptUtils.ConvertLinearUnits(gp,maxrad,distance_units,"meter")
            z_factor = MAScriptUtils.ZFactor(gp,dataset)
            # now convert from meters to geographic 
            maxrad = maxrad * float(z_factor)
            
        elif (spatial_ref.type == "Projected"):
            in_units = str(spatial_ref.LinearUnitName)
            # convert from input units to dataset units
            maxrad = MAScriptUtils.ConvertLinearUnits(gp,maxrad,distance_units,in_units)
            
        else: # for Unknown projection
            gp.AddError(msgUnknownCoordinateSystem)
            raise Exception, msgUnknownCoordinateSystem
        
        
        # expand the envelope
        left = float(fc_extent[0]) - maxrad
        bottom = float(fc_extent[1]) - maxrad
        right = float(fc_extent[2]) + maxrad
        top = float(fc_extent[3]) + maxrad
        
        # set the output list
        output_extent = [left,bottom,right,top]
        
        return output_extent
    
    except Exception, ErrorMessage:
        print ErrorMessage
        gp.AddError(str(ErrorMessage))
        return None

def GetCentroidOfEnvelope(gp,envelope):
    centroid = []
    msgBadEnvelope = "Envelope must contain a left, bottom, right and top coordinate."
    msgBadCoordValues = "Envelope coordinate %s does not fit in the range of %s to %s"
    try:
        # too many or too few arguments
        if (len(envelope) != 4): raise Exception, msgBadEnvelope
        
        # get the individual coords
        left = envelope[0]
        bottom = envelope[1]
        right = envelope[2]
        top = envelope[3]
        
        # check that they're in the right value ranges
        # TODO: what if we want to use non-Lat/Lon values?
        if not (-180 <= left or left <= 180): raise Exception, msgBadCoordValues % (left,-180,180)
        if not (-180 <= right or right <= 180): raise Exception, msgBadCoordValues % (right,-180,180)
        if not (-90 <= bottom or bottom <= 90): raise Exception, msgBadCoordValues % (bottom,-90,90)
        if not (-90 <= top or top <= 90): raise Exception, msgBadCoordValues % (top,-90,90)
        
        
        width = right - left
        height = top - bottom
        
        centroid_x = left + (width / 2.0)
        centroid_y = bottom + (height / 2.0)
        
        centroid = [centroid_x,centroid_y]
        
        return centroid
    
    except Exception, ErrorMessage:
        print ErrorMessage
        gp.AddError(str(ErrorMessage))
        return None

def GetGeometryField(featureClass, gp):
    sShapeField = None
    desc = gp.Describe(featureClass)
    # if (desc.DatasetType == "FeatureClass"): sShapeField = desc.ShapeFieldName
    sShapeField = desc.ShapeFieldName
    return sShapeField        

def GetRasterField(rasterCatalog,gp):
    sRasterField = None
    desc = gp.Describe(rasterCatalog)
    if (desc.DatasetType == "RasterCatalog"): sRasterField = desc.RasterFieldName
    return sRasterField

def GetOIDField(featureClass, gp):
    fcInfo = gp.describe(featureClass)
    sFID = fcInfo.OIDFieldName    
    return sFID

def envelopeContainsPoint(envelope, pointX, pointY):
    contains = False
    tolerance = 0.0000001

    X1 = float(envelope[0])
    Y1 = float(envelope[1])
    X2 = float(envelope[2])
    Y2 = float(envelope[3])

    # find the min, max from each
    minX = min(X1, X2)
    maxX = max(X1, X2)
    minY = min(Y1, Y2)
    maxY = max(Y1, Y2)
  
    if (pointY >= (minY - tolerance)) and (pointY <= (maxY + tolerance)) and (pointX >= (minX - tolerance)) and (pointX <= (maxX + tolerance)):
        contains = True

    return contains

def envelopeContainsEnvelope(envelopeInner, envelopeOuter):
    contains = False
    
    minX = float(envelopeInner[0])
    minY = float(envelopeInner[1])
    maxX = float(envelopeInner[2])
    maxY = float(envelopeInner[3])

    containsP1 = envelopeContainsPoint(envelopeOuter, minX, minY)
    containsP2 = envelopeContainsPoint(envelopeOuter, maxX, maxY)

    if containsP1 and containsP2 :
        contains = True
    
    return contains

def countTableRecords(inputTable, gp) :   
    inRows = gp.searchcursor(inputTable)
    inRow = inRows.next()
    recordCount = 0
    while inRow:
        recordCount = recordCount+1
        inRow = inRows.next()
    return recordCount;

def ProjectPoint(gp,in_point,in_sr,target_sr):
    msgCouldNotMakeTempFile = "Internal Error (MAScriptUtils.ProjectPoint):\n Could not make temp file in the %s workspace."
    
    try:
        n = 0
        # get temp workspace
        #workspace = MAScriptUtils.GetTempWorkspace(gp)
        workspace = gp.workspace
        
        # create feature class
        # CreateFeatureClass_management (out_path, out_name, geometry_type, template, 
        #           has_m, has_z, spatial_reference, config_keyword, spatial_grid_1,
        #           spatial_grid_2, spatial_grid_3)
        tempname = MAScriptUtils.GenerateTempFileName(gp,workspace[1],"FeatureClass")
        tempname2 = MAScriptUtils.GenerateTempFileName(gp,workspace[1],"FeatureClass")
        
        try:
            fc = gp.CreateFeatureClass(workspace,tempname,"POINT","#","#","#",in_sr).GetOutPut(0) # GetOutPut(0) is assuming that the result is a return object
        except:
            raise Exception, msgCouldNotMakeTempFile % (workspace)
        
        # add point to feature class
        cur = gp.InsertCursor(fc)                      
        feat = cur.NewRow()
        feat.shape = pnt
        cur.InsertRow(feat)
        del cur
        
        # project feature class
        # Project_management (in_dataset, out_dataset, out_coor_system, transform_method, in_coor_system)
        pfc = gp.Project(fc,tempname2,target_sr,"#",in_sr).GetOutPut(0) # GetOutPut(0) is assuming that the result is a return object
                
        # get xy coords from feature class
        shapefieldname = GetGeometryField(pfc,gp)
        cur2 = gp.SearchCursor(pfc)
        row = cur2.next()
        feat = row.GetValue(shapefieldname)
        out_point = feat.GetPart()
        
        # delete temp points
        gp.delete_management(fc)
        gp.delete_management(pfc)
            
        return out_point
        
    except Exception, ErrorMessage:
        print ErrorMessage
        gp.AddError(str(ErrorMessage))
        return None
    
def CreateSpatialReferenceFromString(gp,sr_as_string):
    
    #
    #
    # ERROR:
    # ("esri.SpatRefEnvironment") the input is not a workstation prj file.
    #
    # Does this file have to be a ArcInfo Workstation PRJ file and not
    # and ArcView GIS PRJ file? Yes, the two are different.
    #
    
    sr_object = None
    try:

        # set temp workspace
        #tempworkspace = MAScriptUtils.GetTempWorkspace(gp)
        tempworkspace = gp.workspace
                
        # create temp file
        temppath = MAScriptUtils.GenerateTempFileName(gp,tempworkspace,"ProjectionFile")
        
        tempfilehandle = open(temppath,"w")
        
        # write string to temp file
        tempfilehandle.write(sr_as_string)
        
        # close temp file
        tempfilehandle.close()
        
        # create spatial refernce object
        sr_object = gp.CreateObject("SpatialReference")
                
        # load spatial reference from file
        sr_object.CreateFromFile(temppath)
        
        # remove temp file
        os.remove(temppath)
        
    except Exception, ErrorMessage:
        sr_object = None
        gp.AddError(str(ErrorMessage))
        print ErrorMessage
        
    return sr_object

def EnvelopeRelation(gp,A,B):

    # A[Left,Bottom,Right,Top]
    # B[Left,Bottom,Right,Top]
    L1,B1,R1,T1 = float(A[0]),float(A[1]),float(A[2]),float(A[3])
    L2,B2,R2,T2 = float(B[0]),float(B[1]),float(B[2]),float(B[3])
    
    if debug == True:
        msg = "start EnvelopeRelation"
        print msg
        gp.AddMessage(msg)

##
##  This tool compares the adjacency (or coincidence) relation between two input envelopes.
##  A result of -1 means the two envelopes share no adjacent relationship.
##  Any other number suggests the two envelopes are adjacent or coincident in some fashion.
##  The results are defined using the figure below:
##
##              -1      
##
##        +---+---+---+
##        |128| 1 | 2 |
##        +---+---+---+
##  -1    |64 | 0 | 4 |     -1
##        +---+---+---+
##        |32 |16 | 8 |
##        +---+---+---+
##
##              -1
##

    # COINCIDENT:
    # A and B share same envelope
    if ((L1 == L2) and (B1 == B2) and (R1 == R2) and (T1 == T2)): return 256
    
    # CONTAINS:
    # A is completely within B
    if ((T1 < T2) and (B1 > B2) and (L1 > L2) and (R1 < R2)): return 0

    # CONTAINED (B within A):
    # B is completely within A
    if ((L1 < L2) and (B1 < B2) and (R1 > R2) and (T1 > T2)): return 256

    # PARTIAL:
    # Only top, no corners
    if ((T1 >= T2) and (B1 < T2) and (B1 > B2) and (L1 > L2) and (R1 < R2)): return 1
    # Top Right corner only
    if ((T1 >= T2) and (B1 < T2) and (B1 > B2) and (L1 > L2) and (L1 < R2) and (R2 <= R1)) : return 2
    # Right side only, no corners
    if ((T1 < T2) and (B1 > B2) and (L1 > L2) and (L1 < R2) and (R1 >= R2)) : return 4
    # Bottom Right corner only
    if ((T1 > B2) and (T1 < T2) and (B1 <= B2) and (L1 > L2) and (L1 < R2) and (R2 <= R1)) : return 8
    # Bottom only, no corners
    if ((T1 > B2) and (T1 < T2) and (B1 <= B2) and (L1 > L2) and (R1 < R2)) : return 16
    # Bottom Left corner only
    if ((T1 > B2) and (T1 < T2) and (B1 <= B2) and (L1 <= L2) and (R1 > L2) and (R1 < R2)) : return 32
    # Left side only, no corners
    if ((T1 < T2) and (B1 > B2) and (L1 <= L2) and (R1 > L1) and (R1 < R2)) : return 64  
    # Top Left corner only
    if ((T1 >= T2) and (B1 < T2) and (B1 > B2) and (L1 <= L2) and (R1 > L2) and (R1 < R2)): return 128

    # PARTIAL SIDE:
    #Entire left side
    # 128 + 64 + 32 = 224
    if ((T1 >= T2) and (B1 <= B2) and (L1 <= L2) and (R1 > L2) and (R1 < R2)): return  224
    # Vertical through middle
    # 1 + 0 + 16 = 17
    if ((L1 > L2) and (R1 < R2) and (T1 >= T2) and (B1 <= B2)) : return 17
    #Entire Right side
    # 2 + 4 + 8 = 14
    if ((T1 >= T2) and (B1 <= B2) and (L1 > L2) and (L1 < R2) and (R1 >= R2)) : return 14
    #Entire top
    # 128 + 1 + 2 = 131
    if ((T1 >= T2) and (B1 > B2) and (B1 < T2) and (L1 <= L2) and (R1 >= R2)) : return 131
    # horizontally through middle
    # 64 + 0 + 4 = 68
    if ((L1 <= L2) and (R1 >= R2) and (T1 < T2) and (B1 > B2)) : return 68
    #Entire bottom
    # 32 + 16 + 8 = 56
    if ((T1 < T2) and (T1 > B2) and (B1 <= B2) and (L1 <= L2) and (R1 >= R2)) : return 56


    return -1

def ReturnDTEDTypes(gp,inCatalog):
    # given an input MA DTED Catalog we want to figure out what DTED types
    # are present in the catalog. This tool returns a list of DTED types.
    
    # error messages
    msgNoCatalog = "Catalog %s does not exist."
    msgEmptyCatalog = "Catalog %s does not contain DTED_TYPE information.  (Is it a Military Analyst catalog?)"
    outDTEDType = []
    try:
        # Check that inCatalog exists
        if (gp.exists(inCatalog) == False):
            raise Exception, msgNoCatalog % str(inCatalog)
        field_names = GetFieldNames(gp,inCatalog)
        if not ("DTED_TYPE" in field_names):
            raise Exception, msgEmptyCatalog % str(inCatalog)
        
        productList = []
        searchcur = gp.SearchCursor(inCatalog)
        row = searchcur.next()
        while row:
            dtedtype = row.GetValue("DTED_TYPE")
            if not (dtedtype in productList):
                productList.append(dtedtype)
            row = searchcur.next()
        
        if (len(productList) == 0):
            raise Exception, msgEmptyCatalog % (inCatalog)
        else:
            outDTEDType = productList
    
    except Exception, ErrorMessage:
        gp.AddError(str(ErrorMessage))
        print ErrorMessage

    return outDTEDType

def ReturnRPFProduct(gp,inCatalog):
    outRPFProduct = []
    
    try:
        # check that input catalog exists
        if (gp.exists(inCatalog) == False):
            raise Exception, msgNoCatalog % (inCatalog)
        
        searchcur = gp.searchcursor(inCatalog)
        row = searchcur.next()
        while row:
            rpfprod = str(row.GetValue("PRODUCT"))
            rpfseries = str(row.GetValue("SERIES"))
            product = rpfprod[:(string.find(rpfprod,"$"))]
            producttype =  rpfprod[(string.find(rpfprod,"$") + 1):]
            finalproduct = product + "\\" + producttype + "\\" + rpfseries
            if not (finalproduct in outRPFProduct):
                outRPFProduct.append(finalproduct)
            else:
                pass

            row = searchcur.next()
        
        del row, searchcur

    except Exception, ErrorMessage:
        gp.AddError(str(ErrorMessage))
        print ErrorMessage        
    
    return outRPFProduct
def ConvertLinearUnits(gp,inValue,inUnit,outUnit):
#    # Converts between linear units.
#    #possible input units: meter, kilometer, feet, US Survey feet, miles, nautical miles
    outValue = None
    patternDictionary = {}
    
    #Error messages
    msgConvertToMeterError = "Input unit %s could not be understood."
    msgConvertToOutputError = "Output unit % could not be understood."
    msgUnknownError = "Internal conversion error: Output empty (MAScriptUtils.ConvertLinearUnits)"

    try:
        # Regex parsing of input and ouptut units
        patternDictionary = MAScriptUtils.RegExPatterns()
        patternKeys = patternDictionary['Linear'].keys()
        
        for patternName in patternKeys:
            # check pattern exists pattternDictionary.has_key(patternName)
            patternExpression = patternDictionary['Linear'][patternName]
            #compare inUnit
            patternSearch = re.search(patternExpression,inUnit)
            if (patternSearch != None): inUnit = patternName
            #compare outUnit
            patternSearch = re.search(patternExpression,outUnit)
            if (patternSearch != None): outUnit = patternName
        
        # To Meters
        if (inUnit == "meters" and outUnit == "meters"):
            outValue = inValue # no conversion necessary
        else:
        # First convert to meters
            if (inUnit == "meters"): meterValue = float(inValue)
            elif (inUnit == "kilometer"): meterValue = float(inValue * 1000.0) # constant is exact
            elif (inUnit == "feet"): meterValue = float(inValue * 0.3048) # constant is exact
            elif (inUnit == "US Survey feet"): meterValue = float(inValue * (1200.0/3937.0)) # fraction is exact
            elif (inUnit == "miles"): meterValue = float(inValue * 1609.344) # constant is exact
            elif (inUnit == "nautical miles"): meterValue = float(inValue * 1852.0) # constant is exact
            else:
                raise Exception, msgConvertToMeterError % (inUnit)
            
            # Then convert to output units
            if (outUnit == "meters"): outValue = float(meterValue)
            elif (outUnit == "kilometer"): outValue = float(meterValue / 1000.0)
            elif (outUnit == "feet"): outValue = float(meterValue * 3.280839895)
            elif (outUnit == "US Survey feet"): outValue = float(meterValue * (3937.0/1200.0))
            elif (outUnit == "miles"): outValue = float(meterValue / 1609.344)
            elif (outUnit == "nautical miles"): outValue = float(meterValue / 1852.0)
            else:
                raise Exception, msgConvertToOutputError % (outUnit)
            
        #last check that output is not empty
        if (outValue == None or str(outValue) == 0):
            raise Exception, msgUnknownError
            
    except Exception, ErrorMessage:
        gp.AddError(ErrorMessage)
        print ErrorMessage
       
    return outValue

def ConvertAngularUnits(gp,inValue,inUnit,outUnit):
    #
    # possible units: degrees, radians, grads, mils
    #
    outValue = None
    #Error messages
    msgConvertToRadiansError = "Input unit %s could not be understood."
    msgConvertToOutputError = "Output unit % could not be understood."
    msgUnknownError = "Internal conversion error: Output empty (MAScriptUtils.ConvertAngularUnits)"
    
    # constants (in radians)
    # web ref: http://en.wikipedia.org/wiki/Conversion_of_units#Angle
    #
    ma_degrees = float(math.pi/180.0)
    ma_mil = float((2 * math.pi)/6400)
    ma_grad = float((2 * math.pi)/400)
    
    try:
        
        # Regex parsing of input and ouptut units
        MAScriptUtils.RegExPatterns()
        
        for patternName in patternKeys:
            # check pattern exists pattternDictionary.has_key(patternName)
            patternExpression = patternDictionary['Angular'][patternName]
            #compare inUnit
            patternSearch = re.search(patternExpression,inUnit)
            if (patternSearch != None):
                inUnit = patternName
            #compare outUnit
            patternSearch = re.search(patternExpression,outUnit)
            if (patternSearch != None):
                outUnit = patternName

        
        if (inUnit == "radians" and outUnit == "radians"):
            outValue = float(inValue)
        else:
            # convert everything to radians
            if (inUnit == "radians"): radianValue = float(inValue)
            elif (inUnit == "degrees"): radianValue = float(inValue * ma_degrees)
            elif (inUnit == "gradians"): radianValue = float(inValue * ma_grad)
            elif (inUnit == "mils"): radianValue = float(inValue * ma_mil)
            else:
                raise Exception, msgConvertToRadiansError % (inUnit)
        
            # convert radians to output units
            if (outUnit == "radians"): outValue = float(radianValue)
            elif (outUnit == "degrees"): outValue = float(radianValue / ma_degrees)
            elif (outUnit == "gradians"): outValue = float(radianValue / ma_grad)
            elif (outUnit == "mils"): outValue = float(radianValue / ma_mil)
            else:
                raise Exception, msgConvertToOutputError % (outUnit)
        
        #last check that output is not empty
        if (outValue == None or str(outValue) == 0):
            raise Exception, msgUnknownError
                
    except Exception, ErrorMessage:
        gp.AddError(ErrorMessage)
        print ErrorMessage
        
    return outValue

def ConvertAreaUnits(gp,inValue,inUnit,outUnit):
    #
    # possible units: square meters, square feet, square kilometers, square miles, acres, hectares
    #
    outValue = None
    #Error messages
    msgConvertToRadiansError = "Input unit %s could not be understood."
    msgConvertToOutputError = "Output unit % could not be understood."
    msgUnknownError = "Internal conversion error: Output empty (MAScriptUtils.ConvertAreaUnits)"
    
    # constants (in square meters)

    try:
        
        # Regex parsing of input and ouptut units
        MAScriptUtils.RegExPatterns()
        
        for patternName in patternKeys:
            # check pattern exists pattternDictionary.has_key(patternName)
            patternExpression = patternDictionary['Area'][patternName]
            #compare inUnit
            patternSearch = re.search(patternExpression,inUnit)
            if (patternSearch != None):
                inUnit = patternName
            #compare outUnit
            patternSearch = re.search(patternExpression,outUnit)
            if (patternSearch != None):
                outUnit = patternName
        
        if (inUnit == "square meters" and outUnit == "square meters"):
            outValue = float(inValue)
        else:
            # convert everything to radians
            if (inUnit == "square meters"): sqmeterValue = float(inValue)
            elif (inUnit == "square feet"): sqmeterValue = float(inValue * 0.09290304)
            elif (inUnit == "square kilometers"): sqmeterValue = float(inValue * 1000.0**2)
            elif (inUnit == "square miles"): sqmeterValue = float(inValue * 2589998.0)
            elif (inUnit == "acres"): sqmeterValue = float(inValue * 4046.856)
            elif (inUnit == "hectares"): sqmeterValue = float(inValue * 10000.0)
            else:
                raise Exception, msgConvertToSqMetersError % (inUnit)
        
            # convert radians to output units
            if (outUnit == "square meters"): outValue = float(sqmeterValue)
            elif (outUnit == "square feet"): outValue = float(sqmeterValue / 0.09290304)
            elif (outUnit == "square kilometers"): outValue = float(sqmeterValue / 1000.0**2)
            elif (outUnit == "square miles"): outValue = float(sqmeterValue / 2589998.0)
            elif (outUnit == "acres"): outValue = float(sqmeterValue / 4046.856)
            elif (outUnit == "hectares"): outValue = float(sqmeterValue / 10000.0)
            else:
                raise Exception, msgConvertToOutputError % (outUnit)
        
        #last check that output is not empty
        if (outValue == None or str(outValue) == 0):
            raise Exception, msgUnknownError
                
    except Exception, ErrorMessage:
        gp.AddError(ErrorMessage)
        print ErrorMessage
        
    return outValue  

def ListToString(inList):
    outString = ""
    itemnum = 1
    for item in inList:
        item = str(item)
        item = item.lstrip("'") # remove leading single quote
        item = item.rstrip("'") # remove trailing single quote
        if (itemnum < len(inList)): # build the list with spaces
            outString = outString + item + " "
        else:
            outString = outString + item
        itemnum += 1
    pass

    # print "ListToString result: " + outString
    return outString

def GenerateTempFileName(gp,workspace,inType):
    
    # generate the temp name
    tempname = "tmp" + str(time.strftime("%d%H%M%S", time.gmtime()))
    
    # get the workspace type: FileSystem, LocalDatabase or RemoteDatabase
    workspace_type = gp.Describe(workspace).WorkspaceType
    
    # For FileSystem
    if (workspace_type == "FileSystem"):
        # temp raster dataset as IMAGINE Image
        if (inType == "RasterDataset"):
            outFile = workspace + os.sep + tempname + ".img"
        # temp raster dataset with NODATA cells must be a GRID
        if (inType == "NoDataRasterDataset"):
            #check for ArcInfoWorkspace
            if (os.path.exists(workspace + os.sep + "info")):
                outFile = workspace + os.sep + tempname
            else:
                os.mkdir(workspace + os.sep + "info")
                outFile = workspace + os.sep + tempname
        # temp shapefile
        if (inType == "FeatureClass"):
            outFile = workspace + os.sep + tempname + ".shp"
        # temp PRJ file
        if (inType == "ProjectionFile"):
            outFile = workspace + os.sep + tempname + ".prj"
        if (inType == "ASCIIFile"):
            outFile = workspace + os.sep + tempname + ".txt"
    
    # For File or Personal Geodatabases
    if (workspace_type == "LocalDatabase"):
        if (inType == "FeatureClass"):
            outFile = workspace + os.sep + tempname
        if (inType == "RasterDataset"):
            # need to force this to become a GRID
            outFile = workspace + os.sep + tempname
        # temp raster dataset with NODATA cells must be a GRID
        if (inType == "NoDataRasterDataset"):
            #check for ArcInfoWorkspace
            if (os.path.exists(os.path.dirname(workspace) + os.sep + "info")):
                outFile = os.path.dirname(workspace) + os.sep + tempname
            else:
                os.mkdir(os.path.dirname(workspace) + os.sep + "info") # make an info folder
                outFile = os.path.dirname(workspace) + os.sep + tempname
        if (inType == "ProjectionFile"):
            outFile = os.path.dirname(workspace) + os.sep +  tempname + ".prj"
        if (inType == "ASCIIFile"):
            outFile = os.path.dirname(workspace) + os.sep + tempname + ".txt"
        
    # For ArcSDE Geodatabases
    if (workspace_type == "RemoteDatabase"):
        if (inType == "FeatureClass"):
            outFile = workspace + os.sep + tempname
        if (inType == "RasterDataset"):
            outFile = workspace + os.sep + tempname
        if (inType == "ProjectionFile"):
            outFile = os.environ['TEMP'] + os.sep + tempname + ".prj"
            
    return outFile

def StringToList(inString):
    outList = []
    outList = inString.split(" ")
    return outList

def GetTempWorkspace(gp):
    #
    # Create a temporary (to be deleted) workspace for
    # intermediate datasets.
    #
    msgErrorSettingWorkspace = "Internal Error: Could not get temporary workspace."
    out_workspace = [False,""] # workspace to return to calling function
    workspace = "" # temp workspace for this local function
    try:
        # get temp workspace from registry
        options = MAScriptUtils.GetMAOptions(gp)
        # if options returned are empty
        if (len(options) == 0 or options == None):
            workspace = os.curdir
        else:
            gen_opt = options["General"]
            workspace = gen_opt["GeneralWorkspacePathName"]

        # temp gdb name
        out_gdb_name = "matempgdb" + str(time.strftime("%d%H%M%S", time.gmtime()))

        # is the workspace a geodatabase or file?
        workspace_describe = gp.Describe(workspace)
        workspace_type = workspace_describe.WorkspaceType
        if (workspace_type == "FileSystem"):
            # make new GDB temp
            out_gdb_name = out_gdb_name + ".gdb"
            gp.CreateFileGDB_management(workspace,out_gdb_name)
            out_workspace = [True,workspace + os.sep + out_gdb_name]
        elif (workspace_type == "RemoteDatabase"):
            # for SDE????
            other_temp_path = os.environ['TEMP'] # get the systems temp path
            gp.CreateFileGDB_management(other_temp_path,out_gdb_name)
            out_workspace = [True,other_temp_path + os.sep + out_gdb_name]
        elif (workspace_type == "LocalDatabase"):
            # for FGDB or PGDB
            out_workspace = [False,workspace]
        else:
            # anything else we can do here?
            pass

    except:
        gp.AddError(msgErrorSettingWorkspace)
        out_workspace = None
        
    return out_workspace

def GenerateProfileLine(gp,input_polyline,inUnits):
    
    #
    #input_polyline:
    #
    #The output line feature class along which visibility has been determined.
    #Two attribute fields are created.
    #VisCode indicates visibility along the line, 1 being visible and 2 not visible.
    #TarIsVis indicates the target visibility, 0 being not visible and 1 being visible.
    #
    debug = True
    profileLine = []
    runCoords = []
    riseCoords = []

    msgCouldNotConvertunits = "Internal Error: Could not convert z coordinate values."
    
    try:
        # if the ouput line of sight is a shapefile, append ".shp" to the end of the pathname.
        if (gp.Describe( os.path.dirname( input_polyline)).WorkspaceType == "FileSystem"):
            input_polyline += ".shp"
            
        zfactor = MAScriptUtils.ZFactor(gp,input_polyline) # get the zfactor for this dataset
        linenumber = 0
        desc = gp.Describe(input_polyline)
        shapefieldname = desc.ShapeFieldName
        startX,startY,startZ = 0.0,0.0,0.0
        
        rows = gp.SearchCursor(input_polyline)
        row = rows.next()
        
        while row: # for each line in the shapefile    
            feat = row.GetValue(shapefieldname)
            visiblity = row.GetValue("VisCode")
            target_visible = row.GetValue("TarIsVis")
            partnum = 0
            partcount = feat.PartCount
            while partnum < partcount: # for each part in the line
                part = feat.GetPart(partnum)
                print "points %s in part %s" % (part.Count,str(partnum))
                pnt = part.Next()
                pntcount = 0
                
                while pnt: # for each shape point in the part
                    shpX,shpY,shpZ = pnt.x, pnt.y, pnt.z # get coords for part shape
                    
                    if (linenumber == 0 and partnum == 0 and pntcount == 0):
                        startX,startY,startZ = pnt.x,pnt.y,pnt.z
                        
                    # convert the z units to xy units.
                    if (MAScriptUtils.IsGeographicSR(gp,input_polyline) == True):
                        meters = MAScriptUtils.ConvertLinearUnits(gp,shpZ,inUnits,"meter") # convert input units to meters
                        if (meters == None):
                            raise Exception, msgCouldNotConvertunits
                        shpZ = meters * float(zfactor) # do the conversion
                    elif (MAScriptUtils.IsProjectedSR(gp,input_polyline) == True):
                        xyunits = gp.Describe(input_polyline).SpatialReference.LinearUnitName # get xy (linear) units
                        shpZ = MAScriptUtils.ConvertLinearUnits(gp,shpZ,inUnits,xyunits) # convert from z units to xy units
                    else: # if its Unknown?
                        pass
                    
                    # find distance between point and previous point
                    if (linenumber == 0 and partnum == 0 and pntcount == 0 and len(profileLine) == 0):
                        xydist = 0
                    else:
                        xydist = math.sqrt((shpX - startX)**2 + (shpY - startY)**2)
                    
                    runCoords.append(xydist) # add the distance
                    riseCoords.append(shpZ) # add the elevation
                    
                    pnt = part.Next()
                    pntcount += 1
                    if not pnt: 
                        pnt = part.Next()
                    
                    if debug == True:
                        print str(linenumber) + "," + str(partnum) + "," + str(xydist) + "," + str(shpZ)
                    
                partList = [linenumber,partnum,visiblity,runCoords,riseCoords]
                runCoords = []
                riseCoords = []
                profileLine.append(partList)
                    
                partnum += 1
                
            row = rows.Next()
            linenumber += 1
            
        
        #target_visible
        # plot line
        MAScriptUtils.PlotProfile(target_visible,profileLine)
        
    except Exception, ErrorMessage:
        profileLine = []
        gp.AddError(str(ErrorMessage))
        print str(ErrorMessage)
        
    return profileLine

def PlotProfile(target_visible,lstProfileList):
    #
    # THIS TOOL REQUIRES 3RD PARTY PYTHON LIBs:
    # numpy: www.scipy.org
    # pylab (matplotlib): http://matplotlib.sourceforge.net/
    
    msgIsVisible = "Line of Sight Surface Profile Plot. \n The target is visible."
    msgIsNotVisible = "Line of Sight Surface Profile Plot. \n The target is not visible."
    
    import numpy
    import pylab
    
    if debug == True:
        print "Number of parts: = " + str(len(lstProfileList))
        print
        print lstProfileList
        print
    
    list1 = []
    list2 = []
    for sortList in lstProfileList:
        if sortList[0] == 0:
            list1.append(sortList)
        else:
            list2.append(sortList)

    finalList = []
    maxlist = max(len(list1),len(list2))
    a = 0
    while a <= (maxlist -1):
        try:
            appendlist = list1[a]
            if (appendlist != None):
                finalList.append(appendlist)
        except IndexError:
            pass
        try:
            appendlist = list2[a]
            if (appendlist != None):
                finalList.append(appendlist)
        except IndexError:
            pass
        a += 1

    obsx = 0.0
    obsy = 0.0
    tgtx = 0.0
    tgty = 0.0
    partCount = len(finalList)
    partCheck = 0
    for partList in finalList:
        partCheck += 1
        linenum = partList[0]
        partnum = partList[1]
        visibility = partList[2]
        runList = partList[3]
        riseList = partList[4]
        
        # get observer point
        if (linenum == 0 and partnum == 0):
            obsx = runList[0]
            obsy = riseList[0]
            
        # get target point
        if (partCheck == partCount):
            runListLen = len(runList)
            riseListLen = len(riseList)
            tgtx = runList[runListLen - 1]
            tgty = riseList[riseListLen - 1]
        
        if debug == True: print "line " + str(linenum) + " part " + str(partnum) + " has " + str(len(runList)) +  " in x and " + str(len(riseList)) + " in y."
        if (visibility == 1):
            plotColor = 'b'
        elif (visibility == 2):
            plotColor = 'r'
        else:
            plotColor = 'k'
            
        pylab.plot(runList,riseList,plotColor,linewidth=2)

    # plot the line of sight
    pylab.plot([obsx,tgtx],[obsy,tgty],'k-')

    # titles & labels
    if (target_visible == True):
        pylab.title(msgIsVisible)
    else:
        pylab.title(msgIsNotVisible)
        
    pylab.ylabel("Elevation")
    pylab.xlabel("Distance")
    
    # graph lines
    pylab.grid(True)
    
    # display plot
    pylab.show()
    
    return


def LineIntersection2D(L1,L2):
    
    import numpy
    msgBadLineCoords = "Both input lines must contain only two points"
    Intersect = []
    try:
        if (len(L1) != 2 or len(L2 != 2)):
            raise Exception, msgBadLineCoords
        
        x1,y1 = L1[0],L1[1]
        x2,y2 = L1[2],L1[3]
        x3,y3 = L2[0],L2[1]
        x4,y4 = L2[2],L2[3]
        
        
        #outX1 = numpy.matrix([numpy.matrix([x1,y1],[x2,y2]),(x1 - x2)],[numpy.matrix([x1,x2],[x3,x4]),(x3 - x4)])
        #outX2 = numpy.matrix([(x1 - x2),(y1 - y2)],[(x3 - x4),(y3 - y4)])
        #outX = outX1 / outX2
        #
        #outY = numpy.matrix([numpy.matrix([x1,y1],[x2,y2]),(y1 - y2)],[numpy.matrix([x3,y3],[x4,y4]),(x3 - x4)]) / numpy.matrix([(x1 - x2),(y1 - y2)],[(x3 - x4),(y3 - y4)])
        #
        #Intersect.append(outX)
        #Intersect.append(outY)
        
    except Exception, ErrorMessage:
        print ErrorMessage
        
    return Intersect

#def SetZDomainOnSpatialRef(gp,dataset,zdomain,zunits):
#    
#    success = False
#    msgCouldNotDefine = "Internal Error: Could not define coordinate system:\n %s"
#    
#    try:
#        oldspatialref = gp.Describe(dataset).SpatialReference
#        newspatialref = gp.CreateObject("SpatialReference")
#        
#        
#        # All coordinate Systems
#        if (hasattr(newspatialref,'Type') == True):
#            newspatialref.Type = oldspatialref.Type
#        if (hasattr(newspatialref,'Name') == True):
#            newspatialref.Name = oldspatialref.Name
#        if (hasattr(newspatialref,'Abbreviation') == True):
#            newspatialref.Abbreviation = oldspatialref.Abbreviation
#        if (hasattr(newspatialref,'Remarks') == True):
#            newspatialref.Remarks = oldspatialref.Remarks
#        if (hasattr(newspatialref,'FactoryCode') == True):
#            newspatialref.FactoryCode = oldspatialref.FactoryCode
#        
#        #fails here :ERROR: attribute: HasMPrecision does not exist
#        if (hasattr(newspatialref,'HasMPrecision') == True):
#            oldHadMPrecision = oldspatialref.HasMPrecision
#            newspatialref.HasMPrecision = oldHasMPrecision
#        
#        if (hasattr(newspatialref,'HasXYPrecision') == True): newspatialref.HasXYPrecision = oldspatialref.HasXYPrecision
#        if (hasattr(newspatialref,'FalseOriginAndUnits') == True): newspatialref.FalseOriginAndUnits = oldspatialref.FalseOriginAndUnits
#        if (hasattr(newspatialref,'MFalseOriginAndUnits') == True): newspatialref.MFalseOriginAndUnits = oldspatialref.MFalseOriginAndUnits
#        if (hasattr(newspatialref,'Domain') == True): newspatialref.Domain = oldspatialref.Domain
#        if (hasattr(newspatialref,'MDomain') == True): newspatialref.MDomain = oldspatialref.MDomain
#        if (hasattr(newspatialref,'ZDomain') == True): newspatialref.ZDomain = zdomain #oldspatialref.ZDomain
#        if (hasattr(newspatialref,'HighPrecision') == True): newspatialref.HighPrecision = oldspatialref.HighPrecision
#        if (hasattr(newspatialref,'XYTolerance') == True): newspatialref.XYTolerance = oldspatialref.XYTolerance
#        if (hasattr(newspatialref,'MTolerance') == True): newspatialref.MTolerance = oldspatialref.MTolerance
#        if (hasattr(newspatialref,'ZTolerance') == True): newspatialref.ZTolerance = oldspatialref.ZTolerance
#        if (hasattr(newspatialref,'XYResolution') == True): newspatialref.XYResolution = oldspatialref.XYResolution
#        if (hasattr(newspatialref,'ZResolution') == True): newspatialref.ZResolution = oldspatialref.ZResolution
#        if (hasattr(newspatialref,'MResolution') == True): newspatialref.MResolution = oldspatialref.MResolution
#        if (hasattr(newspatialref,'Usage') == True): newspatialref.Usage = oldspatialref.Usage
#        if (hasattr(newspatialref,'FactoryCode') == True): newspatialref.FactoryCode = oldspatialref.FactoryCode
#        if (hasattr(newspatialref,'PCSName') == True): newspatialref.PCSName = oldspatialref.PCSName
#        if (hasattr(newspatialref,'PCSCode') == True): newspatialref.PCSCode = oldspatialref.PCSCode
#        if (hasattr(newspatialref,'GCSName') == True): newspatialref.GCSName = oldspatialref.GCSName
#        if (hasattr(newspatialref,'GCSCode') == True): newspatialref.GCSCode = oldspatialref.GCSCode
#        if (hasattr(newspatialref,'SpheroidName') == True): newspatialref.SpheroidName = oldspatialref.SpheroidName
#        if (hasattr(newspatialref,'SpheroidCode') == True): newspatialref.SpheroidCode = oldspatialref.SpheroidCode
#        if (hasattr(newspatialref,'ProjectionName') == True): newspatialref.ProjectionName = oldspatialref.ProjectionName
#        if (hasattr(newspatialref,'ProjectionCode') == True): newspatialref.ProjectionCode = oldspatialref.ProjectionCode
#        if (hasattr(newspatialref,'DatumName') == True): newspatialref.DatumName = oldspatialref.DatumName
#        if (hasattr(newspatialref,'DatumCode') == True): newspatialref.DatumCode = oldspatialref.DatumCode
#        if (hasattr(newspatialref,'PrimeMeridianName') == True): newspatialref.PrimeMeridianName = oldspatialref.PrimeMeridianName
#        if (hasattr(newspatialref,'PrimeMeridianCode') == True): newspatialref.PrimeMeridianCode = oldspatialref.PrimeMeridianCode
#        if (hasattr(newspatialref,'AngularUnitName') == True): newspatialref.AngularUnitName = oldspatialref.AngularUnitName
#        if (hasattr(newspatialref,'AngularUnitCode') == True): newspatialref.AngularUnitCode = oldspatialref.AngularUnitCode
#        if (hasattr(newspatialref,'LinearUnitName') == True): newspatialref.LinearUnitName = oldspatialref.LinearUnitName
#        if (hasattr(newspatialref,'LinearUnitCode') == True): newspatialref.LinearUnitCode = oldspatialref.LinearUnitCode
#        
#            # Projected Coordinate System only
#        if (oldspatialref.Type == "Projected"):
#            
#            if (hasattr(newspatialref,'CentralMeridian') == True): newspatialref.CentralMeridian = oldspatialref.CentralMeridian
#            if (hasattr(newspatialref,'CentralMeridianInDegrees') == True): newspatialref.CentralMeridianInDegrees = oldspatialref.CentralMeridianInDegrees
#            if (hasattr(newspatialref,'LongitudeOfOrigin') == True): newspatialref.LongitudeOfOrigin = oldspatialref.LongitudeOfOrigin
#            if (hasattr(newspatialref,'LatitudeOf1st') == True): newspatialref.LatitudeOf1st = oldspatialref.LatitudeOf1st
#            if (hasattr(newspatialref,'LatitudeOf2nd') == True): newspatialref.LatitudeOf2nd = oldspatialref.LatitudeOf2nd
#            if (hasattr(newspatialref,'FalseEasting') == True): newspatialref.FalseEasting = oldspatialref.FalseEasting
#            if (hasattr(newspatialref,'FalseNorthing') == True): newspatialref.FalseNorthing = oldspatialref.FalseNorthing
#            if (hasattr(newspatialref,'CentralParallel') == True): newspatialref.CentralParallel = oldspatialref.CentralParallel
#            if (hasattr(newspatialref,'StandardParallel1') == True): newspatialref.StandardParallel1 = oldspatialref.StandardParallel1
#            if (hasattr(newspatialref,'StandardParallel2') == True): newspatialref.StandardParallel2 = oldspatialref.StandardParallel2
#            if (hasattr(newspatialref,'LongitudeOf1st') == True): newspatialref.LongitudeOf1st = oldspatialref.LongitudeOf1st
#            if (hasattr(newspatialref,'LongitudeOf1st') == True): newspatialref.LongitudeOf2nd = oldspatialref.LongitudeOf2nd
#            if (hasattr(newspatialref,'ScaleFactor') == True): newspatialref.ScaleFactor = oldspatialref.ScaleFactor
#            if (hasattr(newspatialref,'Azimuth') == True): newspatialref.Azimuth = oldspatialref.Azimuth
#            if (hasattr(newspatialref,'Classification') == True): newspatialref.Classification = oldspatialref.Classification
#            
#            # Geographic Coordinate System only
#        else:
#            if (hasattr(newspatialref,'SemiMajorAxis') == True): newspatialref.SemiMajorAxis = oldspatialref.SemiMajorAxis
#            if (hasattr(newspatialref,'SemiMinorAxis') == True): newspatialref.SemiMinorAxis = oldspatialref.SemiMinorAxis
#            if (hasattr(newspatialref,'Flattening') == True): newspatialref.Flattening = oldspatialref.Flattening
#            if (hasattr(newspatialref,'Longitude') == True): newspatialref.Longitude = oldspatialref.Longitude
#            if (hasattr(newspatialref,'RadiansPerUnit') == True): newspatialref.RadiansPerUnit = oldspatialref.RadiansPerUnit
#        
#        
#        #define the dataset with the new spatial reference
#        try:
#            gp.defineprojection(dataset, newspatialref)
#        except:
#            gpmessages = gp.GetMessages()
#            raise Exception, msgCouldNotDefine % (gpmessages)
#
#        success = True
    #    
    #except Exception, ErrorMessage:
    #    success = False
    #    gp.AddError(str(ErrorMessage))
    #    print ErrorMessage
    #    
    #return success
    
    
def DatabaseType(gp, Input_Geodatabase):
    # returns geodatabase environment info for a workspace (Input_Geodatabase)
    type = gp.Describe(Input_Geodatabase).WorkspaceType # Known issue with PGDB
    return type

