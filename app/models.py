from app import db
from datetime import datetime

class Recipient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {"id": self.id, "email": self.email, "name": self.name}

class EmailTemplate(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    subject = db.Column(db.String(200), nullable=False)
    body = db.Column(db.Text, nullable=False) # Stores HTML or Text

    def to_dict(self):
        return {"id": self.id, "name": self.name, "subject": self.subject, "body": self.body}

class EmailLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    recipient_email = db.Column(db.String(120), nullable=False)
    status = db.Column(db.String(20), nullable=False) # 'Sent' or 'Failed'
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    error_message = db.Column(db.String(500), nullable=True)

    def to_dict(self):
        return {
            "id": self.id,
            "recipient": self.recipient_email,
            "status": self.status,
            "timestamp": self.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            "error": self.error_message
        }
