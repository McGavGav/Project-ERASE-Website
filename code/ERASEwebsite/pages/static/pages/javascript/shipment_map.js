var originCoord = [46.7298, -117.1817];
var destinationCoord = [14.6349, -90.5069];
var totalTransitSeconds = 0;
var startTime = null;
var animationInterval = null;
var routePoints = [];
var completedRoute = null;
var remainingRoute = null;
var shipmentMarker = null;

function haversineDistance(lat1, lon1, lat2, lon2) {
  var R = 3958.8;
  var dLat = (lat2 - lat1) * Math.PI / 180;
  var dLon = (lon2 - lon1) * Math.PI / 180;
  var a = Math.sin(dLat / 2) * Math.sin(dLat / 2) + Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) * Math.sin(dLon / 2) * Math.sin(dLon / 2);
  var c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
  return R * c;
}

function createArc(start, end, segments = 120) {
  var latlngs = [];
  for (var i = 0; i <= segments; i++) {
    var t = i / segments;
    var lat = start[0] + (end[0] - start[0]) * t;
    var lng = start[1] + (end[1] - start[1]) * t;
    var offset = Math.sin(Math.PI * t) * 5;
    latlngs.push([lat + offset, lng]);
  }
  return latlngs;
}

function resetMapRoute() {
  routePoints = createArc(originCoord, destinationCoord);
  if (completedRoute) {
    completedRoute.setLatLngs([]);
  } else {
    completedRoute = L.polyline([], { color: 'green', weight: 4 }).addTo(map);
  }
  if (remainingRoute) {
    remainingRoute.setLatLngs(routePoints);
  } else {
    remainingRoute = L.polyline(routePoints, { color: 'blue', weight: 4 }).addTo(map);
  }
  if (shipmentMarker) {
    shipmentMarker.setLatLng(originCoord);
  } else {
    shipmentMarker = L.circleMarker(originCoord, { radius: 12, color: 'black', fillColor: 'red', fillOpacity: 1, weight: 2 }).addTo(map);
    shipmentMarker.bindPopup('ERASE Shipment 001');
  }
}

var map = L.map('map').setView([35, -105], 4);
L.tileLayer('https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}.png', {
  attribution: '&copy; OpenStreetMap contributors &copy; CARTO',
  maxZoom: 18,
  subdomains: ['a', 'b', 'c', 'd']
}).addTo(map);
resetMapRoute();
L.marker(originCoord).addTo(map).bindPopup('Origin: Pullman, WA');
L.marker(destinationCoord).addTo(map).bindPopup('Destination: Guatemala');

var totalDistance = haversineDistance(originCoord[0], originCoord[1], destinationCoord[0], destinationCoord[1]);
document.getElementById('remaining').innerText = totalDistance.toFixed(2) + ' miles';

function updateShipmentPosition() {
  if (!startTime || totalTransitSeconds <= 0) return;
  var elapsedSeconds = (Date.now() - startTime) / 1000;
  var progress = elapsedSeconds / totalTransitSeconds;
  if (progress > 1) progress = 1;
  var index = Math.floor(progress * (routePoints.length - 1));
  if (index < 0) index = 0;
  var position = routePoints[index];
  shipmentMarker.setLatLng(position);
  completedRoute.setLatLngs(routePoints.slice(0, index + 1));
  remainingRoute.setLatLngs(routePoints.slice(index));
  document.getElementById('timer').innerText = elapsedSeconds.toFixed(1) + ' s';
  var traveled = totalDistance * progress;
  var remaining = totalDistance - traveled;
  document.getElementById('remaining').innerText = remaining.toFixed(2) + ' miles';
  document.getElementById('progress').innerText = (progress * 100).toFixed(1) + '%';
  document.getElementById('distance').innerText = traveled.toFixed(2) + ' miles';
  shipmentMarker.bindPopup('Shipment ERASE-001<br>' + (progress * 100).toFixed(1) + '% complete');
  if (progress >= 1) {
    clearInterval(animationInterval);
    animationInterval = null;
    document.getElementById('status').innerText = 'Delivered';
  }
}

function startShipment() {
  if (totalTransitSeconds <= 0) return;
  if (animationInterval) clearInterval(animationInterval);
  startTime = Date.now();
  document.getElementById('status').innerText = 'In Transit';
  var etaTime = new Date(Date.now() + totalTransitSeconds * 1000);
  document.getElementById('eta').innerText = etaTime.toLocaleTimeString();
  animationInterval = setInterval(updateShipmentPosition, 100);
}

function pauseShipment() {
  if (animationInterval) {
    clearInterval(animationInterval);
    animationInterval = null;
  }
  document.getElementById('status').innerText = 'Paused';
}

function resetShipment() {
  if (animationInterval) {
    clearInterval(animationInterval);
    animationInterval = null;
  }
  startTime = null;
  resetMapRoute();
  totalDistance = haversineDistance(originCoord[0], originCoord[1], destinationCoord[0], destinationCoord[1]);
  document.getElementById('timer').innerText = '0 s';
  document.getElementById('distance').innerText = '0 miles';
  document.getElementById('remaining').innerText = totalDistance.toFixed(2) + ' miles';
  document.getElementById('progress').innerText = '0%';
  document.getElementById('status').innerText = 'Waiting';
  document.getElementById('eta').innerText = '--';
}

var addShipmentBtn = document.getElementById('addShipmentBtn');
var startShipmentBtn = document.getElementById('startShipmentBtn');
var pauseShipmentBtn = document.getElementById('pauseShipmentBtn');
var resetShipmentBtn = document.getElementById('resetShipmentBtn');
var shipmentModal = document.getElementById('shipmentModal');
var closeShipmentModal = document.getElementById('closeShipmentModal');
function geocodeCity(city, callback) {
  fetch('https://nominatim.openstreetmap.org/search?format=json&q=' + encodeURIComponent(city))
    .then(response => response.json())
    .then(data => {
      if (data && data.length > 0) {
        var lat = parseFloat(data[0].lat);
        var lng = parseFloat(data[0].lon);
        callback([lat, lng]);
      } else {
        callback(null);
      }
    })
    .catch(error => {
      console.error('Geocoding error:', error);
      callback(null);
    });
}

var shipmentForm = document.getElementById('shipmentForm');
var originLatInput = document.getElementById('originLat');
var originLngInput = document.getElementById('originLng');
var destLatInput = document.getElementById('destLat');
var destLngInput = document.getElementById('destLng');
var transitDaysInput = document.getElementById('transitDays');
var transitHoursInput = document.getElementById('transitHours');
var transitMinutesInput = document.getElementById('transitMinutes');
var transitSecondsInput = document.getElementById('transitSeconds');

addShipmentBtn.addEventListener('click', function () {
  shipmentModal.style.display = 'block';
});
closeShipmentModal.addEventListener('click', function () {
  shipmentModal.style.display = 'none';
});
startShipmentBtn.addEventListener('click', startShipment);
pauseShipmentBtn.addEventListener('click', pauseShipment);
resetShipmentBtn.addEventListener('click', resetShipment);

shipmentForm.addEventListener('submit', function (event) {
  event.preventDefault();
  var originCity = document.getElementById('originCity').value;
  var destCity = document.getElementById('destCity').value;
  var days = Number(document.getElementById('transitDays').value);
  var hours = Number(document.getElementById('transitHours').value);
  var minutes = Number(document.getElementById('transitMinutes').value);
  var seconds = Number(document.getElementById('transitSeconds').value);
  totalTransitSeconds = days * 86400 + hours * 3600 + minutes * 60 + seconds;
  if (totalTransitSeconds <= 0) {
    return;
  }

  // Geocode origin city
  geocodeCity(originCity, function(originLatLng) {
    if (!originLatLng) {
      alert('Could not find coordinates for origin city: ' + originCity);
      return;
    }
    // Geocode destination city
    geocodeCity(destCity, function(destLatLng) {
      if (!destLatLng) {
        alert('Could not find coordinates for destination city: ' + destCity);
        return;
      }
      originCoord = [originLatLng[0], originLatLng[1]];
      destinationCoord = [destLatLng[0], destLatLng[1]];
      resetShipment();
      shipmentModal.style.display = 'none';
    });
  });
});

var workshopMarkers = (window.workshopMarkersData && Array.isArray(window.workshopMarkersData))
    ? window.workshopMarkersData
    : (window.workshopMarkersData || []);
var workshopMarkerLayers = [];
var todayIso = new Date().toLocaleDateString('en-CA');

function getWorkshopStatus(location) {
  if (!location.date) return 'unknown';
  if (location.date === todayIso) return 'today';
  return location.date > todayIso ? 'future' : 'past';
}

function getLocationText(location) {
  return [
    location.title,
    location.city,
    location.address,
    location.description
  ].filter(Boolean).join(' ').toLowerCase();
}

function renderCityOptions(locations) {
  var cityFilter = document.getElementById('cityFilter');
  var selectedCity = cityFilter.value;
  var cities = [];
  locations.forEach(function (location) {
    if (location.city && cities.indexOf(location.city) === -1) {
      cities.push(location.city);
    }
  });
  cities.sort(function (a, b) { return a.localeCompare(b); });
  cityFilter.innerHTML = '<option value="">All cities</option>';
  cities.forEach(function (city) {
    var option = document.createElement('option');
    option.value = city;
    option.textContent = city;
    cityFilter.appendChild(option);
  });
  cityFilter.value = cities.indexOf(selectedCity) === -1 ? '' : selectedCity;
}

function filterWorkshops() {
  var searchValue = document.getElementById('workshopSearch').value.trim().toLowerCase();
  var cityValue = document.getElementById('cityFilter').value;
  var statusValue = document.getElementById('statusFilter').value;
  var startDate = document.getElementById('startDateFilter').value;
  var endDate = document.getElementById('endDateFilter').value;
  var futureOnly = document.getElementById('futureOnlyFilter').checked;

  return workshopMarkers.filter(function (location) {
    var status = getWorkshopStatus(location);
    if (searchValue && getLocationText(location).indexOf(searchValue) === -1) return false;
    if (cityValue && location.city !== cityValue) return false;
    if (statusValue && status !== statusValue) return false;
    if (futureOnly && status !== 'future' && status !== 'today') return false;
    if (startDate && location.date < startDate) return false;
    if (endDate && location.date > endDate) return false;
    return true;
  });
}

function renderWorkshopMarkers(locations) {
  workshopMarkerLayers.forEach(function (marker) {
    map.removeLayer(marker);
  });
  workshopMarkerLayers = [];
  locations.forEach(function (location) {
    var marker = L.marker([location.latitude, location.longitude]).addTo(map);
    marker.bindPopup(buildPopup(location));
    workshopMarkerLayers.push(marker);
  });
}

function updateFilterSummary(filteredLocations) {
  var summary = document.getElementById('filterSummary');
  var count = filteredLocations.length;
  var total = workshopMarkers.length;
  summary.textContent = 'Showing ' + count + ' of ' + total + ' workshop' + (total === 1 ? '.' : 's.');
}

function updateWorkshopFilters() {
  var filteredLocations = filterWorkshops();
  renderWorkshopMarkers(filteredLocations);
  buildEventList(filteredLocations);
  updateFilterSummary(filteredLocations);
}

function clearWorkshopFilters() {
  document.getElementById('workshopSearch').value = '';
  document.getElementById('cityFilter').value = '';
  document.getElementById('statusFilter').value = '';
  document.getElementById('startDateFilter').value = '';
  document.getElementById('endDateFilter').value = '';
  document.getElementById('futureOnlyFilter').checked = false;
  updateWorkshopFilters();
}

function buildPopup(location) {
  var html = '<strong>' + location.title + '</strong><br>';
  if (location.date) { html += '<em>' + location.date + '</em><br>'; }
  if (location.city) { html += location.city + '<br>'; }
  else if (location.address) { html += location.address + '<br>'; }
  if (location.description) { html += '<div style="margin-top:8px;">' + location.description + '</div>'; }
  if (location.photos && location.photos.length) {
    html += '<div style="margin-top:10px;">';
    location.photos.forEach(function (url) {
      html += '<img src="' + url + '" alt="' + location.title + '" style="width:100px; display:block; margin-top:8px;"/>';
    });
    html += '</div>';
  }
  return html;
}

function buildEventList(locations) {
  var container = document.getElementById('event-list');
  container.innerHTML = '';
  if (!locations.length) {
    var emptyText = workshopMarkers.length ? 'No workshops match the current filters.' : 'No workshop locations yet. Use the Django admin area to add new pins and photos.';
    container.innerHTML = '<div class="empty-state"><strong>' + emptyText + '</strong></div>';
    return;
  }
  locations.forEach(function (location) {
    var card = document.createElement('article');
    card.className = 'event-card';
    var header = document.createElement('div');
    header.className = 'event-card-header';
    var title = document.createElement('h3');
    title.textContent = location.title;
    header.appendChild(title);
    var deleteBtn = document.createElement('button');
    deleteBtn.className = 'delete-btn';
    deleteBtn.innerHTML = '&times;';
    deleteBtn.onclick = function() { 
      console.log('Delete button clicked for workshop ID:', location.id);
      deleteWorkshop(location.id); 
    };
    header.appendChild(deleteBtn);
    card.appendChild(header);
    if (location.date) {
      var date = document.createElement('p');
      date.innerHTML = '<strong>Date:</strong> ' + location.date;
      card.appendChild(date);
    }
    var status = document.createElement('p');
    status.innerHTML = '<strong>Status:</strong> ' + getWorkshopStatus(location).replace(/^\w/, function (letter) { return letter.toUpperCase(); });
    card.appendChild(status);
    if (location.city) {
      var city = document.createElement('p');
      city.innerHTML = '<strong>City:</strong> ' + location.city;
      card.appendChild(city);
    }
    if (location.address && location.address !== location.city) {
      var address = document.createElement('p');
      address.innerHTML = '<strong>Location:</strong> ' + location.address;
      card.appendChild(address);
    }
    if (location.description) {
      var description = document.createElement('p');
      description.textContent = location.description;
      card.appendChild(description);
    }
    if (location.photos) {
      location.photos.forEach(function (photoUrl) {
        var image = document.createElement('img');
        image.src = photoUrl;
        image.alt = location.title;
        card.appendChild(image);
      });
    }
    container.appendChild(card);
  });
}

function deleteWorkshop(workshopId) {
  console.log('deleteWorkshop called with ID:', workshopId);
  if (confirm('Are you sure you want to delete this workshop?')) {
    console.log('User confirmed deletion');
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]');
    console.log('CSRF token element:', csrfToken);
    if (!csrfToken) {
      alert('CSRF token not found');
      return;
    }
    const csrfValue = csrfToken.value;
    console.log('CSRF token value:', csrfValue);
    
    var deleteUrl = (window.urls && window.urls.shipment_map) ? window.urls.shipment_map : '';
    fetch(deleteUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
      body: 'delete_workshop=' + workshopId + '&csrfmiddlewaretoken=' + csrfValue
    })
    .then(response => {
      console.log('Response received:', response);
      console.log('Response status:', response.status);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      return response.json();
    })
    .then(data => {
      console.log('Response data:', data);
      if (data.success) {
        console.log('Success - reloading page');
        location.reload();
      } else {
        console.log('Error:', data.error);
          if (data.error === 'Authentication required') {
          alert('You must be logged in as an admin to delete workshops.');
          window.location.href = (window.urls && window.urls.login) ? window.urls.login : window.location.href;
        } else {
          alert('Error deleting workshop: ' + data.error);
        }
      }
    })
    .catch(error => {
      console.error('Fetch error:', error);
      alert('Error deleting workshop: ' + error.message);
    });
  } else {
    console.log('User cancelled deletion');
  }
}

function updatePinForm(latlng) {
  document.getElementById('pinLatitude').value = latlng.lat.toFixed(6);
  document.getElementById('pinLongitude').value = latlng.lng.toFixed(6);
  document.getElementById('pinCoordinates').innerText = latlng.lat.toFixed(5) + ', ' + latlng.lng.toFixed(5);
}

function cancelPinPlacement() {
  if (newPinMarker) {
    map.removeLayer(newPinMarker);
    newPinMarker = null;
  }
  if (pinHint) { pinHint.innerText = 'Click the button, then click the map to place a new pin.'; }
  if (pinModal) { pinModal.style.display = 'none'; }
}

var newPinMarker = null;
var addPinButton = document.getElementById('addPinButton');
var pinHint = document.getElementById('pinHint');
var pinModal = document.getElementById('pinModal');
var closePinModal = document.getElementById('closePinModal');
var cancelPinButton = document.getElementById('cancelPinButton');

if (addPinButton) {
  addPinButton.addEventListener('click', function () {
    if (pinHint) { pinHint.innerText = 'Click anywhere on the map to place a new workshop pin.'; }
    map.once('click', function (e) {
      var latlng = e.latlng;
      if (newPinMarker) { map.removeLayer(newPinMarker); }
      newPinMarker = L.marker(latlng, { draggable: true }).addTo(map);
      newPinMarker.on('dragend', function (event) { updatePinForm(event.target.getLatLng()); });
      updatePinForm(latlng);
      if (pinModal) { pinModal.style.display = 'block'; }
      map.panTo(latlng);
    });
  });
}

if (closePinModal) { closePinModal.addEventListener('click', cancelPinPlacement); }
if (cancelPinButton) { cancelPinButton.addEventListener('click', cancelPinPlacement); }
window.addEventListener('click', function (event) {
  if (event.target === shipmentModal) { shipmentModal.style.display = 'none'; }
  if (event.target === pinModal) { pinModal.style.display = 'none'; }
});

renderCityOptions(workshopMarkers);
['workshopSearch', 'cityFilter', 'statusFilter', 'startDateFilter', 'endDateFilter', 'futureOnlyFilter'].forEach(function (id) {
  var element = document.getElementById(id);
  var eventName = element.type === 'search' ? 'input' : 'change';
  element.addEventListener(eventName, updateWorkshopFilters);
});
document.getElementById('clearWorkshopFilters').addEventListener('click', clearWorkshopFilters);
updateWorkshopFilters();

var allPoints = [originCoord, destinationCoord];
workshopMarkers.forEach(function (loc) { allPoints.push([loc.latitude, loc.longitude]); });
if (allPoints.length > 2) {
  map.fitBounds(allPoints);
} else {
  map.fitBounds(routePoints);
}