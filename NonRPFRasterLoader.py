##""********************************************************************************************************************
##TOOL NAME:   LoadDataMARasterCatalog
##SOURCE NAME: LoadDataMARasterCatalog.py
##VERSION: ArcGIS 9.2
##AUTHOR:  Environmental Systems Research Institute Inc.
##REQUIRED ARGUMENTS: Military Analyst Raster Catalog
##                    Input rasters
##OPTIONAL ARGUMENTS: Product - text (25 character max)
##                    Scale   - postive integer
##                    Series  - text (5 character max)
##                    Configuration keyword for enterprise geodatabase
##KNOWN LIMITATION:
##  Currently this script only works for SDE and File-based (FGDB) Geodatabases
##  If this script is run on an MA Raster Catalog in a Personal Geodatabase (PGDB/.mdb)
##  An exception "(esriSystem.AoInitialize.1) ArcObjects has not yet been initialized" occurs
##  
##TOOL DESCRIPTION: Copies one or more Rasters to a raster catalog, after the copy, it updates
##the raster catalog fields with the input provided (Scale, Product, etc.)
##
##The name of the output Raster will be based on the name of the input name, but will be unique 
##for the destination catalog.
##
##DATE: 11/30/2006
##
## mfunk - 12/17/2007 - update for 9.3 changes to GP
##
##Usage: LoadDataMARasterCatalog <Input_Catalog> <Input_Rasters;Input_Rasters...>
##            {Product} {Scale} {Series} {Configuration_Keyword}
##
## Parameters:    
## Display Name                       #Data Type      #Type     #Direction   #Multi Value  #Dependency
## Input_Catalog          argv [1]    Raster Catalog  Required  Input        No
## Input_Rasters          argv [2]    Raster Dataset  Required  Input        Yes
## Product                argv [3]    String          Optional  Input        No
## Scale                  argv [4]    Integer         Optional  Input        No
## Series                 argv [5]    String          Optional  Input        No
## Configuration Keyword  argv [6]    String          Optional  Input        No
##*********************************************************************************************************************"""

# Import system modules
import ConversionUtils, sys, string, os, arcgisscripting



# Error Messages
msgNotEnoughParams = "Incorrect number of input parameters."
msgNonExist="Output location does not exist: "
msgNotAnMACatalog  = "Provided catalog is not an MA Catalog (missing required fields)."
msgStringExceedMaximumLength = "String provided exceeds the maximum length for that field."
msgFail="Failed to set dataset properties."
msgDatasetNotGeographicUsingDefaultScale = "Input Raster Dataset Spatial Reference is not Geographic.  Can not perform automatic scale calculation.  Using Default="
msgCalculatedScaleIsOutOfBounds = "The calculated scale is out of bounds."
msgCouldNotCalculateScale="Could not auto-calculate Scale for image, using default=" 

# Set to True to Enable Script Debug Messages 
debug = False

# Constants
gp = ""

MAX_PRODUCT_STRING_LENGTH = 25
MAX_SERIES_STRING_LENGTH = 5

row = None
rows = None

useDefaultSeries  = False          
useDefaultProduct = False
useDefaultScale   = False

# ---------------------------------------
# Helper method: returns the number of records/rows in a dataset
def countTableRecords(inputTable, gp) :
    if debug : gp.AddMessage("Counting # of Features...")    
    inRows = gp.searchcursor(inputTable)
    
    inRow = inRows.next()
    recordCount = 0
    while inRow:
        recordCount = recordCount+1
        inRow = inRows.next()

    if debug : gp.AddMessage("Table: " + inputTable + " Feature count: " + str(recordCount))

    return recordCount;    

# ---------------------------------------
# Helper method: determines if a dataset has the require fields to be an MA Raster Catalog
def isValidRPFCatalog(inputTable, gp):
    # ensure required fields exist (they will be true if this is a true MA raster catalog)
    # mfunk 2/11/2008 - moved to ToolValidator
    isValidRPFCat = True
    checkfield1 = gp.ListFields(inputTable, "PRODUCT", "*")
    checkfield2 = gp.ListFields(inputTable, "SERIES", "*")
    checkfield3 = gp.ListFields(inputTable, "SCALE", "*")
    checkfield4 = gp.ListFields(inputTable, "FULL_NAME", "*")
    #if not (checkfield1.Next() and checkfield2.Next() and checkfield3.Next() and checkfield4.Next()) :
    if not (checkfield1[0] and checkfield2[0] and checkfield3[0] and checkfield4[0]) :
        isValidRPFCat = False

    if debug:
        fields = gp.ListFields(outputCatalog, "*", "*")
        #field = fields.Next()
        #while field:
        for field in fields:
            gp.AddMessage("Field Name: " + field.Name)            
            #field = fields.Next()

    return isValidRPFCat

# ---------------------------------------
# Helper method: Checks if dataset has spatial reference that is Geographic
def IsGeographicSR(dataset, gp):
    ## Check if dataset has spatial reference that is Geographic
    IsGeographic = False
    spatial_reference = gp.Describe(dataset).SpatialReference
    s_r_type = spatial_reference.Type
    if (s_r_type == "Geographic"):
        IsGeographic = True
    return IsGeographic
    
# ---------------------------------------
# Helper method: Checks if dataset has spatial reference that is Geographic WGS 1984
def IsGeographicWGS84SR(dataset, gp):
    ## Check if dataset has spatial reference that is Geographic WGS 1984
    IsGeographicWGS84 = False
    if (IsGeographicSR(dataset, gp)):
        spatial_reference = gp.Describe(dataset).SpatialReference
        datum_name = spatial_reference.DatumName
        if (datum_name == "D_WGS_1984"):
            IsGeographicWGS84 = True
    return IsGeographicWGS84

# ---------------------------------------
# Helper method: attempts to calculate the approximate scale for a raster image 
def getScaleFromRaster(inputRaster, gp):
    ## Automatic Image Scale Calculation (if possible)
    ## The method used in the original Avenue script:
    ## 1. Get the extent of the Image. (This would be in Geographic Decimal Degrees) (theExtent) 
    ## 2. Get the Number of Columns of the image (theCols) 
    ## 3. Divide the Number of Columns / The Width of the image. (This would give Pixels per DD) {theRes = theCols / theExtent.GetWidth} 
    ## 4. Get the approximate # of pixels per meter by dividing {theScale = 111120/theRes } 
    ## 5. Then logic was applied to guess to populate the scale value in the MA Catalog. 
    ## If theScale <= 5
    ## Then 
    ##     theScale = theScale.Round & "M"
    ## Else 
    ##      theScale = theScale * 5000
    ## If (theScale >= 1000000) Then 
    ##      theScale = "1:" + (theScale/1000000).Round & "M"  df
    defaultScale = 50001
    minPossibleScale = 100 # assumes image will never be smaller than 100m
    maxPossibleScale = 40000000 # the circumference of the earth in meters

    try:

        if not IsGeographicSR(inputRaster, gp) : 
            msgNotWGS84 = msgDatasetNotGeographicUsingDefaultScale + str(defaultScale)
            raise Exception, msgNotWGS84
                
        description = gp.describe(inputRaster)
                
        if debug : gp.AddMessage("Extent = " + description.Extent)

        minX = float(string.splitfields(description.Extent," ")[0])
        maxX = float(string.splitfields(description.Extent," ")[2])
        widthDecDegrees = abs(maxX - minX)
        
        if debug : gp.AddMessage("Width (Decimal Degrees) = " + str(widthDecDegrees))

        pixelsPerDecDegrees = description.Width / widthDecDegrees            
        if debug : gp.AddMessage("Pixels per Decimal Degrees = " + str(pixelsPerDecDegrees))

        pixelsPerMeter = 111120 / pixelsPerDecDegrees           
        if debug : gp.AddMessage("Pixels per Meter = " + str(pixelsPerMeter))

        theScale = round(pixelsPerMeter * 5000.0)
        
        if (pixelsPerMeter < 5) : theScale = round(pixelsPerMeter)                
        if debug : gp.AddMessage("Calculated Scale = " + str(theScale))

        nScale = long(theScale)

        # check the calculated scale for bogus values
        if (nScale < minPossibleScale) or (nScale > maxPossibleScale) :
            raise Exception, msgCalculatedScaleIsOutOfBounds                

        return nScale
    
    except Exception, ErrorDesc:
        # Except block if automatic scale calculation can not be performed
        # Just return the default Scale
        gp.AddWarning(msgCouldNotCalculateScale + str(defaultScale) + " Image=" + inputRaster);
        gp.AddWarning(str(ErrorDesc))                
        return defaultScale

# ---------------------------------------
# Main Script
try:

    # Validate number of parameters
    if len(sys.argv) < 2: raise Exception, msgNotEnoughParams


    gp = arcgisscripting.create(9.3)

    # Get parameter input provided    
    outputCatalog = gp.GetParameterAsText(0) #sys.argv[1]
    inputRasters = gp.GetParameterAsText(1) #sys.argv[2]
    product = gp.GetParameterAsText(2) #sys.argv[3]
    scale = gp.GetParameterAsText(3) #sys.argv[4]
    series = gp.GetParameterAsText(4) #sys.argv[5]
    configuration = gp.GetParameterAsText(5) #sys.argv[6]
    

    gp.toolbox = "conversion"

    if debug:
        gp.AddMessage(" " + "Tool Parameter Values:")        
        gp.AddMessage(" " + "OutputCatalog = " + outputCatalog)
        gp.AddMessage(" " + "Input Rasters = " + inputRasters)
        gp.AddMessage(" " + "Product = " + product)
        gp.AddMessage(" " + "Scale = " + scale)
        gp.AddMessage(" " + "Series = " + series)
        gp.AddMessage(" " + "Configuration Keyword = " + configuration)
    
    # mfunk 2/11/2008 - now handled in ToolValidator
    # Error trapping, in case the output workspace doesn't exist
    #if not ConversionUtils.gp.Exists(outputCatalog):
    #    #raise Exception, msgNonExist + " %s" % (outWorkspace)
    #    raise Exception, msgNonExist + " %s" % (outputCatalog)
    
    if debug:
        gp.AddMessage(" " + "Output workspace:")
        gp.AddMessage(" " + "Datatype = " + gp.describe(outputCatalog).DataType +
                      " CatalogPath = " + gp.describe(outputCatalog).CatalogPath)

    # mfunk 2/11/2008 - now handled in ToolValidator
    # Verify that it is a valid MA RFP Catalog or fail
    #if not isValidRPFCatalog(outputCatalog, gp):
    #    raise Exception, msgNotAnMACatalog
    
    # mfunk 2/11/2008 - now handled in ToolValidator
    # Verify max length is not exceeded
    #if product != None :  # should never be null, but just in case
    #    if len(product) > MAX_PRODUCT_STRING_LENGTH:
    #        gp.AddError("Product=" + product + " Len=" + str(len(product)) + ":Max=" + str(MAX_PRODUCT_STRING_LENGTH))
    #        raise Exception, msgStringExceedMaximumLength       
    #if series != None :   # should never be null, but just in case
    #    if len(series) > MAX_SERIES_STRING_LENGTH:
    #        gp.AddError("Series=" + series + " Len=" + str(len(series)) + ":Max=" + str(MAX_SERIES_STRING_LENGTH))
    #        raise Exception, msgStringExceedMaximumLength    


    if series == "#"  : useDefaultSeries  = True          
    if product == "#" : useDefaultProduct = True
    if scale == "#"   : useDefaultScale   = True

    # get the number of records in the dataset 
    startRecordCount = countTableRecords(outputCatalog, gp)
    if debug : gp.AddMessage(" " + "Start # of records = " + str(startRecordCount))

    # use existing GP Copy Rasters tool to import raster data
    try:
        # Example Call: gp.RasterToGeodatabase("Topo.sid" , "MyTest.gdb\TestMACat")
        gp.RasterToGeodatabase(inputRasters, outputCatalog, configuration)
    except:
        raise Exception, gp.GetMessages(2)
    

    # Argument 2 is the list of Rasters to be converted
    inRasters = ConversionUtils.gp.GetParameterAsText(1)
    # The list is split by semicolons ";"
    inRasters = string.split(inputRasters,";")

    endRecordCount = countTableRecords(outputCatalog, gp)
    if debug : gp.AddMessage(" " + "End # of records = " + str(endRecordCount))

    # Get an update cursor and forward the cursor to the start of the newly created records    
    rows = gp.UpdateCursor(outputCatalog)
    row = rows.next()
    recordCount = 0
    while row and (recordCount < startRecordCount):
        #if debug : 
        #    gp.AddMessage(" " + "Scanning for feature: " + str(recordCount) + ":"
        #                  + str(startRecordCount) + ":" + str(endRecordCount))
        #    
        #    gp.AddMessage(" " + str(row.GetValue("ObjectID")) + ":" +
        #                  row.GetValue("NAME") + ":" + str(row.GetValue("FULL_NAME")))
            
        recordCount = recordCount + 1
        row = rows.next()

    if debug: gp.AddMessage(" " + "Getting individual rasters...")
     
    # Loop through the list of input Rasters 
    for inRaster in inRasters:
        raster = inRaster
        try:           
            description = gp.describe(raster)
            raster = ConversionUtils.ValidateInputRaster(raster)

            gp.AddMessage(" " + "Processing Raster Name=" + raster)
            if debug :                 
                gp.AddMessage(" " + "Raster CatalogPath = " + description.CatalogPath)
                gp.AddMessage(" " + "Raster Format = " + description.Format)        

            # get values for optional parameters if nothing supplied
            if useDefaultSeries  : series = "MISC"            
            if useDefaultProduct : product = description.Format
            if useDefaultScale   : scale = getScaleFromRaster(raster, gp)

            if debug : gp.AddMessage(" " + "Setting Row Values")


            # Set row attributes
            row.SetValue("SERIES", series)
            row.SetValue("SCALE", long(scale))
            row.SetValue("FULL_NAME", description.CatalogPath)
            row.SetValue("PRODUCT", series + "$" + product)
            
            if debug : gp.AddMessage(" " + "Updating Row")    
            rows.UpdateRow(row)

            row = rows.next()
            recordCount = recordCount + 1

        except Exception, ErrorDesc:
            # Except block for the loop. If the tool fails to convert one of the Rasters, it will come into this block
            # and add warnings to the messages, then proceed to attempt to convert the next input Raster.
            WarningMessage = (msgFail + " %s" % (raster))

            if ConversionUtils.gp.GetMessages(2) != "":
                WarningMessage = WarningMessage + ". " + (ConversionUtils.gp.GetMessages(2))
            elif ErrorDesc != "":
                WarningMessage = WarningMessage + (str(ErrorDesc))

            # Add the message as a warning.
            ConversionUtils.gp.AddWarning(WarningMessage)
            
    # unlock table and cursor
    del row, rows
    
    # set output parameter
    gp.SetParameter(6,outputCatalog)
    
    
except Exception, ErrorDesc:
    # Except block if the tool could not run at all.
    #  For example, not all parameters are provided, or if other unexpected error
    gp.AddError(" " + str(ErrorDesc))
    print str(ErrorDesc)
    # unlock table and cursor
    if row:
        del row
    if rows:
        del rows

del gp
