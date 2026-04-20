# Imports from cheat sheet.
from qgis.core import *
QgsApplication.setPrefixPath("/usr", True)

# Supply path to qgis install location
print("Initializing QGIS...")
qgs = QgsApplication([], False)
qgs.initQgis()

# Set the CRS.
mycrs = "EPSG:3857" # To match OSM
crs = QgsCoordinateReferenceSystem(mycrs)
QgsProject.instance().setCrs(crs)

# A function to move the features from one layer to another.
# I use this a couple times to merge e.g. all of the CATAGO zones into a single layer.
def copy_features(source_layer, target_layer):
  target_layer.startEditing()
  for feature in source_layer.getFeatures():
    new_feature = QgsFeature(feature)
    target_layer.addFeature(new_feature)
  target_layer.commitChanges()

# Set the project CRS, this is important when importing GPX.
print(f"Project CRS set to: {QgsProject.instance().crs().authid()}")
print()

# CATA fixed routes layer.
print("Adding layer: CATA fixed routes.")
cata_layer = QgsVectorLayer("raw_data/from_marin/CATA_Fall2024_RouteTraces.kml", "CATA", "ogr")
if not cata_layer or not cata_layer.isValid():
  print("Layer failed to load!")
# Reproject to match OSM (EPSG:3857)
# cata_layer.setCrs(QgsCoordinateReferenceSystem('EPSG:4326'))  # If it's in EPSG:4326

# Get a list of bus segments.
cata_features = list(cata_layer.getFeatures()  )
print(f"Loaded {len(cata_features)} bus segments.")

# A sample bus.
# testone = features[0]
# list(testone)

routenames = []
for route in cata_features:
  routenames.append(route[0])
print("Loaded routes:")
print(', '.join(routenames))
print()

# CATAGO layer.
print("Adding layer: CATAGO.")
catago_shp_source = [ "raw_data/from_marin/Boalsburg_Zone.shp", "raw_data/from_marin/College Twp Zone.shp", "raw_data/from_marin/CentreAreaWest_Jul2024.shp" ]

catago_layers = []
for file_path in catago_shp_source:
  templayer = QgsVectorLayer(file_path, "CATAGO!", "ogr")
  if templayer.isValid():
    catago_layers.append(templayer)

# The different catago layers don't have the same fields, so they're hard to merge.    
# catago_layer = QgsVectorLayer("raw_data/from_marin/CentreAreaWest_Jul2024.shp", "CATAGO!", "ogr")
# if not catago_layer or not catago_layer.isValid():
#   print("Layer failed to load!")

# Create a new memory layer that will hold both CATA routes.
# crs = catago_layers[0].crs()  
# all_catago = QgsVectorLayer("MultiPolygon?crs=" + crs.authid(), "CATAGO!", "memory")

# # Add fields from the first layer to the combined layer (assuming same fields)
# all_catago_data = all_catago.dataProvider()
# for thislayer in catago_layers:
#   all_catago_data.addAttributes(thislayer.fields())
# all_catago.updateFields()

# # Copy features from both layers
# for thiszone in catago_layers:
#   copy_features(thiszone,all_catago)


# here
# copy_features(catago_layers[0],all_catago)
# print(len(list(all_catago.getFeatures())))
# copy_features(catago_layers[1],all_catago)
# print(len(list(all_catago.getFeatures())))
# copy_features(catago_layers[2],all_catago)
# print(len(list(all_catago.getFeatures())))

# print("CATAGO layers merged!")

# Save it.
# catago_output_file = "./catago_combined.gpkg"

# error = QgsVectorLayerExporter.exportLayer(
#   all_catago,        # The layer to export
#   catago_output_file,           # Output file path
#   'ogr',                 # Provider for file formats (OGR for vector layers)
#   crs # 'GPKG',                # File format (GeoPackage in this case)
# #  {}                     # Empty options (you can add options like CRS here)
# )

# # Add the saved file to the QGIS map
# all_catago_stored = QgsVectorLayer(catago_output_file, "CATAGO!", "ogr")


# Add a layer: Centre Region Bikeways.
print("Adding layer: Centre Region Bikeways.")
bike_layer = QgsVectorLayer("raw_data/CR_Bikeways.json", "Bicycle", "ogr")
if not bike_layer or not bike_layer.isValid():
  print("Layer failed to load!")

# for field in bike_layer.fields():
#   print(f"-{field.name()}- is a {field.typeName()}")

bike_features = list(bike_layer.getFeatures()  )
print(f"Loaded {len(bike_features)} bike segments.")

# Bike route types.
types = set()
for route in bike_features:
  types.add(route['Path Type'])
types_str = ', '.join(types)
print("Found bike route types:")
print(types_str)



# Add a layer: PSU shuttles.
# I can't find public GIS for these, so I mapped them on MapMyRide
# and exported GPX tracks.
shuttle_gpx_source = ["raw_data/Beaver_Ave_Shuttle_--_Fall_2024.gpx", "raw_data/College_Ave_Shuttle_--_Fall_2024.gpx"]

shuttle_layers = []
for file_path in shuttle_gpx_source:
  templayer = QgsVectorLayer(file_path+"?type=track", "GPX Track", "gpx")
  if templayer.isValid():
    shuttle_layers.append(templayer)

# Create a new memory layer that will hold both CATA routes.
crs = shuttle_layers[0].crs()  
all_shuttles = QgsVectorLayer("LineString?crs=" + crs.authid(), "PSU shuttles", "memory")

# Add fields from the first layer to the combined layer (assuming same fields)
all_shuttles_data = all_shuttles.dataProvider()
all_shuttles_data.addAttributes(shuttle_layers[0].fields())
all_shuttles.updateFields()


# Copy features from both layers
copy_features(shuttle_layers[0], all_shuttles)
copy_features(shuttle_layers[1], all_shuttles)
print("Shuttle layers merged!")

# Save it.
shuttles_output_file = "./shuttles_combined.gpkg"

error = QgsVectorLayerExporter.exportLayer(
  all_shuttles,        # The layer to export
  shuttles_output_file,           # Output file path
  'ogr',                 # Provider for file formats (OGR for vector layers)
  crs # 'GPKG',                # File format (GeoPackage in this case)
#  {}                     # Empty options (you can add options like CRS here)
)

# Add the saved file to the QGIS map
all_shuttles_stored = QgsVectorLayer(shuttles_output_file, "PSU shuttles", "ogr")
# QgsProject.instance().addMapLayer(all_shuttles_stored)


# Get the OSM base map.
tms = r'type=xyz&url=https://tile.openstreetmap.org/{z}/{x}/{y}.png'
osm_layer = QgsRasterLayer(tms,'OSM', 'wms')

# Add those layers to the map.
mylayers = catago_layers+[ osm_layer, cata_layer,  all_shuttles_stored, bike_layer ]
for thislayer in mylayers:
  QgsProject.instance().addMapLayer(thislayer)
# QgsProject.instance().addMapLayer(cata_layer)
# QgsProject.instance().addMapLayer(bike_layer)
# QgsProject.instance().addMapLayer(bike_layer)


# Now try to change the colors of certain types of routes.
# Create a thick red line symbol

# Set up display types.
bike_styles = [ ["\"Path Type\" = 'Bike Lane'",'#00BFFF','1.0'], \
                ["\"Path Type\" = 'Bike Route'",'#89CFF0','1.0'], \
                ["\"Path Type\" = 'Shared Use Path'",'#0000FF','1.0'] ]


# Set the display types (still missing Game Lands paths and some others.)
root_rule = QgsRuleBasedRenderer.Rule(None)
for style in bike_styles:
  symbol = QgsLineSymbol.createSimple({'color': style[1], 'width': style[2]})
  expression = style[0]
  rule = QgsRuleBasedRenderer.Rule(symbol)
  rule.setFilterExpression(expression)
  root_rule.appendChild(rule)

# Apply the rule-based renderer to the layer
bike_renderer = QgsRuleBasedRenderer(root_rule)
bike_layer.setRenderer(bike_renderer)
bike_layer.triggerRepaint()


# PSU shuttle routes
shuttle_styles = [ ["\"name\" = 'Beaver Ave Shuttle -- Fall 2024'",'red','1.0'], \
                ["\"name\" = 'College Ave Shuttle -- Fall 2024'",'red','1.0'] ]

shuttle_rule = QgsRuleBasedRenderer.Rule(None)
for style in shuttle_styles:
  symbol = QgsLineSymbol.createSimple({'color': style[1], 'width': style[2]})
  expression = style[0]
  rule = QgsRuleBasedRenderer.Rule(symbol)
  rule.setFilterExpression(expression)
  shuttle_rule.appendChild(rule)

# Apply the rule-based renderer to the layer
renderer = QgsRuleBasedRenderer(shuttle_rule)
all_shuttles_stored.setRenderer(renderer)
all_shuttles_stored.triggerRepaint()


# CATA style -- all the same for now.
cata_styles = [ 'orange','1.0'] 

cata_rule = QgsRuleBasedRenderer.Rule(None)
symbol = QgsLineSymbol.createSimple({'color': cata_styles[0], 'width': cata_styles[1]})
rule = QgsRuleBasedRenderer.Rule(symbol)
cata_rule.appendChild(rule)

# Apply the rule-based renderer to the layer
renderer = QgsRuleBasedRenderer(cata_rule)
cata_layer.setRenderer(renderer)
cata_layer.triggerRepaint()


# Now going to try to print a specific map.
# Set up some general stuff, I don't really know what this is for.
project = QgsProject.instance()
manager = project.layoutManager()

# Do other incantations.
# manager.addLayout(layout)


j = 0
for feature in bike_features[0:3]:
  print(f"{j} was ok")
# feature = features[0]

  # Generate the layer.
  temp_layer = QgsVectorLayer("LineString?crs=EPSG:4326", "SelectedFeatureLayer", "memory") 
  temp_layer_data = temp_layer.dataProvider()
  temp_layer_data.addAttributes(bike_layer.fields())
  temp_layer.updateFields()
  # Add the route to it.
  temp_layer_data.addFeature(feature)
  # Add the renderer we used before.
  temp_renderer = bike_renderer.clone()
#  temp_layer.setRenderer(temp_renderer) # Use same colors as the bike layer.

  # Add it to the project.
  project.addMapLayer(temp_layer)

  # Create the map layout.
  layout = QgsPrintLayout(project)
  layout.initializeDefaults()
  layout.setName('Bike Path')
#  manager.addLayout(layout)

  # Set the item map.
  map_item = QgsLayoutItemMap(layout)
  map_item.setRect(20, 20, 200, 200)
  # Set the extent of the map to include all layers
  map_item.setExtent(temp_layer.extent())
#  map_item.setLayers([temp_layer, osm_layer])
  map_item.setLayers([temp_layer])

  # Add the map item to the layout
  layout.addLayoutItem(map_item)

  # Export it.
  exporter = QgsLayoutExporter(layout)
  exporter.exportToPdf(f"/tmp/map{j}.pdf", QgsLayoutExporter.PdfExportSettings())
  exporter.exportToImage(f"/tmp/map{j}.png", QgsLayoutExporter.ImageExportSettings())

  # And remove that layer.
  project.removeMapLayer(temp_layer)

  # Increment.
  j += 1




# Other printing-related materials.

layout = QgsPrintLayout(project)
layout.initializeDefaults()
layout.setName('Bikes')
manager.addLayout(layout)

# Add a map item to the layout
map_item = QgsLayoutItemMap(layout)
map_item.setRect(20, 20, 200, 200)

# Set the extent of the map to include all layers
map_item.setExtent(bike_layer.extent())
map_item.setLayers([bike_layer, cata_layer, osm_layer])


# Print the order of layers
layers = QgsProject.instance().layerTreeRoot().children()
print("Current order.")
for i, layer in enumerate(layers):
    print(f"{i+1}: {layer.name()}")

# Add the map item to the layout
layout.addLayoutItem(map_item)

# Export it.
exporter = QgsLayoutExporter(layout)
# exporter.exportToImage('/tmp/map.png', QgsLayoutExporter.ImageExportSettings()) 
exporter.exportToPdf('/tmp/map.pdf', QgsLayoutExporter.PdfExportSettings()) 

project.write('./map.qgz')

# That's kind of cool, and it seems to work.  Now I want to show just a single feature.

# Finally, exitQgis() is called to remove the
# provider and layer registries from memory
# qgs.exitQgis()
