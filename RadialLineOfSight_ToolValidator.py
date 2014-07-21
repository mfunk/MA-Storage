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
    
    # 0 - Input observers
    # 1 - Input surface
    # 2 - Output workspace
    # 3 - Output basename
    # 4 - Radial distance units
    # 5 - Output observers
    # 6 - Output Visiblity
    
    self.params[0].Filter.List = ["POINT"]
    #ERROR
    #self.params[2].Filter.List = ["FileSystem","LocalDatabase","RemoteDatabase"]
    
    self.params[4].Filter.List = ["METERS","FEET","KILOMETERS","US_SURVEY_FEET","MILES","NAUTICAL_MILES"]
    self.params[4].Value = "METERS"
    
    self.params[5].Schema.FeatureTypeRule = "AsSpecified"
    self.params[5].Schema.FeatureType = "Simple"
    self.params[5].Schema.GeometryTypeRule = "AsSpecified"
    self.params[5].Schema.GeometryType = "Point"
    
    self.params[6].Schema.FeatureTypeRule = "AsSpecified"
    self.params[6].Schema.FeatureType = "Simple"
    self.params[6].Schema.GeometryTypeRule = "AsSpecified"
    self.params[6].Schema.GeometryType = "Polygon"
    gridcode_field = self.makeField("GRID_CODE","DOUBLE","10","0","10")
    self.params[6].Schema.FieldsRule = "All"
    self.params[6].Schema.AdditionalFields = gridcode_field
    
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
    
    # Check that the input surface is a raster dataset or raster catalog
    if (self.params[1].Altered):
        surftype = self.GP.Describe(self.params[1].Value).DatasetType
        if (surftype != "RasterDataset" and surftype != "RasterCatalog"):
            self.params[1].SetErrorMessage("Input surface must be a raster dataset or raster catalog")

    # check observers have the visibility modifier fields            
    if (self.params[0].Altered == True):
        #missingfields1 = MAScriptUtils.CheckObserverFields(self.GP,self.params[0].Value)
        missingfields1 = self.CheckObserverFields(self.GP,self.params[0].Value)
        if (len(missingfields1) != 0):
            msg = r"Observers do not contain all visibility modifier fields. The following fields are not present:" + str(missingfields1)
            self.params[0].SetWarningMessage(" " + msg)
        else:
          pass

    # check that output does not exist
    if (self.params[2].Altered == True or self.params[3].Altered == True):
        if (str(self.params[2].Value) != "" or str(self.params[3].Value) != ""):
            obs_file = str(self.params[2].Value) + os.sep + str(self.params[3].Value) + "_obs"
            vis_file = str(self.params[2].Value) + os.sep + str(self.params[3].Value) + "_vis"
            if (self.GP.Exists(vis_file) == True):
                self.params[3].SetErrorMessage("Visibility dataset already exists: " + vis_file)
            if (self.GP.Exists(obs_file) == True):
                self.params[3].SetErrorMessage("Projected observer dataset already exists: " + obs_file)
                
    # check that observer extent is within surface extent
    if (self.params[0].Altered == True and self.params[1].Altered == True):
        obs_ext = self.GP.Describe(self.params[0].Value).Extent
        observer_ext = [obs_ext.Xmin,obs_ext.Ymin,obs_ext.Xmax,obs_ext.Ymax]
        surf_ext = self.GP.Describe(self.params[1].Value).Extent
        surface_ext = [surf_ext.Xmin,surf_ext.Ymin,surf_ext.Xmax,surf_ext.Ymax]
        #relation = MAScriptUtils.EnvelopeRelation(self.GP,observer_ext,surf_ext)
        #relation = self.EnvelopeRelation(self.GP,observer_ext,surf_ext)
        relation = self.EnvelopeRelation(self.GP,observer_ext,surface_ext)
        if (relation != 0):
          msg = r"Observer extent does not fall inside of the extent of the input surface: Relation" + str(relation)
          self.params[0].SetErrorMessage(msg) 
    
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
  
  def CheckObserverFields (self,gp,dataset):
    missingfields = []
    #checkfields = ["SPOT","OFFSETA","OFFSETB","VERT1","VERT2","AZIMUTH1","AZIMUTH2","RADIUS1","RADIUS2"]
    checkfields = ["OFFSETA","OFFSETB","VERT1","VERT2","AZIMUTH1","AZIMUTH2","RADIUS1","RADIUS2"]
    fieldnamelist = []
    
    ## get list of fields in the dataset
    # ERROR: ListFields throws and ERROR 999999 for some reason
    #fields = gp.ListFields(dataset,"*","ALL")
    fields = gp.Describe(dataset).Fields
    
    for field in fields:
        fieldname = field.Name
        fieldnamelist.append(fieldname)
    # which fields is it missing?
    for check in checkfields:
        if not (check in fieldnamelist):
            missingfields.append(str(check))
    # return list of the missing fields
    return missingfields
    


      
      