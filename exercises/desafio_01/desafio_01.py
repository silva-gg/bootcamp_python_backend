def deposito(saldo: float, extrato: str, /):
    valor = float(input("Informe o valor do depósito: "))

    if valor > 0:
        saldo += valor
        extrato += f"Depósito: R$ {valor:.2f}\n"
        return saldo, extrato

    else:
        print("Operação falhou! O valor informado é inválido.")
        raise ValueError("Valor inválido para depósito.")

def saque(*, saldo: float, limite: float, numero_saques: int, limites_saque: int, extrato: str):
    valor = float(input("Informe o valor do saque: "))

    excedeu_saldo = valor > saldo

    excedeu_limite = valor > limite

    excedeu_saques = numero_saques >= limites_saque

    if excedeu_saldo:
        print("Operação falhou! Você não tem saldo suficiente.")
        raise ValueError("Saldo insuficiente.")

    elif excedeu_limite:
        print("Operação falhou! O valor do saque excede o limite.")
        raise ValueError("Limite de saque excedido.")

    elif excedeu_saques:
        print(f"Operação falhou! Número máximo de saques excedido ({limites_saque}).")
        raise ValueError("Número máximo de saques excedido.")

    elif valor > 0:
        saldo -= valor
        extrato += f"Saque: R$ {valor:.2f}\n"
        numero_saques += 1
        return saldo, extrato, numero_saques

    else:
        print("Operação falhou! O valor informado é inválido.")
        raise ValueError("Valor inválido para saque.")

def exibir_extrato(saldo: float, /, *, extrato: str):
    print("\n================ EXTRATO ================")
    print("Não foram realizadas movimentações." if not extrato else extrato)
    print(f"\nSaldo: R$ {saldo:.2f}")
    print("==========================================")

def criar_usuário(banco_de_usuarios: list):
    # armazenar em lista por nome, data de nasc,cpf, endereço (log, num - bairro - cidade/sigla estado)
    print("Informe os dados do usuário:")
    try:
        cpf = input("CPF (somente números): ")
        usuario = filtrar_usuario(cpf, banco_de_usuarios)
        if usuario:
            raise ValueError("Já existe usuário com esse CPF!")
        nome = input("Nome completo: ")
        data_nascimento = input("Data de nascimento (dd-mm-aaaa): ")
        endereco = input("Endereço (logradouro, número - bairro - cidade/sigla estado): ")
        print("Usuário criado com sucesso!")
        banco_de_usuarios.append({"nome": nome, "data_nascimento": data_nascimento, "cpf": cpf, "endereco": endereco})
    except Exception as e:
        print(f"Erro ao criar usuário: {e}")

def filtrar_usuario(cpf: str, banco_de_usuarios: list):
    usuarios_filtrados = [usuario for usuario in banco_de_usuarios if usuario["cpf"] == cpf]
    return usuarios_filtrados[0] if usuarios_filtrados else None

def criar_conta(banco_de_contas: list, banco_de_usuarios: list, agencia: str = "0001", default: dict = {"saldo": 0, "extrato": "", "numero_saques": 0}):
    # vincular conta a um usuário, armazena em lista composta por agência, num conta, usuário
    # num da conta sequencial começando em 1, agencia fixa 0001
    # usuário pode ter mais de uma conta, mas conta só pode ter um usuário
    try:
        cpf_usuario = input("Informe o CPF do usuário: ")
        if len(banco_de_usuarios) == 0:
            raise ValueError("Banco de usuários vazio.")
        for usuario in banco_de_usuarios:
            if usuario["cpf"] == cpf_usuario:
                numero_conta = len(banco_de_contas) + 1
                senha_conta = input("Defina uma senha para a conta: ")
                banco_de_contas.append({"agencia": agencia, "numero_conta": numero_conta, "usuario": usuario, "senha": senha_conta, **default})
                print(f"Conta criada com sucesso! Número da conta: {numero_conta} Agência: {agencia}")
                return banco_de_contas
            raise ValueError("CPF não encontrado.")
    except Exception as e:
        if isinstance(e, ValueError):
            print("CPF não encontrado. Usuário deve ser cadastrado antes de criar uma conta.")
        else:   
            print(f"Erro ao criar conta: {e}")
    return banco_de_contas

def main():
    menu_externo = """
    [c] Criar conta
    [u] Criar usuário
    [l] Login
    [q] Sair
    => """
    menu_interno = """

    [d] Depositar
    [s] Sacar
    [e] Extrato
    [q] Sair

    => """
    try:
        banco_de_usuarios = []
        banco_de_contas = []
        with open("banco_de_usuarios.txt", "r") as f:
            banco_de_usuarios = eval(f.read())
        with open("banco_de_contas.txt", "r") as f:
            banco_de_contas = eval(f.read())

    except Exception as e:
        with open("banco_de_usuarios.txt", "w") as f:
            f.write(str(banco_de_usuarios))
        with open("banco_de_contas.txt", "w") as f:
            f.write(str(banco_de_contas))
        print(f"Erro ao carregar banco de dados: {e}")
    while True:
        conta_logada = None
        opcao_externa = input(menu_externo)
        if opcao_externa == "c":
            try:
                banco_de_contas = criar_conta(banco_de_contas, banco_de_usuarios)
                with open("banco_de_contas.txt", "w") as f:
                    f.write(str(banco_de_contas))
            except:
                print("Escolha uma opção válida.")
        elif opcao_externa == "u":
            try:
                criar_usuário(banco_de_usuarios)
                with open("banco_de_usuarios.txt", "w") as f:
                    f.write(str(banco_de_usuarios))
            except Exception as e:
                print(f"Erro ao criar usuário: {e}")
        elif opcao_externa == "l":
            try:
                agencia_login = input("Informe a agência: ")
                numero_conta_login = int(input("Informe o número da conta: "))
                senha_login = input("Informe a senha da conta: ")
                conta_logada = None
                for conta in banco_de_contas:
                    if (conta["agencia"] == agencia_login and
                        conta["numero_conta"] == numero_conta_login and
                        conta["senha"] == senha_login):
                        conta_logada = conta
                        print(f"Login bem-sucedido! Bem-vindo, {conta_logada["usuario"]["nome"]}.")
                        print("----------------------------------------")
                        print(f"Agência: {conta_logada["agencia"]} | Conta: {conta_logada["numero_conta"]}")
                        saldo = conta_logada["saldo"]
                        limite = conta_logada.get("limite", 500)
                        extrato = conta_logada["extrato"]
                        numero_saques = conta_logada.get("numero_saques", 0)
                        LIMITE_SAQUES = conta_logada.get("limite_saques", 3)
            except:
                print("Escolha uma opção válida.")
                conta_logada = None
            if not conta_logada:
                print("Falha no login! Verifique os dados informados.")
                continue
        elif opcao_externa == "q":
            print("Encerrando o programa. Até mais!")
            break
        else:
            print("Operação inválida, por favor selecione novamente a operação desejada.")
            continue
        while (conta_logada is not None):

            opcao = input(menu_interno)

            if opcao == "d":
                try:
                    saldo, extrato = deposito(saldo, extrato)
                    conta_logada["saldo"] = saldo
                    conta_logada["extrato"] = extrato
                except:
                    print("Escolha uma opção válida.")
            elif opcao == "s":
                try:
                    saldo, extrato, numero_saques = saque(saldo=saldo, limite=limite, numero_saques=numero_saques, limites_saque=LIMITE_SAQUES, extrato=extrato)
                    conta_logada["saldo"] = saldo
                    conta_logada["extrato"] = extrato
                    conta_logada["numero_saques"] = numero_saques
                except:
                    print("Escolha uma opção válida.")
            elif opcao == "e":
                exibir_extrato(saldo, extrato=extrato)
            elif opcao == "q":
                break
            else:
                print("Operação inválida, por favor selecione novamente a operação desejada.")
            banco_de_contas[numero_conta_login - 1] = conta_logada
            with open("banco_de_contas.txt", "w") as f:
                f.write(str(banco_de_contas))

if __name__ == "__main__":
    main()