#!/usr/bin/env python3
"""Build the GeoJSON payload used by the homepage Leaflet overview map.

Run from aux/qgis_chatgpt, normally via::

    make overview

The output is a JavaScript data file rather than fetched GeoJSON so the generated
homepage can also be opened directly from disk for quick inspection.
"""

import argparse
import csv
import html
import json
import re
from collections import defaultdict
from pathlib import Path

from qgis.core import (
    QgsApplication,
    QgsCoordinateReferenceSystem,
    QgsCoordinateTransform,
    QgsGeometry,
    QgsProject,
    QgsVectorLayer,
)


WGS84 = "EPSG:4326"


def text_value(value):
    if value is None:
        return ""
    value = str(value).strip()
    if value.upper() in {"NULL", "NONE"}:
        return ""
    return value


def load_layer(path, name, provider="ogr", suffix=""):
    uri = str(path) + suffix
    layer = QgsVectorLayer(uri, name, provider)
    if not layer.isValid():
        raise RuntimeError(f"Could not load {name}: {uri}")
    return layer


def geometry_as_wgs84(layer, feature, transform_context, simplify=0.0):
    geom = QgsGeometry(feature.geometry())
    if geom.isNull() or geom.isEmpty():
        return None
    source_crs = layer.crs()
    target_crs = QgsCoordinateReferenceSystem(WGS84)
    if source_crs.isValid() and source_crs != target_crs:
        xform = QgsCoordinateTransform(source_crs, target_crs, transform_context)
        geom.transform(xform)
    if simplify:
        simplified = geom.simplify(simplify)
        if not simplified.isNull() and not simplified.isEmpty():
            geom = simplified
    return json.loads(geom.asJson())


def feature_collection(features):
    return {"type": "FeatureCollection", "features": features}


def extract_html_field(description, field_name):
    if not description:
        return ""
    pattern = (
        rf"<td>\s*{re.escape(field_name)}\s*</td>\s*"
        rf"<td>(.*?)</td>"
    )
    match = re.search(pattern, str(description), flags=re.IGNORECASE | re.DOTALL)
    if not match:
        return ""
    value = re.sub(r"<[^>]+>", "", match.group(1))
    value = html.unescape(value).strip()
    return "" if value.lower() in {"<null>", "null"} else value


def build_bikeways(path, project):
    layer = load_layer(path, "Centre Region Bikeways")
    if not layer.crs().isValid() or layer.crs().authid() != "EPSG:3857":
        # This CRCOG export declares EPSG:3857 in its GeoJSON metadata.
        layer.setCrs(QgsCoordinateReferenceSystem("EPSG:3857"))

    features = []
    for f in layer.getFeatures():
        geom = geometry_as_wgs84(layer, f, project.transformContext(), simplify=0.000005)
        if not geom:
            continue
        props = {
            "name": text_value(f["Map Name"]),
            "type": text_value(f["Path Type"]),
            "description": text_value(f["Path Description"]),
            "miles": f["Distance in Miles"] if "Distance in Miles" in f.fields().names() else None,
        }
        features.append({"type": "Feature", "geometry": geom, "properties": props})
    return feature_collection(features)


def build_cata(path, project):
    layer = load_layer(path, "CATA fixed routes")
    features = []
    for f in layer.getFeatures():
        geom = geometry_as_wgs84(layer, f, project.transformContext(), simplify=0.000008)
        if not geom:
            continue
        short_name = text_value(f["Name"])
        description = text_value(f["description"]) if "description" in f.fields().names() else ""
        long_name = extract_html_field(description, "route_long_name")
        color = extract_html_field(description, "ColorCode")
        props = {
            "name": short_name,
            "long_name": long_name,
            "color": color,
        }
        features.append({"type": "Feature", "geometry": geom, "properties": props})
    return feature_collection(features)


def build_shuttles(paths, project):
    features = []
    for path in paths:
        layer = load_layer(path, path.stem, provider="gpx", suffix="?type=track")
        for f in layer.getFeatures():
            geom = geometry_as_wgs84(layer, f, project.transformContext(), simplify=0.000005)
            if not geom:
                continue
            name = text_value(f["name"]) if "name" in f.fields().names() else path.stem
            features.append(
                {
                    "type": "Feature",
                    "geometry": geom,
                    "properties": {"name": name or path.stem},
                }
            )
    return feature_collection(features)


def build_landmarks(path):
    """Read a small, hand-edited CSV of WGS84 landmark points."""
    lines = [
        line for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    ]
    if not lines:
        return feature_collection([])

    reader = csv.DictReader(lines)
    required = {"name", "lat", "lon", "category", "notes"}
    missing = required.difference(reader.fieldnames or [])
    if missing:
        raise RuntimeError(
            f"Landmark CSV {path} is missing column(s): {', '.join(sorted(missing))}"
        )

    features = []
    for row_number, row in enumerate(reader, start=2):
        name = text_value(row.get("name"))
        lat_text = text_value(row.get("lat"))
        lon_text = text_value(row.get("lon"))
        if not name and not lat_text and not lon_text:
            continue
        if not name:
            raise RuntimeError(f"Landmark CSV {path}, row {row_number}: missing name")
        try:
            lat = float(lat_text)
            lon = float(lon_text)
        except ValueError as exc:
            raise RuntimeError(
                f"Landmark CSV {path}, row {row_number}: invalid lat/lon"
            ) from exc
        if not (-90 <= lat <= 90 and -180 <= lon <= 180):
            raise RuntimeError(
                f"Landmark CSV {path}, row {row_number}: lat/lon out of range"
            )

        category = text_value(row.get("category")).lower() or "landmark"
        category = re.sub(r"[^a-z0-9]+", "-", category).strip("-") or "landmark"
        features.append(
            {
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [lon, lat]},
                "properties": {
                    "name": name,
                    "category": category,
                    "notes": text_value(row.get("notes")),
                },
            }
        )
    return feature_collection(features)


def build_catago(specs, project):
    features = []
    for path, fallback_name in specs:
        layer = load_layer(path, fallback_name)
        names = layer.fields().names()
        for f in layer.getFeatures():
            geom = geometry_as_wgs84(layer, f, project.transformContext(), simplify=0.00001)
            if not geom:
                continue
            if "Desc_" in names:
                description = text_value(f["Desc_"])
                zone_name = description or fallback_name
            elif "Name" in names:
                description = text_value(f["Name"])
                zone_name = description.rstrip(".\u00a0") or fallback_name
            else:
                description = ""
                zone_name = fallback_name
            features.append(
                {
                    "type": "Feature",
                    "geometry": geom,
                    "properties": {
                        "name": zone_name,
                        "system": fallback_name,
                        "description": description,
                    },
                }
            )
    return feature_collection(features)


def parse_args():
    here = Path(__file__).resolve().parent
    src = here / "overview_sources"
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bikeways", type=Path, default=here / "CR_Bikeways.json")
    parser.add_argument("--cata", type=Path, default=src / "CATA_Fall2024_RouteTraces.kml")
    parser.add_argument(
        "--landmarks",
        type=Path,
        default=src / "landmarks.csv",
        help="CSV with name,lat,lon,category,notes columns",
    )
    parser.add_argument(
        "--shuttle",
        type=Path,
        action="append",
        default=None,
        help="GPX track file; may be supplied more than once",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=here / "../../docs/maps/overview/overview-data.js",
    )
    parser.add_argument("--prefix-path", default="/usr")
    return parser.parse_args()


def main():
    args = parse_args()
    here = Path(__file__).resolve().parent
    src = here / "overview_sources"
    shuttles = args.shuttle or [
        src / "Beaver_Ave_Shuttle_--_Fall_2024.gpx",
        src / "College_Ave_Shuttle_--_Fall_2024.gpx",
    ]
    catago = [
        (src / "catago/Boalsburg_Zone.shp", "Boalsburg"),
        (src / "catago/College Twp Zone.shp", "Houserville/Lemont"),
        (src / "catago/CentreAreaWest_Jul2024.shp", "Centre Area West"),
    ]

    for path in [args.bikeways, args.cata, args.landmarks, *shuttles, *(p for p, _ in catago)]:
        if not path.exists():
            raise SystemExit(f"Missing source file: {path}")

    QgsApplication.setPrefixPath(args.prefix_path, True)
    qgs = QgsApplication([], False)
    qgs.initQgis()
    try:
        project = QgsProject.instance()
        project.clear()
        payload = {
            "bikeways": build_bikeways(args.bikeways, project),
            "cata": build_cata(args.cata, project),
            "shuttles": build_shuttles(shuttles, project),
            "catago": build_catago(catago, project),
            "landmarks": build_landmarks(args.landmarks),
        }
        args.output.parent.mkdir(parents=True, exist_ok=True)
        serialized = json.dumps(payload, ensure_ascii=False, separators=(",", ":"))
        args.output.write_text(
            "window.CARFREE_OVERVIEW_DATA=" + serialized + ";\n",
            encoding="utf-8",
        )
        print(f"Wrote {args.output}")
        for key, fc in payload.items():
            print(f"  {key}: {len(fc['features'])} feature(s)")
    finally:
        qgs.exitQgis()


if __name__ == "__main__":
    main()
