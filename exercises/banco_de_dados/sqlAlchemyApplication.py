from sqlalchemy.orm import Session
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Column, inspect, select
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import ForeignKey
from sqlalchemy import create_engine
Base = declarative_base()

class UserModel(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    fullname = Column(String)
    # back_populates referencia o nome do atributo na outra classe
    address = relationship("AddressModel", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self):
        # Representação amigável do objeto (útil para debugging mas não obrigatório)
        return f"UserModel(id={self.id!r}, name={self.name!r}, fullname={self.fullname!r})"

class AddressModel(Base):
    __tablename__ = 'addresses'
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    email_address = Column(String(30), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False) # sempre referenciar a tabela com o nome correto
    # back_populates referencia o nome do atributo na outra classe
    user = relationship("UserModel", back_populates="address")

    def __repr__(self):
        # Representação amigável do objeto (útil para debugging mas não obrigatório)
        return f"AddressModel(id={self.id!r}, email_address={self.email_address!r})"

# conexao com o banco de dados
engine = create_engine('sqlite://')

# cria as tabelas no banco de dados
Base.metadata.create_all(engine)

# Definindo inspetor para buscar infos na engine
inspector = inspect(engine)

# Listando todas as tabelas criadas e o schema default
print("Tabelas no banco de dados:", inspector.get_table_names())
print(inspector.default_schema_name)

# criando uma sessão para interagir com o banco de dados
with Session(engine) as session:
    # criando um novo usuário
    new_user = UserModel(name='joao', fullname='João da Silva',
    address=[AddressModel(email_address='joao@example.com'), AddressModel(email_address='joao.silva@example.com')])
    
    other_user = UserModel(name='maria', fullname='Maria Oliveira')
    session.add_all([new_user, other_user])
    session.commit()

# statement retorna a instrução SQL que será executada
# statement = select(UserModel).where(UserModel.name.in_(['joao']))
# for user in session.scalars(statement):
#     print(user)
#     for address in user.address:
#         print("  ", address)

print(*[entry for entry in 
        session.scalars(select(UserModel)
                        .order_by(UserModel.id.desc())).all()], 
                        sep="\n")

print(smt_join := select(UserModel.name, AddressModel.email_address).join_from(
    UserModel, AddressModel, isouter=True))

connection = engine.connect()
result = connection.execute(smt_join).fetchall()
for row in result:
    print(row)

#lembrar de fechar a sessão
session.close()