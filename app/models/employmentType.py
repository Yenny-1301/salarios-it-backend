from app import db

class EmploymentType(db.Model):
    __tablename__ = 'employment_types'
    id = db.Column(db.Integer, primary_key=True)
    employment_type = db.Column(db.String(100))

    def to_dict(self):
        return {
            'id': self.id,
            'employment_type': self.employment_type
        }
