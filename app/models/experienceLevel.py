from app import db

class ExperienceLevel(db.Model):
    __tablename__ = 'experience_levels'
    id = db.Column(db.Integer, primary_key=True)
    experience_level = db.Column(db.String(100))

    def to_dict(self):
        return {
            'id': self.id,
            'experience_level': self.experience_level
        }
