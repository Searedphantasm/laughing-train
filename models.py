from datetime import datetime

from sqlalchemy.orm import Mapped,mapped_column
from sqlalchemy import ForeignKey
from db import db

class Book(db.Model):
    __tablename__ = 'book'

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str]
    description: Mapped[str]
    publisher: Mapped[str]
    version: Mapped[int]
    in_stock: Mapped[int]

class BookWriter(db.Model):
    __tablename__ = 'book_writer'

    id: Mapped[int] = mapped_column(primary_key=True)
    book_id: Mapped[int] = mapped_column(ForeignKey('book.id'))
    writer_id: Mapped[int] = mapped_column(ForeignKey('writer.id'))

class Writer(db.Model):
    __tablename__ = 'writer'

    id: Mapped[int] = mapped_column(primary_key=True)
    first_name: Mapped[str]
    last_name: Mapped[str]

class Customer(db.Model):
    __tablename__ = 'customer'

    id: Mapped[int] = mapped_column(primary_key=True)
    first_name: Mapped[str]
    last_name: Mapped[str]
    phone: Mapped[str] = mapped_column(unique=True)
    national_code: Mapped[str]
    address: Mapped[str]

class CustomerBook(db.Model):
    __tablename__ = 'customer_book'

    id: Mapped[int] = mapped_column(primary_key=True)
    book_id: Mapped[int] = mapped_column(ForeignKey('book.id'))
    customer_id: Mapped[int] = mapped_column(ForeignKey('customer.id'))
    start_date: Mapped[datetime]
    end_date: Mapped[datetime]
