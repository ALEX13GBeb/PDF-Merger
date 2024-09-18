SELECT first_name,
        last_name,
        username,
        email,
        password
FROM users
WHERE username = %s AND
        password = %s;