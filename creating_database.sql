create schema programs_db;
create table programs (
     id int unsigned not null primary key auto_increment,
    `Инженер` varchar(100) not null,
    `Шифр детали` varchar(100) not null,
    `Номер операции` varchar(100) default null,
    `Номер программы` varchar(100) not null unique key,
    `Станок` varchar(100) not null,
    `Тип операции` varchar(100) not null,
    `Статус` varchar(100) not null default 'в работе',
    `Машинное время` varchar(100) default null,
    `Дата создания` datetime not null default now(),
    `Дата расчета` datetime default null,
    `Дата создания ОК` datetime default null,
    `Дата внедрения` datetime default null,
    `Примечание` text default null
);
CREATE USER 'engineer'@'%' IDENTIFIED BY 'password';
FLUSH PRIVILEGES;
GRANT SELECT, INSERT, UPDATE, DELETE ON `programs_db`.* TO 'engineer'@'%';
FLUSH PRIVILEGES;






