document.getElementById('filterData').addEventListener('click', () => {
    const startDate = document.getElementById('startDate').value;
    const endDate = document.getElementById('endDate').value;

    if (startDate && endDate) {
        fetch(`/filter-data?start=${startDate}&end=${endDate}`)
            .then(response => response.json())
            .then(data => {
                alert("Data fetched successfully!"); // Replace with actual graph updates
            })
            .catch(error => console.error("Error fetching data:", error));
    } else {
        alert("Please select both start and end dates.");
    }
});
