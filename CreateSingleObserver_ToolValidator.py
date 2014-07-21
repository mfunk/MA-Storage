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
    
    # 0 - Output Workspace
    # 1 - Output Feature Name
    # 2 - X coordinate (longitude)
    # 3 - Y coordinate (latitude)
    # 4 - Z coordinate (elevation)
    # 5 - Observer offset (OFFSETA)
    # 6 - Terrain offset (OFFSETB)
    # 7 - Near distance (RADIUS1)
    # 8 - Far distance (RADIUS2
    # 9 - Left Azimuth (AZIMUTH1)
    # 10 - Right Azimuth (AZIMUTH2)
    # 11 - Top vertical angle (VERT1)
    # 12 - Bottom vertical angle (VERT2)
    # 13 - Spatial Reference
    # 14 - output point features
    
    
    #GETTING ERROR HERE, DOESN'T VALIDATE CORRECTLY, BUG?????
    #---------------------------
    #Testing get_ParameterInfo
    #---------------------------
    #initializeParameters Execution Error: Runtime error <type 'exceptions.AttributeError'>: 'NoneType' object has no attribute 'Type'
    #---------------------------
    #OK   
    #---------------------------
    #
    #
    #self.params[0].Filter.Type = "Workspace"
    #self.params[0].Filter.List = ["FileSystem", "LocalDatabase", "RemoteDatabase"]
    #

    
    self.params[5].Value = 2.0 # OFFSETA
    self.params[6].Value = 0.0 # OFFSETB
    
    self.params[7].Value = 0.0 # RADIUS1
    self.params[8].Value = 1000.0 # RADIUS2
    
    self.params[9].Filter.Type = "Range"  
    self.params[9].Filter.List = [0.0,360.0]
    self.params[9].Value = 0.0 # AZIMUTH1
    
    self.params[10].Filter.Type = "Range"
    self.params[10].Filter.List = [0.0,360.0]
    self.params[10].Value = 360.0 # AZIMUTH2
    
    self.params[11].Filter.Type = "Range"
    self.params[11].Filter.List = [-90.0,90.0]
    self.params[11].Value = 90.0 # VERT1
    
    self.params[12].Filter.Type = "Range"
    self.params[12].Filter.List = [-90.0,90.0]
    self.params[12].Value = -90.0 # VERT2

    # setting output parameter schema
    self.params[14].Schema.ExtentRule = "Union"
    self.params[14].Schema.FeatureTypeRule = "AsSpecified"
    self.params[14].Schema.FeatureType = "Simple"
    self.params[14].Schema.GeometryTypeRule = "AsSpecified"
    self.params[14].Schema.GeometryType = "Point"
    self.params[14].Schema.FieldsRule = "All" 
    #spot_field = self.makeField("SPOT", "DOUBLE", "8", "4", "12")
    offseta_field = self.makeField("OFFSETA", "DOUBLE", "8", "4", "12")
    offsetb_field = self.makeField("OFFSETB", "DOUBLE", "8", "4", "12")
    vert1_field = self.makeField("VERT1", "DOUBLE", "8", "4", "12")
    vert2_field = self.makeField("VERT2", "DOUBLE", "8", "4", "12")
    azimuth1_field = self.makeField("AZIMUTH1", "DOUBLE", "8", "4", "12")
    azimuth2_field = self.makeField("AZIMUTH2", "DOUBLE", "8", "4", "12")
    radius1_field = self.makeField("RADIUS1", "DOUBLE", "8", "4", "12")
    radius2_field = self.makeField("RADIUS2", "DOUBLE", "8", "4", "12")
    field_list = [offseta_field,offsetb_field,vert1_field,vert2_field,azimuth1_field,azimuth2_field,radius1_field,radius2_field]
    self.params[14].Schema.AdditionalFields = field_list

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
    # check that output does not exist.
    if self.params[0].Altered == True or self.params[1].Altered == True:
        workspace = str(self.params[0].Value)
        if (workspace == None or workspace == ""):
            return
        file = str(self.params[1].Value)
        if (file == None or file == ""):
            return
        outfile = os.path.join(workspace,file)
        outfileExists = self.GP.Exists(outfile)
        if outfileExists == True:
            self.params[1].SetErrorMessage("An output dataset with this name already exists in the workspace.")
    
    
    if (self.params[7].Altered):
        if (self.params[7].Value >= self.params[8].Value):
            self.params[7].SetErrorMessage("Near Distance (RADIUS1) must be less than the Far Distance (RADIUS2)")

    if (self.params[8].Altered):
        if (self.params[7].Value >= self.params[8].Value):
            self.params[8].SetErrorMessage("Far Distance (RADIUS2) must be greater than the Near Distance (RADIUS1)")
    
    if (self.params[9].Altered):
        if (self.params[9].Value >= self.params[10].Value):
            self.params[9].SetErrorMessage("Left Azimuth (AZIMUTH1) must be less than the Right Azimuth (AZIMUTH2).")
    
    if (self.params[10].Altered):
        if (self.params[9].Value >= self.params[10].Value):
            self.params[10].SetErrorMessage("Right Azimuth (AZIMUTH2) must be less than the Left Azimuth (AZIMUTH1)." )
    
    if (self.params[11].Altered):
        if (self.params[11].Value <= self.params[12].Value):
            self.params[11].SetErrorMessage("Top Vertical (VERT1) must be greater than Bottom Vertical (VERT2)")
    
    if (self.params[12].Altered):
        if (self.params[11].Value <= self.params[12].Value):
            self.params[12].SetErrorMessage("Bottom Vertical (VERT2) must be less than Top Vertical (VERT1)")
    
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