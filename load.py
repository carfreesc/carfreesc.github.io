import yaml

def read_yaml_file(file_path):
  with open(file_path, 'r') as file:
    try:
      data = yaml.safe_load(file)
      return data
    except yaml.YAMLError as e:
      print(f"Error reading YAML file: {e}")
      return None

# Example usage
yaml_file_path = "grocery.yaml"  # Replace with your YAML file path
yaml_data = read_yaml_file(yaml_file_path)

if yaml_data is not None:
  print("YAML data:")
  print(yaml_data)
