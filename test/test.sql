| app1_person |
CREATE TABLE `app1_person`
(
    `id`   bigint      NOT NULL AUTO_INCREMENT,
    `name` varchar(50) NOT NULL,
    PRIMARY KEY (`id`)
) ENGINE = InnoDB
  DEFAULT CHARSET = utf8mb3
| app1_group |
CREATE TABLE `app1_group`
(
    `id`   bigint       NOT NULL AUTO_INCREMENT,
    `name` varchar(128) NOT NULL,
    PRIMARY KEY (`id`)
) ENGINE = InnoDB
  DEFAULT CHARSET = utf8mb3
| app1_membership |
CREATE TABLE `app1_membership`
(
    `id`            bigint      NOT NULL AUTO_INCREMENT,
    `invite_reason` varchar(64) NOT NULL,
    `group_id`      bigint      NOT NULL,
    `inviter_id`    bigint      NOT NULL,
    `person_id`     bigint      NOT NULL,
    PRIMARY KEY (`id`),
    KEY `app1_membership_inviter_id_522204d8_fk_app1_person_id` (`inviter_id`),
    KEY `app1_membership_person_id_d270a4b1_fk_app1_person_id` (`person_id`),
    KEY `app1_membership_group_id_c995da4c_fk_app1_group_id` (`group_id`),
    CONSTRAINT `app1_membership_group_id_c995da4c_fk_app1_group_id` FOREIGN KEY (`group_id`) REFERENCES `app1_group` (`id`),
    CONSTRAINT `app1_membership_inviter_id_522204d8_fk_app1_person_id` FOREIGN KEY (`inviter_id`) REFERENCES `app1_person` (`id`),
    CONSTRAINT `app1_membership_person_id_d270a4b1_fk_app1_person_id` FOREIGN KEY (`person_id`) REFERENCES `app1_person` (`id`)
) ENGINE = InnoDB
  DEFAULT CHARSET = utf8mb3 |
