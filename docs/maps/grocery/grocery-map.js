(function () {
  "use strict";

  var container = document.getElementById("grocery-map");
  if (!container || typeof L === "undefined") return;

  var DATA_URL = "maps/grocery/stores.csv";
  var CATEGORY_STYLES = {
    "Supermarket": {color: "#17666a", radius: 8},
    "Specialty": {color: "#7a5a8a", radius: 8},
    "General retail": {color: "#9a6b31", radius: 8}
  };
  var FALLBACK_STYLE = {color: "#6b6257", radius: 8};

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

  function escapeHtml(value) {
    return String(value == null ? "" : value)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#039;");
  }

  // Small CSV parser so store names/notes can safely contain commas when quoted.
  function parseCsv(text) {
    var rows = [];
    var row = [];
    var field = "";
    var quoted = false;

    for (var i = 0; i < text.length; i += 1) {
      var ch = text[i];
      var next = text[i + 1];
      if (quoted) {
        if (ch === '"' && next === '"') {
          field += '"';
          i += 1;
        } else if (ch === '"') {
          quoted = false;
        } else {
          field += ch;
        }
      } else if (ch === '"') {
        quoted = true;
      } else if (ch === ",") {
        row.push(field);
        field = "";
      } else if (ch === "\n" || ch === "\r") {
        if (ch === "\r" && next === "\n") i += 1;
        row.push(field);
        field = "";
        if (row.some(function (value) { return value !== ""; })) rows.push(row);
        row = [];
      } else {
        field += ch;
      }
    }
    if (field !== "" || row.length) {
      row.push(field);
      rows.push(row);
    }
    if (!rows.length) return [];

    var headers = rows.shift().map(function (value) { return value.trim(); });
    return rows.map(function (values) {
      var item = {};
      headers.forEach(function (header, index) {
        item[header] = (values[index] || "").trim();
      });
      return item;
    });
  }

  function popupHtml(store) {
    var html = '<div class="grocery-popup-title">' + escapeHtml(store.name) + "</div>";
    html += '<div class="grocery-popup-meta">' + escapeHtml(store.category);
    if (store.address) html += " &middot; " + escapeHtml(store.address);
    html += "</div>";
    if (store.notes) {
      html += '<div class="grocery-popup-description">' + escapeHtml(store.notes) + "</div>";
    }
    return html;
  }

  function markerFor(store) {
    var lat = Number(store.latitude);
    var lon = Number(store.longitude);
    if (!Number.isFinite(lat) || !Number.isFinite(lon)) return null;

    var style = CATEGORY_STYLES[store.category] || FALLBACK_STYLE;
    var marker = L.circleMarker([lat, lon], {
      radius: style.radius,
      color: "#fffefa",
      weight: 2,
      fillColor: style.color,
      fillOpacity: 0.95,
      opacity: 1
    });
    marker.bindPopup(popupHtml(store));
    marker.bindTooltip(store.name, {direction: "top", opacity: 0.93});
    return marker;
  }

  function className(category) {
    return String(category || "")
      .toLowerCase()
      .replace(/[^a-z0-9]+/g, "-")
      .replace(/^-+|-+$/g, "");
  }

  function render(stores) {
    var groups = {};
    var bounds = [];

    stores.forEach(function (store) {
      var marker = markerFor(store);
      if (!marker) return;
      var category = store.category || "Other";
      if (!groups[category]) groups[category] = L.layerGroup().addTo(map);
      marker.addTo(groups[category]);
      bounds.push(marker.getLatLng());
    });

    if (!bounds.length) throw new Error("No valid grocery-store coordinates found.");

    var orderedGroups = {};
    ["Supermarket", "Specialty", "General retail"].forEach(function (category) {
      if (groups[category]) orderedGroups[category] = groups[category];
    });
    Object.keys(groups).forEach(function (category) {
      if (!orderedGroups[category]) orderedGroups[category] = groups[category];
    });

    L.control.layers(null, orderedGroups, {
      collapsed: window.matchMedia("(max-width: 700px)").matches,
      position: "topright"
    }).addTo(map);

    var legend = L.control({position: "bottomleft"});
    legend.onAdd = function () {
      var div = L.DomUtil.create("div", "grocery-legend");
      var html = "<strong>Store type</strong>";
      Object.keys(CATEGORY_STYLES).forEach(function (category) {
        html += '<div class="grocery-legend-row"><span class="grocery-legend-dot ' +
          className(category) + '"></span>' + escapeHtml(category) + "</div>";
      });
      div.innerHTML = html;
      L.DomEvent.disableClickPropagation(div);
      return div;
    };
    legend.addTo(map);

    map.fitBounds(L.latLngBounds(bounds).pad(0.08), {maxZoom: 13});
  }

  function showError(error) {
    container.innerHTML = '<div class="grocery-map-error">Could not load the grocery-store data. ' +
      'If you opened the HTML directly from disk, preview it through a local web server instead.<br><small>' +
      escapeHtml(error && error.message ? error.message : "Unknown error") + "</small></div>";
  }

  fetch(DATA_URL)
    .then(function (response) {
      if (!response.ok) throw new Error("HTTP " + response.status + " loading " + DATA_URL);
      return response.text();
    })
    .then(parseCsv)
    .then(render)
    .catch(showError);
}());
