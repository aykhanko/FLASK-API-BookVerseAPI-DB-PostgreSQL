from database import db

class BooksModel(db.Model):
    __tablename__ = "books"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)
    author = db.Column(db.String(50), nullable=False)

    comments = db.relationship(
        "CommentsModel",
        back_populates="book",
        lazy=True,
        cascade="all, delete-orphan",  
        passive_deletes=True          
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id", name="fk_books_user_id"),
        nullable=False  
    )
