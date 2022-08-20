Query
SELECT `tb_address`.`id`,
       `tb_address`.`create_time`,
       `tb_address`.`update_time`,
       `tb_address`.`user_id`,
       `tb_address`.`title`,
       `tb_address`.`receiver`,
       `tb_address`.`province_id`,
       `tb_address`.`city_id`,
       `tb_address`.`district_id`,
       `tb_address`.`place`,
       `tb_address`.`mobile`,
       `tb_address`.`tel`,
       `tb_address`.`email`,
       `tb_address`.`is_deleted`
FROM `tb_address`
WHERE (NOT `tb_address`.`is_deleted` AND `tb_address`.`user_id` = 21)
ORDER BY `tb_address`.`update_time` DESC LIMIT 21


INSERT INTO `tb_address` (`create_time`, `update_time`, `user_id`, `title`, `receiver`, `province_id`, `city_id`, `district_id`, `place`, `mobile`, `tel`, `email`, `is_deleted`) VALUES ('2022-08-13 17:43:03.915329', '2022-08-13 17:43:03.915352', 21, 'abc', 'abc', 110000, 110100, 110101, 'dafs', '13816783387', '', '', 0)
