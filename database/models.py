from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class CodeReview(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    code_snippet = db.Column(db.Text)
    language = db.Column(db.String(50))
    review_types = db.Column(db.String(200))
    results = db.Column(db.Text)  # JSON results
    score = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    findings = db.relationship('ReviewFinding', backref='review', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'language': self.language,
            'review_types': self.review_types.split(','),
            'score': self.score,
            'created_at': self.created_at.isoformat(),
            'code_snippet': self.code_snippet
        }

class ReviewFinding(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    review_id = db.Column(db.Integer, db.ForeignKey('code_review.id'), nullable=False)
    review_type = db.Column(db.String(50))
    severity = db.Column(db.String(20))  # CRITICAL, HIGH, MEDIUM, LOW, INFO
    description = db.Column(db.Text)
    suggestion = db.Column(db.Text)
    file_path = db.Column(db.String(500))
    line_number = db.Column(db.Integer)
    
    def to_dict(self):
        return {
            'id': self.id,
            'review_type': self.review_type,
            'severity': self.severity,
            'description': self.description,
            'suggestion': self.suggestion,
            'file_path': self.file_path,
            'line_number': self.line_number
        }