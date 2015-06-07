USE UTF!!!

CREATE TABLE `reddit_comments`.`comments` (
  `idcomments` INT NOT NULL AUTO_INCREMENT,
  `comment_id` VARCHAR(45) NULL,
  `user_id` VARCHAR(45) NULL,
  `submission_id` VARCHAR(45) NULL,
  `prev_comment_id` VARCHAR(45) NULL,
  `created` INT NULL,
  `timestamp` INT NULL,
  `content` BLOB NULL,
  `subreddit` VARCHAR(45) NULL,
  `score` INT NULL,
  PRIMARY KEY (`idcomments`));
