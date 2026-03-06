import os
import hashlib
import smtplib
from email.message import EmailMessage
from datetime import datetime

user_file = "users.txt"
consultas_file = "consultas.txt"

# ========= EMAIL =========
def enviar_notificacao(destinatario, assunto, mensagem):
    email = EmailMessage()
    email['From'] = "alexandrebernardo.santos@gmail.com"
    email['To'] = destinatario
    email['Subject'] = assunto
    email.set_content(mensagem)

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login("alexandre.bernardo.santos@gmail.com", "bhlr zypu webr mxbk")
            smtp.send_message(email)
        print("📧 Notificação enviada!")
    except Exception as e:
        print("Erro ao enviar email:", e)

# ========= UTIL =========
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

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

# ========= UTILIZADORES =========
def user_exists(username):
    if not os.path.exists(user_file):
        return False
    with open(user_file, 'r') as f:
        return any(line.startswith(f"{username}:") for line in f)

def register():
    username = input("Username: ")
    if user_exists(username):
        print("User já existe!")
        return
    password = input("Password: ")
    with open(user_file, 'a') as f:
        f.write(f"{username}:{hash_password(password)}\n")
    print("Registo concluído!")

def login():
    if not os.path.exists(user_file):
        return None
    username = input("Username: ")
    password = input("Password: ")
    hashed = hash_password(password)

    with open(user_file, 'r') as f:
        for line in f:
            if line.strip() == f"{username}:{hashed}":
                print("Login efetuado!\n")
                return username
    print("Login falhou!")
    return None

# ========= CONSULTAS =========
def carregar_consultas():
    consultas = []
    if os.path.exists(consultas_file):
        with open(consultas_file, 'r') as f:
            for linha in f:
                partes = linha.strip().split(";")
                if len(partes) == 6:
                    user, paciente, email, medico, data, hora = partes
                    consultas.append({
                        "user": user,
                        "paciente": paciente,
                        "email": email,
                        "medico": medico,
                        "data": data,
                        "hora": hora
                    })
    return consultas

def guardar_consultas(consultas):
    with open(consultas_file, 'w') as f:
        for c in consultas:
            f.write(f"{c['user']};{c['paciente']};{c['email']};{c['medico']};{c['data']};{c['hora']}\n")

def medico_ocupado(consultas, medico, data, hora):
    return any(c["medico"] == medico and c["data"] == data and c["hora"] == hora for c in consultas)

# ========= FUNCIONALIDADES =========
def marcar_consulta(user):
    consultas = carregar_consultas()

    paciente = input("Nome do paciente: ")
    email = input("Email do paciente: ")
    medico = input("Nome do médico: ")
    data = input("Data (DD/MM/AAAA): ")
    hora = input("Hora (HH:MM): ")

    if not validar_data(data) or not validar_hora(hora):
        print("Data ou hora inválida!\n")
        return

    if medico_ocupado(consultas, medico, data, hora):
        print("Médico já tem consulta nesse horário!\n")
        return

    consulta = {"user": user, "paciente": paciente, "email": email, "medico": medico, "data": data, "hora": hora}
    consultas.append(consulta)
    guardar_consultas(consultas)

    enviar_notificacao(email, "Consulta Marcada", f"Consulta com Dr(a). {medico} em {data} às {hora}.")
    print("Consulta marcada com sucesso!\n")

def listar_minhas_consultas(user):
    consultas = [c for c in carregar_consultas() if c["user"] == user]
    if not consultas:
        print("Sem consultas.\n")
        return
    for i, c in enumerate(consultas):
        print(f"{i+1} - {c['medico']} | {c['data']} {c['hora']}")
    print()

def alterar_consulta(user):
    consultas = carregar_consultas()
    minhas = [c for c in consultas if c["user"] == user]

    if not minhas:
        print("Sem consultas para alterar.\n")
        return

    for i, c in enumerate(minhas):
        print(f"{i+1} - {c['medico']} {c['data']} {c['hora']}")

    try:
        idx = int(input("Número: ")) - 1
        nova_data = input("Nova data: ")
        nova_hora = input("Nova hora: ")

        if medico_ocupado(consultas, minhas[idx]["medico"], nova_data, nova_hora):
            print("Médico ocupado!\n")
            return

        minhas[idx]["data"] = nova_data
        minhas[idx]["hora"] = nova_hora
        guardar_consultas(consultas)

        enviar_notificacao(minhas[idx]["email"], "Consulta Alterada", f"Nova data: {nova_data} às {nova_hora}")
        print("Consulta alterada!\n")
    except:
        print("Erro.\n")

def cancelar_consulta(user):
    consultas = carregar_consultas()
    minhas = [c for c in consultas if c["user"] == user]

    if not minhas:
        print("Sem consultas.\n")
        return

    for i, c in enumerate(minhas):
        print(f"{i+1} - {c['medico']} {c['data']} {c['hora']}")

    try:
        idx = int(input("Número: ")) - 1
        consulta = minhas[idx]
        enviar_notificacao(consulta["email"], "Consulta Cancelada", f"Consulta em {consulta['data']} cancelada.")
        consultas.remove(consulta)
        guardar_consultas(consultas)
        print("Consulta cancelada!\n")
    except:
        print("Erro.\n")

def historico_paciente(user):
    listar_minhas_consultas(user)

def disponibilidade_medico():
    medico = input("Nome do médico: ")
    consultas = carregar_consultas()
    ocupadas = [f"{c['data']} {c['hora']}" for c in consultas if c["medico"] == medico]

    print(f"Horários ocupados do Dr(a). {medico}:")
    for h in ocupadas:
        print("-", h)
    print()

def relatorio_medico():
    medico = input("Nome do médico: ")
    consultas = carregar_consultas()
    lista = [c for c in consultas if c["medico"] == medico]
    print(f"Total consultas: {len(lista)}")
    for c in lista:
        print(f"{c['data']} {c['hora']} - {c['paciente']}")
    print()

# ========= MENU =========
def menu_consultas(user):
    while True:
        print("\n1-Marcar\n2-Listar\n3-Alterar\n4-Cancelar\n5-Histórico\n6-Disponibilidade Médico\n7-Relatório Médico\n0-Logout")
        op = input("Escolha: ")

        if op == "1": marcar_consulta(user)
        elif op == "2": listar_minhas_consultas(user)
        elif op == "3": alterar_consulta(user)
        elif op == "4": cancelar_consulta(user)
        elif op == "5": historico_paciente(user)
        elif op == "6": disponibilidade_medico()
        elif op == "7": relatorio_medico()
        elif op == "0": break

# ========= MAIN =========
def main():
    while True:
        print("\n1-Register\n2-Login\n3-Sair")
        op = input("Escolha: ")

        if op == "1":
            register()
        elif op == "2":
            user = login()
            if user:
                menu_consultas(user)
        elif op == "3":
            break

if __name__ == "__main__":
    main()


