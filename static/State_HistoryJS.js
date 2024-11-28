
let map, marker, speedChart, fuelChart;

// Initialize Google Map
function initMap() {
    const defaultLocation = { lat: 28.7041, lng: 77.1025 };
    map = new google.maps.Map(document.getElementById("map"), {
        center: defaultLocation,
        zoom: 12,
    });

    marker = new google.maps.Marker({
        position: defaultLocation,
        map: map,
        title: "Vehicle Location",
    });
}

// Fetch Real-Time Data
async function fetchRealTimeData(chassisNumber) {
    setInterval(async () => {
        const response = await fetch(`/real-time-data/${chassisNumber}`);
        if (response.ok) {
            const data = await response.json();

            // Update map marker
            const newLocation = { lat: data.lat, lng: data.lng };
            marker.setPosition(newLocation);
            map.panTo(newLocation);

            console.log("Real-Time Data:", data);
        } else {
            console.error("Error fetching real-time data");
        }
    }, 2000);
}

// Fetch Historical Data
async function fetchHistoricalData(chassisNumber, startDate, endDate) {
    const response = await fetch(`/historical-data/${chassisNumber}?start_date=${startDate}&end_date=${endDate}`);
    if (response.ok) {
        const data = await response.json();
        const speedData = data.map((entry) => entry.speed);
        const fuelData = data.map((entry) => entry.fuel_level);
        const labels = data.map((entry) => entry.timestamp);

        updateChart(speedChart, labels, speedData);
        updateChart(fuelChart, labels, fuelData);

        console.log("Historical Data:", data);
    } else {
        console.error("Error fetching historical data");
    }
}

// Update Chart
function updateChart(chart, labels, data) {
    chart.data.labels = labels;
    chart.data.datasets[0].data = data;
    chart.update();
}

// Create Charts
function createCharts() {
    const speedCtx = document.getElementById("speed-chart").getContext("2d");
    const fuelCtx = document.getElementById("fuel-chart").getContext("2d");

    speedChart = new Chart(speedCtx, {
        type: "line",
        data: {
            labels: [],
            datasets: [{ label: "Speed (km/h)", data: [], borderColor: "blue", fill: false }],
        },
    });

    fuelChart = new Chart(fuelCtx, {
        type: "line",
        data: {
            labels: [],
            datasets: [{ label: "Fuel Level (%)", data: [], borderColor: "green", fill: false }],
        },
    });
}

// Button Click Event
document.getElementById("fetch-data").addEventListener("click", () => {
    const chassisNumber = document.getElementById("chassis-number").value;
    const startDate = document.getElementById("start-date").value;
    const endDate = document.getElementById("end-date").value;

    if (chassisNumber) {
        fetchRealTimeData(chassisNumber);
        fetchHistoricalData(chassisNumber, startDate, endDate);
    } else {
        alert("Please enter a chassis number!");
    }
});

// // Initialize map and charts on load
// window.onload = () => {
//     initMap();
//     createCharts();
// };
// const updateStats = () => {
//     document.getElementById("distance").innerText = `${Math.floor(Math.random() * 500)} km`;
//     document.getElementById("speed").innerText = `${Math.floor(Math.random() * 100)} km/h`;
//     document.getElementById("engine-hrs").innerText = `${Math.floor(Math.random() * 20)} hrs`;
//     document.getElementById("fuel-level").innerText = `${Math.floor(Math.random() * 100)}%`;
//     document.getElementById("milage").innerText = `${Math.floor(Math.random() * 30)} km/l`;
//     document.getElementById("adblue").innerText = `${Math.random().toFixed(1)} L`;
//   };
  
//   setInterval(updateStats, 3000); // Update every 3 seconds
  
//   document.getElementById("reset-btn").addEventListener("click", () => {
//     document.getElementById("start-date").value = "";
//     document.getElementById("end-date").value = "";
//     document.getElementById("x-param").value = "";
//     document.getElementById("y-param").value = "";
//   });
  