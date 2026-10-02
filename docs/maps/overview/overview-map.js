(function () {
  "use strict";

  var container = document.getElementById("overview-map");
  var data = window.CARFREE_OVERVIEW_DATA;
  if (!container || !data || typeof L === "undefined") return;

  var map = L.map(container, {
    zoomControl: true,
    zoomSnap: 0.25,
    wheelPxPerZoomLevel: 90,
    preferCanvas: true
  });

  L.tileLayer("https://tile.openstreetmap.org/{z}/{x}/{y}.png", {
    maxZoom: 19,
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
  }).addTo(map);

  map.createPane("catagoPane");
  map.getPane("catagoPane").style.zIndex = 350;
  map.createPane("cataPane");
  map.getPane("cataPane").style.zIndex = 410;
  map.createPane("shuttlePane");
  map.getPane("shuttlePane").style.zIndex = 430;
  map.createPane("bikePane");
  map.getPane("bikePane").style.zIndex = 450;
  map.createPane("landmarkPane");
  map.getPane("landmarkPane").style.zIndex = 500;

  function escapeHtml(value) {
    return String(value == null ? "" : value)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#039;");
  }

  function bikeStyle(feature) {
    var type = (feature.properties && feature.properties.type) || "";
    var zoom = map.getZoom() || 12;
    var scale = zoom >= 15 ? 1.3 : zoom >= 13 ? 1.0 : 0.8;
    if (type === "Shared Use Path") {
      return {pane: "bikePane", color: "#17666a", weight: 3.7 * scale, opacity: 0.9};
    }
    if (type === "Bike Lane") {
      return {pane: "bikePane", color: "#2f8fa3", weight: 3.0 * scale, opacity: 0.88};
    }
    if (type === "Bike Route" || type === "State Bike Route") {
      return {pane: "bikePane", color: "#7aaebe", weight: 2.5 * scale, opacity: 0.86, dashArray: "6 5"};
    }
    return {pane: "bikePane", color: "#536f78", weight: 2.6 * scale, opacity: 0.82};
  }

  function cataStyle() {
    var zoom = map.getZoom() || 12;
    return {
      pane: "cataPane",
      color: "#c56a22",
      weight: zoom >= 15 ? 3.1 : zoom >= 13 ? 2.5 : 2.0,
      opacity: 0.72
    };
  }

  function shuttleStyle() {
    return {
      pane: "shuttlePane",
      color: "#b23a48",
      weight: 3.4,
      opacity: 0.9,
      dashArray: "8 5"
    };
  }

  function catagoStyle() {
    return {
      pane: "catagoPane",
      color: "#55855a",
      weight: 1.4,
      opacity: 0.78,
      fillColor: "#73a471",
      fillOpacity: 0.14
    };
  }

  function landmarkCategory(value) {
    var category = String(value || "landmark").toLowerCase().replace(/[^a-z0-9]+/g, "-");
    return category.replace(/^-+|-+$/g, "") || "landmark";
  }

  function landmarkLabel(value) {
    return landmarkCategory(value)
      .split("-")
      .map(function (part) { return part.charAt(0).toUpperCase() + part.slice(1); })
      .join(" ");
  }

  function landmarkIcon(feature) {
    var p = feature.properties || {};
    var category = landmarkCategory(p.category);
    return L.divIcon({
      className: "landmark-marker",
      html: '<span class="landmark-pin landmark-' + escapeHtml(category) + '"><span></span></span>',
      iconSize: [22, 28],
      iconAnchor: [11, 27],
      popupAnchor: [0, -24],
      tooltipAnchor: [0, -20]
    });
  }

  function popup(title, meta, description) {
    var html = '<div class="map-popup-title">' + escapeHtml(title || "Unnamed") + "</div>";
    if (meta) html += '<div class="map-popup-meta">' + escapeHtml(meta) + "</div>";
    if (description) html += '<div class="map-popup-description">' + escapeHtml(description) + "</div>";
    return html;
  }

  function attachLineInteraction(feature, layer, baseStyle, popupHtml) {
    layer.bindPopup(popupHtml);
    layer.on({
      mouseover: function () {
        var style = typeof baseStyle === "function" ? baseStyle(feature) : baseStyle;
        layer.setStyle({weight: (style.weight || 2) + 2, opacity: 1});
      },
      mouseout: function () {
        layer.setStyle(typeof baseStyle === "function" ? baseStyle(feature) : baseStyle);
      }
    });
  }

  var catagoLayer = L.geoJSON(data.catago, {
    pane: "catagoPane",
    style: catagoStyle,
    onEachFeature: function (feature, layer) {
      var p = feature.properties || {};
      var meta = p.system && p.system !== p.name ? "CATAGO · " + p.system : "CATAGO zone";
      layer.bindPopup(popup(p.name, meta, p.description && p.description !== p.name ? p.description : ""));
      layer.on({
        mouseover: function () { layer.setStyle({fillOpacity: 0.25, weight: 2.2}); },
        mouseout: function () { catagoLayer.resetStyle(layer); }
      });
    }
  }).addTo(map);

  var cataLayer = L.geoJSON(data.cata, {
    pane: "cataPane",
    style: cataStyle,
    onEachFeature: function (feature, layer) {
      var p = feature.properties || {};
      var title = "CATA " + (p.name || "route");
      var meta = p.long_name && p.long_name !== p.name ? p.long_name : "Fixed-route bus";
      attachLineInteraction(feature, layer, cataStyle, popup(title, meta, ""));
    }
  }).addTo(map);

  var shuttleLayer = L.geoJSON(data.shuttles, {
    pane: "shuttlePane",
    style: shuttleStyle,
    onEachFeature: function (feature, layer) {
      var p = feature.properties || {};
      attachLineInteraction(feature, layer, shuttleStyle, popup(p.name, "Penn State shuttle", ""));
    }
  }).addTo(map);

  var bikeLayer = L.geoJSON(data.bikeways, {
    pane: "bikePane",
    style: bikeStyle,
    onEachFeature: function (feature, layer) {
      var p = feature.properties || {};
      var meta = p.type || "Bikeway";
      if (typeof p.miles === "number" && isFinite(p.miles)) {
        meta += " · " + p.miles.toFixed(2) + " mi";
      }
      attachLineInteraction(feature, layer, bikeStyle, popup(p.name || "Bikeway", meta, p.description || ""));
    }
  }).addTo(map);

  var landmarkLayer = L.geoJSON(data.landmarks || {type: "FeatureCollection", features: []}, {
    pane: "landmarkPane",
    pointToLayer: function (feature, latlng) {
      return L.marker(latlng, {pane: "landmarkPane", icon: landmarkIcon(feature)});
    },
    onEachFeature: function (feature, layer) {
      var p = feature.properties || {};
      layer.bindPopup(popup(p.name || "Landmark", landmarkLabel(p.category), p.notes || ""));
      layer.bindTooltip(p.name || "Landmark", {direction: "top", opacity: 0.92});
    }
  }).addTo(map);

  var overlays = {
    "Landmarks": landmarkLayer,
    "Bikeways": bikeLayer,
    "CATA bus routes": cataLayer,
    "Penn State shuttles": shuttleLayer,
    "CATAGO zones": catagoLayer
  };

  L.control.layers(null, overlays, {
    collapsed: window.matchMedia("(max-width: 700px)").matches,
    position: "topright"
  }).addTo(map);

  var legend = L.control({position: "bottomleft"});
  legend.onAdd = function () {
    var div = L.DomUtil.create("div", "overview-legend");
    div.innerHTML =
      "<strong>Map key</strong>" +
      '<div class="legend-row"><span class="legend-pin"></span>Landmark</div>' +
      '<div class="legend-row"><span class="legend-line shared"></span>Shared-use path</div>' +
      '<div class="legend-row"><span class="legend-line lane"></span>Bike lane</div>' +
      '<div class="legend-row"><span class="legend-line route"></span>Bike route</div>' +
      '<div class="legend-row"><span class="legend-line bus"></span>CATA bus</div>' +
      '<div class="legend-row"><span class="legend-line shuttle"></span>PSU shuttle</div>' +
      '<div class="legend-row"><span class="legend-area"></span>CATAGO zone</div>';
    L.DomEvent.disableClickPropagation(div);
    return div;
  };
  legend.addTo(map);

  function restyleForZoom() {
    bikeLayer.setStyle(bikeStyle);
    cataLayer.setStyle(cataStyle);
  }
  map.on("zoomend", restyleForZoom);

  // Fit to the transportation network, not to landmarks, so one stray or
  // mistyped landmark coordinate cannot zoom the whole overview out.
  map.setView([40.7934, -77.86], 12);
})();
