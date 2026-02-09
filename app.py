import os
from datetime import date

def calcular_idade(ano_nascimento: int) -> int:
    ano_atual: int = date.today().year
    return ano_atual - ano_nascimento


def definir_categoria(idade: int) -> str:
    if idade < 10:
        return "Criança"
    elif idade < 18:
        return "Adolescente"
    elif idade < 65:
        return "Adulto"
    elif idade < 100:
        return "Sénior"
    else:
        return "Ancião"


if __name__ == '__main__':
    while True:
        os.system('cls' if os.name == 'nt' else 'clear')

        try:
            ano_nascimento_input = int(input("Introduza o seu ano de nascimento: "))
            idade_aux = calcular_idade(ano_nascimento_input)
            if idade_aux < 0:
                print("Ano de nascimento inválido!")
                input("Pressione qualquer tecla para continuar...")
                continue

            print(
                f"A idade para o ano de nascimento {ano_nascimento_input} é de {idade_aux} anos.")

            print(f"É {definir_categoria(idade_aux)}.")

            continuar: str = input("Deseja continuar? (s/n) ").lower()
            if continuar == 'n':
                break

        except ValueError as e:
            print('Erro:', e)
            print('Introduza um valor válido!')
            print()
            input('Pressione qualquer tecla para continuar...')
