from database import db

class CommentsModel(db.Model):
    __tablename__ = "comments"

    id = db.Column(db.Integer, primary_key=True)
    comment = db.Column(db.String(255), nullable=False)

    book_id = db.Column(
        db.Integer,
        db.ForeignKey("books.id", ondelete="CASCADE", name="fk_comments_book_id"),
        nullable=False
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id", name="fk_comments_user_id"),
        nullable=False 
    )

    book = db.relationship("BooksModel", back_populates="comments", lazy=True)
    user = db.relationship("AuthModel", backref="comments", lazy=True)
