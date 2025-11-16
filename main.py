import urllib
from app import create_app, db
from sqlalchemy import create_engine, text
from app.models.salary import Salary
from seed_from_excel import seed_from_excel

DATABASE_NAME = "it_salaries"

server_params = urllib.parse.quote_plus(
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=(localdb)\\MSSQLLocalDB;"
    "Trusted_Connection=yes;"
)
server_engine = create_engine(f"mssql+pyodbc:///?odbc_connect={server_params}")

with server_engine.connect() as conn:
    # ⬇️ ALTERNATIVA MÁS EXPLÍCITA: Desactivar la transacción para este comando
    conn.execution_options(isolation_level="AUTOCOMMIT").execute(
        text(f"IF DB_ID('{DATABASE_NAME}') IS NULL CREATE DATABASE [{DATABASE_NAME}]")
    )
    # Ya no se necesita conn.commit()

print(f"Base de datos '{DATABASE_NAME}' creada o verificada")

app = create_app()

with app.app_context():
    db.create_all()
    print("Tablas creadas correctamente")
    
    salaries_count = Salary.query.count()
    if salaries_count == 0:
        print("Tabla 'salaries' vacía → ejecutando seed_from_excel()...")
        seed_from_excel()
        print("Seed ejecutado correctamente")
    else:
        print(f"ℹTabla 'salaries' ya tiene {salaries_count} registros → no se ejecuta seed.")

if __name__ == '__main__':
    app.run(debug=True)
