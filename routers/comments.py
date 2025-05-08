from flask.views import MethodView
from flask_smorest import Blueprint, abort

from models.auth import AuthModel
from models.books import BooksModel
from models.comments import CommentsModel
from schemas.comments import CommentSchema

from database import db
from sqlalchemy.exc import SQLAlchemyError

from logging_config import get_module_logger

from flask_jwt_extended import jwt_required, get_jwt_identity

blp = Blueprint("Comments", __name__)
logger = get_module_logger(__file__)


@blp.route("/comments")
class Comments(MethodView):
    @blp.response(200, CommentSchema(many=True))
    def get(self):
        logger.info("GET /comments - All comments fetched")
        query = CommentsModel.query.all()
        return query

    @jwt_required()
    @blp.arguments(CommentSchema)
    @blp.response(201, CommentSchema)
    def post(self, request_data):
        current_user_id = get_jwt_identity()

        user = AuthModel.query.get(current_user_id)
        if not user:
            abort(404, message="User not found")
            logger.error("User not found")

        book = BooksModel.query.get(request_data["book_id"])

        if not book:
            logger.warning(f"POST /comments - Book with ID {request_data['book_id']} not found")
            abort(400, message="Book not found.")   

        comment = CommentsModel(
            comment=request_data["comment"],
            book_id=request_data["book_id"],
            user_id=current_user_id
        )

        try:
            db.session.add(comment)
            db.session.commit()
            logger.info(f"Comment created on book ID {comment.book_id}: '{comment.comment}'")
        except SQLAlchemyError as e:
            logger.error(f"DB error while creating comment: {str(e)}")
            abort(500, message="Comment əlavə edilərkən xəta baş verdi.")
        return comment


@blp.route("/comment/<string:comment_id>")
class CommentsDetail(MethodView):
    def get(self, comment_id):
        comment = CommentsModel.query.get_or_404(comment_id)
        logger.info(f"Comment fetched with ID: {comment_id}")
        return comment
    
    @jwt_required()
    def delete(self, comment_id):
        current_user_id = get_jwt_identity()

        comment = CommentsModel.query.get_or_404(comment_id)

        if comment.user_id != int(current_user_id):
            logger.warning(f"User {current_user_id} unauthorized to delete book ID {comment_id}")
            abort(403, message="You could not delete this book.")

        db.session.delete(comment)
        db.session.commit()
        logger.info(f"Comment deleted with ID: {comment_id}")
        return {"message": "Comment deleted"}
    
    @jwt_required()
    @blp.arguments(CommentSchema)
    @blp.response(201, CommentSchema)
    def put(self, request, comment_id):
        current_user_id = get_jwt_identity()

        comment = CommentsModel.query.get_or_404(comment_id)

        if comment.user_id != int(current_user_id):
            logger.warning(f"User {current_user_id} unauthorized to update comment ID {comment_id}")
            abort(403, message="You cannot edit this comment.")


        old_comment = comment.comment
        comment.comment = request["comment"]

        try:
            db.session.add(comment)
            db.session.commit()
            logger.info(f"Comment updated (ID: {comment_id}) from '{old_comment}' to '{comment.comment}'")
        except SQLAlchemyError as e:
            logger.error(f"Error updating comment ID {comment_id}: {str(e)}")
            abort(400, message="Couldn't update comment")
        return comment
