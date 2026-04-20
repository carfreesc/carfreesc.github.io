import qgis

layers = QgsProject.instance().mapLayers().values()
for layer in layers:
    if "ikew" in layer.name():
        mylayer = layer

print(f"Got {mylayer.name()}")
# for feature in mylayer.getFeatures():
 #   print(f"Feature ID: {feature.id()}, Geometry: {feature.geometry().asWkt()}")

all = list(mylayer.getFeatures())
first = all[0]

fields = mylayer.fields()

print(first['Path Description'])

#for thing in all:
#    print(thing['Path Description'])
    

feature_id = first.id()
mylayer.selectByIds([feature_id])

# Create a new temporary layer containing only the selected feature
selected_features = mylayer.selectedFeatures()
if selected_features:
    single_feature_layer = QgsVectorLayer("Polygon", "Single Feature", "memory")
    single_feature_layer.dataProvider().addFeatures(selected_features)
    QgsProject.instance().addMapLayer(single_feature_layer)
else:
    print("No features selected")
    
iface.mapCanvas().setExtent(single_feature_layer.extent())
iface.mapCanvas().refresh()

### ChatGPT to create a print layout
from qgis.core import QgsPrintLayout, QgsLayoutItemMap, QgsLayoutExporter, QgsProject, QgsLayoutPoint, QgsLayoutItemLabel
from PyQt5.QtGui import QFont

# Create a new print layout
project = QgsProject.instance()
layout = QgsPrintLayout(project)
layout.initializeDefaults()
layout.setName("Single Feature Map")
project.layoutManager().addLayout(layout)

# Add a map item that shows the selected feature  
    
map_item = QgsLayoutItemMap(layout)
map_item.setRect(20, 20, 200, 200)  # Position and size on the page
map_item.setExtent(iface.mapCanvas().extent())  # Match the map canvas extent to the feature
layout.addLayoutItem(map_item)

# Optional: Add a title
title = QgsLayoutItemLabel(layout)
title.setText("Single Bike Path")
title.setFont(QFont("Arial", 18))
title.adjustSizeToText()
title.attemptMove(QgsLayoutPoint(20, 10))  # Position the title
layout.addLayoutItem(title)

# Export the layout to a PDF file
exporter = QgsLayoutExporter(layout)
exporter.exportToPdf('/tmp/out.pdf', QgsLayoutExporter.PdfExportSettings())

# Reset everything
for name in dir():
    if not name.startswith('_'):
        del globals()[name]
