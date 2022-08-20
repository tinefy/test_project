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