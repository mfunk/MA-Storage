class ToolValidator:
  """Class for validating a tool's parameter values and controlling
  the behavior of the tool's dialog."""

  def __init__(self):
    """Setup the Geoprocessor and the list of tool parameters."""
    import arcgisscripting as ARC
    import os
    self.os = os
    self.GP = ARC.create(9.3)
    self.params = self.GP.getparameterinfo()

  def initializeParameters(self):
    """Refine the properties of a tool's parameters.  This method is
    called when the tool is opened."""
    # 0 - input table
    # 1 - output workspace
    # 2 - featureclass name
    # 3 - spatial reference
    # setting output parameter schema
    self.params[4].Schema.ExtentRule = "Union"
    self.params[4].Schema.FeatureTypeRule = "AsSpecified"
    self.params[4].Schema.FeatureType = "Simple"
    self.params[4].Schema.GeometryTypeRule = "AsSpecified"
    self.params[4].Schema.GeometryType = "Point"
    self.params[4].Schema.FieldsRule = "All" 
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
    self.params[4].Schema.AdditionalFields = field_list
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
    #import MAScriptUtils
    
    # check that input table contains correct fields
    if self.params[0].Altered == True:
      input_table = str(self.params[0].Value)
      #missing_fields = MAScriptUtils.CheckMissingObserverFields(self.GP,input_table)
      missing_fields = self.CheckMissingObserverFields(self.GP,input_table)
      if (len(missing_fields) != 0):
        #missing = MAScriptUtils.ListToString(missing_fields)
        missing = "Input table is missing field(s): " + self.ListToString(missing_fields)
        self.params[0].SetErrorMessage(missing)
    
    # check that output does not exist.
    if self.params[1].Altered == True or self.params[2].Altered == True:
      workspace = str(self.params[1].Value)
      if (workspace == None or workspace == ""):
        return
      file = str(self.params[2].Value)
      if (file == None or file == ""):
        return
      outfile = os.path.join(workspace,file)
      outfileExists = self.GP.Exists(outfile)
      if outfileExists == True:
        self.params[2].SetErrorMessage("An output dataset with this name already exists in the workspace.")
        
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
  
  def CheckMissingObserverFields(self,gp,input_table):
    #X,Y,SPOT,OFFSETA,OFFSETB,VERT1,VERT2,AZIMUTH1,AZIMUTH2,RADIUS1,RADIUS2
    
    # check for missing fields
    field_names = self.GetFieldNames(gp,input_table)
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
  
  def ListToString(self,inList):
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
  
  def GetFieldNames(self,gp,input_table):
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