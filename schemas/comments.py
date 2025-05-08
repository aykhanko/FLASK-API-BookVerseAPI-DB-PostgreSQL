from marshmallow import Schema, fields

class CommentSchema(Schema):
    id = fields.Str(dump_only=True)
    comment = fields.Str(required=True)
    book_id = fields.Int(required=True)
    user_id = fields.Int(dump_only=True)
    commenter = fields.Method("get_commenter_username", dump_only=True)


    def get_commenter_username(self, obj):
        return obj.user.username if obj.user else None

