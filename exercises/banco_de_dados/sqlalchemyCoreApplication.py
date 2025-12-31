# definindo schemas sem usar orm
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, ForeignKey, text
from sqlalchemy.orm import relationship, declarative_base, sessionmaker
# :memory: cria um banco de dados temporário na memória RAM
engine = create_engine('sqlite:///:memory:', echo=False)
connection = engine.connect()
metadata_obj = MetaData()
user = Table(
    'users',
    metadata_obj,
    Column('id', Integer, primary_key=True),
    Column('name', String(40), nullable=False),
)

address = Table(
    'addresses',
    metadata_obj,
    Column('id', Integer, primary_key=True),
    Column('user_id', Integer, ForeignKey('users.id')),
    Column('email_address', String(100), nullable=False)
)

metadata_obj.create_all(engine)

sql = text("select name from users") 
sql_insert = text("INSERT INTO users VALUES(2, 'joao')")
connection.execute(sql_insert)
result = connection.execute(sql)
print(result.all())