import mysql.connector

db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="root",
    database="base_de_dados_medica"
)

mycursor = db.cursor()

# mycursor.execute("CREATE DATABASE base_de_dados_medica")

# mycursor.execute("CREATE TABLE utilizadores (id_utilizador INT AUTO_INCREMENT PRIMARY KEY, nome VARCHAR(255), idade SMALLINT, email VARCHAR(255), password VARCHAR(255))")
# mycursor.execute("CREATE TABLE medicos (id_medico INT AUTO_INCREMENT PRIMARY KEY, nome VARCHAR(255), idade SMALLINT, email VARCHAR(255), password VARCHAR(255), especialidade VARCHAR(50))")
# mycursor.execute("CREATE TABLE consultas (id_consulta INT AUTO_INCREMENT PRIMARY KEY, id_utilizador INT, id_medico INT, data_consulta DATE, hora_consulta TIME, motivo_consulta VARCHAR(255), FOREIGN KEY (id_utilizador) REFERENCES utilizadores(id_utilizador), FOREIGN KEY (id_medico) REFERENCES medicos(id_medico))")
# mycursor.execute("CREATE TABLE notificacoes (id_notificacao INT AUTO_INCREMENT PRIMARY KEY, id_utilizador INT, conteudo VARCHAR(255), data_notificacao DATETIME, FOREIGN KEY (id_utilizador) REFERENCES utilizadores(id_utilizador))")
# mycursor.execute("CREATE TABLE relatorios (id_relatorio INT AUTO_INCREMENT PRIMARY KEY, id_consulta INT, descricao VARCHAR(255), data_relatorio DATE, FOREIGN KEY (id_consulta) REFERENCES consultas(id_consulta))")


#mycursor.execute("insert into utilizadores (nome, idade, email, password) values (%s,%s,%s,%s)", ('Bernardo Santos', 30, 'bernardo.santos@email.com', 'bernardo123'))
#mycursor.execute("insert into medicos (nome, idade, email, password, especialidade) values (%s,%s,%s,%s,%s)", ('Dra. Ana Silva', 45, 'ana.silva@email.com', 'ana123', 'Cardiologia'))
#mycursor.execute("insert into medicos (nome, idade, email, password, especialidade) values (%s,%s,%s,%s,%s)", ('Dr. Carlos Pereira', 50, 'carlos.pereira@email.com', 'carlos123', 'Ortopedia'))
#mycursor.execute("insert into medicos (nome, idade, email, password, especialidade) values (%s,%s,%s,%s,%s)", ('Dra. Sofia Costa', 38, 'sofia.costa@email.com', 'sofia123', 'Pediatria'))


db.commit()
# mycursor.execute("describe utilizadores")

mycursor.execute("select * from medicos")

for x in mycursor:
    print(x)

# rows = cursor.fetchall()



# for row in rows:
#     print(row)

# cursor.close()
# conn.close()
