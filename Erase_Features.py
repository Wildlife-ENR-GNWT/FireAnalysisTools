#-------------------------------------------------------------------------------
# Name:        Erase features
# Purpose:      This script can be used to perform location-based 'Erase' of
#               polygons when access to the Advanced licence is unavailable
#               to use the Erase tool
# Author:      bonnie_fournier
#
# Created:     04/04/2016
# Copyright:   (c) bonnie_fournier 2016
# Licence:     <your licence>
#-------------------------------------------------------------------------------

import os
import arcpy
from arcpy import env
arcpy.env.overwriteOutput = True

#outWorkspace = r"H:\BONNIE\Test\test.gdb"

EnvWksp = arcpy.GetParameterAsText(0) #geodatabase for output files
Feature_one = arcpy.GetParameterAsText(1) # Will grab this "erased" chunk.
Feature_two = arcpy.GetParameterAsText(2) # will discard this features entirely.

env.workspace = EnvWksp
outWorkspace = EnvWksp

Fc_1 = os.path.basename(Feature_one) #removes the path from Feature_one
Feature_one_name = Fc_1.strip('.shp')#removes the '.shp' from the shapefile
Fc_2 = os.path.basename(Feature_two)
Feature_two_name = Fc_2.strip('.shp')

infeatures = [Feature_one, Feature_two]
Union1 = Feature_one_name + "_Union" #first output file name, that will contain both feature classes
arcpy.Union_analysis(infeatures, Union1, "ALL", "", "GAPS")

##SQLExpr1 = "FID_" + Feature_one + " = 1 AND FID_" + Feature_two + " < 0"
# Building SQL to select the original feature class minus the overlaps
SQLExpr1 = """ {0} >= 0 AND {1} < 0 """.format("FID_" + Feature_one_name, "FID_" + Feature_two_name)
#create layer file for SelectbyAttributes
arcpy.MakeFeatureLayer_management(Union1, "Union2")

arcpy.SelectLayerByAttribute_management("Union2", "NEW_SELECTION", SQLExpr1)
#Final output file containing the original feature class minus the overlaps
arcpy.CopyFeatures_management("Union2", Feature_one_name + "_erased")









