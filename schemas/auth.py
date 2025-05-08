from marshmallow import Schema, fields

class AuthRegisterSchema(Schema):
    id = fields.Int(dump_only=True)
    username = fields.Str(required=True)
    email = fields.Email(required=True)
    password = fields.Str(required=True) 

class AuthLoginSchema(Schema):
    id = fields.Int(dump_only=True)
    username = fields.Str(required=False)
    email = fields.Email(required=False)
    password = fields.Str(required=True, load_only=True) 

class PublicUserSchema(Schema):
    id = fields.Int(dump_only=True)
    username = fields.Str()
    email = fields.Email()
    
class UpdateUserSchema(Schema):
    username = fields.Str()
    email = fields.Email()

class PasswordChange(Schema):
    old_password = fields.String(required=True)
    new_password = fields.String(required=True)