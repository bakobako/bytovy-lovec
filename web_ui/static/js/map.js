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
  try {
    const layer = event.layer;
    drawnItems.addLayer(layer);

    // Extract and store the polygon's coordinates
    const polygonCoordinates = layer.getLatLngs()[0].map(latlng => [latlng.lat, latlng.lng]);
    polygons.push(polygonCoordinates);
    console.log('Polygon added:', polygonCoordinates);
  } catch (error) {
    console.error('Error handling drawn polygon:', error);
    alert('There was an issue with the drawn polygon. Please try again.');
  }
});

// Submit button event listener
document.getElementById('submit-btn').addEventListener('click', () => {
  try {
    // Collect form data
    const formData = new FormData();

    // Get the selected disposition values
    const dispozice = Array.from(document.querySelectorAll('input[name="dispozice"]:checked'))
      .map(input => input.value);

    // Get the price range values
    const priceFrom = document.getElementById('price_from').value;
    const priceTo = document.getElementById('price_to').value;

    // Get the floor range values
    const floorFrom = document.getElementById('floor_from').value;
    const floorTo = document.getElementById('floor_to').value;

    // Get the ownership values
    const ownership = Array.from(document.querySelectorAll('input[name="ownership"]:checked'))
      .map(input => input.value);

    // Collect polygon data
    if (polygons.length === 0) {
      alert('Please draw at least one polygon before submitting!');
      return;
    }

    // Prepare the data object
    const data = {
      polygons: polygons,
      dispozice: dispozice,
      priceFrom: priceFrom,
      priceTo: priceTo,
      floorFrom: floorFrom,
      floorTo: floorTo,
      ownership: ownership
    };

    // Send the data to the server
    fetch('/save_polygons', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(data => {
      console.log('Response from server:', data);
      alert('Data submitted successfully!');
    })
    .catch(error => {
      console.error('Error sending data to server:', error);
      alert('An error occurred while submitting data. Please try again.');
    });
  } catch (error) {
    console.error('Error during form submission:', error);
    alert('There was an issue with the form data. Please check your input and try again.');
  }
});
