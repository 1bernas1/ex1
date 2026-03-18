#__________Sistema de Agendamento Médico___________

# ALTERAÇÕES REALIZADAS:
# 1. Adicionada coluna 'estado' na tabela consultas (agendada, realizada, cancelada)
# 2. Cancelar consulta agora muda estado para 'cancelada' (não apaga o registo)
# 3. Médico pode marcar consulta como 'realizada'
# 4. Utilizador pode listar consultas por estado (agendada / realizada / cancelada / todas)
#
# SQL necessário para adicionar a coluna estado (executar uma vez na base de dados):
#   ALTER TABLE consultas
#   ADD COLUMN estado ENUM('agendada','realizada','cancelada') NOT NULL DEFAULT 'agendada';

import mysql.connector
import hashlib
from datetime import datetime
import smtplib


#__________Conexão MySQL___________

db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="root",
    database="base_de_dados_médica"
)

cursor = db.cursor(dictionary=True)

#__________Funções Auxiliares___________

def encriptar(palavra):
    return hashlib.sha256(palavra.encode()).hexdigest()

def input_ou_voltar(msg):
    valor = input(msg).strip()
    if valor == "0" or valor == "":
        return None
    return valor

def validar_data(data):
    try:
        datetime.strptime(data, "%d/%m/%Y")
        return True
    except ValueError:
        return False

def validar_hora(hora):
    try:
        datetime.strptime(hora, "%H:%M")
        return True
    except ValueError:
        return False


#__________Registo Utilizador__________

def registar():
    print("\nRegisto (0 para voltar)")
    nome = input_ou_voltar("Nome: ")
    if nome is None: return
    idade = input_ou_voltar("Idade: ")
    if idade is None or not idade.isdigit():
        print("Idade inválida!")
        return
    email = input_ou_voltar("Email: ")
    if email is None: return
    senha = input_ou_voltar("Senha: ")
    if senha is None: return
    password_hash = encriptar(senha)
    try:
        cursor.execute(
            "INSERT INTO utilizadores (nome, idade, email, password) VALUES (%s, %s, %s, %s)",
            (nome, int(idade), email, password_hash)
        )
        db.commit()
        print("Utilizador registado!")
    except Exception as e:
        print("Erro ao registar:", e)


#__________Login__________

def login():
    print("\nLogin (0 para voltar)")
    nome = input_ou_voltar("Nome: ")
    if nome is None: return None
    senha = input_ou_voltar("Senha: ")
    if senha is None: return None
    password_hash = encriptar(senha)

    # Verifica admin/utilizador
    cursor.execute("SELECT * FROM utilizadores WHERE nome=%s AND password=%s", (nome, password_hash))
    usuario = cursor.fetchone()
    if usuario:
        if usuario["nome"].lower() == "admin":
            usuario["tipo"] = "admin"
        else:
            usuario["tipo"] = "utilizador"
        print("Login efetuado!")
        return usuario

    # Verifica médico
    cursor.execute("SELECT * FROM medicos WHERE nome=%s AND password=%s", (nome, password_hash))
    medico = cursor.fetchone()
    if medico:
        medico["tipo"] = "medico"
        print("Login médico!")
        return medico

    print("Login falhou! Verifique nome ou senha")
    return None


#__________Admin funções sobre médicos__________

def criar_medico():
    print("\nCriar Médico (0 para voltar)")
    nome = input_ou_voltar("Nome: ")
    if nome is None: return
    email = input_ou_voltar("Email: ")
    if email is None: return
    senha = input_ou_voltar("Senha: ")
    if senha is None: return
    especialidade = input_ou_voltar("Especialidade: ")
    if especialidade is None: return
    senha_hash = encriptar(senha)
    try:
        cursor.execute(
            "INSERT INTO medicos (nome,email,password,especialidade) VALUES (%s,%s,%s,%s)",
            (nome, email, senha_hash, especialidade)
        )
        db.commit()
        print("Médico criado!")
    except Exception as e:
        print("Erro ao criar médico:", e)

def listar_medicos():
    cursor.execute("SELECT * FROM medicos")
    medicos = cursor.fetchall()
    if not medicos:
        print("Nenhum médico cadastrado!")
        return []
    for m in medicos:
        print(f"{m['id_medico']} - {m['nome']} ({m['especialidade']})")
    return medicos

def alterar_medico():
    medicos = listar_medicos()
    if not medicos:
        print("Nenhum médico cadastrado para alterar.")
        return

    while True:
        id_medico = input_ou_voltar("ID do médico para alterar: ")
        if id_medico is None: return
        if not id_medico.isdigit():
            print("ID inválido! Digite novamente.")
            continue
        cursor.execute("SELECT * FROM medicos WHERE id_medico=%s", (id_medico,))
        medico = cursor.fetchone()
        if not medico:
            print("Médico não encontrado! Digite novamente.")
            continue
        break

    novo_nome = input("Novo nome: ").strip()
    if novo_nome == "0": return
    novo_email = input("Novo email: ").strip()
    if novo_email == "0": return
    nova_senha = input("Nova senha: ").strip()
    if nova_senha == "0": return
    nova_especialidade = input("Nova especialidade: ").strip()
    if nova_especialidade == "0": return

    if novo_nome:          medico["nome"] = novo_nome
    if novo_email:         medico["email"] = novo_email
    if nova_senha:         medico["password"] = encriptar(nova_senha)
    if nova_especialidade: medico["especialidade"] = nova_especialidade

    try:
        cursor.execute("""
            UPDATE medicos
            SET nome=%s, email=%s, password=%s, especialidade=%s
            WHERE id_medico=%s
        """, (medico["nome"], medico["email"], medico["password"], medico["especialidade"], id_medico))
        db.commit()
        print("Médico alterado com sucesso!")
    except Exception as e:
        print("Erro ao alterar médico:", e)

def apagar_medico():
    medicos = listar_medicos()
    if not medicos:
        print("Nenhum médico cadastrado para apagar.")
        return

    while True:
        id_medico = input_ou_voltar("ID do médico para apagar: ")
        if id_medico is None: return
        if not id_medico.isdigit():
            print("ID inválido! Digite novamente.")
            continue
        cursor.execute("SELECT * FROM medicos WHERE id_medico=%s", (id_medico,))
        medico = cursor.fetchone()
        if not medico:
            print("Médico não encontrado! Digite novamente.")
            continue
        break

    confirmar = input(f"Tem certeza que deseja apagar o médico {medico['nome']}? (s/n): ").strip().lower()
    if confirmar != "s":
        print("Operação cancelada.")
        return

    try:
        cursor.execute("DELETE FROM medicos WHERE id_medico=%s", (id_medico,))
        db.commit()
        print("Médico apagado com sucesso!")
    except Exception as e:
        print("Erro ao apagar médico:", e)


#__________Funções Consultas__________

# ──────────────────────────────────────────────────────────────────────────────
# ALTERADO: listar_consultas aceita filtro de estado opcional.
#   estado=None        → mostra todas
#   estado='agendada'  → apenas agendadas
#   estado='realizada' → apenas realizadas
#   estado='cancelada' → apenas canceladas
# ──────────────────────────────────────────────────────────────────────────────
def listar_consultas(usuario, estado=None):
    if estado:
        cursor.execute("""
            SELECT c.*, m.nome AS medico
            FROM consultas c
            JOIN medicos m ON c.id_medico = m.id_medico
            WHERE c.id_utilizador=%s AND c.estado_consulta=%s
        """, (usuario["id_utilizador"], estado))
    else:
        cursor.execute("""
            SELECT c.*, m.nome AS medico
            FROM consultas c
            JOIN medicos m ON c.id_medico = m.id_medico
            WHERE c.id_utilizador=%s
        """, (usuario["id_utilizador"],))

    consultas = cursor.fetchall()
    if not consultas:
        print("Nenhuma consulta encontrada!")
        return []
    for c in consultas:
        data = datetime.strptime(str(c["data_consulta"]), "%Y-%m-%d").strftime("%d/%m/%Y")
        print(f"{c['id_consulta']} | {c['medico']} | {data} {c['hora_consulta']} "
              f"| {c['motivo_consulta']} | [{c['estado_consulta'].upper()}]")
    return consultas


# ──────────────────────────────────────────────────────────────────────────────
# NOVO: submenu para o utilizador filtrar consultas por estado
# ──────────────────────────────────────────────────────────────────────────────
def menu_listar_consultas(usuario):
    while True:
        print("\nListar consultas por estado:")
        print("1 Agendadas")
        print("2 Realizadas")
        print("3 Canceladas")
        print("4 Todas")
        print("0 Voltar")
        op = input("Escolha: ").strip()
        if   op == "1": listar_consultas(usuario, estado="agendada")
        elif op == "2": listar_consultas(usuario, estado="realizada")
        elif op == "3": listar_consultas(usuario, estado="cancelada")
        elif op == "4": listar_consultas(usuario)
        elif op == "0": break
        else: print("Opção inválida!")


def marcar_consulta(usuario):
    medicos = listar_medicos()
    if not medicos:
        print("Não há médicos disponíveis para agendamento.")
        return

    while True:
        id_medico = input_ou_voltar("ID do médico: ")
        if id_medico is None: return
        if not id_medico.isdigit():
            print("ID inválido! Digite novamente.")
            continue
        cursor.execute("SELECT * FROM medicos WHERE id_medico=%s", (id_medico,))
        medico = cursor.fetchone()
        if not medico:
            print("Médico não encontrado! Digite novamente.")
            continue
        break

    while True:
        data = input_ou_voltar("Data DD/MM/AAAA: ")
        if data is None: return
        if validar_data(data): break
        print("Data inválida! Use o formato DD/MM/AAAA.")

    while True:
        hora = input_ou_voltar("Hora HH:MM: ")
        if hora is None: return
        if validar_hora(hora): break
        print("Hora inválida! Use o formato HH:MM (00:00 a 23:59).")

    motivo = input_ou_voltar("Motivo: ")
    if motivo is None: motivo = ""

    data_mysql = datetime.strptime(data, "%d/%m/%Y").strftime("%Y-%m-%d")

    # Verifica se médico está livre (apenas consultas agendadas ocupam o horário)
    cursor.execute("""
        SELECT * FROM consultas
        WHERE id_medico=%s AND data_consulta=%s AND hora_consulta=%s AND estado_consulta='agendada'
    """, (id_medico, data_mysql, hora))
    if cursor.fetchone():
        print("Médico ocupado neste horário! Escolha outro horário ou médico.")
        return

    try:
        cursor.execute("""
            INSERT INTO consultas (id_utilizador, id_medico, data_consulta, hora_consulta, motivo_consulta, estado_consulta)
            VALUES (%s, %s, %s, %s, %s, 'agendada')
        """, (usuario["id_utilizador"], id_medico, data_mysql, hora, motivo))
        db.commit()
        print("Consulta marcada com sucesso!")
    except Exception as e:
        print("Erro ao marcar consulta:", e)
        return

    cursor.execute("SELECT LAST_INSERT_ID() AS id_consulta")
    consulta_id = cursor.fetchone()["id_consulta"]

    mensagem = f"Consulta marcada com Dr(a) {medico['nome']} em {data} às {hora}. Motivo: {motivo}"
    try:
        cursor.execute("""
            INSERT INTO notificacoes (id_utilizador, id_notificacao, mensagem, data_notificacao)
            VALUES (%s, %s, %s, %s)
        """, (usuario["id_utilizador"], consulta_id, mensagem, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        db.commit()
        print("Notificação registrada com sucesso!")
    except Exception as e:
        print("Erro ao registrar notificação:", e)


# ──────────────────────────────────────────────────────────────────────────────
# ALTERADO: cancelar_consulta muda estado para 'cancelada' (não apaga).
#   Só é possível cancelar consultas com estado 'agendada'.
# ──────────────────────────────────────────────────────────────────────────────
def cancelar_consulta(usuario):
    # Mostra apenas consultas agendadas (as únicas que podem ser canceladas)
    consultas = listar_consultas(usuario, estado="agendada")
    if not consultas:
        return

    while True:
        id_consulta = input_ou_voltar("ID da consulta para cancelar: ")
        if id_consulta is None: return
        if not id_consulta.isdigit():
            print("ID inválido! Digite novamente.")
            continue
        cursor.execute(
            "SELECT * FROM consultas WHERE id_consulta=%s AND id_utilizador=%s AND estado_consulta='agendada'",
            (id_consulta, usuario["id_utilizador"])
        )
        consulta = cursor.fetchone()
        if not consulta:
            print("Consulta não encontrada ou já não está agendada! Digite novamente.")
            continue
        break

    try:
        cursor.execute(
            "UPDATE consultas SET estado_consulta='cancelada' WHERE id_consulta=%s AND id_utilizador=%s",
            (id_consulta, usuario["id_utilizador"])
        )
        db.commit()
        print("Consulta cancelada com sucesso!")
    except Exception as e:
        print("Erro ao cancelar consulta:", e)


def alterar_consulta(usuario):
    # Só faz sentido alterar consultas agendadas
    consultas = listar_consultas(usuario, estado="agendada")
    if not consultas:
        return

    while True:
        id_consulta = input_ou_voltar("ID da consulta para alterar: ")
        if id_consulta is None: return
        if not id_consulta.isdigit():
            print("ID inválido! Digite novamente.")
            continue
        cursor.execute(
            "SELECT * FROM consultas WHERE id_consulta=%s AND id_utilizador=%s AND estado_consulta='agendada'",
            (id_consulta, usuario["id_utilizador"])
        )
        consulta = cursor.fetchone()
        if not consulta:
            print("Consulta não encontrada ou já não está agendada! Digite novamente.")
            continue
        break

    while True:
        nova_data = input_ou_voltar("Nova data DD/MM/AAAA: ")
        if nova_data is None: return
        try:
            data_obj = datetime.strptime(nova_data, "%d/%m/%Y")
            break
        except ValueError:
            print("Data inválida! Use o formato DD/MM/AAAA.")

    while True:
        nova_hora = input_ou_voltar("Nova hora HH:MM: ")
        if nova_hora is None: return
        try:
            datetime.strptime(nova_hora, "%H:%M")
            break
        except ValueError:
            print("Hora inválida! Use o formato HH:MM (00:00 a 23:59).")

    data_mysql = data_obj.strftime("%Y-%m-%d")

    # Verifica disponibilidade do médico no novo horário (ignora a própria consulta)
    cursor.execute("""
        SELECT * FROM consultas
        WHERE id_medico=%s AND data_consulta=%s AND hora_consulta=%s
          AND estado_consulta='agendada' AND id_consulta!=%s
    """, (consulta["id_medico"], data_mysql, nova_hora, id_consulta))
    if cursor.fetchone():
        print("Médico ocupado neste horário! Escolha outro horário.")
        return

    try:
        cursor.execute("""
            UPDATE consultas
            SET data_consulta=%s, hora_consulta=%s
            WHERE id_consulta=%s AND id_utilizador=%s
        """, (data_mysql, nova_hora, id_consulta, usuario["id_utilizador"]))
        db.commit()
        print("Consulta alterada com sucesso!")
    except Exception as e:
        print("Erro ao alterar consulta:", e)


def disponibilidade_medico():
    medicos = listar_medicos()
    if not medicos:
        print("Não há médicos cadastrados.")
        return

    while True:
        id_medico = input_ou_voltar("ID do médico para verificar disponibilidade: ")
        if id_medico is None: return
        if not id_medico.isdigit():
            print("ID inválido! Digite novamente.")
            continue
        cursor.execute("SELECT * FROM medicos WHERE id_medico=%s", (id_medico,))
        medico = cursor.fetchone()
        if not medico:
            print("Médico não encontrado! Digite novamente.")
            continue
        break

    # Apenas consultas agendadas representam horários ocupados
    cursor.execute(
        "SELECT data_consulta, hora_consulta FROM consultas WHERE id_medico=%s AND estado_consulta='agendada'",
        (id_medico,)
    )
    consultas = cursor.fetchall()
    if not consultas:
        print(f"O médico {medico['nome']} não tem consultas agendadas.")
        return

    print(f"Consultas agendadas de Dr(a) {medico['nome']}:")
    for c in consultas:
        data = datetime.strptime(str(c["data_consulta"]), "%Y-%m-%d").strftime("%d/%m/%Y")
        print(f"  - {data} às {c['hora_consulta']}")


#__________Funções Relatórios__________

def ver_relatorios(medico):
    cursor.execute("""
        SELECT r.*, u.nome AS paciente
        FROM relatorios r
        JOIN consultas c ON r.id_consulta = c.id_consulta
        JOIN utilizadores u ON c.id_utilizador = u.id_utilizador
        WHERE c.id_medico=%s
    """, (medico["id_medico"],))
    relatorios = cursor.fetchall()
    if not relatorios:
        print("Nenhum relatório encontrado!")
        return
    for r in relatorios:
        data = datetime.strptime(str(r["data_relatorio"]), "%Y-%m-%d").strftime("%d/%m/%Y")
        print(r["id_relatorio"], r["paciente"], data, r["descricao"])

def adicionar_relatorio(medico):
    cursor.execute("""
        SELECT c.*, u.nome AS paciente
        FROM consultas c
        JOIN utilizadores u ON c.id_utilizador = u.id_utilizador
        WHERE c.id_medico=%s
    """, (medico["id_medico"],))
    consultas = cursor.fetchall()
    if not consultas:
        print("Você não tem consultas para adicionar relatório.")
        return

    for c in consultas:
        data = datetime.strptime(str(c["data_consulta"]), "%Y-%m-%d").strftime("%d/%m/%Y")
        print(f"{c['id_consulta']} - {c['paciente']} - {data} às {c['hora_consulta']} [{c['estado_consulta'].upper()}]")

    while True:
        id_consulta = input_ou_voltar("ID da consulta para adicionar relatório: ")
        if id_consulta is None: return
        if not id_consulta.isdigit():
            print("ID inválido! Digite novamente.")
            continue
        cursor.execute(
            "SELECT * FROM consultas WHERE id_consulta=%s AND id_medico=%s",
            (id_consulta, medico["id_medico"])
        )
        consulta = cursor.fetchone()
        if not consulta:
            print("Consulta não encontrada! Digite novamente.")
            continue
        break

    descricao = input_ou_voltar("Descrição do relatório: ")
    if descricao is None: descricao = ""

    data_relatorio = datetime.now().strftime("%Y-%m-%d")
    try:
        cursor.execute("""
            INSERT INTO relatorios (id_consulta, descricao, data_relatorio)
            VALUES (%s, %s, %s)
        """, (id_consulta, descricao, data_relatorio))
        db.commit()
        print("Relatório adicionado com sucesso!")
    except Exception as e:
        print("Erro ao adicionar relatório:", e)

def alterar_relatorio(medico):
    cursor.execute("""
        SELECT r.*, u.nome AS paciente
        FROM relatorios r
        JOIN consultas c ON r.id_consulta = c.id_consulta
        JOIN utilizadores u ON c.id_utilizador = u.id_utilizador
        WHERE c.id_medico=%s
    """, (medico["id_medico"],))
    relatorios = cursor.fetchall()
    if not relatorios:
        print("Nenhum relatório encontrado.")
        return

    for r in relatorios:
        data = datetime.strptime(str(r["data_relatorio"]), "%Y-%m-%d").strftime("%d/%m/%Y")
        print(f"{r['id_relatorio']} - {r['paciente']} - {data} - {r['descricao']}")

    while True:
        id_relatorio = input_ou_voltar("ID do relatório para alterar: ")
        if id_relatorio is None: return
        if not id_relatorio.isdigit():
            print("ID inválido! Digite novamente.")
            continue
        cursor.execute(
            "SELECT r.* FROM relatorios r JOIN consultas c ON r.id_consulta=c.id_consulta "
            "WHERE r.id_relatorio=%s AND c.id_medico=%s",
            (id_relatorio, medico["id_medico"])
        )
        relatorio = cursor.fetchone()
        if not relatorio:
            print("Relatório não encontrado! Digite novamente.")
            continue
        break

    descricao = input_ou_voltar("Nova descrição do relatório: ")
    if descricao is None: descricao = ""

    try:
        cursor.execute(
            "UPDATE relatorios SET descricao=%s WHERE id_relatorio=%s",
            (descricao, id_relatorio)
        )
        db.commit()
        print("Relatório alterado com sucesso!")
    except Exception as e:
        print("Erro ao alterar relatório:", e)


# ──────────────────────────────────────────────────────────────────────────────
# NOVO (médico): marcar uma consulta agendada como 'realizada'
# ──────────────────────────────────────────────────────────────────────────────
def marcar_consulta_realizada(medico):
    cursor.execute("""
        SELECT c.*, u.nome AS paciente
        FROM consultas c
        JOIN utilizadores u ON c.id_utilizador = u.id_utilizador
        WHERE c.id_medico=%s AND c.estado_consulta='agendada'
    """, (medico["id_medico"],))
    consultas = cursor.fetchall()
    if not consultas:
        print("Não há consultas agendadas para marcar como realizadas.")
        return

    print("\nConsultas agendadas:")
    for c in consultas:
        data = datetime.strptime(str(c["data_consulta"]), "%Y-%m-%d").strftime("%d/%m/%Y")
        print(f"{c['id_consulta']} - {c['paciente']} - {data} às {c['hora_consulta']}")

    while True:
        id_consulta = input_ou_voltar("ID da consulta para marcar como realizada: ")
        if id_consulta is None: return
        if not id_consulta.isdigit():
            print("ID inválido! Digite novamente.")
            continue
        cursor.execute(
            "SELECT * FROM consultas WHERE id_consulta=%s AND id_medico=%s AND estado_consulta='agendada'",
            (id_consulta, medico["id_medico"])
        )
        consulta = cursor.fetchone()
        if not consulta:
            print("Consulta não encontrada ou já não está agendada! Digite novamente.")
            continue
        break

    try:
        cursor.execute(
            "UPDATE consultas SET estado_consulta='realizada' WHERE id_consulta=%s",
            (id_consulta,)
        )
        db.commit()
        print("Consulta marcada como realizada com sucesso!")
    except Exception as e:
        print("Erro ao atualizar consulta:", e)


#__________Menus__________

def menu_utilizador(usuario):
    while True:
        print(f"\nBem-vindo {usuario['nome']}")
        print("1 Marcar consulta")
        print("2 Listar consultas")       # abre submenu por estado
        print("3 Cancelar consulta")
        print("4 Alterar consulta")
        print("5 Disponibilidade médico")
        print("0 Sair")
        op = input("Escolha: ").strip()
        if   op == "1": marcar_consulta(usuario)
        elif op == "2": menu_listar_consultas(usuario)  # ALTERADO: submenu de estados
        elif op == "3": cancelar_consulta(usuario)
        elif op == "4": alterar_consulta(usuario)
        elif op == "5": disponibilidade_medico()
        elif op == "0": break
        else: print("Opção inválida!")

def menu_medico(medico):
    while True:
        print(f"\nDr(a) {medico['nome']}")
        print("1 Ver consultas")
        print("2 Marcar consulta como realizada")  # NOVO
        print("3 Ver relatórios")
        print("4 Adicionar relatório")
        print("5 Alterar relatório")
        print("0 Sair")
        op = input("Escolha: ").strip()
        if op == "1":
            cursor.execute("""
                SELECT c.*, u.nome AS paciente
                FROM consultas c
                JOIN utilizadores u ON c.id_utilizador = u.id_utilizador
                WHERE c.id_medico=%s
            """, (medico["id_medico"],))
            consultas = cursor.fetchall()
            if not consultas:
                print("Nenhuma consulta encontrada!")
            for c in consultas:
                data = datetime.strptime(str(c["data_consulta"]), "%Y-%m-%d").strftime("%d/%m/%Y")
                print(f"{c['id_consulta']} | {c['paciente']} | {data} {c['hora_consulta']} "
                      f"| {c['motivo_consulta']} | [{c['estado_consulta'].upper()}]")
        elif op == "2": marcar_consulta_realizada(medico)  # NOVO
        elif op == "3": ver_relatorios(medico)
        elif op == "4": adicionar_relatorio(medico)
        elif op == "5": alterar_relatorio(medico)
        elif op == "0": break
        else: print("Opção inválida!")

def menu_admin(admin):
    while True:
        print("\nMenu ADMIN")
        print("1 Criar médico")
        print("2 Listar médicos")
        print("3 Alterar médico")
        print("4 Apagar médico")
        print("0 Sair")
        op = input("Escolha: ").strip()
        if   op == "1": criar_medico()
        elif op == "2": listar_medicos()
        elif op == "3": alterar_medico()
        elif op == "4": apagar_medico()
        elif op == "0": break
        else: print("Opção inválida!")


#__________Menu Principal__________

def principal():
    while True:
        print("\n1 Registar")
        print("2 Login")
        print("3 Sair")
        op = input("Escolha: ").strip()
        if   op == "1": registar()
        elif op == "2":
            usuario = login()
            if usuario:
                if   usuario["tipo"] == "admin":  menu_admin(usuario)
                elif usuario["tipo"] == "medico": menu_medico(usuario)
                else:                             menu_utilizador(usuario)
        elif op == "3": break
        else: print("Opção inválida!")

if __name__ == "__main__":
    principal()