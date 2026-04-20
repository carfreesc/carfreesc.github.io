# python makemap.py
# cd maps/gpx
# bash stripall.sh
# cd ../..
pandoc --template=template.htm --lua-filter=include-files.lua --metadata title="Do Getting to State College" -s -o live_site/index.htm notes.md
