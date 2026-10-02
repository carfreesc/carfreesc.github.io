# Centre Region Bikeway Map Exporter

This little package turns CRCOG's `CR_Bikeways.json` GIS file into a collection of individual bikeway maps.

For each route, `export_bikeway_maps.py`:

- loads the CRCOG bikeway GeoJSON;
- draws the route over the standard OpenStreetMap basemap;
- chooses a sensible bounding box with some surrounding geographic context;
- combines multiple GIS features when they have the same route name;
- applies any custom merges listed in `bikeway_merges.txt`;
- exports a borderless, untitled PNG with a numbered filename;
- writes `manifest.csv`; and
- writes `index.html`, a thumbnail gallery that is convenient for browsing the results.

The script assumes the CRCOG data are in `EPSG:3857`, as in the current download.

## Files

The useful files are:

```text
export_bikeway_maps.py   main PyQGIS exporter
bikeway_merges.txt       hand-edited list of routes to combine/select
CR_Bikeways.json         current CRCOG bikeway data
```

The output directory (by default `bikeway_maps/`) contains:

```text
001 - Some Route.png
002 - Another Route.png
...
manifest.csv
index.html
```

Open `index.html` in a browser to browse thumbnails together with their route names. Clicking a thumbnail opens the full PNG.

## Requirements

This is a standalone PyQGIS script, so QGIS and its Python bindings must be installed. It was written for the Arch Linux-style QGIS installation prefix `/usr`.

The OpenStreetMap background is downloaded while the maps are rendered, so an Internet connection is required.

## Normal use

From the directory containing the script, run:

```bash
python export_bikeway_maps.py \
    --input raw_data/CR_Bikeways.json \
    --output bikeway_maps
```

Adjust the input path if `CR_Bikeways.json` lives somewhere else.

Then browse the results with, for example:

```bash
xdg-open bikeway_maps/index.html
```

The maps themselves deliberately contain no title. The numbered filename and the HTML index identify the route.

## Custom merges

The script automatically looks for `bikeway_merges.txt` beside `export_bikeway_maps.py`.

The format is:

```text
Name I want for the combined output:
  Exact CRCOG Map Name 1
  Exact CRCOG Map Name 2
  Exact CRCOG Map Name 3
```

For example:

```text
Foster Avenue Bikeway:
  East Foster Ave Bike Route
  West Foster Ave Bike Lane
  West Foster Ave Bike Route
  Sidney Friedman Parklet Path
```

That produces one map called `Foster Avenue Bikeway` containing all four source routes.

The indented source names must match the `Map Name` field in `CR_Bikeways.json` exactly. Blank lines and lines beginning with `#` are ignored.

A source route should not appear in more than one custom group.

### Including a route without merging it

A group is allowed to contain only one source route:

```text
Park Ave Bike Lane:
  Park Ave Bike Lane
```

This is especially useful with `--merge-file-only` (below): it means "include this route in my curated set," even though it does not need to be merged with anything.

## Export only the routes in `bikeway_merges.txt`

To use the merge file as a curated list and export nothing else:

```bash
python export_bikeway_maps.py \
    --input raw_data/CR_Bikeways.json \
    --output bikeway_maps \
    --merge-file-only
```

Every heading in `bikeway_merges.txt` becomes one output map. A heading may combine several CRCOG routes or contain just one route.

Without `--merge-file-only`, the custom merges are still applied, but all the other CRCOG bikeways are exported as well.

## Using a different merge file

Normally the script uses `bikeway_merges.txt` beside the script. To use another file:

```bash
python export_bikeway_maps.py \
    --merge-file experimental_merges.txt
```

This can be combined with `--merge-file-only`.

## Useful testing commands

List the route groups without drawing anything:

```bash
python export_bikeway_maps.py --list-only
```

Export only routes whose resulting name contains some text:

```bash
python export_bikeway_maps.py --only "Bellefonte Central"
```

Export only the first few selected routes:

```bash
python export_bikeway_maps.py --limit 3
```

These options can be combined. They are useful when testing a new merge or formatting change without regenerating every PNG.

## Map framing and resolution

The default output is A4 landscape at 180 dpi. The map fills the page, so there is essentially no border.

The exporter adds surrounding context automatically. For unusual cases, these options can be adjusted:

```text
--dpi 180
--padding 0.12
--min-padding 250
```

`--padding` is proportional to the route's span. `--min-padding` ensures that very short routes still show enough nearby streets to be geographically understandable.

## Updating when CRCOG releases new data

The intended refresh workflow is:

1. Replace `CR_Bikeways.json` with the new CRCOG version.
2. Run `python export_bikeway_maps.py --list-only` if you want to inspect the grouping first.
3. Run the exporter normally.
4. Open `bikeway_maps/index.html` and visually inspect the maps.
5. If CRCOG has split or renamed routes, update `bikeway_merges.txt` and rerun.

The numbered filenames are assigned from the alphabetized route list. They are useful for browsing, but the durable merge configuration uses CRCOG route names rather than numbers, because numbers can change when the underlying data change.

## Built-in special cases

In addition to `bikeway_merges.txt`, the Python script currently contains a few built-in grouping rules:

- `Allen St Mall Path 1` and `Allen St Mall Path 2` are combined as `Allen St Mall Path`.
- `Harvest Fields Trail` is split into its individually described trails.
- `State Game Lands Trail` is split into its individually described trails.

If CRCOG changes the structure of those records, the constants near the top of `export_bikeway_maps.py` (`MERGE_GROUPS` and `SPLIT_BY_DESCRIPTION`) are the places to adjust them.

## A harmless PNG warning

Some QGIS/GDAL versions print this repeatedly during export:

```text
ERROR 6: The PNG driver does not support update access to existing datasets.
```

If the PNG files are being produced correctly and the exporter continues to the next route, this warning can be ignored. It is GDAL complaining about an attempted in-place update of PNG metadata, not a failed map export.

## If PyQGIS cannot be found

The script defaults to the QGIS prefix `/usr`:

```text
--prefix-path /usr
```

If QGIS is installed somewhere else, specify its prefix explicitly:

```bash
python export_bikeway_maps.py --prefix-path /path/to/qgis/prefix
```

## Typical personal workflow

For maintaining a hand-selected set of maps, the easiest routine is:

1. Browse the full `index.html` once.
2. Put the routes you care about into `bikeway_merges.txt`, combining pieces where appropriate.
3. Thereafter run with `--merge-file-only`.
4. When CRCOG publishes an update, replace the JSON and rerun.

That leaves all of the subjective route grouping in one small, human-readable text file while the PyQGIS script handles the GIS and map export automatically.
