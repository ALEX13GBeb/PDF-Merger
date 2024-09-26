UPDATE users
SET
    username = "-",
    password = "-" ,
    first_name = "-",
    last_name = "-",
    gender = DEFAULT,
    account_type = "Deleted"
WHERE id = %s;