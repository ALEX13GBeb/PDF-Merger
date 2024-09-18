UPDATE `merge_data`.`users`
SET
`username` = %s,
`password` = %s,
`email` = %s,
`first_name` = %s,
`last_name` = %s
WHERE `username` = %s;