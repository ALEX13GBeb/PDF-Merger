CREATE TABLE IF NOT EXISTS `merge_data`.`subscriptions` (
    `user_id` INT(6) UNSIGNED ZEROFILL NOT NULL,
    `account_type` VARCHAR(50) NOT NULL DEFAULT 'Free',
    `points` INT UNSIGNED NOT NULL DEFAULT 0,
    `pro_subscription` INT DEFAULT NULL,
    `pro_start_date` DATE DEFAULT NULL,
    `pro_end_date` DATE DEFAULT NULL,
    PRIMARY KEY (`user_id`)
);