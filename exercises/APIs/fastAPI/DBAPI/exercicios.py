import sqlite3

conexao = sqlite3.connect('clientes.db')
cursor = conexao.cursor()

def criar_tabela(conexao, cursor, nome_tabela):
    if not nome_tabela.replace('_', '').isalnum():
        raise ValueError("Invalid table name: only alphanumeric characters and underscores allowed")
    
    cursor.execute(f'CREATE TABLE IF NOT EXISTS {nome_tabela} (id INTEGER PRIMARY KEY AUTOINCREMENT, nome VARCHAR(110), preco FLOAT)')
    conexao.commit()

def inserir_registro(conexao, cursor, nome_tabela, nome, email):
    if not nome_tabela.replace('_', '').isalnum():
        raise ValueError("Invalid table name: only alphanumeric characters and underscores allowed")
    
    data = (nome, email)
    cursor.execute(f"INSERT INTO {nome_tabela} (nome, email) VALUES (?, ?)", data)
    conexao.commit()

def atualizar_registro(conexao, cursor, nome_tabela, id_cliente, novo_email):
    if not nome_tabela.replace('_', '').isalnum():
        raise ValueError("Invalid table name: only alphanumeric characters and underscores allowed")
    
    data = (novo_email, id_cliente)
    cursor.execute(f"UPDATE {nome_tabela} SET email = ? WHERE id = ?", data)
    conexao.commit()

def deletar_registro(conexao, cursor, nome_tabela, id_cliente):
    if not nome_tabela.replace('_', '').isalnum():
        raise ValueError("Invalid table name: only alphanumeric characters and underscores allowed")
    
    data = (id_cliente,)
    cursor.execute(f"DELETE FROM {nome_tabela} WHERE id = ?", data)
    conexao.commit()

def batch_inserir_registros(conexao, cursor, nome_tabela, lista_clientes):
    if not nome_tabela.replace('_', '').isalnum():
        raise ValueError("Invalid table name: only alphanumeric characters and underscores allowed")
    
    cursor.executemany(f"INSERT INTO {nome_tabela} (nome, email) VALUES (?, ?)", lista_clientes)
    conexao.commit()

def buscar_todos_registros(conexao, cursor, nome_tabela, coluna, valor):
    if not nome_tabela.replace('_', '').isalnum():
        raise ValueError("Invalid table name: only alphanumeric characters and underscores allowed")
    
    # Get column names from database schema
    cursor.execute(f"PRAGMA table_info({nome_tabela})")
    columns_info = cursor.fetchall()
    allowed_columns = [column[1] for column in columns_info]
    if coluna not in allowed_columns:
        raise ValueError(f"Invalid column name: {coluna}. Allowed columns: {allowed_columns}")
    
    cursor.execute(f"SELECT * FROM {nome_tabela} WHERE {coluna}=?", (valor,))
    return cursor.fetchall()

criar_tabela(conexao, cursor, 'produtos')

inserir_registro(conexao, cursor, 'clientes', 'João Silva', 'joao.silva@example.com')
dados = [('Maria Oliveira', 'maria.oliveira@example.com'), ('Carlos Souza', 'carlos.souza@example.com'), ('Ana Pereira', 'ana.pereira@example.com')]

batch_inserir_registros(conexao, cursor, 'clientes', dados)

reg = buscar_todos_registros(conexao, cursor, 'clientes', 'nome', 'Maria Oliveira')

for r in reg:
    print(r)