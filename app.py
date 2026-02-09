idade = input("Introduza a sua idade: ")
if idade.isnumeric():
    idade = int(idade)

    if idade >= 18:
        print("Maior de idade")
    else:
        print("Menor de idade")
else:
    print("Por favor, introduza um valor numérico válido para o ano de nascimento. Ex: 1990")