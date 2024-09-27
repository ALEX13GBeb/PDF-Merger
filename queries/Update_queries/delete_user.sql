UPDATE users
SET
    username = "-",
    password = "-" ,
    first_name = "-",
    last_name = "-",
    gender = DEFAULT
WHERE id = %s;