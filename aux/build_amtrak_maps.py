#!/usr/bin/env python3
"""Build the two Amtrak orientation maps used by carfreesc.github.io.

The route geometry comes from Amtrak's official GTFS Schedule feed.  In
particular, the script reads ``shapes.txt`` rather than approximating train
routes with hand-drawn straight segments.  This gives us detailed track-following
alignments while keeping the build reproducible from a public source.

The script produces:

* ``docs/maps/pa_map.png`` -- broad Pennsylvania / Northeast Corridor context;
* ``docs/maps/local_map.png`` -- a closer view of the stations near State College.

By default the current Amtrak GTFS zip is downloaded from Amtrak at build time.
For an offline or pinned build, download that zip yourself and pass ``--gtfs``.

Typical use from ``aux``::

    make amtrak

or::

    python build_amtrak_maps.py --gtfs /path/to/GTFS.zip --prefix-path /usr
"""

import argparse
import csv
import io
import os
import urllib.request
import zipfile
from collections import Counter, defaultdict
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from qgis.core import (
    QgsApplication,
    QgsCategorizedSymbolRenderer,
    QgsCoordinateReferenceSystem,
    QgsCoordinateTransform,
    QgsFeature,
    QgsField,
    QgsGeometry,
    QgsLayoutExporter,
    QgsLayoutItemMap,
    QgsLayoutPoint,
    QgsLayoutSize,
    QgsLineSymbol,
    QgsMarkerSymbol,
    QgsPalLayerSettings,
    QgsPointXY,
    QgsPrintLayout,
    QgsProject,
    QgsRasterLayer,
    QgsRectangle,
    QgsRendererCategory,
    QgsTextBufferSettings,
    QgsTextFormat,
    QgsUnitTypes,
    QgsVectorLayer,
    QgsVectorLayerSimpleLabeling,
)
from qgis.PyQt.QtCore import QVariant
from qgis.PyQt.QtGui import QColor, QFont


AMTRAK_GTFS_URL = "https://content.amtrak.com/content/gtfs/GTFS.zip"
TARGET_CRS = QgsCoordinateReferenceSystem("EPSG:3857")
LL_CRS = QgsCoordinateReferenceSystem("EPSG:4326")

# The map extents are deliberately fixed: these are orientation maps, not maps
# whose scale should jump when Amtrak adds an outlying route to the feed.
MAP_SPECS = {
    "pa_map": {
        "filename": "pa_map.png",
        "bbox": (-80.75, 39.20, -73.55, 41.35),
        "stations_field": "show_statewide",
        "page_mm": (297.0, 148.0),
    },
    "local_map": {
        "filename": "local_map.png",
        "bbox": (-78.85, 39.95, -76.45, 40.98),
        "stations_field": "show_local",
        "page_mm": (240.0, 180.0),
    },
}

# route_long_name in Amtrak GTFS is human-readable, while route_id is opaque
# and can change between feed editions.  Select by name, then choose the
# longest representative shape used by trips on that route.  The longest
# Keystone shape reaches New York; the longest Northeast Regional shape gives
# the through NEC alignment; and the long-distance shapes naturally extend
# beyond our fixed map extent and are clipped by QGIS at render time.
ROUTE_SPECS = [
    {
        "label": "Pennsylvanian",
        "needles": ("pennsylvanian",),
        "color": "#0B57D0",
        "width": 1.9,
        "offset": 0.0,
    },
    {
        "label": "Keystone Service",
        "needles": ("keystone service", "keystone"),
        "color": "#F6C445",
        "width": 1.5,
        "offset": -1.4,
    },
    {
        "label": "Northeast Regional",
        "needles": ("northeast regional",),
        "color": "#D93025",
        "width": 1.5,
        "offset": 1.4,
    },
    {
        "label": "Floridian",
        "needles": ("floridian",),
        "color": "#2E7D32",
        "width": 1.5,
        "offset": 0.0,
    },
]


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--stations",
        default=str(Path(__file__).with_name("amtrak_stations.csv")),
        help="CSV describing which station labels to show",
    )
    parser.add_argument(
        "--gtfs",
        default=None,
        help=(
            "Optional local Amtrak GTFS.zip. If omitted, download the current "
            "feed from Amtrak."
        ),
    )
    parser.add_argument(
        "--gtfs-url",
        default=AMTRAK_GTFS_URL,
        help=f"GTFS URL used when --gtfs is omitted (default: {AMTRAK_GTFS_URL})",
    )
    parser.add_argument(
        "--output-dir",
        default=str(Path(__file__).resolve().parents[1] / "docs" / "maps"),
        help="Directory for pa_map.png and local_map.png",
    )
    parser.add_argument(
        "--prefix-path",
        default="/usr",
        help="QGIS installation prefix (default: /usr, suitable for Arch)",
    )
    parser.add_argument(
        "--dpi",
        type=float,
        default=180.0,
        help="Export resolution (default: 180 dpi)",
    )
    return parser.parse_args()


def open_gtfs(local_path, url):
    """Return a ZipFile for either a pinned local feed or Amtrak's live feed."""
    if local_path:
        path = Path(local_path).expanduser().resolve()
        if not path.exists():
            raise FileNotFoundError(f"GTFS zip not found: {path}")
        print(f"Reading Amtrak GTFS from {path}")
        return zipfile.ZipFile(path)

    print(f"Downloading current Amtrak GTFS from {url}")
    request = urllib.request.Request(
        url,
        headers={"User-Agent": "carfreesc.github.io map builder"},
    )
    with urllib.request.urlopen(request, timeout=60) as response:
        payload = response.read()
    print(f"Downloaded {len(payload) / (1024 * 1024):.1f} MiB")
    return zipfile.ZipFile(io.BytesIO(payload))


def read_csv_from_zip(zf, filename):
    with zf.open(filename) as raw:
        wrapper = io.TextIOWrapper(raw, encoding="utf-8-sig", newline="")
        return list(csv.DictReader(wrapper))


def route_ids_for_spec(route_rows, spec):
    matches = []
    for row in route_rows:
        if str(row.get("route_type", "")).strip() != "2":
            continue
        long_name = (row.get("route_long_name") or "").strip()
        folded = long_name.casefold()
        if any(needle in folded for needle in spec["needles"]):
            matches.append((row["route_id"], long_name))
    if not matches:
        available = sorted(
            {
                (row.get("route_long_name") or "").strip()
                for row in route_rows
                if str(row.get("route_type", "")).strip() == "2"
            }
        )
        raise RuntimeError(
            f"Could not find Amtrak GTFS route for {spec['label']!r}. "
            "Available rail route names include: " + ", ".join(available)
        )
    return matches


def extract_route_shapes(zf):
    """Return one detailed GTFS shape (list of lon/lat pairs) per route spec."""
    route_rows = read_csv_from_zip(zf, "routes.txt")
    trip_rows = read_csv_from_zip(zf, "trips.txt")

    spec_route_ids = {}
    route_id_to_spec = {}
    for spec in ROUTE_SPECS:
        matches = route_ids_for_spec(route_rows, spec)
        ids = {route_id for route_id, _ in matches}
        spec_route_ids[spec["label"]] = ids
        for route_id in ids:
            route_id_to_spec[route_id] = spec["label"]
        names = ", ".join(sorted({name for _, name in matches}))
        print(f"GTFS {spec['label']}: matched route name(s): {names}")

    candidate_shapes = defaultdict(list)
    for row in trip_rows:
        route_id = row.get("route_id")
        shape_id = (row.get("shape_id") or "").strip()
        label = route_id_to_spec.get(route_id)
        if label and shape_id:
            candidate_shapes[label].append(shape_id)

    all_candidate_ids = {
        shape_id
        for values in candidate_shapes.values()
        for shape_id in values
    }
    if not all_candidate_ids:
        raise RuntimeError("Matched Amtrak routes but found no GTFS shape IDs for them")

    points = defaultdict(list)
    with zf.open("shapes.txt") as raw:
        wrapper = io.TextIOWrapper(raw, encoding="utf-8-sig", newline="")
        for row in csv.DictReader(wrapper):
            shape_id = row.get("shape_id")
            if shape_id not in all_candidate_ids:
                continue
            points[shape_id].append(
                (
                    int(row["shape_pt_sequence"]),
                    float(row["shape_pt_lon"]),
                    float(row["shape_pt_lat"]),
                )
            )

    chosen = {}
    for spec in ROUTE_SPECS:
        label = spec["label"]
        counts = Counter(candidate_shapes[label])
        unique_ids = set(counts)
        usable = [shape_id for shape_id in unique_ids if points.get(shape_id)]
        if not usable:
            raise RuntimeError(f"No populated shapes.txt geometry found for {label}")

        # Point count is a simple and robust proxy for the most complete route
        # variant. Break ties in favor of a shape used by more trips.
        shape_id = max(
            usable,
            key=lambda sid: (len(points[sid]), counts[sid]),
        )
        ordered = sorted(points[shape_id], key=lambda item: item[0])
        coords = [(lon, lat) for _, lon, lat in ordered]

        # Line-symbol offsets are defined relative to geometry direction.
        # Normalize predominantly east-west routes west -> east so positive
        # and negative offsets stay on consistent sides of the track instead
        # of swapping when GTFS happens to choose the opposite trip direction.
        if len(coords) >= 2 and coords[0][0] > coords[-1][0]:
            coords.reverse()

        chosen[label] = coords
        print(
            f"GTFS {label}: using shape {shape_id} "
            f"({len(ordered):,} points; used by {counts[shape_id]} trip(s))"
        )

    return chosen


def extract_gtfs_stops(zf):
    stops = {}
    for row in read_csv_from_zip(zf, "stops.txt"):
        stop_id = (row.get("stop_id") or row.get("stop_code") or "").strip().upper()
        stop_code = (row.get("stop_code") or "").strip().upper()
        for code in {stop_id, stop_code} - {""}:
            stops[code] = (
                float(row["stop_lon"]),
                float(row["stop_lat"]),
                (row.get("stop_name") or "").strip(),
            )
    return stops


def load_station_rows(csv_path, gtfs_stops):
    rows = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            code = (row.get("stop_code") or "").strip().upper()
            if code:
                if code not in gtfs_stops:
                    raise RuntimeError(
                        f"Station code {code!r} ({row['name']}) not found in Amtrak GTFS stops.txt"
                    )
                lon, lat, gtfs_name = gtfs_stops[code]
                row["lon"] = lon
                row["lat"] = lat
                row["gtfs_name"] = gtfs_name
            else:
                row["lat"] = float(row["lat"])
                row["lon"] = float(row["lon"])
            row["show_statewide"] = int(row["show_statewide"])
            row["show_local"] = int(row["show_local"])
            rows.append(row)
    return rows


def make_osm_layer():
    tms = "type=xyz&url=https://tile.openstreetmap.org/{z}/{x}/{y}.png"
    layer = QgsRasterLayer(tms, "OpenStreetMap", "wms")
    if not layer.isValid():
        raise RuntimeError("Could not create OpenStreetMap XYZ layer")
    return layer


def create_station_layer(rows):
    layer = QgsVectorLayer("Point?crs=EPSG:4326", "Stations", "memory")
    pr = layer.dataProvider()
    pr.addAttributes([
        QgsField("name", QVariant.String),
        QgsField("kind", QVariant.String),
        QgsField("show_statewide", QVariant.Int),
        QgsField("show_local", QVariant.Int),
    ])
    layer.updateFields()

    feats = []
    for row in rows:
        feat = QgsFeature(layer.fields())
        feat["name"] = row["name"]
        feat["kind"] = row["kind"]
        feat["show_statewide"] = row["show_statewide"]
        feat["show_local"] = row["show_local"]
        feat.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(row["lon"], row["lat"])))
        feats.append(feat)
    pr.addFeatures(feats)
    layer.updateExtents()

    station_symbol = QgsMarkerSymbol.createSimple({
        "name": "circle",
        "color": "#111111",
        "outline_color": "#ffffff",
        "outline_width": "0.5",
        "size": "4.0",
    })
    home_symbol = QgsMarkerSymbol.createSimple({
        "name": "circle",
        "color": "#d93025",
        "outline_color": "#ffffff",
        "outline_width": "0.6",
        "size": "5.0",
    })
    layer.setRenderer(QgsCategorizedSymbolRenderer("kind", [
        QgsRendererCategory("station", station_symbol, "Amtrak station"),
        QgsRendererCategory("home", home_symbol, "State College"),
    ]))

    settings = QgsPalLayerSettings()
    settings.fieldName = "name"
    settings.placement = QgsPalLayerSettings.AroundPoint
    settings.quadOffset = QgsPalLayerSettings.QuadrantAboveRight
    text = QgsTextFormat()
    text.setFont(QFont("Arial", 11))
    text.setSize(11)
    text.setColor(QColor("#111111"))
    buffer = QgsTextBufferSettings()
    buffer.setEnabled(True)
    buffer.setSize(1.2)
    buffer.setColor(QColor("white"))
    text.setBuffer(buffer)
    settings.setFormat(text)
    layer.setLabelsEnabled(True)
    layer.setLabeling(QgsVectorLayerSimpleLabeling(settings))
    return layer


def create_route_layer(spec, points):
    layer = QgsVectorLayer("LineString?crs=EPSG:4326", spec["label"], "memory")
    pr = layer.dataProvider()
    pr.addAttributes([QgsField("name", QVariant.String)])
    layer.updateFields()

    feat = QgsFeature(layer.fields())
    feat["name"] = spec["label"]
    feat.setGeometry(QgsGeometry.fromPolylineXY([
        QgsPointXY(lon, lat) for lon, lat in points
    ]))
    pr.addFeature(feat)
    layer.updateExtents()

    symbol = QgsLineSymbol.createSimple({
        "color": spec["color"],
        "width": str(spec["width"]),
        "capstyle": "round",
        "joinstyle": "round",
        "offset": str(spec.get("offset", 0.0)),
    })
    layer.renderer().setSymbol(symbol)
    return layer


def transformed_extent(bbox_lonlat):
    xmin, ymin, xmax, ymax = bbox_lonlat
    transform = QgsCoordinateTransform(LL_CRS, TARGET_CRS, QgsProject.instance())
    ll = transform.transform(xmin, ymin)
    ur = transform.transform(xmax, ymax)
    return QgsRectangle(ll.x(), ll.y(), ur.x(), ur.y())


def make_map(layers, output_path, bbox_lonlat, page_mm, dpi):
    project = QgsProject.instance()
    layout = QgsPrintLayout(project)
    layout.initializeDefaults()
    layout.setName(output_path.stem)

    page = layout.pageCollection().page(0)
    page.setPageSize(QgsLayoutSize(page_mm[0], page_mm[1], QgsUnitTypes.LayoutMillimeters))
    layout.pageCollection().reflow()

    map_item = QgsLayoutItemMap(layout)
    # Add the item before moving/resizing it. This is the order used by the
    # bikeway exporter and avoids QGIS retaining part of its default map-item
    # geometry, which can leave a white strip along the exported page.
    layout.addLayoutItem(map_item)
    map_item.attemptMove(QgsLayoutPoint(0, 0, QgsUnitTypes.LayoutMillimeters))
    map_item.attemptResize(QgsLayoutSize(page_mm[0], page_mm[1], QgsUnitTypes.LayoutMillimeters))
    map_item.setFrameEnabled(False)
    # QGIS expects topmost layer first here. OSM belongs at the bottom.
    map_item.setLayers(layers)
    map_item.setExtent(transformed_extent(bbox_lonlat))

    settings = QgsLayoutExporter.ImageExportSettings()
    settings.dpi = dpi
    # Crop to the map item itself. This avoids a white strip if QGIS retains
    # any extra page canvas around a custom-sized layout page.
    settings.cropToContents = True
    result = QgsLayoutExporter(layout).exportToImage(str(output_path), settings)
    if result != QgsLayoutExporter.Success:
        raise RuntimeError(f"Failed to export {output_path}")


def main():
    args = parse_args()
    stations_path = Path(args.stations).expanduser().resolve()
    output_dir = Path(args.output_dir).expanduser().resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    if not stations_path.exists():
        raise SystemExit(f"Station CSV not found: {stations_path}")

    # Parse the portable GTFS material before initializing QGIS. This also makes
    # GTFS errors much easier to read than errors emitted during rendering.
    with open_gtfs(args.gtfs, args.gtfs_url) as zf:
        route_shapes = extract_route_shapes(zf)
        gtfs_stops = extract_gtfs_stops(zf)
    station_rows = load_station_rows(stations_path, gtfs_stops)

    QgsApplication.setPrefixPath(args.prefix_path, True)
    qgs = QgsApplication([], False)
    qgs.initQgis()

    try:
        project = QgsProject.instance()
        project.clear()
        project.setCrs(TARGET_CRS)

        stations_layer = create_station_layer(station_rows)
        osm_layer = make_osm_layer()
        route_layers = [
            create_route_layer(spec, route_shapes[spec["label"]])
            for spec in ROUTE_SPECS
        ]

        project.addMapLayer(osm_layer)
        for layer in route_layers:
            project.addMapLayer(layer)
        project.addMapLayer(stations_layer)

        for spec in MAP_SPECS.values():
            stations_layer.setSubsetString(f'"{spec["stations_field"]}" = 1')
            output_path = output_dir / spec["filename"]
            # Topmost first: station symbols, route lines, OSM background.
            layer_order = [stations_layer] + list(reversed(route_layers)) + [osm_layer]
            make_map(layer_order, output_path, spec["bbox"], spec["page_mm"], args.dpi)
            print(f"Wrote {output_path}")

        stations_layer.setSubsetString("")

    finally:
        qgs.exitQgis()


if __name__ == "__main__":
    main()
