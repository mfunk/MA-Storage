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
    
    # Parameters:
    # 0 - Input path (Featureclass)
    # 1 - Input surface (Dataset)
    # 2 - Output Workspace (Workspace)
    # 3 - Output name (String)
    # 4 - output FC (DERIVED: Featureclass)
    #
    self.params[0].Filter.List = ["POLYLINE"]
    
    self.params[4].Schema.ExtentRule = "Union"
    self.params[4].Schema.FeatureTypeRule = "AsSpecified"
    self.params[4].Schema.FeatureType = "Simple"
    self.params[4].Schema.GeometryTypeRule = "AsSpecified"
    self.params[4].Schema.GeometryType = "Polyline"
    self.params[4].Schema.FieldsRule = "All"
    # need to add fields:
    code_field = self.makeField("ATT_CODE", "TEXT", "#", "#", "5")
    val_field = self.makeField("ATT_VAL", "TEXT", "#", "#", "5")
    desc_field = self.makeField("ATT_DESC", "TEXT", "#", "#", "5")
    field_list = [code_field,val_field,desc_field]
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
    #import MAScriptUtils
    import os
    
    #Check that input surface is a raster dataset or raster catalog
    if (self.params[1].Altered):
        surf = self.params[1].Value
        surftype = self.GP.Describe(surf).DatasetType
        if (surftype != "RasterDataset" and surftype != "RasterCatalog"):
            self.params[1].SetErrorMessage("Input surface must be a raster dataset or raster catalog")
    
    # compare input path to input surface
    if (self.params[0].Altered == True and self.params[1].Altered == True):
        
        slope_ext = self.GP.Describe(self.params[0].Value).Extent
        slope_ext = [slope_ext.xmin,slope_ext.ymin,slope_ext.xmax,slope_ext.ymax]
        slope_spref_name = self.GP.Describe(self.params[0].Value).SpatialReference.Name
        
        surf_ext = self.GP.Describe(self.params[1].Value).Extent
        surf_ext = [surf_ext.xmin,surf_ext.ymin,surf_ext.xmax,surf_ext.ymax]
        surf_spref_name = self.GP.Describe(self.params[1].Value).SpatialReference.Name
        # check that inputs have same coordinate system
        if (slope_spref_name.upper() != surf_spref_name.upper()):
            self.params[1].SetErrorMessage(r"Spatial references between the input path polyline and input surface must be the same.")
        #Check that extent (param 0) falls within extent of surface (param 1).
        #relation = MAScriptUtils.EnvelopeRelation(self.GP,slope_ext,surf_ext)
        relation = self.EnvelopeRelation(self.GP,slope_ext,surf_ext)
        if (relation != 0):
            self.params[1].SetErrorMessage(r"Input path polyline extent does not fall inside of the extent of the input surface (Relation " + str(relation) + ")") 
    
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