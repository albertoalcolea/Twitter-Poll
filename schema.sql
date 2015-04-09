DROP TABLE IF EXISTS `metadata`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `metadata` (
  `project_hashtag` varchar(140) NOT NULL PRIMARY KEY,
  `start_date` timestamp NOT NULL DEFAULT '0000-00-00 00:00:00',
  `end_date` timestamp NOT NULL DEFAULT '0000-00-00 00:00:00',
  `consumer_key` text NULL,
  `consumer_secret` text NULL,
  `access_token_key` text NULL,
  `access_token_secret` text NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;


DROP TABLE IF EXISTS `options`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `options` (
  `hashtag` varchar(140) NOT NULL PRIMARY KEY
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;


DROP TABLE IF EXISTS `tweets`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `tweets` (
  `id` bigint(20) NOT NULL DEFAULT '0' PRIMARY KEY,
  `author_id` bigint(20) NOT NULL DEFAULT '0',
  `author_name` varchar(15) NOT NULL,
  `published_on` timestamp NOT NULL DEFAULT '0000-00-00 00:00:00',
  `tweet` varchar(140) NOT NULL,
  `option` varchar(140) NOT NULL,
  `is_retweet` bool NOT NULL,
  `original_id` bigint(20),
  CONSTRAINT `FK_option` FOREIGN KEY (`option`) REFERENCES `options` (`hashtag`) ON DELETE CASCADE,
  CONSTRAINT `UC_author_id` UNIQUE (`author_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;