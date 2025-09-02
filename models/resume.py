# Resume model
from models.db import db
from datetime import datetime


class Resume(db.Model):
    __tablename__ = "resumes"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    text_content = db.Column(db.Text)
    file_path = db.Column(db.String(255))
    parsed_data = db.Column(db.JSON)  # Store structured resume data
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "text_content": self.text_content,
            "file_path": self.file_path,
            "created_at": self.created_at.isoformat(),
        }

