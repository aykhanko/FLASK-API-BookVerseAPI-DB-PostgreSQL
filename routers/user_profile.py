from flask.views import MethodView
from flask_smorest import Blueprint, abort

from models.auth import AuthModel
from schemas.auth import PublicUserSchema, UpdateUserSchema, PasswordChange
from security.auth import verify_password, hash_password

from database import db
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from flask_jwt_extended import jwt_required, get_jwt_identity

from logging_config import get_module_logger


blp = Blueprint("Users", __name__)
logger = get_module_logger(__file__)

@blp.route("/profile/<string:username>")
class UserProfile(MethodView):
    @jwt_required()
    @blp.response(200, PublicUserSchema)
    def get(self, username):
        profile = AuthModel.query.filter_by(username=username).first()
        current_user = get_jwt_identity()

        if not profile:
            logger.warning(f"User '{username}' not found when accessed by user ID {current_user}")
            abort(404, message="User not found.")
        if current_user != str(profile.id):
            logger.warning(f"Unauthorized access attempt! User ID {current_user} tried to access '{username}' profile.")
            abort(403, message="Access denied.") 

        logger.info(f"User ID {current_user} acessed their own profile '{username}'")    
        return profile
    
    @jwt_required()
    @blp.arguments(UpdateUserSchema)
    @blp.response(200, PublicUserSchema)
    def put(self, request, username):
        user = AuthModel.query.filter_by(username=username).first()
        current_user = get_jwt_identity()

        if not user:
            logger.warning(f"Update attempt failed. Target user '{username}' not found.")
            abort(404, message="User not found.")
        if current_user != str(user.id):
            logger.warning(f"Unauthorized update attempt! User ID {current_user} tried to update '{username}' profile.")
            abort(403, message="Access denied.")

        if "username" in request:
            user.username = request["username"]
        elif "email" in request:
            user.email = request["email"]

        try:
            db.session.add(user)
            db.session.commit()
            logger.info(f"User ID {current_user} updated profile '{user.username}' - updated email '{user.email}'")

        except SQLAlchemyError:
            logger.error(f"DB error while updating profile for '{username}' by user ID {current_user}")
            abort(400, message="Couldn't update profile")
        
        return user

    @jwt_required()
    def delete(self, username):
        profile = AuthModel.query.filter_by(username=username).first()
        current_user = get_jwt_identity()

        if not profile:
            logger.warning(f"Deletion failed. User '{username}' not found.")
            abort(404, message="User not found.")

        if current_user != str(profile.id):
            logger.warning(f"Unauthorized deletion attempt! User ID {current_user} tried to delete '{username}'")
            abort(403, message="Access denied.")
        

        db.session.delete(profile)
        db.session.commit()
        logger.info(f"User ID {current_user} deleted their profile '{username}'.")

        return {"message": "Profile deleted"}

@blp.route("/profile/<string:username>/changepassword")
class ChangePassword(MethodView):
    @jwt_required()
    @blp.arguments(PasswordChange)
    def put(self, request, username):
        user = AuthModel.query.filter_by(username=username).first()
        current_user_id = get_jwt_identity()

        if not user:
            logger.warning(f"Password change failed. User '{username}' not found.")
            abort(404, message="User not found")

        if str(user.id) != str(current_user_id):
            logger.warning(f"Unauthorized password change attempt! User ID {current_user_id} tried to access '{username}'")
            abort(403, message="You can only change your own password.")

        if verify_password(request["old_password"], user.password):
            user.password = hash_password(request["new_password"])
            db.session.commit()
            logger.info(f"User ID {current_user_id} changed password for user '{username}'")
            return {"message": "Password changed successfully."}, 200
        else:
            logger.warning(f"Incorrect old password attempt by user ID {current_user_id} for user '{username}'")
            abort(400, message="Old password is incorrect.")