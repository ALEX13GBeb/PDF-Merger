console.log("script.js loaded");

// Your actual JavaScript code for password strength
document.getElementById('password').addEventListener('input', function() {
    const password = this.value;
    const strength = getPasswordStrength(password);

    console.log('Password:', password, 'Strength:', strength); // Debugging

    const passwordBar = document.getElementById('password-bar');
    if (passwordBar) {
        passwordBar.className = 'strength-' + strength;
        console.log('Password bar class:', passwordBar.className); // Debugging
    } else {
        console.log('Element with ID "password-bar" not found.');
    }
});

function getPasswordStrength(password) {
    let strength = 0;
    if (password.length >= 8) {
        strength += 1;
        if (/\d/.test(password)) {
            strength += 1;
            if (/[a-zA-Z]/.test(password)) {
                strength += 1;
                if (/[^\da-zA-Z]/.test(password)) {
                    strength += 1;
                }
            }
        }
    }
    return strength;
}
