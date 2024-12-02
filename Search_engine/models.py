from database import db

class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())

    # Relationship with SearchHistory
    search_history = db.relationship("SearchHistory", back_populates="user")

    def __repr__(self):
        return f"<User {self.username}>"


class SearchHistory(db.Model):
    __tablename__ = "search_history"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    query = db.Column(db.String(255), nullable=False)
    results = db.Column(db.JSON, nullable=False)  # Use JSON for structured data
    searched_at = db.Column(db.DateTime, default=db.func.current_timestamp())

    user = db.relationship("User", back_populates="search_history")

    def __repr__(self):
        return f"<SearchHistory {self.query} by User {self.user_id}>"
