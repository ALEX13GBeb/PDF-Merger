document.getElementById('fileInput').addEventListener('change', function() {
    document.getElementById('addform').submit();
});

document.getElementById('convert_button').addEventListener('click', function() {
    document.getElementById("convert_button").disabled = true;
    document.getElementById('convert_form').submit();
    document.getElementById('convert_form').remove();
    document.getElementById("file-count").style.display = "none";
});

function removeFile(button) {
    const iconItem = button.closest('.icon-item');
    const fileName = iconItem.getAttribute('data-file-name');
    const fileCounter = document.getElementById("file-count-value")
    const countContainer = document.getElementById("file-count")
    // Send an AJAX request to delete the file from the server
    fetch('/deleteFile', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json' // - indicates that the body of the request will be in JSON format.
        },
        body: JSON.stringify({ fileName: fileName })
    })// The request body is a JSON object containing the file name

    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Remove the icon item from the DOM if deletion is successful
            iconItem.remove();
            if (data.file_count!==0) {
                fileCounter.textContent = data.file_count;}
            else {
                countContainer.style.display = "none";
                document.getElementById("convert_button").disabled = true;
            }
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
