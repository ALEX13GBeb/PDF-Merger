SELECT u.first_name,
        u.last_name,
        u.username,
        u.email,
        u.password,
        s.points
FROM users u
JOIN subscriptions s
ON u.id = s.user_id
WHERE u.id = %s