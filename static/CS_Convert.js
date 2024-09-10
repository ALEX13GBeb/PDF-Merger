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

function restrictFileNameInput(event) {
    const invalidChars = ['/', '\\', ':', '*', '?', '"', '|', '<', '>']; // Array of invalid characters
    const key = event.key; // The key that was pressed

    // If the pressed key is in the list of restricted characters
    if (invalidChars.includes(key)) {
        event.preventDefault(); // Prevent the character from being typed
        alert(`The character "${key}" is not allowed in the file name.\nList of invalid characters: / \\ : * ? " | < >`);

    }
}
