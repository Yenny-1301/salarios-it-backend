from app import db
from werkzeug.security import generate_password_hash, check_password_hash
from app.models.role import Role

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)
    role_id = db.Column('role', db.Integer, db.ForeignKey('roles.id')) 
    created_date = db.Column(db.DateTime, default=db.func.current_timestamp())

    role_type_ref = db.relationship('Role', backref='users', lazy=True)

    def set_password(self, password):
        """Hashea y guarda la contraseña."""
        self.password = generate_password_hash(password)

    def check_password(self, password):
        """Verifica la contraseña hasheada."""
        return check_password_hash(self.password, password)

    @classmethod
    def exists_by_email(cls, email):
        """Devuelve True si existe un usuario con el email dado."""
        return cls.query.filter_by(email=email).first() is not None

    def to_dict(self):
        role_name = self.role_type_ref.role if self.role_type_ref else None

        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'role': role_name,
            'created_date': self.created_date.isoformat() if self.created_date else None,
        }