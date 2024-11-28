document.getElementById('reset-button').addEventListener('click', () => {
    document.getElementById('start-date').value = '';
    document.getElementById('end-date').value = '';
    document.getElementById('x-param').value = '';
    document.getElementById('y-param').value = '';
    alert('Form reset!');
});

