-- Run sql with command: sqlite3 file.db < file.sql 

delete from domains where name='cdn.sstatic.net';
insert into domains(name, tags) values ('cdn.sstatic.net', 'Content Delivery Networks');
delete from domains where name='ssl.gstatic.com';
insert into domains(name, tags) values ('ssl.gstatic.com', 'Content Delivery Networks');
delete from domains where name='www.gstatic.com';
insert into domains(name, tags) values ('www.gstatic.com', 'Content Delivery Networks');
delete from domains where name='gstatic.com';
insert into domains(name, tags) values ('gstatic.com', 'Content Delivery Networks');
