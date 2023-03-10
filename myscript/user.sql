use weibo;

DROP TABLE IF EXISTS `t_follow_userprofile`;
CREATE TABLE `t_follow_userprofile` (
  `_id` varchar(45) NOT NULL,
  `avatar_hd` varchar(240) DEFAULT NULL,
  `nick_name` varchar(45) DEFAULT NULL,
  `verified` varchar(45) DEFAULT NULL,
  `description` varchar(360) DEFAULT NULL,
  `followers_count` int DEFAULT NULL,
  `friends_count` int DEFAULT NULL,
  `statuses_count` int DEFAULT NULL,
  `gender` varchar(45) DEFAULT NULL,
  `location` varchar(45) DEFAULT NULL,
  `mbrank` int DEFAULT NULL,
  `mbtype` int DEFAULT NULL,
  `birthday` varchar(120) DEFAULT NULL,
  `created_at` varchar(120) DEFAULT NULL,
  `desc_text` varchar(45) DEFAULT NULL,
  `ip_location` varchar(45) DEFAULT NULL,
  `sunshine_credit` varchar(45) DEFAULT NULL,
  `label_desc` varchar(45) DEFAULT NULL,
  `company` varchar(45) DEFAULT NULL,
  `education` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

