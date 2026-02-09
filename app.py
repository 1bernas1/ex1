from datetime import date

def calcular_idade(ano_nascimento: int) -> int:
    ano_atual: int = date.today().year
    return ano_atual - ano_nascimento

ano_nascimento_input = input("Introduza o seu ano de nascimento: ")

if ano_nascimento_input.isnumeric():
    ano_nascimento_arg = int(ano_nascimento_input)
    idade = calcular_idade(ano_nascimento_arg)

    if idade >= 18:
        print("Maior de idade")
    else:
        print("Menor de idade")
else:
    print("Por favor, introduza um valor numérico válido para o ano de nascimento. Ex: 1990")