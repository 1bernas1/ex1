#__________Sistema de Agendamento Médico___________

import mysql.connector
import hashlib
import smtplib
from email.message import EmailMessage
from datetime import datetime

#__________Conexão com MySQL___________

db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="root",
    database="base_de_dados_médica"
)
cursor = db.cursor(dictionary=True)

#__________Configurações de Email___________

EMAIL_REMETENTE = "alexandre.bernardo.santos@gmail.com"
SENHA_APP = "kvvz alvc hhyq pgkl"  # Use senha de app do Gmail

#__________Funções Auxiliares___________

def encriptar(palavra):
    return hashlib.sha256(palavra.encode()).hexdigest()

def validar_data(data):
    try:
        datetime.strptime(data, "%d/%m/%Y")
        return True
    except:
        return False

def validar_hora(hora):
    try:
        datetime.strptime(hora, "%H:%M")
        return True
    except:
        return False

def input_ou_voltar(msg):
    valor = input(msg)
    if valor == "0":
        return None
    return valor

def enviar_notificacao(destinatario, assunto, mensagem):
    if not EMAIL_REMETENTE or not SENHA_APP:
        print("Credenciais do email não configuradas.")
        return
    email = EmailMessage()
    email['From'] = EMAIL_REMETENTE
    email['To'] = destinatario
    email['Subject'] = assunto
    email.set_content(mensagem)
    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(EMAIL_REMETENTE, SENHA_APP)
            smtp.send_message(email)
        print("Email enviado!")
    except Exception as e:
        print("Erro ao enviar email:", e)

#__________Autenticação do Utilizador__________

def registar():
    nome = input("Nome do utilizador: ")
    email = input("Email: ")
    idade = input("Idade: ")
    password = input("Senha: ")
    password_hash = encriptar(password)
    cursor.execute("INSERT INTO utilizadores (nome, idade, email, password) VALUES (%s,%s,%s,%s)",
                   (nome, idade, email, password_hash))
    db.commit()
    print("Registo concluído!")

def login():
    nome = input("Nome: ")
    password = input("Senha: ")
    password_hash = encriptar(password)

    # Verificar utilizador
    cursor.execute("SELECT * FROM utilizadores WHERE nome=%s AND password=%s", (nome, password_hash))
    usuario = cursor.fetchone()

    if usuario:
        usuario["tipo"] = "utilizador"
        print("Login efetuado como utilizador!\n")
        return usuario

    # Verificar médico
    cursor.execute("SELECT * FROM medicos WHERE nome=%s AND password=%s", (nome, password_hash))
    medico = cursor.fetchone()

    if medico:
        medico["tipo"] = "medico"
        print("Login efetuado como médico!\n")
        return medico

    print("Login falhou!")
    return None

#__________Funções de Médicos__________

def listar_medicos():
    
    cursor.execute("SELECT * FROM medicos")
    medicos = cursor.fetchall()
    for m in medicos:
        print(f"{m['id_medico']} - {m['nome']} ({m['especialidade']})")
    return medicos

def disponibilidade_medico():
    listar_medicos()
    id_medico = input_ou_voltar("Insira o ID do médico para ver a sua disponibilidade: ")
    if id_medico is None: return
    id_medico = int(id_medico)
    cursor.execute("SELECT data_consulta, hora_consulta FROM consultas WHERE id_medico=%s", (id_medico,))
    consultas = cursor.fetchall()
    if not consultas:
        print("Nenhuma consulta marcada para este médico.")
        return
    print(f"Horários ocupados do médico {id_medico}:")
    for c in consultas:
        data_formatada = datetime.strptime(str(c['data_consulta']), "%Y-%m-%d").strftime("%d/%m/%Y")
        print(f"- {data_formatada} {c['hora_consulta']}")

#__________Funções de Consultas__________

def marcar_consulta(usuario):
    paciente = input_ou_voltar("Nome do paciente: ")
    if paciente is None: return
    email = input_ou_voltar("Email do paciente: ")
    if email is None: return
    medicos = listar_medicos()
    id_medico = input_ou_voltar("ID do médico: ")
    if id_medico is None: return
    id_medico = int(id_medico)

    # Buscar nome do médico
    cursor.execute("SELECT nome FROM medicos WHERE id_medico=%s", (id_medico,))
    medico = cursor.fetchone()
    nome_medico = medico['nome'] if medico else f"ID {id_medico}"

    while True:
        data = input_ou_voltar("Data (DD/MM/AAAA): ")
        if data is None: return
        if validar_data(data): break
        print("Data inválida!")
    while True:
        hora = input_ou_voltar("Hora (HH:MM): ")
        if hora is None: return
        if validar_hora(hora): break
        print("Hora inválida!")
    motivo = input_ou_voltar("Motivo da consulta: ")
    if motivo is None: return

    data_mysql = datetime.strptime(data, "%d/%m/%Y").strftime("%Y-%m-%d")

    cursor.execute("SELECT * FROM consultas WHERE id_medico=%s AND data_consulta=%s AND hora_consulta=%s",
                   (id_medico, data_mysql, hora))
    if cursor.fetchone():
        print("Médico já ocupado nesse horário!")
        return

    cursor.execute("INSERT INTO consultas (id_utilizador, id_medico, data_consulta, hora_consulta, motivo_consulta) VALUES (%s,%s,%s,%s,%s)",
                   (usuario['id_utilizador'], id_medico, data_mysql, hora, motivo))
    db.commit()

    enviar_notificacao(email, "Consulta Marcada", f"Consulta marcada com {nome_medico} a {data} às {hora}.")
    print("Consulta marcada com sucesso!\n")

def listar_consultas(usuario):
    cursor.execute(
        "SELECT c.*, m.nome AS nome_medico FROM consultas c JOIN medicos m ON c.id_medico = m.id_medico WHERE c.id_utilizador=%s",
        (usuario['id_utilizador'],))
    consultas = cursor.fetchall()
    if not consultas:
        print("Sem consultas.")
        return
    for c in consultas:
        data_formatada = datetime.strptime(str(c['data_consulta']), "%Y-%m-%d").strftime("%d/%m/%Y")
        print(f"{c['id_consulta']} - Dr(a). {c['nome_medico']} | {data_formatada} {c['hora_consulta']} - {c['motivo_consulta']}")

def cancelar_consulta(usuario):
    listar_consultas(usuario)
    id_consulta = input_ou_voltar("Insira o ID da consulta para a cancelar: ")
    if id_consulta is None: return
    id_consulta = int(id_consulta)
    cursor.execute("SELECT * FROM consultas WHERE id_consulta=%s AND id_utilizador=%s", (id_consulta, usuario['id_utilizador']))
    consulta = cursor.fetchone()
    if not consulta:
        print("Consulta inválida!")
        return
    cursor.execute("DELETE FROM consultas WHERE id_consulta=%s", (id_consulta,))
    db.commit()
    print("Consulta cancelada!")
    enviar_notificacao(usuario['email'], "Consulta Cancelada", f"Consulta em {datetime.strptime(str(consulta['data_consulta']), '%Y-%m-%d').strftime('%d/%m/%Y')} cancelada.")

def alterar_consulta(usuario):
    listar_consultas(usuario)
    id_consulta = input_ou_voltar("Insira o ID da consulta para a alterar: ")
    if id_consulta is None: return
    id_consulta = int(id_consulta)
    cursor.execute("SELECT * FROM consultas WHERE id_consulta=%s AND id_utilizador=%s", (id_consulta, usuario['id_utilizador']))
    consulta = cursor.fetchone()
    if not consulta:
        print("Consulta inválida!")
        return

    # Nome do médico
    cursor.execute("SELECT nome FROM medicos WHERE id_medico=%s", (consulta['id_medico'],))
    medico = cursor.fetchone()
    nome_medico = medico['nome'] if medico else f"ID {consulta['id_medico']}"

    while True:
        nova_data = input_ou_voltar("Nova data (DD/MM/AAAA): ")
        if nova_data is None: return
        if validar_data(nova_data): break
    while True:
        nova_hora = input_ou_voltar("Nova hora (HH:MM): ")
        if nova_hora is None: return
        if validar_hora(nova_hora): break

    nova_data_mysql = datetime.strptime(nova_data, "%d/%m/%Y").strftime("%Y-%m-%d")

    cursor.execute("SELECT * FROM consultas WHERE id_medico=%s AND data_consulta=%s AND hora_consulta=%s AND id_consulta!=%s",
                   (consulta['id_medico'], nova_data_mysql, nova_hora, id_consulta))
    if cursor.fetchone():
        print("Médico ocupado nesse horário!")
        return

    cursor.execute("UPDATE consultas SET data_consulta=%s, hora_consulta=%s WHERE id_consulta=%s",
                   (nova_data_mysql, nova_hora, id_consulta))
    db.commit()
    print("Consulta alterada!")
    enviar_notificacao(usuario['email'], "Consulta Alterada", f"Consulta alterada com {nome_medico} a {nova_data} às {nova_hora}.")

#__________Menu do Utilizador__________

def menu(usuario):
    while True:
        print(f"\nBem-vindo, {usuario['nome']}!\n(Prima 0 para sair ou para voltar para o menu principal)")
        print("\n1 - Marcar Consulta ")
        print("2 - Listar Consultas ")
        print("3 - Alterar Consulta ")
        print("4 - Cancelar Consulta ")
        print("5 - Disponibilidade Médico ")
        print("0 - Sair")
        op = input("Escolha: ")
        if op == "1":
            marcar_consulta(usuario)
        elif op == "2":
            listar_consultas(usuario)
        elif op == "3":
            alterar_consulta(usuario)
        elif op == "4":
            cancelar_consulta(usuario)
        elif op == "5":
            disponibilidade_medico()
        elif op == "0":
            break
        else:
            print("Opção inválida!")

#__________Menu do Médico__________

def menu_medico(medico):

    while True:

        print(f"\nBem-vindo Dr(a). {medico['nome']}!")
        print("\n1 - Ver consultas do médico")
        print("2 - Consultas de hoje")
        print("0 - Sair")

        op = input("Escolha: ")

        if op == "1":

            cursor.execute("""
                SELECT c.*, u.nome AS paciente
                FROM consultas c
                JOIN utilizadores u ON c.id_utilizador = u.id_utilizador
                WHERE c.id_medico=%s
            """, (medico['id_medico'],))

            consultas = cursor.fetchall()

            if not consultas:
                print("Não existem consultas.")
            else:
                for c in consultas:
                    data_formatada = datetime.strptime(str(c['data_consulta']), "%Y-%m-%d").strftime("%d/%m/%Y")
                    print(f"{c['paciente']} | {data_formatada} {c['hora_consulta']} | {c['motivo_consulta']}")

        elif op == "2":

            hoje = datetime.now().strftime("%Y-%m-%d")

            cursor.execute("""
                SELECT c.*, u.nome AS paciente
                FROM consultas c
                JOIN utilizadores u ON c.id_utilizador = u.id_utilizador
                WHERE c.id_medico=%s AND data_consulta=%s
            """, (medico['id_medico'], hoje))

            consultas = cursor.fetchall()

            if not consultas:
                print("Não existem consultas hoje.")
            else:
                for c in consultas:
                    print(f"{c['hora_consulta']} - {c['paciente']}")

        elif op == "0":
            break

        else:
            print("Opção inválida!")

#__________Menu de Login/Registro__________

def principal():
    while True:
        print("\n1 - Registrar")
        print("2 - Login")
        print("3 - Sair")
        op = input("Escolha: ")
        if op == "1":
            registar()
        elif op == "2":
            usuario = login()
            if usuario:
                menu(usuario)
        elif op == "3":
            break
        else:
            print("Opção inválida!")

if __name__ == "__main__":
    principal()
