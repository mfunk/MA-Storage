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
    
    # 0 - Input Surface
    # 1 - Output workspace
    # 2 - Output hillshade name
    # 3 - Clip Extent
    self.params[3].ParameterDependencies = [0]
    # 4 - Automatic Z-factor calc method
    self.params[4].Filter.Type = "ValueList"
    self.params[4].Filter.List = ["AUTO_CALC_Z","MANUAL_Z"]
    self.params[4].Value = "AUTO_CALC_Z"
    # 5 - Manual Z Factor
    self.params[5].Enabled = False
    self.params[5].Value = 1.0
    # 6 - Azimuth
    self.params[6].Filter.Type = "Range"
    self.params[6].Filter.List = [0.0,360.0]
    self.params[6].Value = 315.0
    # 7 - Altitude
    self.params[7].Filter.Type = "Range"
    self.params[7].Filter.List = [0.0,90.0]
    self.params[7].Value = 45.0
    # 8 - Shading Type
    self.params[8].Filter.Type = "ValueList"
    self.params[8].Filter.List = ["NO_SHADOWS","SHADOWS"]
    self.params[8].Value = "NO_SHADOWS"
    # 9 - Output Hillshade
    self.params[9].ParameterDependencies = [0]
    self.params[9].Schema.RasterRule = "Integer"
    self.params[9].Schema.CellSizeRule = "FirstDependency"
    self.params[9].Schema.ExtentRule = "AsSpecified"
    
    return

  def updateParameters(self):
    """Modify the values and properties of parameters before internal
    validation is performed.  This method is called whenever a parmater
    has been changed."""
    
    # Add extent based on input surface
    if (self.params[0].Altered == True and self.params[3].Altered == False):
      f = self.GP.Describe(self.params[0].Value).Extent
      ext = str(f.xmin) + " " + str(f.ymin) + " " + str(f.xmax) + " " + str(f.ymax)
      self.params[3].Value = ext
      #self.params[9].Schema.Extent = ext
    
    # Toggle auto/manual Z calculation
    if (self.params[4].Altered == True):
        if (self.params[4].Value == "MANUAL_Z"):
            self.params[5].Enabled = True
        else:
            self.params[5].Enabled = False
    
    return

  def updateMessages(self):
    """Modify the messages created by internal validation for each tool
    parameter.  This method is called after internal validation."""
    #import MAScriptUtils
    import os
    
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
            self.params[2].SetErrorMessage("An output raster with this name already exists in the workspace.")
            
    # check that z-factor is a positive number (greater than 0.0)
    if self.params[5].Altered == True:
        if self.params[5].Value < 0.0:
          self.params[5].SetErrorMessage("Z factor must be a positive number.")

    #Check that input surface is a raster dataset or raster catalog
    if (self.params[0].Altered):
        surf = self.params[0].Value
        surftype = self.GP.Describe(surf).DatasetType
        if (surftype != "RasterDataset" and surftype != "RasterCatalog"):
            self.params[0].SetErrorMessage("Input surface must be a raster dataset or raster catalog")
    
    #Check that extent (param 3) falls within extent of surface (param 0).
    if (self.params[0].Altered == True and self.params[3].Altered == True):
        extent = self.GP.Describe(self.params[0].Value).Extent
        surf_ext = [extent.xmin,extent.ymin,extent.xmax,extent.ymax]
        input_ext = str(self.params[3].Value).split(" ")
        #relation = MAScriptUtils.EnvelopeRelation(self.GP,surf_ext,input_ext)
        relation = self.EnvelopeRelation(self.GP,surf_ext,input_ext)
        if (relation == -1):
            self.params[3].SetErrorMessage("Specified extent does not fall inside of the extent of the input surface: Relation " + relation)
    
    return


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