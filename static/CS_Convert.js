function removeFile(button) {
    const iconItem = button.closest('.icon-item');
    const fileName = iconItem.getAttribute('data-file-name');

    // Send an AJAX request to delete the file from the server
    fetch('/deleteFile', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ fileName: fileName })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Remove the icon item from the DOM if deletion is successful
            iconItem.remove();
        } else {
            alert('Failed to delete the file');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('An error occurred');
    });
}