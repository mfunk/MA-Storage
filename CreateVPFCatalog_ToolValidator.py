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
    
    # 0 - Input Geodatabase
    #self.params[0].Filter.Type = "Workspace"
    self.params[0].Filter.List = ["LocalDatabase","RemoteDatabase"]
    # 1 - Catalog Name
    # 2 - Output VPF Catalog
    self.params[2].Schema.FeatureTypeRule = "AsSpecified"
    self.params[2].Schema.FeatureType = "Simple"
    self.params[2].Schema.GeometryTypeRule = "AsSpecified"
    self.params[2].Schema.GeometryType = "Polygon"
    self.params[2].Schema.FieldsRule = "All"
    product_field = self.makeField("PRODUCT", "TEXT", "#", "#", "25")
    library_field = self.makeField("LIBRARY","TEXT","#","#","20")
    scale_field = self.makeField("SCALE","LONG","#","#","#")
    tile_id_field = self.makeField("TILE_ID","LONG","#","#","#")
    field_list = [product_field,library_field,scale_field,tile_id_field]
    self.params[2].Schema.AdditionalFields = field_list
        
    return

  def updateParameters(self):
    """Modify the values and properties of parameters before internal
    validation is performed.  This method is called whenever a parmater
    has been changed."""
    
    return

  def updateMessages(self):
    """Modify the messages created by internal validation for each tool
    parameter.  This method is called after internal validation."""
    import os
    # Check that feature class does not exist
    if (self.params[0].Altered == True or self.params[1].Altered == True):
        if (self.params[0].Value != "" or self.params[0].Value != None):
            if (self.params[1].Value != "" or self.params[1].Value != None):
                workspace = str(self.params[0].Value)
                file = str(self.params[1].Value)
                cat_path = os.path.join(workspace,file)
                if (self.GP.Exists(cat_path) == True):
                    self.params[1].SetErrorMessage("Dataset with this name already exists.")
    
    # check that associated table does not exist
    if (self.params[0].Altered == True or self.params[1].Altered == True):
        if (self.params[0].Value != "" or self.params[0].Value != None):
            if (self.params[1].Value != "" or self.params[1].Value != None):
                workspace = str(self.params[0].Value)
                file = str(self.params[1].Value) + "_features"
                cat_path = os.path.join(workspace,file)
                if (self.GP.Exists(cat_path) == True):
                    self.params[1].SetErrorMessage("Dataset with this name already exists.")
    
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