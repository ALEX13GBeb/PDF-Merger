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


window.onload = function() {
    if (!window.loggedIn) {
        console.log("Page fully loaded");
        console.log("User logged in status:", window.loggedIn);

        // Disable all form inputs if not logged in
        const forms = document.querySelectorAll("form");
        forms.forEach(form => {
            const inputs = form.querySelectorAll("input");
            inputs.forEach(input => input.disabled = true);
        });

        // Hide the paragraph with the accountNeeded class
        const accountMessage = document.querySelector(".accountNeeded");
        if (accountMessage) {
            accountMessage.style.display = "block"; // Ensure it's visible when not logged in
        }
    } else {
        // Hide the paragraph if the user is logged in
        const accountMessage = document.querySelector(".accountNeeded");
        if (accountMessage) {
            accountMessage.style.display = "none";
        }
    }
};

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


document.getElementById('ppfiles').addEventListener('change', function() {
    document.getElementById('pp_form').submit();
});

document.getElementById('wordfiles').addEventListener('change', function() {
    document.getElementById('word_form').submit();
});

document.getElementById('excelfiles').addEventListener('change', function() {
    document.getElementById('excel_form').submit();
});

document.getElementById('jpegfiles').addEventListener('change', function() {
    document.getElementById('jpeg_form').submit();
});

document.getElementById('giffiles').addEventListener('change', function() {
    document.getElementById('gif_form').submit();
});

document.getElementById('pngfiles').addEventListener('change', function() {
    document.getElementById('png_form').submit();
});

document.getElementById('bmpfiles').addEventListener('change', function() {
    document.getElementById('bmp_form').submit();
});

document.addEventListener('scroll', function() {
        var footer = document.querySelector('footer');
        var scrollPosition = window.scrollY + window.innerHeight;
        var documentHeight = document.documentElement.scrollHeight;

        // Show footer when scrolling down past 80% of the page
        if (scrollPosition > documentHeight * 0.8) {
            footer.classList.add('show');
        } else {
            footer.classList.remove('show');
        }
    });
