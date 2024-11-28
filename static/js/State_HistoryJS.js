// Reset Button Logic
document.getElementById('reset-button').addEventListener('click', () => {
    document.getElementById('start-date').value = '';
    document.getElementById('end-date').value = '';
    document.getElementById('x-param').value = '';
    document.getElementById('y-param').value = '';
    alert('Form reset!');
});

// Handle Form Submission
document.getElementById('data-form').addEventListener('submit', function (e) {
    e.preventDefault();
    const formData = new FormData(this);

    fetch('/get-data', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            document.getElementById('graph-area').innerHTML = data.graph;
            alert(data.message);
        } else {
            alert('Error fetching data');
        }
    })
    .catch(error => console.error('Error:', error));
});
