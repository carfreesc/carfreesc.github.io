import re
import sys


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

    return

# Grab the actual path name from the unix filepath.
first_argument = sys.argv[1]
pattern = re.compile(r'\./(.*?)_raw.gpx')
matched = pattern.search(first_argument)
short = matched.group(1)

# Clear out waypoints from the path.
delete_wpt(short)
