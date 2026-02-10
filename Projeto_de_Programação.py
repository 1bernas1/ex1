import os
import hashlib

utilizador_ficheiro = 'utilizador_ficheiror.txt'
consultas_ficheiro = 'consultas.txt'

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def users_exits(username):
    if not os.path.exists(utilizador_ficheiro):
        return False
    with open(utilizador_ficheiro,'r') as f:
        return any(line.startswith(f"{username}:") for line in f)
    
def register():
    username = input("Enter username: ")
    if users_exits(username):
        print("Utilizador já existe!")
        return
    password = input("Enter a new password") 
    with open(utilizador_ficheiro, 'a') as f:
        f.write(f"{username}:{hash_password(password)}\n")
    print("Registro realizado com sucesso!")

def login():
    if not os.path.exists(utilizador_ficheiro):
        print("No users registered")
        return False

    username = input("Utilizador: ")
    password = input("Palavra-passe: ")
    hashed = hash_password(password)

    with open(utilizador_ficheiro, 'r') as f:
        for line in f:
            if line.strip() == f"{username}:{hashed}":
                print("Login Successful\n")
                return True

    print("Login Failed")
    return False

def main():
    options = {'1':register, '2':login, '3':exit}
    while True:
        print ("\n1.Register \n2.Login\n3.exit ")
        choice = input("choose an option: ")
        action = options.get(choice)
        if action:
            action()

        else:
            print("invalid option")

def carregar_consultas():
    consultas_ficheiro = []
    if os.path.exists(consultas_ficheiro):
        with open(consultas_ficheiro, 'r') as f:
            for linha in f:
                paciente, medico, data, hora = linha.strip().split(";")
                consultas.append({
                    "Pacente": paciente,
                    "medico": medico,
                    "data": data,
                    "hora": hora
                })
    return consultas

def guardar_consultas(consultas):
    with open(consultas_ficheiro, 'w') as f:
        f.write(f"{c['paciente']};{c['medico']};{c['data']};{c['hora']}\n")

def marcar_consulta():
    consultas = carregar_consultas()

    paciente = input("Nome do paciente:")
    medico = input("Nome do médico: ")
    data = input("Data (DD/MM/AAAA): ")
    hora = input("Hora (HH:MM): ")

    consultas.append({
        "paciente": paciente,
        "medico": medico,
        "data": data,
        "hora": hora
    })

    guardar_consultas(consultas)
    print("Consultas marcada com sucesso!\n")

if __name__ == "__main__":
    main()

