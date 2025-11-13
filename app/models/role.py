from app import db

class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    role = db.Column(db.String(100))

    def to_dict(self):
        return {
            'id': self.id,
            'role': self.role
        }