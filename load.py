# This script handles all reading of YAML files and generation of map scripts.
import yaml

def read_yaml_file(file_path):
  with open(file_path, 'r') as file:
    try:
      data = yaml.safe_load(file)
      return data
    except yaml.YAMLError as e:
      print(f"Error reading YAML file: {e}")
      return None

# Generate labels for neighborhoods and developments.

# Generate labels for CATA routes.
    
# Generate markers for grocery stores.
grocery_file_path = "grocery.yaml"  # Replace with your YAML file path
grocery_data = read_yaml_file(grocery_file_path)

if yaml_data is not None:
  print("YAML data:")
  print(yaml_data)
