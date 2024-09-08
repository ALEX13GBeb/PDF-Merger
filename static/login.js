const passwordEye = document.getElementById("pass_img");
const passwordInput = document.getElementById("password");

// Get the image URLs from data attributes
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