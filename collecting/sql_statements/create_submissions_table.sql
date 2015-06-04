CREATE TABLE `reddit_comments`.`submissions` (
  `idsubmissions` INT NOT NULL AUTO_INCREMENT,
  `submission_id` VARCHAR(45) NULL,
  `title` VARCHAR(45) NULL,
  `content` BLOB NULL,
  `timestamp` INT NULL,
  `created` INT NULL,
  `score` INT NULL,
  `author` VARCHAR(45) NULL,
  `num_comments` INT NULL,
  PRIMARY KEY (`idsubmissions`));
