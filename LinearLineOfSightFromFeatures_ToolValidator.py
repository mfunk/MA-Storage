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
    
    # 0 - Observer points
    self.params[0].Filter.List = ["Point"]
    # 1 - Target points
    self.params[1].Filter.List = ["Point"]
    # 2 - Input surface
    # 3 - Output workspace
    # 4 - Output LOS name
    # 5 - Output obstructions name
    # 6 - Match method (ALL | MATCH)
    self.params[6].Filter.Type = "ValueList"
    self.params[6].Filter.List = ["ALL","MATCH"]
    self.params[6].Value = "ALL"
    
    # 7 - Output LOS FC
    VisCode_field = self.makeField("VisCode", "LONG", "8", "8", "12")
    SourceOID_field = self.makeField("SourceOID", "LONG", "8", "8", "12")
    TarIsVis_field = self.makeField("TarIsVis", "SHORT", "4", "4", "8")
    self.params[7].Schema.FeatureTypeRule = "AsSpecified"
    self.params[7].Schema.FeatureType = "Simple"
    self.params[7].Schema.GeometryTypeRule = "AsSpecified"
    self.params[7].Schema.GeometryType = "Polyline"
    self.params[7].Schema.FieldsRule = "All"
    self.params[7].Schema.AdditionalFields = [VisCode_field,SourceOID_field,TarIsVis_field]

    # 8 - Output OXT FC
    self.params[8].Schema.FeatureTypeRule = "AsSpecified"
    self.params[8].Schema.FeatureType = "Simple"
    self.params[8].Schema.GeometryTypeRule = "AsSpecified"
    self.params[8].Schema.GeometryType = "Point"
    self.params[8].Schema.FieldsRule = "All"
    self.params[8].Schema.AdditionalFields = [SourceOID_field]
    
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
    
    # check if observer and targets have desired fields, if not give warning (not error)
    if (self.params[0].Altered == True):
        #missingfields1 = MAScriptUtils.CheckObserverFields(self.GP,self.params[0].Value)
        missingfields1 = self.CheckObserverFields(self.GP,self.params[0].Value)
        if (len(missingfields1) != 0):
            msg = "Observers do not contain all LOS modifier fields. The following fields are not present:" + str(missingfields1)
            self.params[0].SetWarningMessage(msg)

    if (self.params[1].Altered == True):
        #missingfields2 = MAScriptUtils.CheckObserverFields(self.GP,self.params[1].Value)
        missingfields2 = self.CheckObserverFields(self.GP,self.params[1].Value)
        if (len(missingfields2) != 0):
            msg = "Targets do not contain all visibility modifier fields. The following fields are not present:" + str(missingfields2)
            self.params[1].SetWarningMessage(msg)

    # check observers and surface have same extent, same spatial ref
    if (self.params[0].Altered == True and self.params[2].Altered == True):
        observer_ext = self.GP.Describe(self.params[0].Value).Extent
        observer_ext = [observer_ext.xmin,observer_ext.ymin,observer_ext.xmax,observer_ext.ymax]
        observer_spref_name = self.GP.Describe(self.params[0].Value).SpatialReference.Name
        
        surf_ext = self.GP.Describe(self.params[2].Value).Extent
        surf_ext = [surf_ext.xmin,surf_ext.ymin,surf_ext.xmax,surf_ext.ymax]
        surf_spref_name = self.GP.Describe(self.params[2].Value).SpatialReference.Name
        
        # check that inputs have same coordinate system
        if (observer_spref_name.upper() != surf_spref_name.upper()):
            self.params[0].SetErrorMessage("Spatial references between the input observers and input surface must be the same.")
        
        #relation = MAScriptUtils.EnvelopeRelation(self.GP,observer_ext,surf_ext)
        relation = self.EnvelopeRelation(self.GP,observer_ext,surf_ext)
        if (relation != 0):
            self.params[0].SetErrorMessage("Input observer extent does not fall inside of the extent of the input surface: Relation" + str(relation)) 
        
    # check targets and surface have same extent, same spatial ref
    if (self.params[1].Altered == True and self.params[2].Altered == True):
        target_ext = self.GP.Describe(self.params[1].Value).Extent
        target_ext = [target_ext.xmin,target_ext.ymin,target_ext.xmax,target_ext.ymax]
        target_spref_name = self.GP.Describe(self.params[1].Value).SpatialReference.Name
        
        surf_ext = self.GP.Describe(self.params[2].Value).Extent
        surf_ext = [surf_ext.xmin,surf_ext.ymin,surf_ext.xmax,surf_ext.ymax]
        surf_spref_name = self.GP.Describe(self.params[2].Value).SpatialReference.Name
      
        if (target_spref_name.upper() != surf_spref_name.upper()):
              self.params[1].SetErrorMessage("Spatial references between the input targets and input surface must be the same.")
              
        #relation2 = MAScriptUtils.EnvelopeRelation(self.GP,observer_ext,surf_ext)
        relation2 = self.EnvelopeRelation(self.GP,target_ext,surf_ext)
        if (relation2 != 0):
            self.params[1].SetErrorMessage("Input target extent does not fall inside of the extent of the input surface: Relation" + str(relation))
    
    # check that input surface is a raster dataset or raster catalog
    if (self.params[2].Altered):
        surf = self.params[2].Value
        surftype = self.GP.Describe(surf).DatasetType
        if (surftype != "RasterDataset" and surftype != "RasterCatalog"):
            self.params[2].SetErrorMessage("Input surface must be a raster dataset or raster catalog")
    
    # check that output line of sight does not exist
    if self.params[3].Altered == True or self.params[4].Altered == True: 
        workspace = str(self.params[3].Value)
        if (workspace == None or workspace == ""):
            return
        los = str(self.params[4].Value)
        if (los == None or los == ""):
            return
        losfile = os.path.join(workspace,los)
        losfileExists = self.GP.Exists(losfile)
        if losfileExists == True:
            self.params[4].SetErrorMessage("An output dataset with this name already exists in the workspace.")
    
    # check that output obstructions do not exist
    if self.params[3].Altered == True or self.params[5].Altered == True: 
        workspace = str(self.params[3].Value)
        if (workspace == None or workspace == ""):
            return
        oxt = str(self.params[5].Value)
        if (oxt == None or oxt == ""):
            return
        oxtfile = os.path.join(workspace,oxt)
        oxtfileExists = self.GP.Exists(oxtfile)
        if oxtfileExists == True:
            self.params[5].SetErrorMessage("An output dataset with this name already exists in the workspace.")
    
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
  
  def CheckObserverFields (self,gp,dataset):
    msgNoDataset = "Dataset %s does not exist."
    missingfields = []
    #checkfields = ["SPOT","OFFSETA","OFFSETB","VERT1","VERT2","AZIMUTH1","AZIMUTH2","RADIUS1","RADIUS2"]
    checkfields = ["OFFSETA","OFFSETB","VERT1","VERT2","AZIMUTH1","AZIMUTH2","RADIUS1","RADIUS2"]
    try:
      # check that dataset exists
      #if (gp.Exists(dataset) == False):
      #  raise Exception, msgNoDataset % (str(dataset))
      #
      # get list of fields in dataset
      fieldnamelist = []
      #desc = gp.Describe(dataset)
      fields = gp.ListFields(dataset)
  
      #field = fields.next()
      for field in fields:
      #while field:
          fieldname = field.Name
          fieldnamelist.append(fieldname)
          #field = fields.next()
          
      #print fieldnamelist
      for check in checkfields:
          if not (check in fieldnamelist):
              missingfields.append(str(check))
              
      
  
    except Exception, ErrorMessage:
      #print ErrorMessage
      #missingfields = str(ErrorMessage)
      pass
      
    return missingfields
      

  def CheckExists(self,gp,dataset):
      exists = gp.exists(dataset)
      if (exists == 0 or exists == "False" or exists == False):
          return False
      else:
          return True
 
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