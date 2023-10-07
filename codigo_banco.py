"""
create database usuarios_pwa5;

create table usuario(
	id int auto_increment primary key,
    nome_usuario varchar(254) not null,
    email varchar(254) not null,
    senha varchar(254) not null,
    tipo_usu int not null default 0,
    usuario_ativo int not null default 1
);

insert into usuario (id, nome_usuario, email, senha, tipo_usu) 
values (5, 'admin', 'admin@admin', '1234', '1');

"""
