// Initialize the map centered on Prague
const map = L.map('map').setView([50.0755, 14.4378], 13);

// Add OpenStreetMap tiles
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
  attribution: '© OpenStreetMap contributors'
}).addTo(map);

// Feature group for drawn items
const drawnItems = new L.FeatureGroup();
map.addLayer(drawnItems);

// Draw control with only the polygon tool enabled
const drawControl = new L.Control.Draw({
  edit: { featureGroup: drawnItems },
  draw: {
    polygon: true,
    polyline: false,
    rectangle: false,
    circle: false,
    circlemarker: false,
    marker: false
  }
});
map.addControl(drawControl);

// Store all drawn polygons
let polygons = [];

// Handle the completion of a drawing
map.on(L.Draw.Event.CREATED, function (event) {
  const layer = event.layer;
  drawnItems.addLayer(layer);

  // Extract and store the polygon's coordinates
  const polygonCoordinates = layer.getLatLngs()[0].map(latlng => [latlng.lat, latlng.lng]);
  polygons.push(polygonCoordinates);
  console.log('Polygon added:', polygonCoordinates);
});

// Handle export button click
document.getElementById('export-data').addEventListener('click', () => {
  if (polygons.length === 0) {
    alert('Please draw at least one polygon before exporting!');
    return;
  }

  // Send all polygons to the backend
  fetch('/save_polygons', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ polygons })
  })
    .then(response => {
      if (response.ok) {
        console.log('Polygons exported successfully.');
        alert('Polygons exported to the backend successfully!');
      } else {
        alert('Failed to export polygons to the backend.');
      }
    })
    .catch(error => console.error('Error:', error));
});
