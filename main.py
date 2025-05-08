from flask import Flask
from flask_smorest import Api

from database import db
from models import BooksModel, CommentsModel, AuthModel
from flask_migrate import Migrate

from routers.books import blp as BookBlp
from routers.comments import blp as CommentBlp
from routers.auth import blp as AuthBlp
from routers.user_profile import blp as UserProfile

from flask_jwt_extended import JWTManager
from blocklist import BLOCKLIST
import os
from dotenv import load_dotenv 

from datetime import timedelta
app = Flask(__name__)
load_dotenv()

app.config["PROPAGATE_EXCEPTIONS"] = True

app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

app.config["API_TITLE"] = "Books REST API"
app.config["API_VERSION"] = "v1"
app.config["OPENAPI_VERSION"] = "3.0.3"
app.config["OPENAPI_URL_PREFIX"] = "/"
app.config["OPENAPI_SWAGGER_UI_PATH"] = "/swagger-ui"
app.config["OPENAPI_SWAGGER_UI_URL"]  = "https://cdn.jsdelivr.net/npm/swagger-ui-dist/"

app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY")
app.config["JWT_BLACKLIST_ENABLED"] = True
app.config["JWT_BLACKLIST_TOKEN_CHECKS"] = ["access"]
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(minutes=15)
app.config["JWT_REFRESH_TOKEN_EXPIRES"] = timedelta(days=30)


db.init_app(app)
migrate = Migrate(app, db)
api = Api(app)
jwt = JWTManager(app)


@jwt.token_in_blocklist_loader
def check_if_token_revoked(jwt_header, jwt_payload):
    jti = jwt_payload["jti"]
    return jti in BLOCKLIST


api.register_blueprint(BookBlp)
api.register_blueprint(CommentBlp)
api.register_blueprint(AuthBlp) 
api.register_blueprint(UserProfile) 


from flask import request
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
from models.auth import AuthModel  
from logging_config import get_module_logger

logger = get_module_logger(__file__)

@app.before_request
def log_all_requests():
    ip = request.remote_addr
    ua = request.headers.get("User-Agent")
    method = request.method
    path = request.path

    try:
        verify_jwt_in_request()
        user_id = get_jwt_identity()
        user = AuthModel.query.get(user_id)
        logger.info(f"{method} {path} | IP: {ip} | User ID: {user_id} | Username: {user.username} | UA: {ua}")
    except:
        logger.info(f"{method} {path} | IP: {ip} | ANONYMOUS | UA: {ua}")