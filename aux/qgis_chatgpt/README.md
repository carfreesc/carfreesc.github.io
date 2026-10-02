# Centre Region bikeway map generator

This directory contains the PyQGIS machinery used to turn the CRCOG
`CR_Bikeways.json` GIS export into static route maps for
[carfreesc.github.io](https://carfreesc.github.io/).

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

Published PNGs go to `../../docs/maps/bikeways/`.

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
git add aux/qgis_chatgpt notes/gettingaround.md docs/gettingaround.html docs/maps/bikeways .gitignore
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
