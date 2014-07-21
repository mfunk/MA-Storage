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
    
    # 0 - Input catalog
    # 1 - Input rasters (multiple)
    # 2 - Product
    # 3 - Scale
    # 4 - Series
    # 5 - Configuration Keyword
    # 6 - Output catalog
    self.params[6].ParameterDependencies = [0]
    self.params[6].Schema.Clone = True
    self.params[6].Schema.FieldsRule = "All"
    
    return

  def updateParameters(self):
    """Modify the values and properties of parameters before internal
    validation is performed.  This method is called whenever a parmater
    has been changed."""
    
    return

  def updateMessages(self):
    """Modify the messages created by internal validation for each tool
    parameter.  This method is called after internal validation."""
    
    # check that the catalog is a valid RPF catalog
    if (self.params[0].Altered == True):
        gp = self.GP
        input_catalog = str(self.params[0].Value)
        isValidRPF = self.ValidRPFCatalog(input_catalog)
        if (isValidRPF == False):
            self.GP.params[0].SetErrorMessage("Input catalog is not a valid Military Analyst RPF catalog.")
    
    # check string lengths
    if (self.params[2].Altered == True):
        if (len(self.params[2].Value) > 25):
            self.params[2].SetErrorMessage("Product string exceeds maximum length of 25 characters.")
    if (self.params[4].Altered == True):
        if (len(self.params[4].Value) > 5):
            self.params[4].SetErrorMessage("Series string exceeds maximum length of 5 characters.")
    
    return
  
  def ValidRPFCatalog(self,inputTable):
    # ensure required fields exist (they will be true if this is a true MA raster catalog)
    isValidRPFCat = True
    checkfield1 = self.GP.ListFields(inputTable, "PRODUCT", "*")
    checkfield2 = self.GP.ListFields(inputTable, "SERIES", "*")
    checkfield3 = self.GP.ListFields(inputTable, "SCALE", "*")
    checkfield4 = self.GP.ListFields(inputTable, "FULL_NAME", "*")
    #if not (checkfield1.Next() and checkfield2.Next() and checkfield3.Next() and checkfield4.Next()) :
    if not (checkfield1[0] and checkfield2[0] and checkfield3[0] and checkfield4[0]):
        isValidRPFCat = False
        
    return isValidRPFCat
  
  