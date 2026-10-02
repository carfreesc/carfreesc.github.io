#!/usr/bin/env python3
"""Export one PNG map per Centre Region bikeway.

This is intended to be run as a standalone PyQGIS script, e.g. on Arch Linux:

    python export_bikeway_maps.py \
        --input raw_data/CR_Bikeways.json \
        --output bikeway_maps

The script:
  * loads the CRCOG bikeway GeoJSON in EPSG:3857;
  * groups multiple JSON features which share the same "Map Name";
  * applies a small number of explicit merge/split rules below;
  * renders each route over the standard OpenStreetMap XYZ layer;
  * chooses a padded, aspect-correct extent for each route;
  * writes one numbered, named PNG per route, plus a manifest.csv and index.html;
  * optionally reads human-editable merge rules from bikeway_merges.txt.

For quick testing, use e.g.:

    python export_bikeway_maps.py --only "Bellefonte Central" --limit 2

Edit MERGE_GROUPS / SPLIT_BY_DESCRIPTION if CRCOG changes how routes are
partitioned in a future export.
"""

import argparse
import csv
import html
import os
import re
from collections import defaultdict
from pathlib import Path
from urllib.parse import quote

# Headless rendering works more reliably when no X display is present.
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from qgis.PyQt.QtGui import QFont
from qgis.core import (
    QgsApplication,
    QgsCoordinateReferenceSystem,
    QgsFeature,
    QgsGeometry,
    QgsLayoutExporter,
    QgsLayoutItemLabel,
    QgsLayoutItemMap,
    QgsLayoutItemPage,
    QgsLayoutPoint,
    QgsLayoutSize,
    QgsLineSymbol,
    QgsPrintLayout,
    QgsProject,
    QgsRasterLayer,
    QgsRectangle,
    QgsRuleBasedRenderer,
    QgsTextFormat,
    QgsVectorLayer,
)


# ---------------------------------------------------------------------------
# Route grouping rules
# ---------------------------------------------------------------------------

# Features with exactly the same "Map Name" are merged automatically.
# These are additional cases where two different map names are clearly pieces
# of the same named facility.
MERGE_GROUPS = {
    "Allen St Mall Path": {
        "Allen St Mall Path 1",
        "Allen St Mall Path 2",
    },
}

# These two Map Name values are really umbrella trail systems; their
# Path Description values name distinct trails, so export those separately.
SPLIT_BY_DESCRIPTION = {
    "Harvest Fields Trail",
    "State Game Lands Trail",
}

# Add route names here if you ever want to suppress them without editing data.
SKIP_ROUTE_NAMES = set()


# Colors retain the spirit of the old script and add coverage for the newer
# path types now present in CR_Bikeways.json.
BIKE_STYLES = {
    "Bike Lane": ("#00BFFF", "1.5"),
    "Bike Route": ("#89CFF0", "1.5"),
    "Shared Use Path": ("#0000FF", "1.5"),
    "Single Track": ("#7B2CBF", "1.5"),
    "State Game Lands Trail": ("#6A4C93", "1.5"),
    "State Bike Route": ("#1E90FF", "1.5"),
}
FALLBACK_STYLE = ("#0057B8", "1.5")

# A4 landscape map frame dimensions (millimetres).  Fill the page so the
# exported PNG has essentially no white border.
MAP_X_MM = 0.0
MAP_Y_MM = 0.0
MAP_W_MM = 297.0
MAP_H_MM = 210.0
MAP_ASPECT = MAP_W_MM / MAP_H_MM


def text_value(value):
    """Turn a QGIS attribute value into a useful Python string."""
    if value is None:
        return ""
    s = str(value).strip()
    if s.upper() in {"NULL", "NONE"}:
        return ""
    return s


def safe_filename(name):
    """Human-readable filename, but safe for slashes and common filesystems."""
    name = name.replace("/", " - ").replace("\\", " - ")
    name = re.sub(r'[:*?"<>|]+', "-", name)
    name = re.sub(r"\s+", " ", name).strip().rstrip(".")
    return name or "Unnamed route"


def load_merge_file(path):
    """Read a simple human-editable merge file.

    Format:

        Foster Avenue Bikeway:
          East Foster Ave Bike Route
          West Foster Ave Bike Lane
          West Foster Ave Bike Route
          Sidney Friedman Parklet Path

    Blank lines and lines beginning with # are ignored.
    """
    groups = {}
    if path is None:
        return groups

    path = Path(path).expanduser()
    if not path.exists():
        return groups

    current_name = None
    for lineno, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        stripped = raw.strip()
        if not stripped or stripped.startswith("#"):
            continue

        # A non-indented line ending in ':' starts a new output group.
        if raw == raw.lstrip() and stripped.endswith(":"):
            current_name = stripped[:-1].strip()
            if not current_name:
                raise ValueError(f"Empty merge-group name in {path}:{lineno}")
            if current_name in groups:
                raise ValueError(f"Duplicate merge-group name {current_name!r} in {path}:{lineno}")
            groups[current_name] = set()
            continue

        if current_name is None:
            raise ValueError(
                f"Source route appears before any group heading in {path}:{lineno}: {stripped!r}"
            )

        groups[current_name].add(stripped)

    empty = [name for name, sources in groups.items() if not sources]
    if empty:
        raise ValueError(f"Merge group(s) with no source routes in {path}: {', '.join(empty)}")

    # Make sure one source name is not assigned to two external groups.
    seen = {}
    for output_name, source_names in groups.items():
        for source_name in source_names:
            if source_name in seen:
                raise ValueError(
                    f"Source route {source_name!r} appears in both {seen[source_name]!r} "
                    f"and {output_name!r} in {path}"
                )
            seen[source_name] = output_name

    return groups


def build_merge_lookup(extra_merge_groups=None):
    lookup = {}
    combined = dict(MERGE_GROUPS)
    if extra_merge_groups:
        combined.update(extra_merge_groups)

    for output_name, source_names in combined.items():
        for source_name in source_names:
            if source_name in lookup:
                raise ValueError(f"Merge rule repeated for {source_name!r}")
            lookup[source_name] = output_name
    return lookup


def group_features(bike_layer, extra_merge_groups=None):
    """Return {display_route_name: [QgsFeature, ...]}."""
    groups = defaultdict(list)
    merge_lookup = build_merge_lookup(extra_merge_groups)

    fields = bike_layer.fields()
    has_objectid = fields.indexFromName("OBJECTID") >= 0
    has_description = fields.indexFromName("Path Description") >= 0

    for feature in bike_layer.getFeatures():
        map_name = text_value(feature["Map Name"])
        object_id = feature["OBJECTID"] if has_objectid else feature.id()

        if not map_name:
            # There are several genuinely unnamed records in the current file.
            # Keep them separate rather than pretending we know which belong
            # together.
            route_name = f"Unnamed route {object_id}"
        else:
            merged_name = merge_lookup.get(map_name, map_name)
            if map_name in SPLIT_BY_DESCRIPTION:
                description = text_value(feature["Path Description"]) if has_description else ""
                suffix = description or f"feature {object_id}"
                route_name = f"{merged_name} - {suffix}"
            else:
                route_name = merged_name

        if route_name not in SKIP_ROUTE_NAMES:
            groups[route_name].append(QgsFeature(feature))

    return dict(groups)


def make_renderer():
    """Rule-based line renderer keyed by Path Type."""
    root = QgsRuleBasedRenderer.Rule(None)

    for path_type, (color, width) in BIKE_STYLES.items():
        symbol = QgsLineSymbol.createSimple({"color": color, "width": width})
        rule = QgsRuleBasedRenderer.Rule(symbol)
        escaped = path_type.replace("'", "''")
        rule.setFilterExpression(f'"Path Type" = \'{escaped}\'')
        root.appendChild(rule)

    fallback_color, fallback_width = FALLBACK_STYLE
    fallback_symbol = QgsLineSymbol.createSimple(
        {"color": fallback_color, "width": fallback_width}
    )
    fallback_rule = QgsRuleBasedRenderer.Rule(fallback_symbol)
    fallback_rule.setIsElse(True)
    root.appendChild(fallback_rule)

    return QgsRuleBasedRenderer(root)


def make_route_layer(source_layer, route_name, features):
    """Copy one route's features to a temporary MultiLineString memory layer."""
    crs = source_layer.crs()
    layer = QgsVectorLayer(
        f"MultiLineString?crs={crs.authid()}",
        route_name,
        "memory",
    )
    if not layer.isValid():
        raise RuntimeError(f"Could not create memory layer for {route_name}")

    provider = layer.dataProvider()
    provider.addAttributes(source_layer.fields())
    layer.updateFields()

    new_features = []
    for feature in features:
        new_feature = QgsFeature(layer.fields())
        new_feature.setAttributes(feature.attributes())
        geometry = QgsGeometry(feature.geometry())
        # The GeoJSON mixes LineString and MultiLineString.  A single memory
        # geometry type keeps the layer valid and makes all pieces render.
        geometry.convertToMultiType()
        new_feature.setGeometry(geometry)
        new_features.append(new_feature)

    added = provider.addFeatures(new_features)
    ok = added[0] if isinstance(added, tuple) else bool(added)
    if not ok:
        raise RuntimeError(f"Could not copy features for {route_name}")

    layer.updateExtents()
    layer.setRenderer(make_renderer())
    return layer


def padded_extent(extent, pad_fraction, min_padding_m):
    """Add geographic context and force the extent to match the map frame."""
    if extent.isEmpty():
        raise ValueError("Route has an empty extent")

    width = max(extent.width(), 1.0)
    height = max(extent.height(), 1.0)

    # Give tiny paths enough surrounding street context, while scaling context
    # naturally for long routes.
    padding = max(min_padding_m, pad_fraction * max(width, height))

    xmin = extent.xMinimum() - padding
    xmax = extent.xMaximum() + padding
    ymin = extent.yMinimum() - padding
    ymax = extent.yMaximum() + padding

    width = xmax - xmin
    height = ymax - ymin
    cx = (xmin + xmax) / 2.0
    cy = (ymin + ymax) / 2.0

    current_aspect = width / height
    if current_aspect < MAP_ASPECT:
        width = height * MAP_ASPECT
    else:
        height = width / MAP_ASPECT

    return QgsRectangle(
        cx - width / 2.0,
        cy - height / 2.0,
        cx + width / 2.0,
        cy + height / 2.0,
    )


def add_label(layout, text, x, y, width, height, point_size):
    label = QgsLayoutItemLabel(layout)
    label.setText(text)
    fmt = QgsTextFormat()
    font = QFont("DejaVu Sans")
    fmt.setFont(font)
    fmt.setSize(point_size)
    label.setTextFormat(fmt)
    layout.addLayoutItem(label)
    label.attemptMove(QgsLayoutPoint(x, y))
    label.attemptResize(QgsLayoutSize(width, height))
    return label


def export_route(
    project,
    osm_layer,
    source_layer,
    route_name,
    features,
    output_path,
    dpi,
    pad_fraction,
    min_padding_m,
):
    route_layer = make_route_layer(source_layer, route_name, features)
    project.addMapLayer(route_layer, False)

    try:
        layout = QgsPrintLayout(project)
        layout.initializeDefaults()
        page = layout.pageCollection().page(0)
        page.setPageSize("A4", QgsLayoutItemPage.Landscape)

        # Map itself.  There is deliberately no title: the filename identifies
        # the route, and the map fills the page to minimize the border.
        map_item = QgsLayoutItemMap(layout)
        layout.addLayoutItem(map_item)
        map_item.attemptMove(QgsLayoutPoint(MAP_X_MM, MAP_Y_MM))
        map_item.attemptResize(QgsLayoutSize(MAP_W_MM, MAP_H_MM))
        map_item.setFrameEnabled(False)
        map_item.setLayers([route_layer, osm_layer])
        map_item.setExtent(
            padded_extent(route_layer.extent(), pad_fraction, min_padding_m)
        )

        # Standard OSM attribution, overlaid unobtrusively inside the map so it
        # does not require a separate white margin.
        add_label(
            layout,
            "© OpenStreetMap contributors",
            2,
            204,
            80,
            4,
            5.5,
        )

        settings = QgsLayoutExporter.ImageExportSettings()
        settings.dpi = dpi
        exporter = QgsLayoutExporter(layout)
        result = exporter.exportToImage(str(output_path), settings)
        if result != QgsLayoutExporter.Success:
            message = ""
            if hasattr(exporter, "errorMessage"):
                message = exporter.errorMessage()
            if not message:
                message = exporter.errorFile()
            raise RuntimeError(
                f"Export failed for {route_name!r}: result={result}; {message}"
            )
    finally:
        project.removeMapLayer(route_layer.id())


def choose_output_names(route_names):
    """Give every route a stable, zero-padded numbered filename.

    Call this with the complete sorted route list *before* --only/--limit
    filtering, so a route keeps the same number during test exports.
    """
    used = defaultdict(int)
    result = {}
    width = max(3, len(str(len(route_names))))
    for number, route_name in enumerate(route_names, start=1):
        stem = safe_filename(route_name)
        used[stem] += 1
        if used[stem] > 1:
            stem = f"{stem} {used[stem]}"
        result[route_name] = f"{number:0{width}d} - {stem}.png"
    return result



def write_index_html(output_dir, manifest_rows):
    """Write a simple thumbnail browser for the exported PNGs."""
    title = "Centre Region Bikeway Maps"

    cards = []
    for row in manifest_rows:
        route_name = html.escape(row["route_name"])
        filename = row["png"]
        filename_url = quote(filename)
        feature_count = row["feature_count"]
        source_map_names = html.escape(row["source_map_names"])
        path_types = html.escape(row["path_types"])
        cards.append(
            f"""
        <a class="card" href="{filename_url}" target="_blank">
          <img src="{filename_url}" alt="{route_name}" loading="lazy">
          <div class="caption">
            <div class="name">{route_name}</div>
            <div class="meta">{html.escape(filename)}</div>
            <div class="meta">{feature_count} feature(s)</div>
            <div class="meta">{source_map_names}</div>
            <div class="meta">{path_types}</div>
          </div>
        </a>
            """.strip()
        )

    cards_html = "\n      ".join(cards)
    page = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{title}</title>
  <style>
    body {{
      font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      margin: 0;
      background: #f6f7f9;
      color: #222;
    }}
    header {{
      position: sticky;
      top: 0;
      background: #ffffffee;
      backdrop-filter: blur(4px);
      border-bottom: 1px solid #ddd;
      padding: 0.8rem 1rem;
      z-index: 10;
    }}
    header h1 {{
      margin: 0;
      font-size: 1.1rem;
    }}
    header p {{
      margin: 0.25rem 0 0;
      color: #555;
      font-size: 0.95rem;
    }}
    main {{
      padding: 1rem;
    }}
    .grid {{
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
      gap: 1rem;
    }}
    .card {{
      display: block;
      text-decoration: none;
      color: inherit;
      background: white;
      border: 1px solid #ddd;
      border-radius: 10px;
      overflow: hidden;
      box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08);
      transition: transform 0.12s ease, box-shadow 0.12s ease;
    }}
    .card:hover {{
      box-shadow: 0 3px 12px rgba(0, 0, 0, 0.15);
      transform: translateY(-1px);
    }}
    img {{
      display: block;
      width: 100%;
      height: auto;
      background: #eee;
    }}
    .caption {{
      padding: 0.75rem 0.9rem 0.9rem;
    }}
    .name {{
      font-weight: 600;
      margin-bottom: 0.35rem;
    }}
    .meta {{
      font-size: 0.88rem;
      line-height: 1.35;
      color: #555;
      margin-top: 0.15rem;
      word-break: break-word;
    }}
  </style>
</head>
<body>
  <header>
    <h1>{title}</h1>
    <p>{len(manifest_rows)} exported maps. Click a thumbnail to open the full PNG.</p>
  </header>
  <main>
    <div class="grid">
      {cards_html}
    </div>
  </main>
</body>
</html>
"""

    index_path = output_dir / "index.html"
    index_path.write_text(page, encoding="utf-8")
    return index_path

def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--input",
        default="raw_data/CR_Bikeways.json",
        help="CR_Bikeways GeoJSON (default: raw_data/CR_Bikeways.json)",
    )
    parser.add_argument(
        "--output",
        default="bikeway_maps",
        help="Output directory (default: bikeway_maps)",
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
        help="PNG export resolution (default: 180)",
    )
    parser.add_argument(
        "--padding",
        type=float,
        default=0.12,
        help="Extra context as a fraction of route span (default: 0.12)",
    )
    parser.add_argument(
        "--min-padding",
        type=float,
        default=250.0,
        help="Minimum context on each side in EPSG:3857 metres (default: 250)",
    )
    parser.add_argument(
        "--merge-file",
        default=str(Path(__file__).with_name("bikeway_merges.txt")),
        help=(
            "Optional human-editable merge file (default: bikeway_merges.txt "
            "beside this script; ignored if it does not exist)"
        ),
    )
    parser.add_argument(
        "--only",
        default=None,
        help="Export only routes whose names contain this text (case-insensitive)",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Export only the first N selected routes (useful for testing)",
    )
    parser.add_argument(
        "--list-only",
        action="store_true",
        help="Print route groups but do not render PNGs",
    )
    return parser.parse_args()


def main():
    args = parse_args()

    input_path = Path(args.input).expanduser().resolve()
    output_dir = Path(args.output).expanduser().resolve()

    if not input_path.exists():
        raise SystemExit(f"Input file not found: {input_path}")

    QgsApplication.setPrefixPath(args.prefix_path, True)
    qgs = QgsApplication([], False)
    qgs.initQgis()

    try:
        project = QgsProject.instance()
        project.clear()

        target_crs = QgsCoordinateReferenceSystem("EPSG:3857")
        project.setCrs(target_crs)

        bike_layer = QgsVectorLayer(str(input_path), "Centre Region Bikeways", "ogr")
        if not bike_layer.isValid():
            raise RuntimeError(f"Could not load {input_path}")

        # This CRCOG export explicitly declares EPSG:3857.  Force that
        # interpretation if a GDAL/QGIS build ignores GeoJSON's legacy crs key.
        if bike_layer.crs().authid() != "EPSG:3857":
            print(
                f"WARNING: provider reported {bike_layer.crs().authid() or 'no CRS'}; "
                "interpreting CR_Bikeways as EPSG:3857."
            )
            bike_layer.setCrs(target_crs)

        merge_file = Path(args.merge_file).expanduser() if args.merge_file else None
        external_merge_groups = load_merge_file(merge_file)
        if external_merge_groups:
            print(
                f"Loaded {len(external_merge_groups)} custom merge group(s) "
                f"from {merge_file.resolve()}"
            )
        elif merge_file is not None and merge_file.exists():
            print(f"Merge file {merge_file.resolve()} contains no active groups.")

        groups = group_features(bike_layer, external_merge_groups)
        all_route_names = sorted(groups, key=str.casefold)
        # Assign filenames before filtering so route numbers remain stable when
        # using --only or --limit for test runs.
        output_names = choose_output_names(all_route_names)
        route_names = list(all_route_names)

        if args.only:
            needle = args.only.casefold()
            route_names = [name for name in route_names if needle in name.casefold()]
        if args.limit is not None:
            route_names = route_names[: max(args.limit, 0)]

        print(f"Loaded {bike_layer.featureCount()} JSON features.")
        print(f"Built {len(groups)} route maps before filtering.")
        print(f"Selected {len(route_names)} route maps for this run.")
        for name in route_names:
            ids = []
            for f in groups[name]:
                try:
                    ids.append(str(f["OBJECTID"]))
                except Exception:
                    ids.append(str(f.id()))
            print(f"  {name}  [{len(groups[name])} feature(s): {', '.join(ids)}]")

        if args.list_only:
            return

        output_dir.mkdir(parents=True, exist_ok=True)

        # Same basic OSM setup as the original script, with explicit zoom/CRS.
        osm_uri = (
            "type=xyz&url=https://tile.openstreetmap.org/{z}/{x}/{y}.png"
            "&zmax=19&zmin=0&crs=EPSG3857"
        )
        osm_layer = QgsRasterLayer(osm_uri, "OpenStreetMap", "wms")
        if not osm_layer.isValid():
            raise RuntimeError("Could not create OpenStreetMap XYZ layer")
        project.addMapLayer(osm_layer, False)

        manifest_rows = []

        for number, route_name in enumerate(route_names, start=1):
            filename = output_names[route_name]
            output_path = output_dir / filename
            features = groups[route_name]
            print(f"[{number}/{len(route_names)}] {route_name} -> {filename}")

            export_route(
                project=project,
                osm_layer=osm_layer,
                source_layer=bike_layer,
                route_name=route_name,
                features=features,
                output_path=output_path,
                dpi=args.dpi,
                pad_fraction=args.padding,
                min_padding_m=args.min_padding,
            )

            object_ids = []
            map_names = []
            path_types = []
            for feature in features:
                object_ids.append(text_value(feature["OBJECTID"]))
                map_names.append(text_value(feature["Map Name"]))
                path_types.append(text_value(feature["Path Type"]))

            manifest_rows.append(
                {
                    "route_name": route_name,
                    "png": filename,
                    "feature_count": len(features),
                    "object_ids": "; ".join(x for x in object_ids if x),
                    "source_map_names": "; ".join(sorted(set(x for x in map_names if x))),
                    "path_types": "; ".join(sorted(set(x for x in path_types if x))),
                }
            )

        manifest_path = output_dir / "manifest.csv"
        with manifest_path.open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(
                f,
                fieldnames=[
                    "route_name",
                    "png",
                    "feature_count",
                    "object_ids",
                    "source_map_names",
                    "path_types",
                ],
            )
            writer.writeheader()
            writer.writerows(manifest_rows)

        index_path = write_index_html(output_dir, manifest_rows)

        print(f"Done. Wrote {len(manifest_rows)} PNG(s) to {output_dir}")
        print(f"Manifest: {manifest_path}")
        print(f"Index: {index_path}")

    finally:
        qgs.exitQgis()


if __name__ == "__main__":
    main()
