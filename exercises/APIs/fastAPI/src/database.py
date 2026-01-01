import databases
import sqlalchemy as sqa

DATABASE_URL = "sqlite:///./test.db"
metadata = sqa.MetaData()
database = databases.Database(DATABASE_URL)

engine = sqa.create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
