import os
import re
from datetime import datetime

import pandas as pd

from app import create_app, db
from app.models.employmentType import EmploymentType
from app.models.experienceLevel import ExperienceLevel
from app.models.jobTitle import JobTitle
from app.models.location import Location
from app.models.salary import Salary

EXCEL_PATH = os.path.join("data", "salarios.xlsx")

EMPLOYMENT_TYPE_MAP = {
    "FT": "Full-Time",
    "PT": "Part-Time",
    "CT": "Contract",
    "FL": "Freelance",
}

EXPERIENCE_LEVEL_MAP = {
    "EN": "Junior",
    "MI": "Semi-Senior",
    "SE": "Senior",
    "EX": "Executive",
}

COUNTRY_MAP = {
    "AD": "Andorra",
    "AE": "United Arab Emirates",
    "AM": "Armenia",
    "AR": "Argentina",
    "AS": "American Samoa",
    "AT": "Austria",
    "AU": "Australia",
    "BA": "Bosnia and Herzegovina",
    "BE": "Belgium",
    "BR": "Brazil",
    "BS": "Bahamas",
    "CA": "Canada",
    "CF": "Central African Republic",
    "CH": "Switzerland",
    "CL": "Chile",
    "CN": "China",
    "CO": "Colombia",
    "CZ": "Czech Republic",
    "DE": "Germany",
    "DK": "Denmark",
    "DZ": "Algeria",
    "EC": "Ecuador",
    "EE": "Estonia",
    "EG": "Egypt",
    "ES": "Spain",
    "FI": "Finland",
    "FR": "France",
    "GB": "United Kingdom",
    "GH": "Ghana",
    "GR": "Greece",
    "HK": "Hong Kong",
    "HN": "Honduras",
    "HR": "Croatia",
    "HU": "Hungary",
    "ID": "Indonesia",
    "IE": "Ireland",
    "IL": "Israel",
    "IN": "India",
    "IQ": "Iraq",
    "IR": "Iran",
    "IT": "Italy",
    "JP": "Japan",
    "KE": "Kenya",
    "KR": "South Korea",
    "LT": "Lithuania",
    "LU": "Luxembourg",
    "LV": "Latvia",
    "MD": "Moldova",
    "MT": "Malta",
    "MU": "Mauritius",
    "MX": "Mexico",
    "MY": "Malaysia",
    "NG": "Nigeria",
    "NL": "Netherlands",
    "NO": "Norway",
    "NZ": "New Zealand",
    "PH": "Philippines",
    "PK": "Pakistan",
    "PL": "Poland",
    "PR": "Puerto Rico",
    "PT": "Portugal",
    "QA": "Qatar",
    "RO": "Romania",
    "RU": "Russia",
    "SA": "Saudi Arabia",
    "SE": "Sweden",
    "SG": "Singapore",
    "SI": "Slovenia",
    "TH": "Thailand",
    "TR": "Turkey",
    "UA": "Ukraine",
    "US": "United States",
    "ZA": "South Africa",
}

JOB_TITLE_ALIASES = {
    "ML Engineer": "Machine Learning Engineer",
    "MLOps Engineer": "Machine Learning Operations Engineer",
    "Finance Data Analyst": "Financial Data Analyst",
    "BI Analyst": "Business Intelligence Analyst",
    "BI Data Analyst": "Business Intelligence Data Analyst",
    "Data Modeller": "Data Modeler",
}


def clean_spaces(text: str) -> str:
    """Limpia espacios extra: strip + colapsar múltiples espacios internos."""
    text = text.strip()
    text = re.sub(r"\s+", " ", text)
    return text


def normalize_job_title(raw_title: str) -> str:
    """
    Normaliza el job_title:
    - Limpia espacios extra
    - Aplica alias si existe (ML Engineer -> Machine Learning Engineer, etc.)
    - Si no está en el diccionario, lo devuelve tal cual limpio.
    """
    if raw_title is None:
        return None

    title = clean_spaces(str(raw_title))

    if title in JOB_TITLE_ALIASES:
        return JOB_TITLE_ALIASES[title]

    return title


def get_or_create(model, **kwargs):
    """
    Busca un registro en model con los campos kwargs.
    Si existe, lo devuelve.
    Si no existe, lo crea (sin commit).
    """
    instance = model.query.filter_by(**kwargs).first()
    if instance:
        return instance

    instance = model(**kwargs)
    db.session.add(instance)
    db.session.flush()
    return instance


def seed_from_excel():
    """
    Función principal que crea el app context y ejecuta el seed
    """
    # Crear la aplicación con configuración SQLite
    app = create_app()
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data/salarios.db'
    
    with app.app_context():
        _seed_from_excel()


def _seed_from_excel():
    """
    Lee el archivo Excel y carga los datos en las tablas:
    EmploymentType, ExperienceLevel, JobTitle, Location y Salary.

    IMPORTANTE: esta función asume que YA ESTÁS dentro de app.app_context().
    """
    print(f"Leyendo archivo Excel: {EXCEL_PATH}")

    try:
        df = pd.read_excel(EXCEL_PATH)
        print("Lectura exitosa del archivo\n")
    except FileNotFoundError:
        print("ERROR: El archivo no fue encontrado.")
        print("Verifica que exista en la carpeta 'data' y que el nombre sea correcto.")
        return
    except Exception as e:
        print("ERROR al leer el archivo Excel:")
        print(str(e))
        return

    print("=== INFO BÁSICA DEL DATASET ===")
    print(f"Filas: {len(df)}")
    print(f"Columnas: {len(df.columns)}")
    print("Columnas:", df.columns.tolist())
    print()

    total = len(df)
    insertados = 0
    saltados = 0

    for idx, row in df.iterrows():
        try:
            year_raw = row.get("work_year")
            salary_raw = row.get("salary_in_usd")
            emp_type_code = row.get("employment_type")
            exp_level_code = row.get("experience_level")
            job_title_raw = row.get("job_title")
            residence_code = row.get("employee_residence")

            if (
                pd.isna(year_raw)
                or pd.isna(salary_raw)
                or pd.isna(emp_type_code)
                or pd.isna(exp_level_code)
                or pd.isna(job_title_raw)
                or pd.isna(residence_code)
            ):
                print(f"Fila {idx}: datos esenciales faltantes, se salta.")
                saltados += 1
                continue

            try:
                year_int = int(year_raw)
                year = str(year_int)
            except ValueError:
                print(f"Fila {idx}: work_year inválido ({year_raw}), se salta.")
                saltados += 1
                continue

            try:
                salary_in_usd = int(salary_raw)
            except ValueError:
                print(f"Fila {idx}: salary_in_usd inválido ({salary_raw}), se salta.")
                saltados += 1
                continue

            emp_type_code = str(emp_type_code).strip()
            emp_type_text = EMPLOYMENT_TYPE_MAP.get(emp_type_code)
            if emp_type_text is None:
                print(f"Fila {idx}: employment_type código desconocido ({emp_type_code}), se salta.")
                saltados += 1
                continue

            exp_level_code = str(exp_level_code).strip()
            exp_level_text = EXPERIENCE_LEVEL_MAP.get(exp_level_code)
            if exp_level_text is None:
                print(f"Fila {idx}: experience_level código desconocido ({exp_level_code}), se salta.")
                saltados += 1
                continue

            job_title = normalize_job_title(job_title_raw)
            if not job_title:
                print(f"Fila {idx}: job_title vacío tras normalización, se salta.")
                saltados += 1
                continue

            residence_code = str(residence_code).strip()
            location_text = COUNTRY_MAP.get(residence_code, residence_code)

            employment_type_obj = get_or_create(
                EmploymentType,
                employment_type=emp_type_text,
            )

            experience_level_obj = get_or_create(
                ExperienceLevel,
                experience_level=exp_level_text,
            )

            job_title_obj = get_or_create(
                JobTitle,
                job_title=job_title,
            )

            location_obj = get_or_create(
                Location,
                location=location_text,
            )

            salary = Salary(
                year=year,
                salary_in_usd=salary_in_usd,
                employment_type=employment_type_obj.id,
                job_title=job_title_obj.id,
                location=location_obj.id,
                experience_level=experience_level_obj.id,
                created_date=datetime.utcnow(),
                updated_date=datetime.utcnow(),
            )

            db.session.add(salary)
            insertados += 1

        except Exception as e:
            print(f"Error en fila {idx}: {e}")
            saltados += 1

    db.session.commit()
    print("\nSeed completado")
    print(f"Total filas en Excel: {total}")
    print(f"Registros de Salary insertados: {insertados}")
    print(f"Filas saltadas por errores/validación: {saltados}")


if __name__ == '__main__':
    # Para ejecutar el seed directamente
    seed_from_excel()