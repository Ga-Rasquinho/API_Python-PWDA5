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

create table livros(
	id_livro int auto_increment primary key,
    nome_livro varchar(254) not null,
    autor_livro varchar(254) not null,
    categoria_livro varchar(254) not null,
    preco_livro double not null,
    status_livro varchar(10) not null default "ATIVO",
    usuario_id int,
    foreign key (usuario_id) references usuario(id)
);

insert into usuario (id, nome_usuario, email, senha, tipo_usu) 
values (5, 'admin', 'admin@admin', '1234', '1');

"""
