from sqlalchemy import MetaData
from sqlalchemy import Table,Column
from sqlalchemy import Integer,String
from sqlalchemy import create_engine
meta = MetaData() # Collection of tables
tabla = Table('user', meta,
              Column('id', Integer, primary_key=True),
              Column('name', String, primary_key=True),
              Column('fullname',String)
              )


engine = create_engine("sqlite://")
meta.create_all(engine)