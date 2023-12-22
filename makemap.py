import yaml
import random

allmaps = ["grocery","bus","path-orchard"]

def read_yaml_file(file_path):
  with open(file_path, 'r') as infile:
    data = yaml.load(infile, Loader=yaml.Loader)
  return data

# String for markers.
marker_str = "var marker = new L.marker([{lat}, {long}]).addTo(map{id}).bindPopup(\"{name}\");"
route_str = """var route = new L.GPX('maps/gpx/{file}', {{
    async: true,
    marker_options: {{
      startIconUrl: false,
      endIconUrl: false,
      shadowUrl: false,
    }},
    polyline_options: {{
      color: '{color}',
      weight: 5,
      opacity: 0.7,
    }},
  }}).addTo(map{id});"""

def fill_map_template(info,outfile_name):

  # Read in the template file
  template_path = "maps/blankmap.div"
  with open(template_path, 'r') as file:
    template = file.read()

  id_random = str(random.randint(100000, 999999)) # Random ID for this map to avoid collisions on the page.

  fill = {}

  # First, grab the map metadata and fill it in.  (Also remove it from the list.)
  mapinfo = info.pop('metadata')
  fill['width'] = mapinfo['width']
  fill['height'] = mapinfo['height']
  fill['center_lat'] = mapinfo['lat']
  fill['center_long'] = mapinfo['long']
  fill['zoom'] = mapinfo['zoom']
  fill['id'] = id_random

  # Loop through all the stuff listed in the YAML file.
  additions = ""
  for item in info:
    thisinfo = info[item]
    thisinfo['id'] = id_random

    # If it's a marker, add it.
    if thisinfo['type'] == 'marker':
      thisstr = marker_str.format(**thisinfo)
      additions += "  "+thisstr+"\n"

    # If it's a rotue, add it.
    if thisinfo['type'] == 'route':
      thisstr = route_str.format(**thisinfo)
      additions += "  "+thisstr+"\n"

  # Finally, fill in the template and write it out.
  fill['additions'] = additions

  filled_map = template.format(**fill)
  with open(outfile_name, 'w') as outfile:
    outfile.write(filled_map)

  return

def refresh_map( map_name ):
  # map_name = "bus"
  map_in = f"maps/data/{map_name}.yaml"
  map_out = f"maps/output/{map_name}.div"

  # Read in map file.
  map_data = read_yaml_file(map_in)

  fill_map_template(map_data,map_out)

  return

for thismap in allmaps:
  print(f"Updating map \"{thismap}\".")
  refresh_map( thismap )
