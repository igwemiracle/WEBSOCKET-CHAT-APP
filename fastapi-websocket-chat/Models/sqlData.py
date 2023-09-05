from sqlalchemy.ext.declarative import declarative_base
import sqlalchemy as sa
Base = declarative_base()


class User(Base):
    __tablename__ = "users"
    id = sa.Column(sa.Integer, primary_key=True, index=True)
    username = sa.Column(sa.String)
    hash_password = sa.Column(sa.String)
    email = sa.Column(sa.String, unique=True, index=True)


class SavedMessage(Base):
    __tablename__ = "messages"
    id = sa.Column(sa.Integer, primary_key=True)
    sender_username = sa.Column(sa.String)
    recipient_username = sa.Column(sa.String)
    text = sa.Column(sa.String)
