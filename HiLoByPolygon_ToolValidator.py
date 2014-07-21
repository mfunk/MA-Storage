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
    
    # 0 - Input polygons
    # 1 - Input surface
    # 2 - Output workspace
    # 3 - Output feature class
    # 4 - Highest point/Lowest point
    # 5 - Analysis grouping
    # 6 - Zone analaysis field
    # 7 - output feature class
    
    self.params[0].Filter.List = ["POLYGON"]
    
    self.params[4].Filter.Type = "ValueList"
    self.params[4].Filter.List = ["HIGHEST","LOWEST"]
    self.params[4].Value = "HIGHEST"
    
    self.params[5].Filter.Type = "ValueList"
    self.params[5].Filter.List = ["REGION","ZONE"]
    self.params[5].Value = "REGION"
    
    self.params[6].Enabled = False #disabled for "REGION"
    self.params[6].ParameterDependencies = [0] #depends on input polys
    
    self.params[7].ParameterDependencies = [0]
    self.params[7].Schema.ExtentRule = "FirstDependency"
    self.params[7].Schema.GeometryTypeRule = "AsSpecified"
    self.params[7].Schema.GeometryType = "POINT"
    gridcode_field = self.makeField("GRID_CODE","DOUBLE","10","0","10")
    self.params[7].Schema.AdditionalFields = gridcode_field
    
    return

  def updateParameters(self):
    """Modify the values and properties of parameters before internal
    validation is performed.  This method is called whenever a parmater
    has been changed."""
    
    # update zone analysis field based on grouping type
    if (self.params[5].Altered):
        if (self.params[5].Value == "ZONE"):
            self.params[6].Enabled = True
        else:
            self.params[6].Enabled = False

    return

  def updateMessages(self):
    """Modify the messages created by internal validation for each tool
    parameter.  This method is called after internal validation."""
    #import MAScriptUtils
    import os
    
    #Check that input surface is a raster dataset or raster catalog
    if (self.params[1].Altered):
        surf = self.params[1].Value
        surftype = self.GP.Describe(surf).DatasetType
        if (surftype != "RasterDataset" and surftype != "RasterCatalog"):
            self.params[1].SetErrorMessage("Input surface must be a raster dataset or raster catalog")
            
    #Check Spatial reference of input Polygon and input Surface
    if (self.params[0].Altered == True and self.params[1].Altered == True):
      poly_desc = self.GP.Describe(self.params[0].Value)
      poly_sr = poly_desc.spatialreference
      surf_desc = self.GP.Describe(self.params[1].Value)
      surf_sr = surf_desc.spatialreference
      if (poly_sr.Name.upper() != surf_sr.Name.upper()):
        self.params[1].SetErrorMessage("Coordinate system between polygons and surface do not match.\nThe coordinate systems must be exactly the same.")
        
        
    
    #Check that polygon extent (param 1) falls within extent of surface (param 1).
    if (self.params[0].Altered == True and self.params[1].Altered == True):
        poly_ext = self.GP.Describe(self.params[0].Value).Extent
        poly_ext = [poly_ext.Xmin,poly_ext.Ymin,poly_ext.Xmax,poly_ext.Ymax]
        surf_ext = self.GP.Describe(self.params[1].Value).Extent
        surf_ext = [surf_ext.Xmin,surf_ext.Ymin,surf_ext.Xmax,surf_ext.Ymax]

        #relation = MAScriptUtils.EnvelopeRelation(self.GP,surf_ext,poly_ext)
        relation = self.EnvelopeRelation(self.GP,surf_ext,poly_ext)
        if (relation == -1):
            self.params[1].SetError("Specified extent does not fall inside of the extent of the input surface: Relation" + relation)
    
    # check that output does not exist.
    if self.params[2].Altered == True or self.params[3].Altered == True:
      workspace = str(self.params[2].Value)
      if (workspace == None or workspace == ""):
        return
      file = str(self.params[3].Value)
      if (file == None or file == ""):
        return
      outfile = os.path.join(workspace,file)
      outfileExists = self.GP.Exists(outfile)
      if outfileExists == True:
        self.params[3].SetErrorMessage("An output dataset with this name already exists in the workspace.")

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
  
  
  def EnvelopeRelation(self,gp,A,B):

    # A[Left,Bottom,Right,Top]
    # B[Left,Bottom,Right,Top]
    L1,B1,R1,T1 = float(A[0]),float(A[1]),float(A[2]),float(A[3])
    L2,B2,R2,T2 = float(B[0]),float(B[1]),float(B[2]),float(B[3])

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
  