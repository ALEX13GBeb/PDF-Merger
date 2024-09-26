const editButton = document.getElementById('info_edit');
const saveButton = document.getElementById('save_button');
const cancelButton = document.getElementById("cancel_button");
const inputs = document.querySelectorAll('.info-box input');
const changePassButton = document.getElementById("changePass");
const cancelPassButton = document.getElementById("cancel_pass_button");
const submitPassButton = document.getElementById('submit_pass_button');
const passForm = document.getElementById("changePasswordForm");
//The querySelectorAll method is used to select multiple elements from the DOM (Document Object Model)
//that match a specified CSS selector.
//It returns a static (non-live) NodeList of all matching elements.

editButton.addEventListener('click', function() {
    inputs.forEach(input => input.disabled = false); // Enable all input fields
    saveButton.style.display = 'block'; // Show the save button
    cancelButton.style.display = 'block'; // Show the cancel button
});

saveButton.addEventListener('click', function() {
    const updatedData = {
        lastName: document.getElementById('last_name').value,
        firstName: document.getElementById('first_name').value,
        username: document.getElementById('username').value,
        email: document.getElementById('email').value,
    };

    fetch('/update_user', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(updatedData),
    })
    .then(response => response.json())
    .then(data => {
        console.log('Success:', data); // Debugging
    })
    .catch((error) => {
        console.error('Error:', error);
    });// Debugging

    // Disable input fields after saving
    inputs.forEach(input => input.disabled = true);
    saveButton.style.display = 'none'; // Hide the save button again
    cancelButton.style.display = 'none';
});

cancelButton.addEventListener("click", function(){
    inputs.forEach(input => {
         if (input.id !== 'password' && input.id !== 're_password') {
         input.disabled = true}
    });
    saveButton.style.display = 'none'; // Hide the save button again
    cancelButton.style.display = 'none'; // Hide the cancel button
});

const passwordEye = document.getElementById("pass_img");
const passwordInput = document.getElementById("password");

const re_passwordEye = document.getElementById("re_pass_img");
const re_passwordInput = document.getElementById("re_password");

const eyeOpenSrc = passwordEye.getAttribute('data-eye-open');
const eyeCloseSrc = passwordEye.getAttribute('data-eye-close');

passwordEye.onclick = function() {
    if (passwordInput.type === "password") {
        passwordInput.type = "text";
        passwordEye.src = eyeOpenSrc;
    } else {
        passwordInput.type = "password";
        passwordEye.src = eyeCloseSrc;
    }
};

re_passwordEye.onclick = function() {
    if (re_passwordInput.type === "password") {
        re_passwordInput.type = "text";
        re_passwordEye.src = eyeOpenSrc;
    } else {
        re_passwordInput.type = "password";
        re_passwordEye.src = eyeCloseSrc;
    }
};


function confirmDelete() {
    if (confirm("Are you sure you want to delete your account? This action cannot be undone.")) {
        document.getElementById("deleteAccountForm").submit();
    }
};

function displayChangePassword(button) {
    // Hide the button that was clicked
    changePassButton.style.display = "none"; // Hide the button
    submitPassButton.style.display = "block";
    cancelPassButton.style.display = "block";
    // Show the form
    if (passForm) {
        passForm.style.display = "block"; // Show the form
    }
};

submitPassButton.addEventListener("click", function() {
    if (document.getElementById("password").value == document.getElementById("re_password").value) {
        passForm.submit();
        changePassButton.style.display = "block";
        submitPassButton.style.display = 'none'; // Hide the save button again
        cancelPassButton.style.display = 'none'; // Hide the cancel button
        if (passForm) {
            passForm.style.display = "none"; // Show the form
        }
        document.getElementById("password").value = "";
        document.getElementById("re_password").value = "";
    }
    else {alert("The passwords don't match!")};
});

cancelPassButton.addEventListener("click", function(){
    changePassButton.style.display = "block";
    submitPassButton.style.display = 'none'; // Hide the save button again
    cancelPassButton.style.display = 'none'; // Hide the cancel button
    if (passForm) {
        passForm.style.display = "none"; // Show the form
    }
});

document.addEventListener('DOMContentLoaded', function() {
    const points = parseInt(document.getElementById('points').value);
    const premiumButton = document.getElementById('premium-button');

    // Check if points are 1000 or more
    if (points >= 1000) {
        premiumButton.disabled = false;
        premiumButton.classList.add('enabled');
        premiumButton.style.cursor = "pointer";
    }
});



