from flask import render_template, Blueprint, request, jsonify
from sqlalchemy import text

from db import db

blp = Blueprint('main', __name__)


@blp.route('/')
def index():
    return render_template("home.page.html")


@blp.route('/books/<book_id>')
def book_detail(book_id):
    book = db.session.execute(text(
        "SELECT b.*,w.* FROM book b JOIN book_writer bk ON b.id = bk.book_id JOIN writer w ON bk.writer_id = w.id WHERE b.id = :id"),
                              {'id': book_id}).one()
    return render_template("book-detail.page.html", book=book)


@blp.route('/books')
def book_list():
    books = db.session.execute(text(
        "SELECT b.*,w.* FROM book b JOIN book_writer bk ON b.id = bk.book_id JOIN writer w ON bk.writer_id = w.id")).all()

    return render_template("books.page.html", books=books)


@blp.route('/writers')
def writer_list():
    writers = db.session.execute(text(
        """SELECT 
    w.first_name, 
    w.last_name, 
    w.id,
    COUNT(DISTINCT b.id) AS unique_book_count
FROM writer w
JOIN book_writer bw ON w.id = bw.writer_id
JOIN book b ON bw.book_id = b.id
GROUP BY w.first_name, w.last_name; """
    )).all()

    return render_template("writers.page.html", writers=writers)

@blp.route('/writers/<writer_id>')
def writer_detail(writer_id):
    writer = db.session.execute(text(
        """SELECT 
    first_name, 
    last_name
FROM writer WHERE id = :id ; """
    ),{"id":writer_id}).one()

    books = db.session.execute(text(
        """
        SELECT * FROM book b JOIN book_writer bw ON b.id = bw.book_id JOIN writer w ON bw.writer_id = w.id WHERE w.id = :writer_id
        """
    ),{"writer_id":writer_id}).all()

    ctx = {
        "writer":writer,
        "books": books
    }

    return render_template("writer-detail.page.html", ctx=ctx)


@blp.route('/rent')
def rent_book():
    books = db.session.execute(text(
        "SELECT * FROM book WHERE in_stock > 0")).all()
    return render_template("rent.page.html", books=books)

@blp.route('/signed/rent')
def signed_rent_book():
    books = db.session.execute(text(
        "SELECT * FROM book WHERE in_stock > 0")).all()
    return render_template("signed-rent.page.html", books=books)

@blp.route('/api/rent', methods=['POST'])
def handle_rent():
    data = request.get_json()

    # extracting data
    first_name = data['first_name']
    last_name = data['last_name']
    phone = data['phone']
    national_code = data['national_code']
    address = data['address']
    start_date = data['start_date']
    end_date = data['end_date']
    book_id = data['book_id']

    try:
        customer = db.session.execute(text(
            "SELECT * FROM customer WHERE phone = :phone"
        ), {'phone': phone}).one_or_none()
        print(1)
        if customer:
            return jsonify({'error': 'Invalid phone'}), 400
        # creating customer
        db.session.execute(text(
            "INSERT INTO customer (first_name,last_name,phone,national_code,address) VALUES (:first_name,:last_name,:phone,:national_code,:address)"
        ), {'first_name': first_name, 'last_name': last_name, 'phone': phone, 'national_code': national_code,
            'address': address})

        db.session.commit()

        customer = db.session.execute(text(
            "SELECT * FROM customer WHERE phone = :phone"
        ), {'phone': phone}).one()

        print(2)
        # creating CustomerBook

        customer_id = customer.id

        db.session.execute(text(
            "INSERT INTO customer_book (customer_id,book_id,start_date,end_date) VALUES (:customer_id,:book_id,:start_date,:end_date)"
        ), {'customer_id': customer_id, 'book_id': book_id, 'start_date': start_date, 'end_date': end_date})

        db.session.commit()

        db.session.execute(text(
            "UPDATE book SET in_stock = in_stock - 1 WHERE id = :book_id"
        ), {'book_id': book_id})

        db.session.commit()

        return jsonify({'message': 'Book rented successfully'}), 201

    except Exception as e:
        # undo the changes to database
        db.session.rollback()
        return jsonify({'error': str(e)}), 400




@blp.route('/rented-books')
def rented_books():

    rented = db.session.execute(text(
        """
        SELECT cb.*,b.*,c.* FROM customer_book cb JOIN customer c on  cb.customer_id = c.id JOIN book b on cb.book_id = b.id
        """
    ))

    return render_template("rented-books.page.html", rented=rented)


@blp.route('/rented-books/<phone>')
def search_rented_books(phone):
    rented = db.session.execute(text(
        """
        SELECT cb.*,b.*,c.* FROM customer_book cb JOIN customer c on  cb.customer_id = c.id JOIN book b on cb.book_id = b.id WHERE c.phone = :phone
        """
    ),{'phone': phone}).all()

    if len(rented) == 0:
        return render_template("not-found.page.html")

    return render_template("rented-books.page.html", rented=rented)


@blp.route('/api/signed/rent', methods=['POST'])
def handle_signed_rent():
    data = request.get_json()

    # extracting data
    phone = data['phone']
    start_date = data['start_date']
    end_date = data['end_date']
    book_id = data['book_id']

    try:

        customer = db.session.execute(text(
            "SELECT * FROM customer WHERE phone = :phone"
        ), {'phone': phone}).one()

        customer_id = customer.id

        db.session.execute(text(
            "INSERT INTO customer_book (customer_id,book_id,start_date,end_date) VALUES (:customer_id,:book_id,:start_date,:end_date)"
        ), {'customer_id': customer_id, 'book_id': book_id, 'start_date': start_date, 'end_date': end_date})

        db.session.commit()

        db.session.execute(text(
            "UPDATE book SET in_stock = in_stock - 1 WHERE id = :book_id"
        ), {'book_id': book_id})

        db.session.commit()

        return jsonify({'message': 'Book rented successfully'}), 201

    except Exception as e:
        # undo the changes to database
        db.session.rollback()
        return jsonify({'error': str(e)}), 400


