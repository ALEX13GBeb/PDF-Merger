UPDATE subscriptions
SET
    account_type = "Deleted",
    points = 0,
    pro_subscription = NULL,
    pro_start_date = NULL,
    pro_end_date = NULL
WHERE user_id = %s;