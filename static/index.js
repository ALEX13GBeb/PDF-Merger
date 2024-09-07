document.addEventListener("DOMContentLoaded", function() {
    var fileInput = document.getElementById("inputfiles");
    var errorElement = document.getElementById("error_number_files");
    var submitButton = document.getElementById("submit_button");
    var form = document.getElementById("index_form");
    submitButton.disabled = true;
    // Event listener for file input changes
    fileInput.addEventListener("change", function() {
        var fileCount = fileInput.files.length;

        if (fileCount < 2) {
            errorElement.textContent = "Not enough files to merge";
            submitButton.disabled = true; // Disable the submit button if less than 2 files
        } else {
            errorElement.textContent = "";
            submitButton.disabled = false; // Enable the submit button if 2 or more files
        }
    });
});


function showPdfForm() {
    document.getElementById("red_rectangle").style.display = "none"; // Hide the rectangle
    document.getElementById("blue_rectangle").style.display = "flex"; // Hide the rectangle
    document.getElementById("green_rectangle").style.display = "flex"; // Hide the rectangle
    document.getElementById("orange_rectangle").style.display = "flex"; // Hide the rectangle
    document.getElementById("index_form").style.display = "flex"; // Show the form
    document.getElementById("word_form").style.display = "none"; // Show the form
    document.getElementById("excel_form").style.display = "none"; // Show the form
    document.getElementById("pp_form").style.display = "none";
}

function showWordForm() {
    document.getElementById("red_rectangle").style.display = "flex"; // Hide the rectangle
    document.getElementById("blue_rectangle").style.display = "none"; // Hide the rectangle
    document.getElementById("green_rectangle").style.display = "flex"; // Hide the rectangle
    document.getElementById("orange_rectangle").style.display = "flex"; // Hide the rectangle
    document.getElementById("index_form").style.display = "none"; // Show the form
    document.getElementById("word_form").style.display = "flex"; // Show the form
    document.getElementById("excel_form").style.display = "none"; // Show the form
    document.getElementById("pp_form").style.display = "none";
}

function showExcelForm() {
    document.getElementById("red_rectangle").style.display = "flex"; // Hide the rectangle
    document.getElementById("blue_rectangle").style.display = "flex"; // Hide the rectangle
    document.getElementById("green_rectangle").style.display = "none"; // Hide the rectangle
    document.getElementById("orange_rectangle").style.display = "flex"; // Hide the rectangle
    document.getElementById("index_form").style.display = "none"; // Show the form
    document.getElementById("word_form").style.display = "none"; // Show the form
    document.getElementById("excel_form").style.display = "flex"; // Show the form
    document.getElementById("pp_form").style.display = "none";
}

function showPPForm() {
    document.getElementById("red_rectangle").style.display = "flex"; // Hide the rectangle
    document.getElementById("blue_rectangle").style.display = "flex"; // Hide the rectangle
    document.getElementById("green_rectangle").style.display = "flex"; // Hide the rectangle
    document.getElementById("orange_rectangle").style.display = "none"; // Hide the rectangle
    document.getElementById("index_form").style.display = "none"; // Show the form
    document.getElementById("word_form").style.display = "none"; // Show the form
    document.getElementById("excel_form").style.display = "none"; // Show the form
    document.getElementById("pp_form").style.display = "flex";
}
