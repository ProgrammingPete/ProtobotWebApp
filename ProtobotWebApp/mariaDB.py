from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://test:qwegmyr123@localhost/test'

engine = create_engine(SQLALCHEMY_DATABASE_URI,
        connect_args = {
        'port': 3306
            },
        echo=True)

db_session = scoped_session(
    sessionmaker(
        bind=engine,
        autocommit=False,
        autoflush=False
    )
)
Base = declarative_base()

def init_db():
    import ProtobotWebApp.models
    Base.metadata.create_all(engine)

    from ProtobotWebApp.models import User
    db_session.add_all([
        User(username='admin', hashvalue='qwegmyr123', password_salt='NA'),
        User(username='test', hashvalue='test', password_salt='NA')
    ])
    db_session.commit()

    print("Init Database Has Finished")


