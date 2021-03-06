# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# FireHabitat_Analysis.py
# Created on: 2015-05-11 10:35:15.00000
#   (generated by ArcGIS/ModelBuilder)
# Description:
#The folder that works with the script is located here: H:\GIS\EA\Boreal Caribou\FireHistory. An empty geodatabase (FireHistory.gdb)
#with a Albers Equal Area dataset is used in the processing.
#Paste the empty geodatabase (FireHistory.gdb) into the above folder: H:\GIS\EA\Boreal Caribou\FireHistory.gdb.
#This script Loops through all years indicated in xrange to subtract newly burned habitat
#from older burned habitat, and appends these polygons into a table. Then it calculates the
#area (hectares) of possible babitat coming back to 40 years in age. The first
#fire year is used to create the append table.
#NOTE: Add fire feature class to analyze to FireHistory.gdb before running
# ---------------------------------------------------------------------------

# Import arcpy module

import os
import arcpy
from arcpy import env
arcpy.env.overwriteOutput = True
#env.workspace = r"C:\ActiveProjects\FireHistory\FireHistory.gdb"

EnvWksp = arcpy.GetParameterAsText(0)
FireHistory = arcpy.GetParameterAsText(1)
StartYear = int(arcpy.GetParameterAsText(2))
FinalYear = int(arcpy.GetParameterAsText(3))
Outwksp = arcpy.GetParameterAsText(4)


env.workspace = EnvWksp
outWorkspace =Outwksp

newField1 = arcpy.AddFieldDelimiters(arcpy.env.workspace, "FIRE_YEAR")
#Select first Fire Year habitat sql expressions
SQLExpr1 = str(newField1) + " = " + str(StartYear)
#Select habitat 40 years after Fire Year
Fire40 = StartYear + 40
SQLExpr2 = str(newField1) + ">" + str(StartYear) + " AND " + str(newField1)+ " <= " + str(Fire40)
#SQLExpr2 = str(newField1) + " > " + str(StartYear)

#Create temporary layer files
arcpy.MakeFeatureLayer_management(FireHistory, "FireHist1", SQLExpr1)
arcpy.MakeFeatureLayer_management(FireHistory, "FireHist2", SQLExpr2)

# Process: Clip newer overlapping fire habitat from Fire Start Year
Clip = EnvWksp + "\FireHab_Overlap"
arcpy.Clip_analysis("FireHist1"," FireHist2", Clip, "")

#Computes the geometric union of FireHist1 and the clipped habitat for subtraction
infeatures = ["FireHist1", Clip]
Union1 = EnvWksp + "\Fire" + "_" + str(StartYear)
arcpy.Union_analysis(infeatures, Union1, "ALL", "", "GAPS")

#Delete overlapping habitat
newField2 = arcpy.AddFieldDelimiters(arcpy.env.workspace, "FIRE_YEAR_1")
SQLExpr3 = str(newField2) + " = " + str(StartYear)
arcpy.MakeFeatureLayer_management(Union1, "Union2")
#select row with overlapping habitat
arcpy.SelectLayerByAttribute_management("Union2", "NEW_SELECTION", SQLExpr3)
#Delete overlapping habitat row
arcpy.DeleteRows_management("Union2")
#create feature class from layer file
arcpy.CopyFeatures_management("Union2", "Union3")

#Delete temporary layer files
arcpy.Delete_management("FireHist1")
arcpy.Delete_management("FireHist2")

#create feature class (target table) to hold calculated values for each year:
spatial_reference = arcpy.Describe(outWorkspace).spatialReference
arcpy.CreateFeatureclass_management(outWorkspace, "HabRecover40yr", "Polygon",Union1, "DISABLED", "DISABLED", spatial_reference)

#Append leftover habitat to target table
TargetTable = Outwksp + "\HabRecover40yr"
arcpy.Append_management("Union3", TargetTable)

#loops through model from NextYear to lastYear. Can change these parameters
LoopYr = StartYear + 1
LoopEnd = FinalYear +1
for x in xrange(LoopYr, LoopEnd):

    FireYear = x
    Fire40 = x + 40
    newField1 = arcpy.AddFieldDelimiters(arcpy.env.workspace, "FIRE_YEAR")

    #Select Fire Year habitat
    SQLExpr1 = str(newField1) + " = " + str(FireYear)

    #Select habitat after Fire Year
    SQLExpr2 = str(newField1) + ">" + str(FireYear) + " AND " + str(newField1)+ " <= " + str(Fire40)
    #print x, Fire40

    #Create temporary layer files
    arcpy.MakeFeatureLayer_management(FireHistory, "FireHist1", SQLExpr1)
    arcpy.MakeFeatureLayer_management(FireHistory, "FireHist2", SQLExpr2)

    # Process: Clip newer fire habitat from Fire Year
    Clip =EnvWksp + "\FireHab_Overlap"
    arcpy.Clip_analysis("FireHist1"," FireHist2", Clip, "")

    #Computes the geometric union of FireHist1 and the clipped habitat for subtraction
    infeatures = ["FireHist1", Clip]
    Union1 = EnvWksp + "\Fire" + "_" + str(FireYear)
    arcpy.Union_analysis(infeatures, Union1, "ALL", "", "GAPS")

    #Delete overlapping habitat
    newField2 = arcpy.AddFieldDelimiters(arcpy.env.workspace, "FIRE_YEAR_1")
    SQLExpr3 = str(newField2) + " = " + str(FireYear)
    arcpy.MakeFeatureLayer_management(Union1, "Union2")
    #select row with overlapping habitat and delete row
    arcpy.SelectLayerByAttribute_management("Union2", "NEW_SELECTION", SQLExpr3)
    arcpy.DeleteRows_management("Union2")

    #create feature class from layer file
    arcpy.CopyFeatures_management("Union2", "Union3")
    #Append leftover habitat to target table
    TargetTable = Outwksp + "\HabRecover40yr"
    arcpy.Append_management("Union3", TargetTable)
    arcpy.Delete_management("FireHist2")


#Calculate Area in hectares of leftover habitat for every year in TargetTable

arcpy.env.outputCoordinateSystem = arcpy.Describe(TargetTable).spatialReference
arcpy.AddGeometryAttributes_management(TargetTable, "AREA", "KILOMETERS", "HECTARES", "")

arcpy.AddField_management(TargetTable, "PercentRnge", "DOUBLE", "", "", "")

arcpy.CalculateField_management(TargetTable, "PercentRnge", "[POLY_AREA] / 44165456194.3", "VB")

#print "script complete"
