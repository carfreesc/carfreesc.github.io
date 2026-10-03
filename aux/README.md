# Map generation tools

This directory contains the PyQGIS machinery used to turn the CRCOG
`CR_Bikeways.json` GIS export into static route maps for
[carfreesc.github.io](https://carfreesc.github.io/).

Run the commands below from `aux/` (or use `make -C aux …` from the repository root).

The important distinction is:

* **CRCOG features** are the source GIS data and may split one useful route into
  several records or names.
* **Site routes** are the editorial units used by the guide. They are defined in
  `site_routes.txt` and may combine several CRCOG `Map Name` values.

The generated website never depends on the numbered review filenames. Published
maps get stable names derived from the site-route heading, such as
`orchard-park.png` and `tudek-circleville.png`.

## Files

* `export_bikeway_maps.py` -- standalone PyQGIS exporter.
* `CR_Bikeways.json` -- current CRCOG bikeway export. Replace this when CRCOG
  publishes a newer version.
* `site_routes.txt` -- the hand-maintained list of route units used by the site.
* `Makefile` -- convenient commands described below.
* `review/` -- generated numbered maps and thumbnail index; ignored by Git.
* `.site-build/` -- temporary numbered copies made while producing site assets;
  ignored by Git.

Published PNGs go to `../docs/maps/bikeways/`.

## Normal workflow

From this directory:

```sh
make review
```

This renders the full CRCOG inventory, applying the merge rules in
`site_routes.txt`, and writes a numbered thumbnail browser to
`review/index.html`. Open it with e.g.

```sh
xdg-open review/index.html
```

Use the gallery to decide which CRCOG records belong together. Edit
`site_routes.txt` as needed. Its format is deliberately simple:

```text
Foster Avenue Bikeway:
  East Foster Ave Bike Route
  West Foster Ave Bike Lane
  West Foster Ave Bike Route
  Sidney Friedman Parklet Path
```

A one-item group is valid and means "publish this route as-is":

```text
Orchard Park:
  Orchard Park Bikeway
```

When the groups look right, run:

```sh
make site
```

That command:

1. removes stale generated bikeway PNGs from `docs/maps/bikeways/`;
2. exports only the groups in `site_routes.txt`;
3. copies them there under stable URL-friendly filenames;
4. writes a manifest alongside the PNGs; and
5. rebuilds `docs/gettingaround.html` from `notes/gettingaround.md`.

Then inspect and commit in the repository root:

```sh
git status
git diff
git add aux notes/gettingaround.md docs/gettingaround.html docs/maps/bikeways .gitignore
git commit -m "Update bikeway maps"
git push
```

## Updating the CRCOG data later

Replace `CR_Bikeways.json` with the new CRCOG export, then run:

```sh
make review
```

Check `review/index.html` for renamed, added, removed, or regrouped routes. Update
`site_routes.txt` if necessary, then run `make site` and inspect the diff.

Because the site uses stable filenames based on the headings in
`site_routes.txt`, ordinary changes to CRCOG feature IDs or to the numbered
review order do not require changes to the Markdown.

## Useful commands

```sh
make list      # inspect grouping without rendering maps
make review    # render everything + review/index.html
make site      # render curated site maps + rebuild gettingaround.html
make clean     # remove only local review/temp output
```

You can override the Python executable or QGIS prefix if necessary:

```sh
make site PYTHON=/usr/bin/python QGIS_PREFIX=/usr
```

The script also has direct command-line options; run:

```sh
python export_bikeway_maps.py --help
```

## Rendering details

The source data and OSM basemap use EPSG:3857. Each map is cropped to the route
with extra geographic context and adjusted to an A4-landscape aspect ratio.
The route itself is colored by CRCOG `Path Type`. Maps have no internal title,
because the surrounding web page identifies the route.

QGIS/GDAL may print this warning during PNG export:

```text
ERROR 6: The PNG driver does not support update access to existing datasets.
```

If the PNG is successfully created and the exporter continues to the next
route, this is harmless GDAL chatter and can be ignored.

## Homepage interactive overview map

The homepage Leaflet map is a separate product from the individual static
bikeway PNGs. It combines four systems in one interactive map:

* the full CRCOG bikeway layer (`CR_Bikeways.json`);
* CATA fixed-route geometry;
* the Beaver Avenue and College Avenue Penn State shuttle tracks; and
* the Boalsburg, Houserville/Lemont, and Centre Area West CATAGO zones; and
* hand-maintained landmark pins from `overview_sources/landmarks.csv`.

The additional source files live under `overview_sources/`. The generated web
payload is `../docs/maps/overview/overview-data.js`; the Leaflet behavior and
styles live beside it as `overview-map.js` and `overview-map.css`.

### Landmarks

`overview_sources/landmarks.csv` is deliberately simple so landmarks can be
added without touching Python or JavaScript. It has five columns:

```text
name,lat,lon,category,notes
Old Main,40.79646,-77.86282,campus,Penn State
Mount Nittany Medical Center,40.819137,-77.843297,hospital,
```

Coordinates are WGS84 decimal degrees. `name`, `lat`, and `lon` are required.
`category` and `notes` may be left blank. Blank categories become `landmark`.
Lines beginning with `#` and blank lines are ignored.

The built-in pin colors recognize `hospital`, `campus`, `transit`, `park`,
`shopping`, and `landmark`. Other category names are allowed and simply use the
neutral landmark pin; their category name still appears in the popup. The
landmark layer has its own checkbox in Leaflet's layer control and is on by
default. Hovering a pin shows its name, and clicking it opens the category and
optional notes.

To rebuild the interactive map after replacing any source data, run:

```sh
make overview
```

This regenerates `overview-data.js` and then rebuilds `docs/index.html`. Open
`docs/index.html` directly, or serve `docs/` with a small local web server if
you want to test it exactly as GitHub Pages will serve it:

```sh
python -m http.server --directory ../docs 8000
```

Then visit <http://localhost:8000/>.

The map uses Leaflet 1.9.4 from jsDelivr and OpenStreetMap tiles. All overlay
geometry is stored locally in the repository, so future data refreshes only
require replacing the GIS source files and rerunning `make overview`.

## Amtrak orientation maps

`build_amtrak_maps.py` rebuilds the two static Amtrak maps used on the
getting-here page:

* `../docs/maps/pa_map.png` -- the broad Pennsylvania / Northeast Corridor
  view; and
* `../docs/maps/local_map.png` -- the zoomed central-Pennsylvania view.

The route geometry comes from Amtrak's official GTFS Schedule feed at
`https://content.amtrak.com/content/gtfs/GTFS.zip`. The script reads
`routes.txt`, `trips.txt`, and especially `shapes.txt`, so the rendered lines
follow Amtrak's detailed published route alignments rather than hand-drawn
straight segments. Amtrak station coordinates are likewise read from
`stops.txt`; only the State College reference point is hand-specified.

The display list lives in `amtrak_stations.csv`. Its `stop_code` values select
Amtrak stations by their three-letter code, while the two `show_*` columns
control which labels appear on the statewide and local maps.

The statewide map labels State College plus Pittsburgh, Altoona, Tyrone,
Huntingdon, Lewistown, Harrisburg, Middletown, Philadelphia, and New York. The
local map shows State College and the nearby Altoona, Tyrone, Huntingdon,
Lewistown, Harrisburg, and Middletown stations.

To download the current feed and rebuild both maps:

```sh
make amtrak
```

For a pinned or offline build, download an Amtrak GTFS zip and run:

```sh
python build_amtrak_maps.py --gtfs /path/to/GTFS.zip --prefix-path /usr
```

The PNGs overwrite the existing files in `docs/maps/`, so the existing Markdown
and generated HTML continue to use the new maps without any path changes. If
only the maps changed, no Pandoc rebuild is needed.
