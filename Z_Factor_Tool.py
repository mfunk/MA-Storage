
#
# Z Factor Tool
#
# Calculates the z-factor conversion for geographic datasets.
#

import os, sys, string, math, decimal
import arcgisscripting

# create geoprocessor
gp = arcgisscripting.create(9.3)

msgBadExtent = "Input dataset %s has bad extent values. A z-factor could not be determined."
msgNotGeographic = "%s is not in a Geographic Coordinate System."
msgResult = "Calculated Z-Factor: %s"

dataset = gp.GetParameterAsText(0)
#dataset = sys.argv[1]
#dataset = "c:\\workspace\\lobwizard_TableToGeodesyLine.shp"

#Space delimited string (XMin YMin XMax YMax).
extent = gp.Describe(dataset).Extent

#Check that dataset is geographic
spatial_reference = gp.Describe(dataset).SpatialReference
s_r_type = spatial_reference.Type

try:
    # check that dataset is geographic
    if (s_r_type != "Geographic"):
        raise Exception, msgNotGeographic % (dataset)
    else:
        pass
        
    #get the top and bottom
    extent_split = [extent.xmin,extent.ymin,extent.xmax,extent.ymax]
    
    # check that the extent is valid
    bExtOK = True
    for splst in extent_split:
        if (splst == '1.#QNAN'):
            bExtOK = False
    if (bExtOK == False):
        raise Exception, msgBadExtent % (dataset)
    
    top = float(extent_split[3])
    bottom = float(extent_split[1])
    
    #find the mid-latitude of the dataset
    if (top > bottom):
        height = (top - bottom)
        mid = (height/2) + bottom
    elif (top < bottom):
        height = bottom - top
        mid = (height/2) + top
    else: # top == bottom
        mid = top

    # convert degrees to radians
    mid = math.radians(mid)

    #
    # function:
    # Z-Factor = 1.0/(111320 * cos(mid-latitude in radians))
    decimal.getcontext().prec = 28
    decimal.getcontext().rounding = decimal.ROUND_UP
    a = decimal.Decimal("1.0")
    b = decimal.Decimal("111320.0")
    c = decimal.Decimal(str(math.cos(mid)))
    zfactor = a/(b * c)
    zfactor = "%06f" % (zfactor.__abs__())
    
    gp.SetParameterAsText(1,str(zfactor))

    # return Z factor message
    print msgResult % (str(zfactor))
    gp.addmessage(msgResult % (str(zfactor)))

except Exception, ErrorMessage:
    print ErrorMessage
    gp.adderror(str(ErrorMessage))
    
del gp
