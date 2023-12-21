import yaml

def read_yaml_file(file_path):
    with open(file_path, 'r') as infile:
        data = yaml.load(infile, Loader=yaml.Loader)
    return data

map_name = "grocery"
map_in = f"maps/data/{map_name}.yaml"
map_out = f"maps/output/{map_name}.div"

# String for markers.
marker_str = "var marker = L.marker([40.7848927, -77.8685289]).addTo(map).bindPopup(\"International Market\")"

# Read in map file.
map_data = read_yaml_file(map_in)

# Read in the template file
template_path = "maps/template.htm"
with open(template_path, 'r') as file:
  template = file.read()

def fill_map_template(info,outfile_name):
  fill = {}

  # First, grab the map metadata and fill it in.  (Also remove it from the list.)
  mapinfo = info.pop('metadata')
  fill['width'] = mapinfo['width']
  fill['height'] = mapinfo['height']
  fill['center_lat'] = mapinfo['lat']
  fill['center_long'] = mapinfo['long']

  fill['additions'] = ""

  # Finally, fill in the template and write it out.
  filled_map = template.format(**fill)
  with open(outfile_name, 'w') as outfile:
    outfile.write(filled_map)

  return

fill_map_template(map_data,map_out)

# Example usage:
file_path = "grocery.yaml"
yaml_data = read_yaml_file(file_path)

# Now 'yaml_data' contains the data from the YAML file
print(yaml_data)
