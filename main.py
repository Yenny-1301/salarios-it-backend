import os
from app import create_app, db
from app.models.salary import Salary
from seed_from_excel import seed_from_excel

print("Configurando base de datos SQLite...")

# Crear carpeta data con ruta absoluta
base_dir = os.path.abspath(os.path.dirname(__file__))
data_dir = os.path.join(base_dir, 'data')
os.makedirs(data_dir, exist_ok=True)

print(f"Carpeta data creada en: {data_dir}")

# Crear la aplicación
app = create_app()

with app.app_context():
    # Crear todas las tablas
    db.create_all()
    print("Tablas creadas correctamente")
    
    # Verificar si ya hay datos
    salaries_count = Salary.query.count()
    if salaries_count == 0:
        print("Tabla 'salaries' vacía → ejecutando seed_from_excel()...")
        seed_from_excel()
        print("Seed ejecutado correctamente")
    else:
        print(f"ℹTabla 'salaries' ya tiene {salaries_count} registros → no se ejecuta seed.")

if __name__ == '__main__':
    app.run(debug=True)