"""SQLAlchemy 2.0: motor, sesión por petición y base declarativa de los modelos."""

from sqlalchemy import MetaData, create_engine
from sqlalchemy.orm import DeclarativeBase, scoped_session, sessionmaker

# Nombres de constraints estables, para que Alembic genere migraciones reproducibles.
CONVENCION_NOMBRES = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}


class Base(DeclarativeBase):
    metadata = MetaData(naming_convention=CONVENCION_NOMBRES)


sesion = scoped_session(sessionmaker(autoflush=False, expire_on_commit=False))


def iniciar_db(app):
    motor = create_engine(app.config["DATABASE_URL"], pool_pre_ping=True)
    sesion.configure(bind=motor)
    app.extensions["motor_db"] = motor

    @app.teardown_appcontext
    def cerrar_sesion(_error=None):
        sesion.remove()
