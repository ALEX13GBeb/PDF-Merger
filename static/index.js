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

function DisplayList0() {
    var listItem0 = document.getElementById("list_item0");

    if (listItem0.style.display === "flex") {
        listItem0.style.display = "none"; // Hide the forms
    }
    else {
        listItem0.style.display = "flex"; // Show the forms
        document.getElementById("red_rectangle").style.display = "flex"; // Hide the rectangle
        document.getElementById("index_form").style.display = "none"; // Show the form
        }}

function DisplayList1() {
    var listItem1 = document.getElementById("list_item1");

    if (listItem1.style.display === "flex") {
        listItem1.style.display = "none"; // Hide the forms
    }
    else {
        listItem1.style.display = "flex"; // Show the forms
        document.getElementById("blue_rectangle").style.display = "flex"; // Hide the rectangle
        document.getElementById("green_rectangle").style.display = "flex"; // Hide the rectangle
        document.getElementById("orange_rectangle").style.display = "flex"; // Hide the rectangle
        document.getElementById("word_form").style.display = "none"; // Show the form
        document.getElementById("excel_form").style.display = "none"; // Show the form
        document.getElementById("pp_form").style.display = "none";
        }}

function DisplayList2() {
    var listItem2 = document.getElementById("list_item2");

    if (listItem2.style.display === "flex") {
        listItem2.style.display = "none"; // Hide the forms
    }
    else {
        listItem2.style.display = "flex"; // Show the forms
        document.getElementById("jpeg_rectangle").style.display = "flex"; // Hide the rectangle
        document.getElementById("png_rectangle").style.display = "flex"; // Hide the rectangle
        document.getElementById("gif_rectangle").style.display = "flex"; // Hide the rectangle
        document.getElementById("bmp_rectangle").style.display = "flex"; // Hide the rectangle
        document.getElementById("jpeg_form").style.display = "none"; // Show the form
        document.getElementById("png_form").style.display = "none"; // Show the form
        document.getElementById("gif_form").style.display = "none"; // Show the form
        document.getElementById("bmp_form").style.display = "none";

        }
    }

function showJPEGForm() {
    document.getElementById("jpeg_rectangle").style.display = "none"; // Hide the rectangle
    document.getElementById("png_rectangle").style.display = "flex"; // Hide the rectangle
    document.getElementById("gif_rectangle").style.display = "flex"; // Hide the rectangle
    document.getElementById("bmp_rectangle").style.display = "flex"; // Hide the rectangle
    document.getElementById("jpeg_form").style.display = "flex"; // Show the form
    document.getElementById("png_form").style.display = "none"; // Show the form
    document.getElementById("gif_form").style.display = "none"; // Show the form
    document.getElementById("bmp_form").style.display = "none";
}
function showPNGForm() {
    document.getElementById("jpeg_rectangle").style.display = "flex"; // Hide the rectangle
    document.getElementById("png_rectangle").style.display = "none"; // Hide the rectangle
    document.getElementById("gif_rectangle").style.display = "flex"; // Hide the rectangle
    document.getElementById("bmp_rectangle").style.display = "flex"; // Hide the rectangle
    document.getElementById("jpeg_form").style.display = "none"; // Show the form
    document.getElementById("png_form").style.display = "flex"; // Show the form
    document.getElementById("gif_form").style.display = "none"; // Show the form
    document.getElementById("bmp_form").style.display = "none";
}
function showGIFForm() {
    document.getElementById("jpeg_rectangle").style.display = "flex"; // Hide the rectangle
    document.getElementById("png_rectangle").style.display = "flex"; // Hide the rectangle
    document.getElementById("gif_rectangle").style.display = "none"; // Hide the rectangle
    document.getElementById("bmp_rectangle").style.display = "flex"; // Hide the rectangle
    document.getElementById("jpeg_form").style.display = "none"; // Show the form
    document.getElementById("png_form").style.display = "none"; // Show the form
    document.getElementById("gif_form").style.display = "flex"; // Show the form
    document.getElementById("bmp_form").style.display = "none";
}
function showBMPForm() {
    document.getElementById("jpeg_rectangle").style.display = "flex"; // Hide the rectangle
    document.getElementById("png_rectangle").style.display = "flex"; // Hide the rectangle
    document.getElementById("gif_rectangle").style.display = "flex"; // Hide the rectangle
    document.getElementById("bmp_rectangle").style.display = "none"; // Hide the rectangle
    document.getElementById("jpeg_form").style.display = "none"; // Show the form
    document.getElementById("png_form").style.display = "none"; // Show the form
    document.getElementById("gif_form").style.display = "none"; // Show the form
    document.getElementById("bmp_form").style.display = "flex";
}





function showPdfForm() {
    document.getElementById("red_rectangle").style.display = "none"; // Hide the rectangle
    document.getElementById("index_form").style.display = "flex"; // Show the form
}

function showWordForm() {
    document.getElementById("blue_rectangle").style.display = "none"; // Hide the rectangle
    document.getElementById("green_rectangle").style.display = "flex"; // Hide the rectangle
    document.getElementById("orange_rectangle").style.display = "flex"; // Hide the rectangle
    document.getElementById("word_form").style.display = "flex"; // Show the form
    document.getElementById("excel_form").style.display = "none"; // Show the form
    document.getElementById("pp_form").style.display = "none";
}

function showExcelForm() {
    document.getElementById("blue_rectangle").style.display = "flex"; // Hide the rectangle
    document.getElementById("green_rectangle").style.display = "none"; // Hide the rectangle
    document.getElementById("orange_rectangle").style.display = "flex"; // Hide the rectangle
    document.getElementById("word_form").style.display = "none"; // Show the form
    document.getElementById("excel_form").style.display = "flex"; // Show the form
    document.getElementById("pp_form").style.display = "none";
}

function showPPForm() {
    document.getElementById("blue_rectangle").style.display = "flex"; // Hide the rectangle
    document.getElementById("green_rectangle").style.display = "flex"; // Hide the rectangle
    document.getElementById("orange_rectangle").style.display = "none"; // Hide the rectangle
    document.getElementById("word_form").style.display = "none"; // Show the form
    document.getElementById("excel_form").style.display = "none"; // Show the form
    document.getElementById("pp_form").style.display = "flex";
}
