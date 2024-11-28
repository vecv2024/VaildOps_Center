function toggleMenu() {
    const menu = document.getElementById('dropdown-menu');
    menu.style.display = menu.style.display === 'block' ? 'none' : 'block';
}

function initMap() {
    const userLocation = { lat: 28.6139, lng: 77.209 }; // Example: Delhi
    const map = new google.maps.Map(document.getElementById('map'), {
        center: userLocation,
        zoom: 14,
    });

    new google.maps.Marker({
        position: userLocation,
        map: map,
        title: 'Your Location',
        icon: 'http://maps.google.com/mapfiles/ms/icons/blue-dot.png',
    });

    for (let i = 0; i < 5; i++) {
        const randomLocation = getRandomLocation(userLocation, 2000);
        new google.maps.Marker({
            position: randomLocation,
            map: map,
            title: `Vehicle ${i + 1}`,
            icon: 'http://maps.google.com/mapfiles/ms/icons/red-dot.png',
        });
    }
}

function getRandomLocation(center, radius) {
    const y0 = center.lat;
    const x0 = center.lng;
    const rd = radius / 111300;

    const u = Math.random();
    const v = Math.random();
    const w = rd * Math.sqrt(u);
    const t = 2 * Math.PI * v;
    const x = w * Math.cos(t);
    const y = w * Math.sin(t);

    return { lat: y0 + y, lng: x0 + x };
}

function updateParameters() {
    // Generate random values within a realistic range
    const distance = getRandomValue(50, 100); // Distance in KM updated.......
    const operationHours = getRandomValue(10, 100); // Hours......
    const speed = getRandomValue(20, 120); // Speed in km/h........
    const engineRpm = getRandomValue(1000, 2000); // RPM
    const fuelLevel = getRandomValue(10, 100); // Fuel level %
    const engineTemp = getRandomValue(70, 110); // Engine Temp in °C
    const coolantTemp = getRandomValue(50, 90); // Coolant Temp in °C
    const oilPressure = getRandomValue(1, 5); // Oil Pressure in bar

    // Update HTML
    document.getElementById('distance').textContent = `${distance.toFixed(1)} KM`;
    document.getElementById('operation-hrs').textContent = `${operationHours.toFixed(1)} Hrs`;
    document.getElementById('speed').textContent = `${speed.toFixed(1)} km/h`;
    document.getElementById('engine-rpm').textContent = engineRpm.toFixed(0);
    document.getElementById('fuel-level').textContent = `${fuelLevel.toFixed(1)}%`;
    document.getElementById('engine-temp').textContent = `${engineTemp.toFixed(1)}°C`;
    document.getElementById('coolant-temp').textContent = `${coolantTemp.toFixed(1)}°C`;
    document.getElementById('oil-pressure').textContent = `${oilPressure.toFixed(1)} bar`;
}

function updateTime() {
    const now = new Date();
    const timeString = now.toLocaleTimeString('en-US', { hour12: false });
    document.title = `Dashboard - ${timeString}`;
}

function initCharts() {
    const accelerationCtx = document.getElementById('acceleration-chart').getContext('2d');
    const speedCtx = document.getElementById('speed-chart').getContext('2d');
    const oilPressureCtx = document.getElementById('oil-pressure-chart').getContext('2d');

    const accelerationChart = new Chart(accelerationCtx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [{
                label: 'Acceleration',
                data: [],
                borderColor: '#D32F2F', /* Red */
                fill: false,
            }],
        },
    });

    const speedChart = new Chart(speedCtx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [{
                label: 'Speed',
                data: [],
                borderColor: '#004080', /* Dark blue */
                fill: false,
            }],
        },
    });

    const oilPressureChart = new Chart(oilPressureCtx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [{
                label: 'Oil Pressure',
                data: [],
                borderColor: '#FF9800', /* Orange */
                fill: false,
            }],
        },
    });

    setInterval(() => {
        const currentTime = new Date().toLocaleTimeString('en-US', { hour12: false });
        updateChart(accelerationChart, getRandomValue(0, 30), currentTime);
        updateChart(speedChart, getRandomValue(20, 120), currentTime);
        updateChart(oilPressureChart, getRandomValue(1, 5), currentTime);
    }, 5000);
}

function updateChart(chart, newValue, time) {
    const labels = chart.data.labels;
    const data = chart.data.datasets[0].data;

    labels.push(time);
    data.push(newValue);

    if (data.length > 10) {
        labels.shift();
        data.shift();
    }

    chart.update();
}

function getRandomValue(min, max) {
    return parseFloat((Math.random() * (max - min) + min).toFixed(2));
}

window.onload = function () {
    initMap();
    initCharts();
    updateParameters();
    updateTime();

    // Update parameters and time every 5 seconds
    setInterval(() => {
        updateParameters();
        updateTime();
    }, 5000);
};
