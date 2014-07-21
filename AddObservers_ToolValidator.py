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
    
    self.params[0].Filter.List = ["Point","Polyline"]
    
    self.params[1].ParameterDependencies = [0]
    self.params[1].Schema.Clone = True
    spot_field = self.makeField("SPOT", "DOUBLE", "8", "4", "12")
    offseta_field = self.makeField("OFFSETA", "DOUBLE", "8", "4", "12")
    offsetb_field = self.makeField("OFFSETB", "DOUBLE", "8", "4", "12")
    vert1_field = self.makeField("VERT1", "DOUBLE", "8", "4", "12")
    vert2_field = self.makeField("VERT2", "DOUBLE", "8", "4", "12")
    azimuth1_field = self.makeField("AZIMUTH1", "DOUBLE", "8", "4", "12")
    azimuth2_field = self.makeField("AZIMUTH2", "DOUBLE", "8", "4", "12")
    radius1_field = self.makeField("RADIUS1", "DOUBLE", "8", "4", "12")
    radius2_field = self.makeField("RADIUS2", "DOUBLE", "8", "4", "12")
    field_list = [spot_field,offseta_field,offsetb_field,vert1_field,vert2_field,azimuth1_field,azimuth2_field,radius1_field,radius2_field]
    self.params[1].Schema.AdditionalFields = field_list
    
    return

  def updateParameters(self):
    """Modify the values and properties of parameters before internal
    validation is performed.  This method is called whenever a parmater
    has been changed."""
    return

  def updateMessages(self):
    """Modify the messages created by internal validation for each tool
    parameter.  This method is called after internal validation."""
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