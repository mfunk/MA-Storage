#!/usr/bin/env python
class ToolValidator:
  """Class for validating a tool's parameter values and controlling
  the behavior of the tool's dialog."""

  def __init__(self):
    """Setup the Geoprocessor and the list of tool parameters."""
    import arcgisscripting as ARC
    self.GP = ARC.create(9.3)
    self.params = self.GP.getparameterinfo()

  def initializeParameters(self):
    """Refine the properties of a tool's parameters.  This method is
    called when the tool is opened."""
    
    # 0 - Observer X
    # 1 - Observer Y
    # 2 - Observer offset
    # 3 - Target X
    # 4 - Target Y
    # 5 - Target offset
    # 6 - Input surface
    # 7 - Surface elevation units
    self.params[7].Filter.Type = "ValueList"
    self.params[7].Filter.List = ["METERS","FEET","US SURVEY FEET","KILOMETERS","MILES","NAUTICAL MILES"]
    self.params[7].Value = "METERS"
    # 8 - Output workspace
    # 9 - Output line of sight name
    # 10 - Output obstruction name
    # 11 - Spatial Reference

    # 12 - Output Linear Line of Sight
    VisCode_field = self.makeField("VisCode", "LONG", "8", "8", "12")
    SourceOID_field = self.makeField("SourceOID", "LONG", "8", "8", "12")
    TarIsVis_field = self.makeField("TarIsVis", "SHORT", "4", "4", "8")
    self.params[12].Schema.FeatureTypeRule = "AsSpecified"
    self.params[12].Schema.FeatureType = "Simple"
    self.params[12].Schema.GeometryTypeRule = "AsSpecified"
    self.params[12].Schema.GeometryType = "Polyline"
    self.params[12].Schema.FieldsRule = "All"
    self.params[12].Schema.AdditionalFields = [VisCode_field,SourceOID_field,TarIsVis_field]
    # 13 - Output obstructions
    self.params[13].Schema.FeatureTypeRule = "AsSpecified"
    self.params[13].Schema.FeatureType = "Simple"
    self.params[13].Schema.GeometryTypeRule = "AsSpecified"
    self.params[13].Schema.GeometryType = "Point"
    self.params[13].Schema.FieldsRule = "All"
    self.params[13].Schema.AdditionalFields = [SourceOID_field]
    # 14 - Output Target is visible (boolean)
    
    return

  def updateParameters(self):
    """Modify the values and properties of parameters before internal
    validation is performed.  This method is called whenever a parmater
    has been changed."""
    return

  def updateMessages(self):
    """Modify the messages created by internal validation for each tool
    parameter.  This method is called after internal validation."""
    #import MAScriptUtils
    import os
    
    # surface must be a raster catalog or raster dataset
    if (self.params[6].Altered):
        surf = self.params[6].Value
        surftype = self.GP.Describe(surf).DatasetType
        if (surftype != "RasterDataset" and surftype != "RasterCatalog"):
            self.params[6].SetErrorMessage("Input surface must be a raster dataset or raster catalog")
    
    # check spatial ref of surface is same as inputs
    if self.params[6].Altered == True:
      surf_sr_name = self.GP.Describe(self.params[6].Value).SpatialReference.Name
      sr_name = self.params[11].Value.Name
      if (surf_sr_name != sr_name):
        self.params[6].SetErrorMessage("Spatial Reference of input surface does not match Spatial Reference of input values.")
    
    # check input coordinates are within the surface extent
    if self.params[6].Altered == True:
      extent = self.GP.Describe(self.params[6].Value).Extent
      envelope = [extent.xmin,extent.ymin,extent.xmax,extent.ymax]
      # check observer
      if (self.params[0].Altered == True or self.params[1].Altered == True):
        if (self.params[0].Value != "" and self.params[1].Value != ""):
          obsX = self.params[0].Value
          obsY = self.params[1].Value
          #observer_contained = MAScriptUtils.envelopeContainsPoint(envelope,obsX,obsY)
          observer_contained = self.envelopeContainsPoint(envelope,obsX,obsY)
          if (observer_contained == False):
            msg = "Observer point coordinates do not fall within the extent of the input surface."
            self.params[0].SetErrorMessage(msg)
            self.params[1].SetErrorMessage(msg)
            
      # check target
      if (self.params[3].Altered == True or self.params[4].Altered == True):
        if (self.params[3].Value != "" and self.params[4].Value != ""):
          tgtX = self.params[3].Value
          tgtY = self.params[4].Value
          #target_contained = MAScriptUtils.envelopeContainsPoint(envelope,tgtX,tgtY)
          target_contained = self.envelopeContainsPoint(envelope,tgtX,tgtY)
          if (target_contained == False):
            msg = "Target point coordinates do not fall within the extent of the input surface."
            self.params[3].SetErrorMessage(msg)
            self.params[4].SetErrorMessage(msg)
      
    # check outputs do not exist
    if self.params[8].Altered == True or self.params[9].Altered == True: 
      workspace = str(self.params[8].Value)
      if (workspace == None or workspace == ""):
        return
      los = str(self.params[9].Value)
      if (los == None or los == ""):
        return
      losfile = os.path.join(workspace,los)
      losfileExists = self.GP.Exists(losfile)
      if losfileExists == True:
        self.params[9].SetErrorMessage("An output dataset with this name already exists in the workspace.")
    
    if self.params[8].Altered == True or self.params[10].Altered == True: 
      workspace = str(self.params[8].Value)
      if (workspace == None or workspace == ""):
        return
      oxt = str(self.params[10].Value)
      if (oxt == None or oxt == ""):
        return
      oxtfile = os.path.join(workspace,oxt)
      oxtfileExists = self.GP.Exists(oxtfile)
      if oxtfileExists == True:
        self.params[10].SetErrorMessage("An output dataset with this name already exists in the workspace.")
    
    return

  def makeField(self,field_name,field_type,field_precision,field_scale,field_length):
    """ take inputs and return a field type """
    
    new_field = self.GP.CreateObject("field")
    new_field.Name = field_name
    new_field.Type = field_type
    new_field.Precision = field_precision
    new_field.Scale = field_scale
    new_field.Length = field_length
    new_field.IsNullable = True
    
    return new_field

  def envelopeContainsPoint(self,envelope, pointX, pointY):
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
  