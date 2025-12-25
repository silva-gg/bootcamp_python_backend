import functools
import datetime
import inquirer
import logging
import json
import colorlog
from abc import ABC, abstractmethod
from typing import List, Dict, Any
from pathlib import Path

# setup logger with colorlog
handler = colorlog.StreamHandler()
handler.setFormatter(colorlog.ColoredFormatter(
    '[%(cyan)s%(asctime)s%(reset)s] [%(log_color)s%(levelname)s%(reset)s] : %(message)s',
    log_colors={
        'DEBUG': 'blue',
        'INFO': 'green',
        'AVISO': 'yellow',
        'ERRO': 'red',
        'CRITICO': 'red,bg_white',
    }
))

logger = colorlog.getLogger(__name__)
logger.addHandler(handler)
logger.setLevel(logging.INFO)

# Decorator for logging function calls
def _log(function) -> None:
    @functools.wraps(function)
    def wrapper(*args, **kwargs):
        try:
            resultado = function(*args, **kwargs)
        except Exception as e:
            logger.error(f"Function '{function.__name__}' raised an exception: {e}")
            raise e
        match function.__name__:
            case "deposito":
                logger.info("Depósito realizado com sucesso.")
            case "saque":
                logger.info("Saque realizado com sucesso.")
            case "exibir_extrato":
                logger.info("Extrato consultado com sucesso.")
            case "criar_usuário":
                logger.info("Usuário criado com sucesso.")
            case "criar_conta":
                logger.info("Conta criada com sucesso.")
            case _:  # default
                logger.info("Operação bem-sucedida.")
        logger.debug(f"Function '{function.__name__}' executed successfully.")
        return resultado
    return wrapper

class Historico:
    def __init__(self) -> None:
        self._transacoes = []
    
    @property
    def transacoes(self) -> List[Dict[str, Any]]:
        return self._transacoes
    
    def adicionar_transacao(self, transacao : object) -> None:
        self._transacoes.append(transacao.info)

class Cliente:
    def __init__(self, endereco : str, contas_cliente : List[Dict[str, Any]] = [], senha : str = "") -> None:
        self._endereco = endereco
        self._contas = contas_cliente
        self._senha = senha
    
    def realizar_transacao(self, conta : object, transacao : object) -> None:
        transacao.registrar(conta)
    
    @_log
    def adicionar_conta(self, conta : object, senha_conta : str) -> None:
        self._contas.append(conta.nova_conta(cliente = self, numero_conta = len(self._contas) + 1, senha_conta = senha_conta).info)

class PessoaFisica(Cliente):
    def __init__(self, nome : str, cpf : str, data_nascimento : str, **kwargs : Dict[str, Any]) -> None:
        super().__init__(**kwargs)
        self._nome = nome
        self._num_cliente = cpf
        self._data_nascimento = data_nascimento
    @property
    def info(self) -> Dict[str, Any]:
        return {
            "nome": self._nome,
            "num_cliente": self._num_cliente,
            "data_nascimento": self._data_nascimento,
            "endereco": self._endereco,
            "contas": self._contas,
            "senha": self._senha
        }

class Conta:
    def __init__(self, numero_conta: str, agencia: str, cliente: object, senha_conta: str) -> None:
        self._saldo = 0.0        
        self._numero_conta = numero_conta
        self._agencia = agencia
        self._cliente = cliente
        self._senha = senha_conta
        self._historico = Historico()

    @property
    def info(self) -> Dict[str, Any]:
        return {
            "numero_conta": self._numero_conta,
            "num_cliente": self._cliente._num_cliente,
            "agencia": self._agencia,
            "saldo": self._saldo,
            "senha": self._senha,
            "historico": self._historico.transacoes
        }

    @property
    def saldo(self) -> float:
        return self._saldo
    
    @property
    def numero_conta(self) -> str:
        return self._numero_conta
    
    @property
    def agencia(self) -> str:
        return self._agencia
    
    @property
    def cliente(self) -> object:
        return self._cliente
    
    @property
    def historico(self) -> object:
        return self._historico

    @classmethod
    def nova_conta(cls, cliente : object, numero_conta : int, senha_conta : str) -> object:
        return cls(
            numero_conta = numero_conta,
            agencia = "0001",
            cliente = cliente,
            senha_conta = senha_conta
        )
    
    def sacar(self, valor: float) -> bool:
        if valor > self._saldo:
            logger.error("Operação falhou! Você não tem saldo suficiente.")
            raise ValueError("Saldo insuficiente.")
        elif valor > 0:
            Saque(valor).registrar(self)
            return True

    def depositar(self, valor: float) -> bool:
        if (valor <= 0) or (isinstance(valor, float) is False):
            logger.error("Operação falhou! O valor informado é inválido.")
            raise ValueError("Valor inválido para depósito.")
        else:
            return True

class ContaCorrente(Conta):
    def __init__(self, limite: float = 500.0, limite_saques: int = 3, **kwargs: Dict[str, Any]) -> None:
        super().__init__(**kwargs)
        self._limite = limite   
        self._limite_saques = limite_saques
    
    def sacar(self, valor: float) -> bool:
        numero_saques = len([transacao for transacao in self.historico.transacoes if (transacao["tipo"] == Saque.__name__
                            and datetime.datetime.strptime(transacao["data_hora"], "%Y-%m-%d %H:%M:%S").date() == datetime.datetime.now().date())])

        excedeu_saldo = valor > self._saldo

        excedeu_limite = valor > self._limite

        excedeu_saques = numero_saques >= self._limite_saques

        if excedeu_saldo:
            logger.error("Operação falhou! Você não tem saldo suficiente.")
            raise ValueError("Saldo insuficiente.")

        elif excedeu_limite:
            logger.error("Operação falhou! O valor do saque excede o limite.")
            raise ValueError("Limite de saque excedido.")

        elif excedeu_saques:
            logger.error(f"Operação falhou! Número máximo de saques excedido ({self._limite_saques}).")
            raise ValueError("Número máximo de saques excedido.")

        elif valor > 0:
            return True

        else:
            logger.error("Operação falhou! O valor informado é inválido.")
            raise ValueError("Valor inválido para saque.")
    def __str__(self) -> str:
        return f"C/C: {self._numero_conta} Ag: {self._agencia} Titular: {self._cliente._nome}"

class Transacao(ABC):
    @abstractmethod
    def __init__(self) -> None:
        pass
    
    @abstractmethod
    def registrar(cls) -> None:
        pass

class Deposito(Transacao):
    def __init__(self, valor: float) -> None:
        self._valor = valor
        self._data_hora = datetime.datetime.now()
    
    @property
    def valor(self) -> float:
        return self._valor
    
    @property
    def data_hora(self) -> str:
        return self._data_hora.strftime("%Y-%m-%d %H:%M:%S")

    @property
    def info(self) -> Dict[str, Any]:
        return {
            "tipo": self.__class__.__name__,
            "valor": self._valor,
            "data_hora": self._data_hora.strftime("%Y-%m-%d %H:%M:%S")
        }
    @_log
    def registrar(self, conta) -> None:
        if conta.depositar(self._valor):
            conta._saldo += self._valor
            conta.historico.adicionar_transacao(self)

class Saque(Transacao):
    def __init__(self, valor: float) -> None:
        self._valor = valor
        self._data_hora = datetime.datetime.now()
    
    @property
    def info(self) -> Dict[str, Any]:
        return {
            "tipo": self.__class__.__name__,
            "valor": self._valor,
            "data_hora": self._data_hora.strftime("%Y-%m-%d %H:%M:%S")
        }
    
    @_log
    def registrar(self, conta) -> None:
        try:
            if conta.sacar(self._valor):
                conta._saldo -= self._valor
                conta.historico.adicionar_transacao(self)
        except ValueError as e:
            raise e

class SistemaBancario:
    def __init__(self) -> None:
        try:
            self._script_dir = Path(__file__).parent
            with open(self._script_dir / "banco_dados.json", "r") as f:
                dados = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            # Create or recreate the database file if it doesn't exist or is corrupted
            dados = {"clientes": [], "contas": []}
            with open(self._script_dir / "banco_dados.json", "w") as f:
                json.dump(dados, f, indent=4)
        self._clientes = dados["clientes"]
        self._contas = dados["contas"]
    
    @_log
    def criar_usuario(self, nome : str, cpf : str, data_nascimento : str, endereco : str, senha_cliente : str) -> None:
        if any(cliente["num_cliente"] == cpf for cliente in self._clientes):
            logger.error("Já existe um usuário com o CPF informado.")
            raise ValueError("CPF já cadastrado.")
        novo_cliente = PessoaFisica(
            nome = nome,
            cpf = cpf,
            data_nascimento = data_nascimento,
            endereco = endereco,
            senha = senha_cliente
        )
        self._clientes.append(novo_cliente.info)
        self.update_database()
    
    @_log
    def update_database(self) -> None:
        with open(self._script_dir / "banco_dados.json", "w") as f:
            json.dump({
                "clientes": self._clientes,
                "contas": self._contas
            }, f, indent=4)

    @_log
    def criar_conta(self, cliente : Cliente, senha_conta: str) -> None:
        nova_conta = ContaCorrente.nova_conta(
            cliente = cliente,
            numero_conta = len(self._contas) + 1,
            senha_conta = senha_conta
        )
        conta_info = nova_conta.info
        self._contas.append(conta_info)
        
        for i, c in enumerate(self._clientes):
            if c["num_cliente"] == cliente._num_cliente:
                self._clientes[i]["contas"].append({
                    "numero_conta": conta_info["numero_conta"],
                    "agencia": conta_info["agencia"]
                })
                break
        
        self.update_database()
        logger.info(f"{nova_conta.__str__()}")
    
    def realizar_transacao(self, conta : Conta, transacao : Transacao, valor : float) -> None:
        for index, conta_banco_dados in enumerate(self._contas):
            if conta_banco_dados["numero_conta"] == conta.numero_conta:
                transacao(valor).registrar(conta)
                self._contas[index] = conta.info
                self.update_database()
                break


class Autenticacao:
    @staticmethod
    def autenticar(cliente : Cliente, senha : str) -> bool:
        if cliente.info["senha"] == senha:
            return True
        else:
            logger.error("Falha na autenticação! Senha incorreta.")
            raise PermissionError("Senha incorreta.")

class Menu:
    def __init__(self) -> None:
        self._sistema_bancario = SistemaBancario()
    
    def mostrar_menu(self) -> None:
        perguntas = [
            inquirer.List(
                "opcao",
                message="Selecione a operação desejada",
                choices=[
                    "Criar Usuário",
                    "Criar Conta",
                    "Sacar",
                    "Depositar",
                    "Exibir Extrato",
                    "login",
                    "logout",
                    "Ligar/Desligar Debug",
                    "Sair"
                ]
            )
        ]
        resposta = inquirer.prompt(perguntas)
        return resposta["opcao"]
    def executar(self) -> None:
        while True:
            opcao = self.mostrar_menu()
            if opcao == "Sair":
                logger.info("Encerrando o sistema bancário. Até logo!")
                break
            elif opcao == "Ligar/Desligar Debug":
                if logger.level == logging.INFO:
                    logger.setLevel(logging.DEBUG)
                    logger.info("Modo DEBUG ativado.")
                else:
                    logger.setLevel(logging.INFO)
                    logger.info("Modo DEBUG desativado.")
            elif opcao == "login":
                try:
                    numero_conta = int(input("Número da conta: "))
                    senha_conta = input("Senha da conta: ")
                    conta_data = next((conta for conta in self._sistema_bancario._contas if conta["numero_conta"] == numero_conta), None)
                    cliente_data = next((cliente for cliente in self._sistema_bancario._clientes if cliente["num_cliente"] == conta_data["num_cliente"]), None)
                    if cliente_data is None:
                        logger.error("Cliente não encontrado.")
                        continue
                    if conta_data is None:
                        logger.error("Conta não encontrada.")
                        continue
                    self._cliente = PessoaFisica(
                        nome = cliente_data["nome"],
                        cpf = cliente_data["num_cliente"],
                        data_nascimento = cliente_data["data_nascimento"],
                        endereco = cliente_data["endereco"],
                        contas_cliente = cliente_data["contas"],
                        senha = cliente_data["senha"]
                    )
                    self._conta = ContaCorrente(
                        numero_conta = conta_data["numero_conta"],
                        agencia = conta_data["agencia"],
                        cliente = self._cliente,
                        senha_conta = conta_data["senha"]
                    )
                except Exception as e:
                    logger.error(f"Erro ao localizar conta ou cliente")
                    logger.debug(f"Falha no login. Detalhes: {e}")
                    continue
                try:
                    Autenticacao.autenticar(self._conta, senha_conta)
                    logger.info("Login realizado com sucesso.")
                except PermissionError as e:
                    del self._cliente
                    del self._conta
                    logger.error(f"Erro no login: {e}")           
            elif opcao == "logout":
                try:
                    del self._cliente
                    del self._conta
                    logger.info("Logout realizado com sucesso.")
                except AttributeError:
                    logger.error("Nenhum usuário está logado no momento.")
            elif opcao == "Criar Usuário":
                try:
                    nome = input("Nome completo: ")
                    cpf = input("CPF (somente números): ")
                    data_nascimento = input("Data de nascimento (DD-MM-AAAA): ")
                    endereco = input("Endereço (logradouro, número - bairro - cidade/sigla estado): ")
                    senha_cliente = input("Senha do cliente: ")
                    self._sistema_bancario.criar_usuario(
                        nome = nome,
                        cpf = cpf,
                        data_nascimento = data_nascimento,
                        endereco = endereco,
                        senha_cliente = senha_cliente
                    )
                except ValueError as e:
                    logger.error(f"Erro ao criar usuário: {e}")
            elif opcao == "Criar Conta":
                try:
                    cpf = input("CPF do cliente: ")
                    senha_cliente = input("Senha do cliente: ")
                    cliente_data = next((cliente for cliente in self._sistema_bancario._clientes if cliente["num_cliente"] == cpf), None)
                    if cliente_data is None:
                        logger.error("Cliente não encontrado.")
                        raise ValueError("Cliente não encontrado.")
                    cliente = PessoaFisica(
                        nome = cliente_data["nome"],
                        cpf = cliente_data["num_cliente"],
                        data_nascimento = cliente_data["data_nascimento"],
                        endereco = cliente_data["endereco"],
                        contas_cliente = cliente_data["contas"],
                        senha = cliente_data["senha"]
                    )
                    Autenticacao.autenticar(cliente, senha_cliente)
                    senha_conta = input("Senha da conta: ")
                    self._sistema_bancario.criar_conta(
                        cliente = cliente,
                        senha_conta = senha_conta
                    )
                except (ValueError, PermissionError) as e:
                    logger.error(f"Erro ao criar conta: {e}")
            elif opcao == "Exibir Extrato":
                try:
                    logger.info("=== EXTRATO ===")
                    if not self._conta.historico.transacoes:
                        logger.info("Não foram realizadas movimentações.")
                    else:
                        for transacao in self._conta.historico.transacoes:
                            logger.info(f"{transacao['data_hora']} - {transacao['tipo']}: R$ {transacao['valor']:.2f}")
                    logger.info(f"Saldo atual: R$ {self._conta.saldo:.2f}")
                    logger.info("=== FIM DO EXTRATO ===")
                except AttributeError:
                    logger.error("Nenhum usuário está logado no momento.")
            elif opcao == "Sacar":
                try:
                    valor = float(input("Valor do saque: "))
                    self._sistema_bancario.realizar_transacao(self._conta, Saque, valor)                  
                except AttributeError as e:
                    logger.error("Nenhum usuário está logado no momento.")
                    logger.debug(f"Detalhes: {e}")
                except ValueError as e:
                    logger.error(f"Valor inválido para saque")
                    logger.debug(f"Detalhes: {e}")

            elif opcao == "Depositar":
                try:
                    valor = float(input("Valor do depósito: "))
                    self._sistema_bancario.realizar_transacao(self._conta, Deposito, valor)
                except AttributeError as e:
                    logger.error("Nenhum usuário está logado no momento.")
                    logger.debug(f"Detalhes: {e}")
                except ValueError as e:
                    logger.error(f"Valor inválido para saque")
                    logger.debug(f"Detalhes: {e}")

if __name__ == "__main__":
    menu = Menu()
    menu.executar()