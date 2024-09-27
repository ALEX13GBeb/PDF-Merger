UPDATE subscriptions
SET points = points - 1000,
    account_type = 'Premium',
    pro_subscription = 7,
    pro_start_date = CURDATE(),
    pro_end_date = DATE_ADD(CURDATE(), INTERVAL 7 DAY)
WHERE user_id = %s;