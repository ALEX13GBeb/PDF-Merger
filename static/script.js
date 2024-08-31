console.log("Hello");
document.getElementById('password').addEventListener('input', function() {
            const password = this.value;
            const strength = getPasswordStrength(password);

            const passwordBar = document.getElementById("password-bar");
            passwordBar.style.backgroundColor = 'white';

            switch (strength) {
                case 1:
                    passwordBar.style.backgroundColor = '#AA0000';
                    console.log(passwordBar.className);
                    passwordBar.textContent = 'Weak Password';
                    break;

                case 2:
                    passwordBar.style.backgroundColor = 'orange';
                    passwordBar.textContent = 'Fair Password';
                    break;

                case 3:
                    passwordBar.style.backgroundColor = '#0066FF';
                    passwordBar.textContent = 'Good Password';
                    break;

                case 4:
                    passwordBar.style.backgroundColor = 'green';
                    passwordBar.textContent = 'Very Strong Password';
                    break;

                default:
                    passwordBar.style.backgroundColor = 'white'; // Default case
                    passwordBar.textContent = '';
            }
        });

function getPasswordStrength(password) {
    let strength = 0;
    if (password.length >= 8) {
        strength += 1;
    }
    if (/\d/.test(password)) {
        strength += 1;
    }
    if (/[a-zA-Z]/.test(password)) {
        strength += 1;
    }
    if (/[^\da-zA-Z]/.test(password)) {
        strength += 1;
    }

    return strength;
}
