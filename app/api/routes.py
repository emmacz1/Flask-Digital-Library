from flask import Blueprint, request, jsonify
from app.helpers import token_required
from app.models import db, Book, book_schema, books_schema
from sqlalchemy.exc import IntegrityError

api = Blueprint('api', __name__, url_prefix='/api')

@api.route('/books', methods=['POST'])
@token_required
def create_book(current_user_token):
    book_data = request.get_json()
    title = book_data['title']
    author = book_data['author']
    isbn = book_data['isbn']
    year = book_data['year']
    user_token = current_user_token.token
    book = Book(title=title, author=author, isbn=isbn, year=year, user_token=user_token)
    db.session.add(book)
     
    try:
        db.session.commit()
    except IntegrityError as e:
        db.session.rollback()
        if 'duplicate key value violates unique constraint' in str(e.orig):
            return jsonify({'error': f'A book with ISBN {isbn} already exists.'}), 400
        else:
            return jsonify({'error': 'An error occurred'}), 400
    response = book_schema.dump(book)
    return jsonify(response), 201


@api.route('/books', methods=['GET'])
@token_required
def get_books(current_user_token):
    books = Book.query.filter_by(user_token=current_user_token.token).all()
    response = books_schema.dump(books)
    return jsonify(response)

@api.route('/books/<id>', methods=['GET'])
@token_required
def get_single_book(current_user_token, id):
    book = Book.query.get(id)
    response = book_schema.dump(book)
    return jsonify(response)

@api.route('/books/<id>', methods=['PUT'])
@token_required
def update_book(current_user_token, id):
    book = Book.query.get(id)
    if book:
        data = request.get_json()
        if not all(k in data for k in ('title', 'author', 'isbn', 'year')):
            return jsonify({'message': 'Missing data'}), 400

        book.title = data['title']
        book.author = data['author']
        book.isbn = data['isbn']
        book.year = data['year']
        db.session.commit()
        response = book_schema.dump(book)
        return jsonify(response), 200
    else:
        return jsonify({'message': 'Book not found'}), 404

@api.route('/books/<id>', methods=['DELETE'])
@token_required
def delete_book(current_user_token, id):
    book = Book.query.get(id)
    if book:
        if book.user_token != current_user_token.token:
            return jsonify({'message': 'Unauthorized to delete this book'}), 403

        db.session.delete(book)
        db.session.commit()
        return jsonify({'message': 'Book deleted successfully'}), 200
    else:
        return jsonify({'message': 'Book not found'}), 404
