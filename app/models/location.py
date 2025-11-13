from app import db

class Location(db.Model):
    __tablename__ = 'locations'
    id = db.Column(db.Integer, primary_key=True)
    location = db.Column(db.String(100))

    def to_dict(self):
        return {
            'id': self.id,
            'location': self.location
        }
