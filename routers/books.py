from flask.views import MethodView
from flask_smorest import Blueprint, abort

from models.auth import AuthModel
from models.books import BooksModel
from schemas.books import BookSchema

from database import db
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from logging_config import get_module_logger

from flask_jwt_extended import jwt_required, get_jwt_identity

blp = Blueprint("Books", __name__)
logger = get_module_logger(__file__)


@blp.route("/books")
class Book(MethodView):
    @blp.response(200, BookSchema(many=True))
    def get(self):
        logger.info("GET /books - All books fetched")
        query = BooksModel.query.all()
        return query
    
    @jwt_required()
    @blp.arguments(BookSchema)
    @blp.response(201, BookSchema)
    def post(self, request):
        current_user_id = get_jwt_identity()
        
        user = AuthModel.query.get(current_user_id)
        if not user:
            abort(404, message="User not found")
            logger.error("User not found")

        book = BooksModel(
            name=request["name"],
            author=user.username,
            user_id=current_user_id
        )
        
        try:
            db.session.add(book)
            db.session.commit()
            logger.info(f"Book added: {book.name} by {book.author}")
        except IntegrityError:
            logger.warning(f"Book already exists: {book.name}")
            abort(400, message="A book already exists")
        except SQLAlchemyError as e:
            logger.error(f"Database error while inserting book: {str(e)}")
            abort(500, message="An error occurred while inserting the book")
        return book  


@blp.route("/books/<string:book_id>")
class BookDetails(MethodView):
    @blp.response(200, BookSchema)
    def get(self, book_id):
        book = BooksModel.query.get_or_404(book_id)
        logger.info(f"Book fetched with ID: {book_id}")
        return book
    
    @jwt_required()
    @blp.arguments(BookSchema)
    @blp.response(201, BookSchema)
    def put(self, request, book_id):
        current_user_id = get_jwt_identity()

        book = BooksModel.query.get_or_404(book_id)

        if book.user_id != int(current_user_id):
            logger.warning(f"User {current_user_id} unauthorized to update book ID {book_id}")
            abort(403, message="You cannot update this book.")

        user = AuthModel.query.get(current_user_id)
        if not user:
            logger.error("User not found")
            abort(404, message="User not found")

        old_name, old_author = book.name, book.author
        book.name = request["name"]
        book.author = user.username
        book.user_id = current_user_id

        try:
            db.session.add(book)
            db.session.commit()
            logger.info(f"Book updated (ID: {book_id}) - From '{old_name}' by {old_author} to '{book.name}' by {book.author}")
        except SQLAlchemyError as e:
            logger.error(f"Error updating book ID {book_id}: {str(e)}")
            abort(400, message="Couldn't update book")
        return book

    @jwt_required()
    def delete(self, book_id):
        current_user_id = get_jwt_identity()
        book = BooksModel.query.get_or_404(book_id)

        if book.user_id != int(current_user_id):
            logger.warning(f"User {current_user_id} unauthorized to delete book ID {book_id}")
            abort(403, message="You could not delete this book.")

        db.session.delete(book)
        db.session.commit()
        logger.info(f"Book deleted by user {current_user_id} - ID: {book_id}, Name: {book.name}")
        return {"message": "Book deleted."}
