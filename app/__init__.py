from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from app.config import Config
import os

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # ✅ CONFIGURACIÓN SQLITE CON RUTA ABSOLUTA EXPLÍCITA
    base_dir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
    db_path = os.path.join(base_dir, 'data', 'salarios.db')
    
    # Asegurar que la carpeta existe
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    print(f"🗄️ Base de datos en: {db_path}")
    
    # ✅ INICIALIZAR DB UNA SOLA VEZ
    db.init_app(app)
    
    # ✅ CONFIGURAR CORS (después de db.init_app)
    CORS(app, resources={r"/api/*": {"origins": "http://localhost:4200"}})
    
    # ✅ MOVER LOS IMPORTS DE MODELOS dentro del contexto
    with app.app_context():
        from app.models import employmentType, experienceLevel, jobTitle, location, role, user, salary

    # Registrar las rutas CRUD
    from app.routes.user_routes import user_bp
    from app.routes.employment_type_routes import employment_type_bp
    from app.routes.experience_level_routes import experience_level_bp
    from app.routes.job_title_routes import job_title_bp
    from app.routes.location_routes import location_bp
    from app.routes.role_routes import role_bp
    from app.routes.salary_routes import salary_bp

    app.register_blueprint(user_bp, url_prefix='/api/users')
    app.register_blueprint(employment_type_bp, url_prefix='/api/employmentTypes')
    app.register_blueprint(experience_level_bp, url_prefix='/api/experienceLevels')
    app.register_blueprint(job_title_bp, url_prefix='/api/jobTitles')
    app.register_blueprint(location_bp, url_prefix='/api/locations')
    app.register_blueprint(role_bp, url_prefix='/api/roles')
    app.register_blueprint(salary_bp, url_prefix='/api/salaries')

    return app