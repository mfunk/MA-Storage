#!/usr/bin/env python


# ----------------------------------------------------------------
#   CreateDTEDCatalog_ma
# ----------------------------------------------------------------

# Run_CreateDTEDCatalog.py
# Description:
#   Creates an MA DTED Catalog
# Requirements: None
# Author: ESRI
# Date: July 31, 2007

# Import system modules
import arcgisscripting

# Create the Geoprocessor object
gp = arcgisscripting.create()

# Input variables
Input_Geodatabase = "C:\Workspace\Test\Hawaii_Data.mdb"
DTED_Catalog_Name = "Hawaii_DTED"

try:
    # Create the catalog
    gp.CreateDTEDCatalog(Input_Geodatabase,DTED_Catalog_Name)

except:
    # If an error occurred while running a tool, then print the messages.
    print gp.GetMessages()
    
    
# ----------------------------------------------------------------
#   CreateRPFCatalog
# ----------------------------------------------------------------

# Run_CreateRPFCatalog.py
# Description:
#   Creates an MA RPF Catalog
# Requirements: None
# Author: ESRI
# Date: July 31, 2007

# Import system modules
import arcgisscripting

# Create the Geoprocessor object
gp = arcgisscripting.create()

# Input variables
Input_Geodatabase = "C:\Workspace\Test\Hawaii_Data.mdb"
RPF_Catalog_Name = "Hawaii_RPF"

try:
    # Create the catalog
    gp.CreateRPFCatalog(Input_Geodatabase,RPF_Catalog_Name)

except:
    # If an error occurred while running a tool, then print the messages.
    print gp.GetMessages()
    
# ----------------------------------------------------------------
#   CreateVPFCatalog
# ----------------------------------------------------------------

# Run_CreateVPFCatalog.py
# Description:
#   Creates an MA VPF Catalog
# Requirements: None
# Author: ESRI
# Date: July 31, 2007

# Import system modules
import arcgisscripting

# Create the Geoprocessor object
gp = arcgisscripting.create()

 # Input variables
Input_Geodatabase = "C:\Workspace\Test\Hawaii_Data.mdb"
VPF_Catalog_Name = "Hawaii_Vector"

try:
    # Create the catalog
    gp.CreateVPFCatalog(Input_Geodatabase,VPF_Catalog_Name)

except:
    # If an error occurred while running a tool, then print the messages.
    print gp.GetMessages()

# ----------------------------------------------------------------
#   LoadMaCatalog
# ----------------------------------------------------------------

# Run_LoadMACatalog.py
# Description:
# Loads DTED data into an MA DTED Catalog
# Author: ESRI
# Date: July 31, 2007

# Import system modules
import arcgisscripting

# Create the Geoprocessor object
gp = arcgisscripting.create()

# Input variables
Input_Catalog = "C:\\Workspace\\Test\\Hawaii_Data.mdb\\Hawaii_DTED"
Input_Folder =  "E:\\dted"


try:
    # Load the catalog
    gp.LoadMaCatalog_ma(Input_Catalog, Input_Folder)

except:
    # If an error occurred while running a tool, then print the messages.
    print gp.GetMessages()

# ----------------------------------------------------------------
#   TableToEllipse
# ----------------------------------------------------------------

# Run_TableToEllipse.py
# Description:
# Creates elliptical polygons from input table
# Author: ESRI
# Date: July 31, 2007

# Import system modules
import sys, string, os
import arcgisscripting

# Create the Geoprocessor object
gp = arcgisscripting.create()

# Load required toolboxes...

# Local variables...
NewEllipses = "C:\\Testing\\Source\\GeometryImporters\\GeoImportOutput\\GeoImportOutput.mdb\\NewEllipses"
ellipses_txt = "C:\\Testing\\Source\\GeometryImporters\\GeoImportTestData\\ellipses.txt"

try:
    #Table To Ellipse...
    gp.TableToEllipse_ma(ellipses_txt, NewEllipses, "DMS 2 Field", "Lat", "Lon", "The_major_", "Minor", "Miles", "Full", "Orient", "Degrees","#", "#", "Date;Time;Cep")
except:
    # trap any errors
    print gp.GetMessages()



# ----------------------------------------------------------------
#   TableToGeodesyLine
# ----------------------------------------------------------------

# Run_TableToGeodesyLine.py
# Description:
# Creates Geodesic lines from input table
# Author: ESRI
# Date: July 31, 2007

# Import system modules
import sys, string, os
import arcgisscripting
# Create the Geoprocessor ArcObject
gp = arcgisscripting.create()

# Set variables
outputGeodesic = r"C:\Testing\Source\GeometryImporters\GeoImportOutput\GeodesicLine_txt_P.shp"
inputLob_xls = r"C:\Testing\Source\GeometryImporters\GeoImportTestData\lob.txt"

try:
    # Table to GeodesyLine
    gp.TableToGeodesyLine_ma(inputLob_xls, outputGeodesic, "Decimal Degrees", "Latd","Lond", "Distance", "Kilometers", "Azimuth", "Degrees", "Geodesic", "#", "#", "Lat;Lon;Date;Time")
except:
    # trap any errors
    gp.GetMessages()



# ----------------------------------------------------------------
#   TableToLine
# ----------------------------------------------------------------

# Run_TableToLine.py
# Description:
# Creates 2-point lines from input table
# Author: ESRI
# Date: July 31, 2007
# Import system modules
import sys, string, os
import arcgisscripting

# Create the Geoprocessor ArcObject
gp = arcgisscripting.create()

# Overwrite output
gp.OverwriteOutput = 1

# Set variables
outputLine = r"C:\Testing\Source\GeometryImporters\GeoImportOutput\line_txt_P.shp"
inputLine_txt = r"C:\Testing\Source\GeometryImporters\GeoImportTestData\line.txt"


try:
    # Table to Line
    gp.TableToLine_ma(inputLine_txt, outputLine,"DMS 2 Field", "Lat", "Lon", "Lat2", "Lon2", "true", "#", "Freq;MGRS;UTM")
except:
    # If an error occurred while running a tool, then print the messages.
    print gp.GetMessages()


# ----------------------------------------------------------------
#   TableToPolygon
# ----------------------------------------------------------------

# Run_TableToPolygon.py
# Description:
# Creates polygons from input table
# Author: ESRI
# Date: July 31, 2007

# Import system modules
import sys, string, os
import arcgisscripting

# Create the Geoprocessor ArcObject
gp = arcgisscripting.create()

# Set the Workspace
gp.Workspace = r"C:\Testing\Source\GeometryImporters"

# Overwrite output
gp.OverwriteOutput = 1

# Set variables
outputPolygon = r"\GeoImportOutput\Polygon_csv_P.shp"
inputPolygon_csv = r"\GeoImportTestData\line.csv"

try:
    # table to polygon
    gp.TableToPolygon_ma(inputPolygon_csv, outputPolygon, "DMS 2 Field", "Lat", "Lon", "Id", "vertsort", "#", "#")
except:
    # trap any errors
    print gp.GetMessages()

# ----------------------------------------------------------------
#   TableToPolyline
# ----------------------------------------------------------------

# Run_TableToPolyline.py
# Description:
# Creates polylines from input table
# Author: ESRI
# Date: July 31, 2007

# Import system modules
import sys, string, os
import arcgisscripting

# Create the Geoprocessor ArcObject
gp = arcgisscripting.create()

# Set variables
outputPolyline = r"C:\Testing\Source\GeometryImporters\GeoImportOutput\Polyline_xls_P.shp"
inputLine_txt = r"C:\Testing\Source\GeometryImporters\GeoImportTestData\line.xls\database"

try:
    # table to polyline
    gp.TableToPolyline(inputLine_txt, outputPolyline, "Decimal Degrees", "Latd", "Lond", "Id", "sort", "#", "#")
except:
    # trap any errors
    print gp.GetMessages()



# ----------------------------------------------------------------
#   TableToPoint
# ----------------------------------------------------------------

# Run_TableToPoint.py
# Description:
# Creates points from input table
# Author: ESRI
# Date: July 31, 2007

# Import system modules
import sys, string, os
import arcgisscripting

# Create the Geoprocessor ArcObject
gp = arcgisscripting.create()

# Set variables
outputPoint = r"C:\Testing\Source\GeometryImporters\GeoImportOutput\CityPoints.shp"
inputTable_xls = r"C:\Testing\Source\GeometryImporters\GeoImportTestData\line.xls\database"

try:
    # table to point
    gp.TableToPoint(inputTable_xls, outputPoint, "Decimal Degrees", "Latd", "Lond", "FALSE","FALSE","Freq;Time;Date")
except:
    # trap any errors
    print gp.GetMessages()


# ----------------------------------------------------------------
#   NonRPFRasterLoader
# ----------------------------------------------------------------

# Run_NonRPFRasterLoader.py
# Description:
# Adds Non-RPF rasters to an existing RPF Catalog
# Author: ESRI
# Date: July 31, 2007

# Import system modules
import sys, string, os
import arcgisscripting

# Create the Geoprocessor ArcObject
gp = arcgisscripting.create()

# Set variables
input_catalog = r"C:\Workspace\Hawaii\hawaii.gdb\hawii_rpf_catalog"
input_rasters = r"C:\Workspace\HawaiiDRG\n1.tif;C:\Workspace\HawaiiDRG\n2.tif;C:\Workspace\HawaiiDRG\n3.tif"

try:
    gp.NonRPFRasterLoader(input_catalog,input_rasters,"USGS 24K DRG",24000,"DRG","#")
except:
    # trap any errors
    print gp.GetMessages()


# ----------------------------------------------------------------
#   ExtractMACatalog
# ----------------------------------------------------------------


# Run_ExtractMACatalog.py
# Description:
# Extracts a specified area from an existing MA Catalog
# Author: ESRI
# Date: July 31, 2007

# Import system modules
import arcgisscripting

# Create the Geoprocessor object
gp = arcgisscripting.create()

# Input variables
Input_Catalog = "C:\\DATA\\Catalogs\\World.gdb\\World_DTED"
Output_Catalog = "C:\\DATA\\Catalogs\\Asia.gdb\\Himalayas_DTED"

try:
    # Extract the area of interest
    gp.ExtractRPF(Input_Catalog, 85.05, 29.96, 87.93, 27.08, Output_Catalog, "INTERSECTS")

except:
    # If an error occurred while running a tool, then print the messages.
    print gp.GetMessages()

# ----------------------------------------------------------------
#   CADRGExporter
# ----------------------------------------------------------------

# Run_RasterToCADRG.py
# Description:
# Converts a valid raster file to CADRG format
# Author: ESRI
# Date: July 31, 2007

# Import system modules
import arcgisscripting

# Create the Geoprocessor object
gp = arcgisscripting.create()

# Input variables
Input_Raster = "C:\\DATA\\Raster\\sample.tif"
Output_Folder = "C:\\DATA\\CADRG"

try:
    # Convert the raster file
    gp.RasterToCADRG(Input_Raster, Output_Folder, "50K", "false", "true")

except:
    # If an error occurred while running a tool, then print the messages.
    print gp.GetMessages()
    
    

# ----------------------------------------------------------------
#   ECRGExporter
# ----------------------------------------------------------------

# Run_RasterToECRG.py
# Description:
# Converts a valid raster file to ECRG format
# Author: ESRI
# Date: July 31, 2007

# Import system modules
import arcgisscripting

# Create the Geoprocessor object
gp = arcgisscripting.create()

# Input variables
Input_Raster = "C:\\DATA\\Raster\\sample.tif"
Output_Folder = "C:\\DATA\\ECRG"

try:
    # Convert the raster file
    gp.RasterToECRG(Input_Raster, Output_Folder, "100K")

except:
    # If an error occurred while running a tool, then print the messages.
    print gp.GetMessages()
    

# ----------------------------------------------------------------
#   AddObserverFields
# ----------------------------------------------------------------

# Run_AddObserverFields.py
# Description:
# Adds observer fields to an existing point or polyline
# Author: ESRI
# Date: July 31, 2007

# Import system modules
import sys, string, os
import arcgisscripting

# Create the Geoprocessor ArcObject
gp = arcgisscripting.create()

# Set variables
input_features = r"C:\Workspace\Current\ImportFeatures.gdb\HilltopImport_points"

try:
    # Add Observer Fields
    gp.AddObserverFields_ma(input_features)
except:
    # trap any errors
    print gp.GetMessages()


# ----------------------------------------------------------------
#   CreateObserversFromTable
# ----------------------------------------------------------------

# Run_CreateObserversFromTable.py
# Description:
# Creates observer point features from input table
# Author: ESRI
# Date: July 31, 2007

# Import system modules
import sys, string, os
import arcgisscripting

# Create the Geoprocessor ArcObject
gp = arcgisscripting.create()

# Set variables
input_table = r"C:\Workspace\Current\ImportFeatures.gdb\fieldObservers"
output_workspace = r"C:\Workspace\Current\ImportFeatures.gdb"

try:
    # create observsers
    gp.CreateObservers(input_table,output_workspace,"FieldObserverPts","#")
except:
    # trap errors
    print gp.GetMessages()


# ----------------------------------------------------------------
#   CreateSingleObserver
# ----------------------------------------------------------------

# Run_CreateSingleObserver.py
# Description:
# Creates single observer point
# Author: ESRI
# Date: July 31, 2007

# Import system modules
import sys, string, os
import arcgisscripting

# Create the Geoprocessor ArcObject
gp = arcgisscripting.create()

# Set variables
output_workspace = r"C:\Workspace\Current\ImportFeatures.gdb"

try:
    # create single observer
    gp.CreateSingleObserver_ma(output_workspace,"FieldHQ","12.4182553","48.245536","1523.448","10","0","0","10000","45","135","90","-90","#")
except:
    # trap errors
    print gp.GetMessages()


# ----------------------------------------------------------------
#   HiLoByExtent
# ----------------------------------------------------------------

# Run_HiLoByExtent.py
# Description:
# Finds highest or lowest point within an extent
# Author: ESRI
# Date: July 31, 2007

# Import system modules
import sys, string, os
import arcgisscripting

# Create the Geoprocessor ArcObject
gp = arcgisscripting.create()

# Set variables
input_surface = r"C:\Workspace\Current\OpsTheater.gdb\DTED_Catalog"
output_workspace = r"C:\Workspace\Current\ImportFeatures.gdb"
aoi = r"-155.671 19.367 -155.572 19.479"

try:
    # Highest point by extent
    gp.HiLoByExtent_ma(input_surface,aoi,output_workspace,"HiPoint","HIGHEST")
except:
    # trap errors
    print gp.GetMessages()


# ----------------------------------------------------------------
#   HiLoByPolygon
# ----------------------------------------------------------------

# Run_HiLoByPolygon.py
# Description:
# Finds highest point within each zone, by the zone's ID
# Author: ESRI
# Date: July 31, 2007

# Import system modules
import sys, string, os
import arcgisscripting

# Create the Geoprocessor ArcObject
gp = arcgisscripting.create()

# Set variables
input_polys = r"C:\Workspace\Current\ImportFeatures.gdb\ActionZones"
input_surface = r"C:\Workspace\Current\OpsTheater.gdb\DTED_Catalog"
output_workspace = r"C:\Workspace\Current\ImportFeatures.gdb"

try:
    # highest by poly
    gp.HiLoByPolygon_ma(input_polys,input_surface,output_workspace,"ActionObs","HIGHEST","ZONE","ZoneID")
except:
    # trap errors
    print gp.GetMessages()



# ----------------------------------------------------------------
#   Hillshade_ma
# ----------------------------------------------------------------

# Run_Hillshade_ma.py
# Description:
# Hillshades DTED Catalog to an extent
# Author: ESRI
# Date: July 31, 2007

# Import system modules
import sys, string, os
import arcgisscripting

# Create the Geoprocessor ArcObject
gp = arcgisscripting.create()

# Set variables
input_surface = r"C:\Workspace\Current\OpsTheater.gdb\DTED_Catalog"
output_workspace = r"C:\Workspace\Current\ImportFeatures.gdb"
aoi = r"-155.671 19.367 -155.572 19.479"

try:
    # hillshade
    gp.Hillshade_ma(input_surface,output_workspace,"AOIHillshade",aoi,"AUTO_CALC_Z","#","#","#","NO_SHADOWS")
except: 
    # trap errors
    print gp.GetMessages()


# ----------------------------------------------------------------
#   LinearLineOfSight
# ----------------------------------------------------------------

# Run_LinearLineOfSight.py
# Description:
# Does a line of sight between observer and target
# Author: ESRI
# Date: July 31, 2007

# Import system modules
import sys, string, os
import arcgisscripting

# Create the Geoprocessor ArcObject
gp = arcgisscripting.create()

# Set variables
input_surface = r"C:\Workspace\Current\OpsTheater.gdb\DTED_Catalog"
output_workspace = r"C:\Workspace\Current\ImportFeatures.gdb"

try:
    # LLOS
    gp.LinearLineOfSight_ma("12.4182553","48.245536","10","12.2597731","48.9110002","2",input_surface,"METERS",output_workspace,"LLOS","LOS_OXT","#","FALSE")
except:
    # trap errors
    print gp.GetMessages()

# ----------------------------------------------------------------
#   LinearLineOfSightFromFeatures
# ----------------------------------------------------------------

# Run_LinearLineOfSightFromFeatures.py
# Description:
# Match LOS between observers
# Author: ESRI
# Date: July 31, 2007

# Import system modules
import sys, string, os
import arcgisscripting

# Create the Geoprocessor ArcObject
gp = arcgisscripting.create()

# Set variables
input_surface = r"C:\Workspace\Current\OpsTheater.gdb\DTED_Catalog"
output_workspace = r"C:\Workspace\Current\ImportFeatures.gdb"
observers = output_workspace + os.sep + "FieldObserverPts"
targets = output_workspace + os.sep + "FieldObserverPts"

try:
    # find LOS between observers
    gp.LinesrLineOfSightFromFeatures_ma(observers,targets,input_surface,output_workspace,"ObsLLOS","ObsOxt","ALL")
except:
    # trap errors
    print gp.GetMessages()

# ----------------------------------------------------------------
#   PathSlope
# ----------------------------------------------------------------

# Run_PathSlope.py
# Description:
# Calculates slope along roadways
# Author: ESRI
# Date: July 31, 2007

# Import system modules
import sys, string, os
import arcgisscripting

# Create the Geoprocessor ArcObject
gp = arcgisscripting.create()

# Set variables
input_path = r"C:\Workspace\Current\OpsTheater.gdb\RoadAdv"
input_surface = r"C:\Workspace\Current\OpsTheater.gdb\DTED_Catalog"
output_workspace = r"C:\Workspace\Current\ImportFeatures.gdb"

try:
    # path slope
    gp.PathSlope_ma(input_path,input_surface,output_workspace,"RoadAdvSlope")
except:
    # trap errors
    print gp.GetMessages()


# ----------------------------------------------------------------
#   RadialLineOfSight
# ----------------------------------------------------------------

# Run_RadialLineOfSight.py
# Description:
# visibility from an observer location
# Author: ESRI
# Date: July 31, 2007

# Import system modules
import sys, string, os
import arcgisscripting

# Create the Geoprocessor ArcObject
gp = arcgisscripting.create()

# Set variables
input_surface = r"C:\Workspace\Current\OpsTheater.gdb\DTED_Catalog"
output_workspace = r"C:\Workspace\Current\ImportFeatures.gdb"
observer = r"C:\Workspace\Current\ImportFeatures.gdb\FieldHQ"

try:
    # RLOS
    gp.RadialLineOfSight_ma(observer,input_surface,output_workspace,"thea722","METERS")
except:
    # trap errors
    print gp.GetMessages()

# ----------------------------------------------------------------
#   Z-factorTool
# ----------------------------------------------------------------

# Run_ZFactorTool.py
# Description:
# Find z-factor conversion for RoadAdv features
# Author: ESRI
# Date: July 31, 2007

# Import system modules
import sys, string, os
import arcgisscripting

# Create the Geoprocessor ArcObject
gp = arcgisscripting.create()

try:
    # z-factor tool
    gp.ZFactorTool_ma(r"C:\Workspace\Current\OpsTheater.gdb\RoadAdv")
except:
    # trap errors
    print gp.GetMessages()


# ----------------------------------------------------------------
#   CreateLinks
# ----------------------------------------------------------------

# Run_CreateLinks.py
# Description:
# create link features between points by name
# Author: ESRI
# Date: July 31, 2007

# Import system modules
import sys, string, os
import arcgisscripting

# Create the Geoprocessor ArcObject
gp = arcgisscripting.create()

# Set variables
input_points = r"C:\Workspace\Current\ImportFeatures.gdb\FieldHQ"
connections = r"C:\Workspace\Current\ImportFeatures.gdb\CommLinksTable"
output_workspace = r"C:\Workspace\Current\ImportFeatures.gdb"

try:
    # create links
    gp.CreateLinks_ma(input_points,"HQName",connections,"FromName","ToName","Date;Time;Freq;Bandwith",output_workspace,"HQLinks")
except:
    # trap errors
    print gp.GetMessages()

# ----------------------------------------------------------------
#   RecalculateLinks
# ----------------------------------------------------------------

# Run_RecalculateLinks.py
# Description:
# Update links 
# Author: ESRI
# Date: July 31, 2007

# Import system modules
import sys, string, os
import arcgisscripting

# Create the Geoprocessor ArcObject
gp = arcgisscripting.create()

# Set variables
input_links = r"C:\Workspace\Current\ImportFeatures.gdb\HQLinks"
input_points = r"C:\Workspace\Current\ImportFeatures.gdb\FieldHQ"

try:
    # update links
    gp.RecalculateLinks_ma(input_links,"FromName","ToName",input_points,"HQName")
except:
    # trap errors
    print gp.GetMessages()


# ----------------------------------------------------------------
#   ConvertCoordinatesInFile
# ----------------------------------------------------------------

# Run_RecalculateLinks.py
# Description:
# Update links 
# Author: ESRI
# Date: July 31, 2007

# Import system modules
import sys, string, os
import arcgisscripting

# Create the Geoprocessor ArcObject
gp = arcgisscripting.create()

# Set variables
input_table = r"C:\Testing\Source\GeometryImporters\GeoImportTestData\lob.txt"
geoWGS84 = r"""GEOGCS["GCS_WGS_1984",DATUM["D_WGS_1984",SPHEROID["WGS_1984",6378137,298.257223563]],PRIMEM["Greenwich",0],UNIT["Degree",0.017453292519943295]]"""
output_workspace = r"C:\Testing\Source\GeometryImporters\GeoImportTestData"
xfer_fields = r"Date;Time;Freq"

try:
    # coordinate conversion
    gp.ConvertCoordinatesInFile_ma(input_table,"FALSE","FALSE","MGRS","MGR","#",
        geoWGS84,geoWGS84,"#",output_workspace,"lob_conv.dbf","FALSE","UTM","#","#",xfer_fields)
except:
    # trap errors
    print gp.GetMessages()


# ----------------------------------------------------------------
#   <tool_name>
# ----------------------------------------------------------------


# ----------------------------------------------------------------
#   <tool_name>
# ----------------------------------------------------------------


# ----------------------------------------------------------------
#   <tool_name>
# ----------------------------------------------------------------

