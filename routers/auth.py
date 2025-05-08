from flask import jsonify
from flask.views import MethodView
from flask_smorest import Blueprint, abort

from models.auth import AuthModel
from schemas.auth import AuthRegisterSchema, AuthLoginSchema, PublicUserSchema

from database import db
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from security.auth import hash_password, verify_password
from flask_jwt_extended import (create_access_token, jwt_required, get_jwt,
                                create_refresh_token, get_jwt_identity, set_refresh_cookies)

from blocklist import BLOCKLIST
from logging_config import get_module_logger

blp = Blueprint("Auth", __name__)
logger = get_module_logger(__file__)


@blp.route("/registration")
class AuthRegistration(MethodView):
    @blp.arguments(AuthRegisterSchema)
    @blp.response(201, PublicUserSchema)
    def post(self, request):
        user = AuthModel(
            username=request["username"],
            email=request["email"],
            password=hash_password(request["password"])
        )
        try:
            db.session.add(user)
            db.session.commit()
            logger.info(f"New user registered: {user.username} ({user.email})")
        except IntegrityError:
            logger.warning(f"Registration failed: user '{request['username']}' already exists.")
            abort(400, message="User already exists")
        except SQLAlchemyError:
            logger.error("Database error during registration.")
            abort(500, message="An error occurred while registration")
        return user


@blp.route("/login")
class AuthLogin(MethodView):
    @blp.arguments(AuthLoginSchema)
    def post(self, request):
        user = None

        if "username" in request:
            user = AuthModel.query.filter_by(username=request["username"]).first()
        elif "email" in request:
            user = AuthModel.query.filter_by(email=request["email"]).first()

        if not user:
            logger.warning("Login failed: User not found.")
            abort(401, message="User not found")
        if not verify_password(request["password"], user.password):
            logger.warning(f"Login failed: Incorrect password for user {user.username}.")
            abort(401, message="Incorrect password")

        access_token = create_access_token(identity=str(user.id), additional_claims={"username": user.username})
        refresh_token = create_refresh_token(identity=str(user.id))

        logger.info(f"User {user.username} (ID: {user.id}) logged in successfully.")

        response = jsonify({"access_token": access_token})
        set_refresh_cookies(response, refresh_token) 
        return response


@blp.route("/logout")
class AuthLogout(MethodView):
    @jwt_required(verify_type=False)
    def post(self):
        jwt = get_jwt()["jti"]
        user_id = get_jwt_identity()
        BLOCKLIST.add(jwt)
        logger.info(f"User ID {user_id} logged out. Token blacklisted.")
        return {"message": "Logged out"}


@blp.route("/refresh")
class RefreshToken(MethodView):
    @jwt_required(refresh=True)
    def post(self):
        user_id = get_jwt_identity()
        new_access_token = create_access_token(identity=user_id)
        logger.info(f"Access token refreshed for user ID {user_id}.")
        return {'access_token': new_access_token}
