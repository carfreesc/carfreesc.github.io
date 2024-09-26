# Imports from cheat sheet.

from qgis.core import *

# Supply path to qgis install location
# QgsApplication.setPrefixPath("/usr/bin/qgis", True)
QgsApplication.setPrefixPath("/usr", True)

# Create a reference to the QgsApplication.  Setting the
# second argument to False disables the GUI.
qgs = QgsApplication([], False)

# Load providers
qgs.initQgis()

# Add a layer
cata_layer = QgsVectorLayer("raw_data/cata.geojson", "CATA", "ogr")
if not cata_layer or not cata_layer.isValid():
  print("Layer failed to load!")
# Reproject to match OSM (EPSG:3857)
cata_layer.setCrs(QgsCoordinateReferenceSystem('EPSG:4326'))  # If it's in EPSG:4326

# Test it.
for field in cata_layer.fields():
  print(field.name(), field.typeName())

features = list(cata_layer.getFeatures()  )

testone = features[0]
list(testone)

for route in features:
  thisone = route[0]
  print(thisone['route_short_name'])

# Add a layer
bike_layer = QgsVectorLayer("raw_data/CR_Bikeways.json", "Bicycle", "ogr")
if not bike_layer or not bike_layer.isValid():
  print("Layer failed to load!")

for field in bike_layer.fields():
  print(f"-{field.name()}- is a {field.typeName()}")

features = list(bike_layer.getFeatures()  )

testone = features[0]
list(testone)

#for route in features:
#   print(route['Map Name'])




# Get the OSM base map.
tms = r'type=xyz&url=https://tile.openstreetmap.org/{z}/{x}/{y}.png'
osm_layer = QgsRasterLayer(tms,'OSM', 'wms')

# Add those layers to the map.
QgsProject.instance().addMapLayer(osm_layer)
QgsProject.instance().addMapLayer(cata_layer)
QgsProject.instance().addMapLayer(bike_layer)



# Now try to change the colors of certain types of routes.
# Create a thick red line symbol
symbol = QgsLineSymbol.createSimple({'color': 'red', 'width': '2.0'})
expression = "\"Path Type\" = 'Bike Lane'"  # Replace with your attribute condition
root_rule = QgsRuleBasedRenderer.Rule(None)
rule = QgsRuleBasedRenderer.Rule(symbol)
rule.setFilterExpression("\"Path Type\" = 'Bike Lane'") 
root_rule.appendChild(rule)

# Apply the rule-based renderer to the layer
renderer = QgsRuleBasedRenderer(root_rule)
bike_layer.setRenderer(renderer)

# Refresh the layer to see the changes
bike_layer.triggerRepaint()






# Now going to try to print a specific map.
project = QgsProject.instance()
manager = project.layoutManager()
layout = QgsPrintLayout(project)
layout.initializeDefaults()
layout.setName('CATA')
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

# Finally, exitQgis() is called to remove the
# provider and layer registries from memory
qgs.exitQgis()
