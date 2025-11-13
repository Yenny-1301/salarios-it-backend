from app import db

class JobTitle(db.Model):
    __tablename__ = 'job_titles'
    id = db.Column(db.Integer, primary_key=True)
    job_title = db.Column(db.String(100))

    def to_dict(self):
        return {
            'id': self.id,
            'job_title': self.job_title
        }
