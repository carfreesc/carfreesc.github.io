import re

def delete_wpt( pathname ):

    path_in = pathname+"_raw"+".gpx"
    path_out = pathname+".gpx"

    with open(path_in, 'r') as infile:
      content = infile.read()

    # Use regular expressions to find and delete content between <div> and </div>
    pattern = re.compile(r'<wpt.*?</wpt>')
    modified_content = re.sub(pattern, '', content)

    # Write the modified content back to the file
    with open(path_out, 'w') as file:
        file.write(modified_content)


delete_wpt("bike/path-orchard")
