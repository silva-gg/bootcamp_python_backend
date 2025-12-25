import datetime, functools
import inquirer

def _log_data_hora(funcion):
    """Retorna a data e hora atual formatada como string."""
    @functools.wraps(funcion)
    def wrapper_log_data_hora(*args, **kwargs):
        data_hora = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        try:
            output = funcion(*args, **kwargs)
        except Exception as e:
            print(f"[{data_hora}] Erro na operação {funcion.__name__}: {e}")
            raise e
        match funcion.__name__:
            case "deposito":
                print(f"[{data_hora}] Depósito realizado")
            case "saque":
                print(f"[{data_hora}] Saque realizado")
            case "exibir_extrato":
                print(f"[{data_hora}] Extrato consultado")
            case "criar_usuário":
                print(f"[{data_hora}] Usuário criado") if output != 0 else print(f"[{data_hora}] Falha ao criar usuário")
            case "criar_conta":
                print(f"[{data_hora}] Conta criada") if output != 0 else print(f"[{data_hora}] Falha ao criar conta")
            case _:  # default
                print(f"[{data_hora}] Operação realizada")
        
        return output
    return wrapper_log_data_hora

def ReportGenerator(extrato: str, filtro: str = None):
    iteravel = extrato.splitlines()
    for line in iteravel:
        if (filtro is None or filtro in line) and line != "":
            yield line

class ContaIterador:
    def __init__(self, banco_de_contas: list):
        self.__banco_de_contas = banco_de_contas
        self.__index = 0

    def __iter__(self):
        return self

    def __next__(self):
        if self.__index < len(self.__banco_de_contas):
            conta = self.__banco_de_contas[self.__index]
            self.__index += 1
            return f"Agência: {conta['agencia']} | Conta: {conta['numero_conta']} | Titular: {conta['usuario']['nome']} | Saldo: R$ {conta['saldo']:.2f}"
        else:
            raise StopIteration

@_log_data_hora
def deposito(saldo: float, extrato: str, /):
    valor = float(input("Informe o valor do depósito: "))

    if valor > 0:
        saldo += valor
        extrato += f"Depósito: R$ {valor:.2f}\n"
        return saldo, extrato

    else:
        print("Operação falhou! O valor informado é inválido.")
        raise ValueError("Valor inválido para depósito.")

@_log_data_hora
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
@_log_data_hora
def exibir_extrato(saldo: float, /, *, extrato: str):
    print("\n================ EXTRATO ================")
    print("Não foram realizadas movimentações." if not extrato else extrato)
    print(f"\nSaldo: R$ {saldo:.2f}")
    print("==========================================")

@_log_data_hora
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
        senha = input("Defina uma senha para o usuário: ")
        print("Usuário criado com sucesso!")
        banco_de_usuarios.append({"nome": nome, "data_nascimento": data_nascimento, "cpf": cpf, "endereco": endereco, "senha": senha})
        return 1
    except Exception as e:
        print(f"Erro ao criar usuário: {e}")
        return 0

def filtrar_usuario(cpf: str, banco_de_usuarios: list):
    usuarios_filtrados = [usuario for usuario in banco_de_usuarios if usuario["cpf"] == cpf]
    return usuarios_filtrados[0] if usuarios_filtrados else None
@_log_data_hora
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
                senha_usuario = input("Informe a senha do usuário: ")
                if usuario["senha"] != senha_usuario:
                    raise ValueError("Senha incorreta.")
                numero_conta = len(banco_de_contas) + 1
                senha_conta = input("Defina uma senha para a conta: ")
                banco_de_contas.append({"agencia": agencia, "numero_conta": numero_conta, "usuario": usuario, "senha": senha_conta, **default})
                print(f"Conta criada com sucesso! Número da conta: {numero_conta} Agência: {agencia}")
                return banco_de_contas
            elif usuario == banco_de_usuarios[-1]:
                raise ValueError("CPF não encontrado. Usuário deve ser cadastrado antes de criar uma conta.")
    except Exception as e:
        if isinstance(e, ValueError):
            print(e)
            return 0
        else:   
            print(f"Erro ao criar conta: {e}")
            return 0
    return banco_de_contas

def main():
    menu_externo = """
    [c] Criar conta
    [u] Criar usuário
    [l] Login
    [r] Relatório de Contas
    [q] Sair
    => """
    menu_interno = """

    [d] Depositar
    [s] Sacar
    [e] Extrato
    [r] Relatório
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
                if banco_de_contas == 0 or banco_de_contas is None:
                    raise ValueError("Falha ao criar conta.")
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
        elif opcao_externa == "r":
            print("\n======= RELATÓRIO DE CONTAS =======")
            conta_iterador = ContaIterador(banco_de_contas)
            for linha in conta_iterador:
                print(linha)
            print("===================================")
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
            elif opcao == "r":
                try:
                    filtros = ['Nenhum filtro', 'Depósito', 'Saque']
                    questions = [
                        inquirer.List('filtro',
                                     message="Selecione um filtro para o relatório",
                                     choices=filtros,
                                     ),
                    ]
                    answers = inquirer.prompt(questions)
                    filtro = answers['filtro'] if answers['filtro'] != 'Nenhum filtro' else ""
                except ImportError:
                    print("Para usar seleção com setas, instale: pip install inquirer")
                    filtro = input("Informe um filtro para o relatório (pressione Enter para nenhum filtro): ")
                print("\n======= RELATÓRIO DE MOVIMENTAÇÕES =======")
                for linha in ReportGenerator(extrato, filtro if filtro != "" else None):
                    print(linha)
                print("==========================================")
            elif opcao == "q":
                break
            else:
                print("Operação inválida, por favor selecione novamente a operação desejada.")
            banco_de_contas[numero_conta_login - 1] = conta_logada
            with open("banco_de_contas.txt", "w") as f:
                f.write(str(banco_de_contas))

if __name__ == "__main__":
    main()