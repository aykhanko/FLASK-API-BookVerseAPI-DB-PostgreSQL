from marshmallow import Schema, fields
from schemas.comments import CommentSchema

class BookSchema(Schema):
    id = fields.Str(dump_only=True)
    name = fields.Str(required=True)
    author = fields.Str(dump_only=True)
    comments = fields.Nested(CommentSchema, many=True, dump_only=True)
    user_id = fields.Int(dump_only=True)
