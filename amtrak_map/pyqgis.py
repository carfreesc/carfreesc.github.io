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

# Set the project CRS, this is important when importing GPX.
print(f"Project CRS set to: {QgsProject.instance().crs().authid()}")
print()

# Amtrak map
print("Adding layer: Amtrak")
amtrak_layer = QgsVectorLayer("amtrak_routes.geojson", "amtrak", "ogr")
if not amtrak_layer or not amtrak_layer.isValid():
  print("Layer failed to load!")


# Add layer with station labels
stations_layer_temp = QgsVectorLayer("Point?crs=EPSG:4326", "stations", "memory")
prov = stations_layer_temp.dataProvider()

from qgis.PyQt.QtCore import QVariant
from qgis.core import QgsField

prov.addAttributes([
    QgsField("name", QVariant.String)
])
stations_layer_temp.updateFields()

stations = [
    ("Altoona",     -78.3947, 40.5150),
    ("Tyrone",      -78.2388, 40.6709),
    ("Harrisburg",  -76.8867, 40.2615),
    ("Huntingdon",  -78.0096, 40.4842),
    ("Lewistown",   -77.5765, 40.5992),
    ("State College", -77.8617, 40.7943), 
]

features = []
for name, lon, lat in stations:
    f = QgsFeature()
    f.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(lon, lat)))
    f.setAttributes([name])
    features.append(f)

prov.addFeatures(features)
stations_layer_temp.updateExtents()

# This is a layer only stored in memory, which is fleeting.
# We need to move it to a file, apparently.
from qgis.core import (
    QgsVectorFileWriter,
    QgsCoordinateTransformContext,
    QgsProject
)
path = "stations.gpkg"

options = QgsVectorFileWriter.SaveVectorOptions()
options.driverName = "GPKG"
options.layerName = "stations"   # important for GPKG

error, message, new_path, new_layer = QgsVectorFileWriter.writeAsVectorFormatV3(
    stations_layer_temp,
    path,
    QgsProject.instance().transformContext(),
    options
)

print("Error:", error)
print("Message:", message)

# reload from file
stations_layer = QgsVectorLayer(path, "stations", "ogr")

field = "name"

categories = []

colors = {
    "Philadelphia": "red",
    "State College": "red",
    "Harrisburg": "blue",
    "Pittsburgh": "green",
    "Altoona": "orange",
    "Tyrone": "purple",
    "Huntingdon": "brown",
    "Lewistown": "pink"
}

for name, color in colors.items():
    symbol = QgsMarkerSymbol.createSimple({
        "name": "square",
        "size": "5",
        "color": color,
        "outline_color": "black"
    })
    categories.append(QgsRendererCategory(name, symbol, name))

renderer = QgsCategorizedSymbolRenderer(field, categories)
stations_layer.setRenderer(renderer)
stations_layer.triggerRepaint()

from PyQt5.QtGui import QColor

layer = stations_layer

# --- Label settings ---
label_settings = QgsPalLayerSettings()
label_settings.fieldName = "name"
label_settings.placement = QgsPalLayerSettings.AroundPoint
label_settings.dist = 2

# --- Text style (no font call!) ---
text_format = QgsTextFormat()
text_format.setSize(11)              # size still works
# text_format.setColor(QColor("black"))

# --- White halo ---
buffer = QgsTextBufferSettings()
buffer.setEnabled(True)
buffer.setSize(1.2)
# buffer.setColor(QColor("white"))

text_format.setBuffer(buffer)
label_settings.setFormat(text_format)

# --- Apply ---
layer.setLabelsEnabled(True)
layer.setLabeling(QgsVectorLayerSimpleLabeling(label_settings))
layer.triggerRepaint()

stations_features = list(stations_layer.getFeatures())
for station in stations_features:
  print(station.attributes())

# Now style the stations a bit.
from qgis.core import QgsMarkerSymbol

symbol = QgsMarkerSymbol.createSimple({
    "name": "square",      # try: circle, square, triangle, star
    "size": "3",           # in mm (try 5–7 for visibility)
    "color": "red",
    "outline_color": "black",
    "outline_width": "0.5"
})

renderer = QgsCategorizedSymbolRenderer(field, categories)
stations_layer.setRenderer(renderer)

stations_layer.triggerRepaint()
  

# Get the OSM base map.
tms = r'type=xyz&url=https://tile.openstreetmap.org/{z}/{x}/{y}.png'
osm_layer = QgsRasterLayer(tms,'OSM', 'wms')

# tms = r'https://a.basemaps.cartocdn.com/light_all/{z}/{x}/{y}.png'
# osm_layer = QgsRasterLayer(tms,'OSM', 'xyz')

# Add those layers to the map.
# mylayers = [ osm_layer, amtrak_layer, stations_layer ]
mylayers = [ osm_layer, amtrak_layer, stations_layer ]
for thislayer in mylayers:
  QgsProject.instance().addMapLayer(thislayer)

# Amtrak style -- all the same for now.
amtrak_styles = [ 'orange','1.0'] 
amtrak_rule = QgsRuleBasedRenderer.Rule(None)
symbol = QgsLineSymbol.createSimple({'color': amtrak_styles[0], 'width': amtrak_styles[1]})
rule = QgsRuleBasedRenderer.Rule(symbol)
amtrak_rule.appendChild(rule)

# Apply the rule-based renderer to the layer
renderer = QgsRuleBasedRenderer(amtrak_rule)
amtrak_layer.setRenderer(renderer)
amtrak_layer.triggerRepaint()


# Now going to try to print a specific map.
# Set up some general stuff, I don't really know what this is for.
project = QgsProject.instance()
manager = project.layoutManager()

# Do other incantations.
# manager.addLayout(layout)

# Other printing-related materials.
layout = QgsPrintLayout(project)
layout.initializeDefaults()
layout.setName('Amtrak')
manager.addLayout(layout)

# Add a map item to the layout
map_item = QgsLayoutItemMap(layout)
map_item.setRect(20, 20, 200, 200)

# Set the extent of the map to include all layers
map_item.setExtent(amtrak_layer.extent())
map_item.setLayers([amtrak_layer, stations_layer, osm_layer])

# Print the order of layers
layers = QgsProject.instance().layerTreeRoot().children()
print("Current order.")
for i, layer in enumerate(layers):
    print(f"{i+1}: {layer.name()}")

# Add the map item to the layout
layout.addLayoutItem(map_item)

print(stations_layer.featureCount())
print([f.attributes() for f in stations_layer.getFeatures()])
print([f.geometry().asWkt() for f in stations_layer.getFeatures()])

# Export it.
exporter = QgsLayoutExporter(layout)
# exporter.exportToImage('/tmp/map.png', QgsLayoutExporter.ImageExportSettings()) 
exporter.exportToPdf('/tmp/map.pdf', QgsLayoutExporter.PdfExportSettings()) 

project.write('./map.qgz')

# Finally, exitQgis() is called to remove the
# provider and layer registries from memory
qgs.exitQgis()
