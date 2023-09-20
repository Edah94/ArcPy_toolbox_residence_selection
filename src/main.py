"""
Tool: Residence Selection Salzburg
Version: ArcGISp Pro 2.9
Python Environment: Python 3.10.8
Author: Edah Šahinović
Description: This script serves as a multicriteria analysis to evaluate the quality of the
local environment based on personal preferences when selecting a location of residence in Salzburg.
"""


# ------------------------------------------------IMPORTS------------------------------------------------
import arcpy

from arcpy.analysis import *
from arcpy.conversion import *
from arcpy.sa import *
from arcpy.analysis import Clip

import os

# ------------------------------------------------PATHS AND USER INPUTS------------------------------------------------

#defining a path of a workspace by the user
workspace_path = arcpy.GetParameterAsText(0)

#workspace path provided is considered, otherwise the os.getcwd() automatically provides filepath
if workspace_path:
    arcpy.AddMessage(workspace_path)
else:
    workspace_path = os.getcwd()
    arcpy.AddMessage("Path to project provided automatically: " + workspace_path)

#relevant paths to the databases
arcpy.env.workspace = os.path.join(workspace_path, 'geodatabase/input.gdb')
residuals_gdb = os.path.join(workspace_path, 'geodatabase/residuals.gdb')
output_gdb = os.path.join(workspace_path, 'geodatabase/output.gdb')

#merged path for the final output
output_final = os.path.join(output_gdb, "salzburg_buildings_suitability")

#access the project and its table of content for subsequent layer import and symbology handling
aprx = arcpy.mp.ArcGISProject("CURRENT")
aprxMap = aprx.listMaps("Map")[0]
arcpy.AddMessage(aprxMap)

#raw vector features stored in the database to be processed and used as weighted overlay input criteria
economic_point = "extracted_point_economic_zones_reproj"
bicycle_point = "extracted_point_osm_bicycle_parking_reproj"
bus_point = "extracted_point_osm_bus_stops_reproj"
park_poly = "extracted_point_osm_park_poly_reproj"
restaurant_point = "extracted_point_osm_restaurants_reproj"
school_point = "extracted_point_osm_schools_reproj"
salzburg_AOI = "salzburg_aoi"
salzburg_buildings = "salzburg_buildings"

#distances list for MultipleRingBuffer
economic_distance = arcpy.GetParameterAsText(1)
park_distance = arcpy.GetParameterAsText(3)
bus_distance = arcpy.GetParameterAsText(5)
bicycle_distance = arcpy.GetParameterAsText(7)
restaurant_distance = arcpy.GetParameterAsText(9)
school_distance = arcpy.GetParameterAsText(11)

economic_weight = arcpy.GetParameterAsText(2)
park_weight = arcpy.GetParameterAsText(4)
bus_weight = arcpy.GetParameterAsText(6)
bicycle_weight = arcpy.GetParameterAsText(8)
restaurant_weight = arcpy.GetParameterAsText(10)
school_weight = arcpy.GetParameterAsText(12)


# ------------------------------------------------LAYER PROCESSING------------------------------------------------

#storage table of all the inputs provided by the user used for subsequent analysis
weighted_overlay_table = []

def layer_processing(layer_distance, layer_weight, layer, layer_name) -> WOTable:
    """
    Layer processing function to proccess each given layer: converting into buffer zones by the given distances, clipping to the extent of the city of Salzburg,
    converting to raster, reclassifying raster to respective score values ranging from 1 to 5 and appending to the WOTable.

    PARAMS:
    layer: layer to be processed
    layer_distance: layer distance to be considered as buffer zones
    layer_weight: given weight for the layer
    layer_name: name of the layer to be appended to the outputs
    """

    layer_weight = int(layer_weight)

    #appending distance values as integers to a new list
    layer_value_list = layer_distance.split(";")
    
    layer_value_list_new = []
    
    for value in layer_value_list:
        layer_value_list_new.append(int(value))
    
    #assigning a score value to each distance value
    layer_remap_list = []
    
    score_value = 5
    
    for value in layer_value_list_new:
        layer_remap_list.append([value, score_value])
        score_value -= 1

    #converting initial layers by applying multiple geoprocessing tools, from buffering to raster reclassification
    layer_buffer = MultipleRingBuffer(layer, os.path.join(residuals_gdb, layer_name + "_buffer"), 
                                  layer_distance, "meters", "distance", "ALL")

    layer_buffer_clip = Clip(layer_buffer, salzburg_AOI, os.path.join(residuals_gdb, layer_name + "_buffer_clip"))
    
    layer_buffer_raster = FeatureToRaster(layer_buffer_clip, "distance", os.path.join(residuals_gdb, layer_name + "_buffer_raster"), 20)

    layer_buffer_raster_reclassify = Reclassify(layer_buffer_raster, "Value", RemapValue(layer_remap_list))

    layer_buffer_raster_reclassify.save(os.path.join(residuals_gdb, layer_name + "_reclass"))
    
    #appending subsequent raster layer ready for weighted overlay analysis
    weighted_overlay_table.append([residuals_gdb + "/" + layer_name + "_reclass", layer_weight, "Value", RemapValue([[1, 1], [2, 2], [3, 3], [4, 4], [5, 5], ["NODATA", "NODATA"]])])
    arcpy.AddMessage(layer_name + " successfully processed and included in the suitability analysis!")



#single layer is used if both distance and weight are considered
if economic_distance and economic_weight:
    arcpy.AddMessage("processing economic layer..")
    layer_processing(economic_distance, economic_weight, economic_point, "economic" )
else:
    arcpy.AddMessage("economic factor skipped: either not considered or misses both distance and weight input")

if park_distance and park_weight:
    arcpy.AddMessage("processing park layer..")
    layer_processing(park_distance, park_weight, park_poly, "park" )
else:
    arcpy.AddMessage("park layer skipped: either not considered or misses both distance and weight input")   

if bus_distance and bus_weight:
    arcpy.AddMessage("processing bus stop layer..")
    layer_processing(bus_distance, bus_weight, bus_point, "bus" )
else:
    arcpy.AddMessage("bus stops layer skipped: either not considered or misses both distance and weight input")    

if restaurant_distance and restaurant_weight:
    arcpy.AddMessage("processing restaurant layer..")
    layer_processing(restaurant_distance, restaurant_weight, restaurant_point, "restaurant" )
else:
    arcpy.AddMessage("restaurants layer skipped: either not considered or misses both distance and weight input")    

if bicycle_distance and bicycle_weight:
    arcpy.AddMessage("processing bicycle parking space layer..")
    layer_processing(bicycle_distance, bicycle_weight, bicycle_point, "bicycle" )
else:
    arcpy.AddMessage("bicycle layer skipped: either not considered or misses both distance and weight input")    

if school_distance and school_weight:
    arcpy.AddMessage("processing schools layer..")
    layer_processing(school_distance, school_weight, school_point, "school" )
else:
    arcpy.AddMessage("schools layer skipped: either not considered or misses both distance and weight input")    



# ------------------------------------------------SUITABILITY ANALYSIS AND RASTER VALUES TO BUILDINGS LAYER TRANSFER------------------------------------------------

#WOTable that carries all the parameters for the weighted overlay processing
wotable = WOTable(weighted_overlay_table, [1, 5, 1])

arcpy.AddMessage("Running weighted overlay analysis..")
outWeightedOverlay = WeightedOverlay(wotable)



#transfering raster values to each building feature that has a certain value 
arcpy.AddMessage("Transfering weighted overlay raster outputs to buildings..")
weighted_overlay_points = RasterToPoint(outWeightedOverlay, residuals_gdb + "/" + "weighted_overlay_points", "Value")

fieldmappings = arcpy.FieldMappings()
fieldmappings.addTable(salzburg_buildings)
fieldmappings.addTable(weighted_overlay_points)

grid_code_field_index = fieldmappings.findFieldMapIndex("grid_code")
fieldmap = fieldmappings.getFieldMap(grid_code_field_index)

field = fieldmap.outputField

fieldmap.mergeRule = "max"
fieldmappings.replaceFieldMap(grid_code_field_index, fieldmap)


SpatialJoin(salzburg_buildings, weighted_overlay_points, output_final, match_option="INTERSECT", join_type=0, search_radius="32 Feet", field_mapping=fieldmappings)
arcpy.AddMessage("Successfully carried out the procedure!")

outWeightedOverlay.save(output_gdb + "/weighted_overlay_output")
arcpy.AddMessage("Added the result layer to the map!")

# ------------------------------------------------VISUALIZING AND SYMBOLIZING THE OUTPUT------------------------------------------------
#MGI Austria GK M31

#add the output to the table of contents of a current project
aprxMap.addDataFromPath(output_final)

#iterate through table of contents, finding an output layer and styling its symbology accordingly
for lyr in aprxMap.listLayers():
    
    if lyr.name == "salzburg_buildings_suitability":
        sym = lyr.symbology
        sym.updateRenderer("UniqueValueRenderer")
        sym.renderer.fields = ['grid_code']

        for grp in sym.renderer.groups:
            for itm in grp.items:
                myVal = itm.values[0][0]

                if myVal == "1":
                    itm.symbol.color = {"RGB": [255, 0, 0, 100]} #red

                if myVal == "2":
                    itm.symbol.color = {"RGB": [255, 167, 0, 100]} #orange

                if myVal == "3":
                    itm.symbol.color = {"RGB": [255, 244, 0, 100]} #yellow

                if myVal == "4":
                    itm.symbol.color = {"RGB": [163, 255, 0, 100]} #light green

                if myVal == "5":
                    itm.symbol.color = {"RGB": [44, 186, 0, 100]} #green

        lyr.symbology = sym
                



####TODO

#handle errors - if person didn't populate some entries
#handle 5 criteria to be entered.
#give option to input point feature as housing consideration
#handling if a person doesnt have Map View open in the project (starts without a template)
#consider inverse weightings, such as further from main streets the bettert
#add option to import and assess a dataset that reflects special interest points
#when the economic parameter is considered, the output buildings are subject to the maximum distance of the economic buffer.
#change field name and values - at least the symbology