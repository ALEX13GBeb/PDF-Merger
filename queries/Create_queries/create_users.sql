CREATE TABLE IF NOT EXISTS `merge_data`.`users` (
  `id` INT(6) UNSIGNED ZEROFILL NOT NULL AUTO_INCREMENT,
  `username` VARCHAR(50) NOT NULL,
  `password` VARCHAR(255) NOT NULL,
  `email` VARCHAR(255) NOT NULL,
  `first_name` VARCHAR(50) NOT NULL,
  `last_name` VARCHAR(50) NOT NULL,
  `gender` ENUM('male', 'female', 'undisclosed') NOT NULL DEFAULT 'undisclosed',
  PRIMARY KEY (`id`)
);