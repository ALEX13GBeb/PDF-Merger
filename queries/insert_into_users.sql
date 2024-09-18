INSERT INTO users (
    username,
    password,
    email,
    first_name,
    last_name,
    gender,
    account_type
) VALUES (%s, %s, %s, %s, %s, %s, DEFAULT)