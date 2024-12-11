from datetime import datetime
from app import db


class ChatHistory(db.Model):
    __tablename__ = 'chat_history'

    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.String(255))
    message = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    keyword = db.Column(db.String(255))

    def __init__(self, session_id, message, keyword):
        self.session_id = session_id
        self.message = message
        self.keyword = keyword