#!/usr/bin/env python
# -*- coding: latin-1 -*-

#
# Observer.py
#
# Military Analyst Observer class
#
#

import os, sys, arcgisscripting, time, MAScriptUtils
debug = False
class Observer:
    #x,y,z,offsetA,offsetB,radius1,radius2,azimuth1,azimuth2,vert1,vert2,sr
    def __init__(self,gp):
        # populate with default values
        self.X = 0.0
        self.Y = 0.0
        self.Z = None
        self.OffsetA = 0.0
        self.OffsetB = 0.0
        self.Radius1 = 0.0
        self.Radius2 = 1000.0
        self.Azimuth1 = 0.0
        self.Azimuth2 = 360.0
        self.Vert1 = 90.0
        self.Vert2 = -90.0
        self.SpatialReference = MAScriptUtils.SetGeographicWGS84(gp)
    
    # set and return individual properties
    def SetX (self,X):
        self.X = X
    def GetX (self):
        return self.X
    def SetY (self,Y):
        self.Y = Y
    def GetY (self):
        return self.Y
    def SetZ (self,Z):
        self.Z = Z
    def GetZ (self):
        return self.Z
    def SetOffsetA (self,OffsetA):
        self.OffsetA = OffsetA
    def GetOffsetA (self):
        return self.OffsetA
    def SetOffsetB (self,OffsetB):
        self.OffsetB = OffsetB
    def GetOffsetB (self):
        return self.OffsetB
    def SetRadius1 (self,Radius1):
        self.Radius1 = Radius1
    def GetRadius1 (self):
        return self.Radius1
    def SetRadius2 (self,Radius2):
        self.Radius2 = Radius2
    def GetRadius2 (self):
        return self.Radius2
    def SetAzimuth1 (self,Azimuth1):
        self.Azimuth1 = Azimuth1
    def GetAzimuth1 (self):
        return self.Azimuth1
    def SetAzimuth2 (self,Azimuth2):
        self.Azimuth2 = Azimuth2
    def GetAzimuth2 (self):
        return self.Azimuth2
    def SetVert1 (self,Vert1):
        self.Vert1 = Vert1
    def GetVert1 (self):
        return self.Vert1
    def SetVert2 (self,Vert2):
        self.Vert2 = Vert2
    def GetVert2 (self):
        return self.Vert2
    def SetSpatialRef (self,sr):
        self.SpatialReference = sr
    def GetSpatialRef (self):
        return self.SpatialReference
    
    
    def SetObserver (self,iX,iY,iZ,iOffsetA,iOffsetB,iRadius1,iRadius2,iAzimuth1,iAzimuth2,iVert1,iVert2,sr):
        success = False
        try:
            if (iX == None or iY == None):
                raise Exception, "Coordinate values X and Y are emtpy"
            self.X = iX #required
            self.Y = iY #required
            if ((iZ != None) and (iZ != "#")):
                self.Z = iZ
            else:
                self.Z = None
                
            if (iOffsetA != None and len(str(iOffsetA)) != 0): self.OffsetA = iOffsetA
            if (iOffsetB != None and len(str(iOffsetB)) != 0): self.OffsetB = iOffsetB
            if (iRadius1 != None and len(str(iRadius1)) != 0): self.Radius1 = iRadius1
            if (iRadius2 != None and len(str(iRadius2)) != 0): self.Radius2 = iRadius2
            if (iAzimuth1 != None and len(str(iAzimuth1)) != 0): self.Azimuth1 = iAzimuth1
            if (iAzimuth2 != None and len(str(iAzimuth2)) != 0): self.Azimuth2 = iAzimuth2
            if (iVert1 != None and len(str(iVert1)) != 0): self.Vert1 = iVert1
            if (iVert2 != None and len(str(iVert2)) != 0): self.Vert2 = iVert2
            if (sr != None): self.SpatialReference = sr
            
            success = True
        except Exception, ErrorMessage:
            print ErrorMessage
            success = False
        return success
      
    def AddObserver(self,gp,target_fc):
        msgFCDoesNotExist = "Internal Error: Input feature class %s does not exist."
        msgFCNotPoint = "Internal Error: Target feature class %s is not a point or multipoint."
        msgDifferentSpatialRef = "Internal Error: Observer spatial reference does not match target feature class."
        msgCouldNotAddPoint = "Internal Error: Could not add observer to %s."
        msgCouldNotObtainSchemaLock = "Internal Error: Could not obtain schema lock on %s."
        msgMissingObserverFields = "Internal Error: Input observers are missing the following required fields:\n %s"
        success = False
        try:
            
            # check that input fc exists
            if (gp.Exists(target_fc) == False):
                raise Exception, msgFCDoesNotExist % (target_fc)
            
            fc_desc = gp.describe(target_fc)
            
            # check that target fc is a point or multipoint
            if (fc_desc.datasettype == "FeatureClass"):
                shape_type = fc_desc.shapetype
                if not (shape_type.upper() == "POINT" or shape_type.upper() == "MULTIPOINT"):
                    raise Exception, msgFCNotPoint % (target_fc)
                else:
                    pass
            else:
                raise Exception, msgFCNotPoint % (target_fc)
            
            # check for schema lock
            #
            # ERROR:
            # schema lock on temp feature class ALWAYS returns
            # an ERROR!!!!
            #
            #lock = MAScriptUtils.CheckForSchemaLock(gp,target_fc)
            #if (lock != True):
            #    success = False
            #    gp.AddError(msgCouldNotObtainSchemaLock % (target_fc))
            #    raise Exception, msgCouldNotObtainSchemaLock % (target_fc)
            
            # check that sr matches fc
            # ERROR: fc_sr is always an object, self_sr is a string!!!!!!
            fc_sr = fc_desc.spatialreference
            fc_sr_name = fc_sr.Name
            self_sr = self.SpatialReference
            self_sr_name = self_sr.Name
            # TODO: need to do a stronger comparison than just by name. New method for MAScriptUtils?
            if (fc_sr_name != self_sr_name): 
                raise Exception, msgDifferentSpatialRef
            
            # check that observer fields exist
            # Check observers for proper fields
            field_check = MAScriptUtils.CheckObserverFields(gp,target_fc)
            if (len(field_check) > 0):
                raise Exception, msgMissingObserverFields % (field_check)
            
            # Open an insert cursor for the new feature class
            cur = gp.InsertCursor(target_fc)
            # Create the point & attributes                        
            pnt = gp.CreateObject("Point")
            pnt.x = self.X
            pnt.y = self.Y
            if (self.Z != None):
                pnt.z = str(float(self.Z) + float(self.OffsetA))
            # Create a new row or feature, in the feature class
            feat = cur.NewRow()
            # Set the geometry of the new feature to the array of points
            feat.shape = pnt
            # add attributes                        
            if (self.Z == None):
                pass # let's just use the defaults instead.
            else:
                fields = gp.Describe(target_fc).Fields
                if ("SPOT" in fields):
                 feat.SetValue("SPOT",self.Z)
                
            feat.SetValue("OFFSETA",self.OffsetA)
            feat.SetValue("OFFSETB",self.OffsetB)
            feat.SetValue("VERT1",self.Vert1)
            feat.SetValue("VERT2",self.Vert2)
            feat.SetValue("AZIMUTH1",self.Azimuth1)
            feat.SetValue("AZIMUTH2",self.Azimuth2)
            feat.SetValue("RADIUS1",self.Radius1)
            feat.SetValue("RADIUS2",self.Radius2)
            
            # Insert the row
            try:
                cur.InsertRow(feat)
            except:
                raise Exception, msgCouldNotAddPoint % (target_fc)
            # delete the insert cursor
            del cur
            success = True
            
        except Exception, ErrorMessage:
            print ErrorMessage
            gp.AddError(str(ErrorMessage))
            success = False
            
        return success
    
    def InterpolateZ (self,gp,inSurface,method):
    #   #given an input surface return interpolated Z value
    #   #X and Y return a Z value at the surface
    #   #Check if observer is within raster surface
        msgNoSurface = "Surface %s does not exist."
        msgNoSchemaLock = "Could not obtain schema lock to create temp files. \n Check %s for schema lock"
        msgNoSPOT = "No SPOT available for surface %s"
        msgSurfaceSpotFailed = "InterpolateZ failed:\n %s"
        msgCouldNotAddObserver = "Internal Error: Could not add observer to temp file."
        msgCouldNotAddObsFields = "Internal Error: Could not add fields to temporary observer."
        msgCouldNotRemoveSpot = "Internal Error: Could not remove SPOT item from temporary feature."
        spot = None
        try:
            
            # check surface exists
            if (gp.Exists(inSurface) == False): raise Exception, msgNoSurface % (str(inSurface))
            
            # make SR for observer
            #sr = gp.CreateObject("SpatialReference")
            #sr.CreateFromFile(self.SpatialReference)
            sr = self.SpatialReference
            
            # create temp point fc
            #workspace = MAScriptUtils.GetTempWorkspace(gp) # by this time it should already be set
            workspace = gp.workspace
            
            #if (MAScriptUtils.CheckForSchemaLock(gp,workspace) != True):
            #    raise Exception, msgNoSchemaLock % (str(workspace))
            
            tempfile = MAScriptUtils.GenerateTempFileName(gp,workspace,"FeatureClass")
            tempname = os.path.basename(tempfile)
            gp.CreateFeatureClass(str(workspace),str(tempname),"POINT","#","#","#",sr,"#","#","#","#")
            
            #Add attributes
            addfieldsuccess = MAScriptUtils.AddObserverFields(gp,tempfile)
            if (addfieldsuccess == False):
                raise Exception,msgCouldNotAddObsFields
            
            # mosaic surface if it isn't a raster dataset?
            # Maybe we find just the one tile needed?
            
            # project points if not same SR as surface
            surf_sr_name = str(gp.Describe(inSurface).SpatialReference.Name)
            self_sr_name = str(sr.Name).replace("'","")
            
            #if (debug == True):
            #    msg = "surf_sr_name: " + str(surf_sr_name) + "\nself_sr_name: " + str(self_sr_name)
            #    print msg
            #    gp.AddMessage(msg)
                
            if (surf_sr_name != self_sr_name):
                ptempfile = tempfile + "p"
                gp.project_management(tempfile,ptempfile,gp.describe(inSurface).SpatialReference,"#","#")
                gp.delete(tempfile)
                gp.rename(ptempfile,tempfile)
            else:
                pass # if the spatial refs match
            
            # add point to temp fc
            addobserversuccess = self.AddObserver(gp,tempfile)
            if (addobserversuccess == False):
                raise Exception, msgCouldNotAddObserver
            
            # surfacespot wants to add the SPOT field itself
            # so we'll remove it from the temp file:
            # "Out, damned spot! Out, I say!" (Act 5, Scene 1) - MacBeth
            try:
                fields = gp.Describe(tempfile).Fields
                if ("SPOT" in fields):
                    gp.deletefield (tempfile, "SPOT")
                del fields
            except:
                raise Exception, msgCouldNotRemoveSpot
            
            
            # Add Z value to spot
            try:
                gp.Surfacespot(inSurface,tempfile,"SPOT","#","BILINEAR")
            except:
                raise Exception, msgSurfaceSpotFailed % (gp.GetMessages())
            
            # get the spot value and return it
            rows = gp.searchcursor(tempfile)
            row = rows.next()
            spot = str(row.SPOT)
            if (len(spot) == 0):
                gp.delete(tempfile)
                del rows
                raise Exception, msgNoSPOT % (str(inSurface))
            del rows
            # clean up temp dataset
            gp.delete(tempfile)
            
        except Exception, ErrorMessage:
            spot = None
            print ErrorMessage
            gp.AddError(str(ErrorMessage))
            
        return spot