// Example Data
const modelData = [
    { stickerNo: 1, speed: "40 Km/h", distance: "150 Km", engineHrs: "4 h", location: "Delhi" },
    { stickerNo: 2, speed: "40 Km/h", distance: "0 Km", engineHrs: "0 h", location: "Indore" },
    { stickerNo: 3, speed: "40 Km/h", distance: "200 Km", engineHrs: "5 h", location: "Pune" },
    { stickerNo: 4, speed: "40 Km/h", distance: "400 Km", engineHrs: "10 h", location: "Bhopal" },
    { stickerNo: 5, speed: "40 Km/h", distance: "350 Km", engineHrs: "9 h", location: "Kolkata" },
    { stickerNo: 6, speed: "40 Km/h", distance: "200 Km", engineHrs: "5 h", location: "Delhi" },
    { stickerNo: 7, speed: "50 Km/h", distance: "120 Km", engineHrs: "6 h", location: "Mumbai" },
    { stickerNo: 8, speed: "45 Km/h", distance: "180 Km", engineHrs: "7 h", location: "Chennai" },
    { stickerNo: 9, speed: "60 Km/h", distance: "250 Km", engineHrs: "8 h", location: "Hyderabad" },
    { stickerNo: 10, speed: "55 Km/h", distance: "300 Km", engineHrs: "9 h", location: "Bangalore" },
    { stickerNo: 11, speed: "70 Km/h", distance: "350 Km", engineHrs: "10 h", location: "Ahmedabad" },
    { stickerNo: 12, speed: "65 Km/h", distance: "400 Km", engineHrs: "12 h", location: "Jaipur" }
];

// Function to create grid boxes
function createGridBoxes(start, end) {
    const container = document.getElementById("grid-box-container");
    container.innerHTML = "";  // Clear existing grid boxes

    // Loop through the data to create the grid boxes
    for (let i = start; i <= end; i++) {
        const boxData = modelData[i - 1];  // Get data for the current model sticker
        const gridBox = document.createElement("div");
        gridBox.classList.add("grid-box");

        gridBox.innerHTML = `
            <table class="box-table">
                <tr>
                    <td colspan="2">Model Sticker No: ${boxData.stickerNo}</td>
                </tr>
                <tr>
                    <td>Speed: ${boxData.speed}</td>
                    <td>Distance: ${boxData.distance}</td>
                </tr>
                <tr>
                    <td>Engine Hrs: ${boxData.engineHrs}</td>
                    <td>Location: ${boxData.location}</td>
                </tr>
            </table>
        `;
        
        container.appendChild(gridBox);  // Add the grid box to the container
    }
}

// Initialize the grid with the first 6 items
createGridBoxes(1, 6);

// Pagination functions
let currentPage = 1;
const totalPages = Math.ceil(modelData.length / 6);  // Calculate total pages

// Function to go to the next page
function goRight() {
    if (currentPage < totalPages) {
        currentPage++;
        const start = (currentPage - 1) * 6 + 1;
        const end = currentPage * 6;
        createGridBoxes(start, end);
        updatePaginationButtons();
    }
}

// Function to go to the previous page
function goLeft() {
    if (currentPage > 1) {
        currentPage--;
        const start = (currentPage - 1) * 6 + 1;
        const end = currentPage * 6;
        createGridBoxes(start, end);
        updatePaginationButtons();
    }
}

// Function to update the state of the pagination buttons
function updatePaginationButtons() {
    document.getElementById('prev-btn').disabled = currentPage === 1;
    document.getElementById('next-btn').disabled = currentPage === totalPages;
}

// Event listeners for pagination buttons
document.getElementById("prev-btn").addEventListener("click", goLeft);
document.getElementById("next-btn").addEventListener("click", goRight);

// Initialize pagination state
updatePaginationButtons();
