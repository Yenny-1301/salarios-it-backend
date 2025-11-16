from flask import Blueprint, request, jsonify
from app import db
from app.models.salary import Salary
from app.models.jobTitle import JobTitle
from app.models.location import Location  
from app.models.experienceLevel import ExperienceLevel
from datetime import datetime
from sqlalchemy import func

salary_bp = Blueprint('salary_bp', __name__)

@salary_bp.route('/', methods=['GET'])
def get_salaries():
    """Obtiene y devuelve todos los registros de salarios."""
    try:
        salaries = Salary.query.all()
        return jsonify([s.to_dict() for s in salaries]), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Error al obtener salarios', 'error': str(e)}), 500

@salary_bp.route('/', methods=['POST'])
def create_salary():
    """Crea un nuevo registro de salario con los datos del formulario Angular."""
    data = request.get_json()
    
    print("Datos recibidos:", data)
    
    required_fields = ['area', 'location', 'position', 'experienceLevel', 'salary']
    missing_fields = [field for field in required_fields if field not in data or not data[field]]
    
    if missing_fields:
        return jsonify({
            'message': 'Faltan campos requeridos', 
            'missing_fields': missing_fields
        }), 400

    try:
        new_salary = Salary(
            year=datetime.now().year,
            salary_in_usd=data['salary'],
            employment_type=data.get('area', ''),
            job_title=data.get('position', ''),
            location=data.get('location', ''),
            experience_level=data.get('experienceLevel', ''),
            created_date=db.func.current_timestamp(),
            updated_date=db.func.current_timestamp()
        )
        
        db.session.add(new_salary)
        db.session.commit()
        
        return jsonify({
            'message': 'Salario creado exitosamente',
            'data': new_salary.to_dict()
        }), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'message': 'Error al crear salario', 
            'error': str(e)
        }), 500

@salary_bp.route('/filters', methods=['GET'])
def get_filter_options():
    """Devuelve las opciones de filtro desde la base de datos."""
    try:
        print("🔄 Obteniendo filtros desde la base de datos...")
        
        job_titles = JobTitle.query.all()
        locations = Location.query.all()
        experience_levels = ExperienceLevel.query.all()
        
        areas = [job.job_title for job in job_titles if job.job_title]
        locations_list = [loc.location for loc in locations if loc.location]
        exp_levels = [exp.experience_level for exp in experience_levels if exp.experience_level]
        
        print(f"📊 Filtros obtenidos: {len(areas)} áreas, {len(locations_list)} ubicaciones, {len(exp_levels)} niveles")
        
        filter_options = {
            "areas": areas,
            "locations": locations_list,
            "positions": areas,
            "experienceLevels": exp_levels
        }
        
        return jsonify(filter_options), 200
    
    except Exception as e:
        print(f"❌ Error obteniendo filtros: {str(e)}")
        try:
            print("🔄 Intentando fallback con tabla salaries...")
            from sqlalchemy import distinct
            job_titles = db.session.query(distinct(Salary.job_title)).all()
            locations = db.session.query(distinct(Salary.location)).all()
            experience_levels = db.session.query(distinct(Salary.experience_level)).all()
            
            areas = [title[0] for title in job_titles if title[0]]
            locations_list = [loc[0] for loc in locations if loc[0]]
            exp_levels = [level[0] for level in experience_levels if level[0]]
            
            filter_options = {
                "areas": areas,
                "locations": locations_list,
                "positions": areas,
                "experienceLevels": exp_levels
            }
            return jsonify(filter_options), 200
        except Exception as fallback_error:
            print(f"❌ Fallback también falló: {fallback_error}")
            return jsonify({'message': 'Error al obtener filtros', 'error': str(e)}), 500

# ✅ ENDPOINT CORREGIDO: Calcular salario promedio
@salary_bp.route('/average-salary', methods=['POST'])
def get_average_salary():
    """Calcula el salario promedio basado en los filtros seleccionados."""
    try:
        data = request.get_json()
        print(f"📥 Datos recibidos para cálculo de promedio: {data}")
        
        area_text = data.get('area')
        location_text = data.get('location')
        experience_level_text = data.get('experienceLevel')
        
        print(f"🔍 Filtros extraídos - Area: '{area_text}', Location: '{location_text}', Experience: '{experience_level_text}'")
        
        # ✅ MAPEAR job_title de texto a número (ID)
        # Primero obtenemos todos los job_titles de la tabla JobTitle
        job_titles_from_table = JobTitle.query.all()
        job_title_map = {job.job_title: job.id for job in job_titles_from_table}
        print(f"🔍 Mapa de Job Titles: {job_title_map}")
        
        area_id = None
        if area_text:
            area_id = job_title_map.get(area_text)
            print(f"🔍 Job Title mapeado: '{area_text}' -> {area_id}")
        
        # ✅ MAPEAR location de texto a número (ID)
        locations_from_table = Location.query.all()
        location_map = {loc.location: loc.id for loc in locations_from_table}
        print(f"🔍 Mapa de Locations: {location_map}")
        
        location_id = None
        if location_text:
            location_id = location_map.get(location_text)
            print(f"🔍 Location mapeada: '{location_text}' -> {location_id}")
        
        # ✅ MAPEAR experience level de texto a número
        experience_level_map = {
            'Junior': 1,
            'Semi-Senior': 2, 
            'Senior': 3,
            'Executive': 4
        }
        
        experience_level_number = None
        if experience_level_text:
            experience_level_number = experience_level_map.get(experience_level_text)
            print(f"🔍 Experience Level mapeado: '{experience_level_text}' -> {experience_level_number}")
        
        # DEBUG: Ver qué valores únicos existen en la BD
        print("🔍 VALORES ÚNICOS EN LA BASE DE DATOS:")
        
        # Ver job_titles únicos en Salary (son IDs)
        job_titles_in_salary = db.session.query(Salary.job_title).distinct().all()
        job_titles_list = [title[0] for title in job_titles_in_salary if title[0]]
        print(f"   Job Titles en Salary (IDs): {job_titles_list[:10]}")
        
        # Ver locations únicas en Salary (son IDs)
        locations_in_salary = db.session.query(Salary.location).distinct().all()
        locations_list = [loc[0] for loc in locations_in_salary if loc[0]]
        print(f"   Locations en Salary (IDs): {locations_list[:10]}")
        
        # Ver experience levels únicos
        exp_levels = db.session.query(Salary.experience_level).distinct().all()
        exp_levels_list = [level[0] for level in exp_levels if level[0]]
        print(f"   Experience Levels: {exp_levels_list}")
        
        # Construir la consulta
        query = db.session.query(
            func.avg(Salary.salary_in_usd).label('average_salary'),
            func.count(Salary.id).label('sample_size')
        )
        
        # Aplicar filtros si se proporcionaron (usando IDs)
        conditions_applied = []
        if area_id:
            query = query.filter(Salary.job_title == area_id)
            conditions_applied.append(f"job_title = {area_id}")
        if location_id:
            query = query.filter(Salary.location == location_id)
            conditions_applied.append(f"location = {location_id}")
        if experience_level_number:
            query = query.filter(Salary.experience_level == experience_level_number)
            conditions_applied.append(f"experience_level = {experience_level_number}")
        
        print(f"🔍 Condiciones aplicadas: {conditions_applied}")
        
        # Ejecutar la consulta
        result = query.first()
        
        average_salary = result.average_salary if result.average_salary else 0
        sample_size = result.sample_size if result.sample_size else 0
        
        print(f"📊 Resultado del cálculo: ${average_salary:.2f} USD (muestra: {sample_size} registros)")
        
        return jsonify({
            "averageSalary": round(float(average_salary), 2),
            "sampleSize": sample_size,
            "currency": "USD",
            "filters": {
                "jobTitle": area_text,
                "location": location_text,
                "experienceLevel": experience_level_text
            }
        })
        
    except Exception as e:
        print(f"❌ Error calculando promedio: {str(e)}")
        import traceback
        print(f"❌ Traceback: {traceback.format_exc()}")
        return jsonify({"error": str(e)}), 500
    """Calcula el salario promedio basado en los filtros seleccionados."""
    try:
        data = request.get_json()
        print(f"📥 Datos recibidos para cálculo de promedio: {data}")
        
        area = data.get('area')
        location = data.get('location')
        experience_level_text = data.get('experienceLevel')
        
        print(f"🔍 Filtros extraídos - Area: '{area}', Location: '{location}', Experience: '{experience_level_text}'")
        
        # ✅ MAPEAR experience level de texto a número
        experience_level_map = {
            'Junior': 1,
            'Semi-Senior': 2, 
            'Senior': 3,
            'Executive': 4
        }
        
        experience_level_number = None
        if experience_level_text:
            experience_level_number = experience_level_map.get(experience_level_text)
            print(f"🔍 Experience Level mapeado: '{experience_level_text}' -> {experience_level_number}")
        
        # DEBUG: Ver qué valores únicos existen en la BD
        print("🔍 VALORES ÚNICOS EN LA BASE DE DATOS:")
        
        # Ver job_titles únicos (sin filtro para ver todos)
        job_titles = db.session.query(Salary.job_title).distinct().all()
        job_titles_list = [title[0] for title in job_titles if title[0]]
        print(f"   Job Titles totales: {len(job_titles_list)}")
        print(f"   Algunos Job Titles: {job_titles_list[:10]}")
        
        # Verificar si el job_title existe exactamente
        if area:
            exact_match = area in job_titles_list
            print(f"🔍 ¿'{area}' existe exactamente en job_titles? {exact_match}")
            if not exact_match:
                print(f"🔍 Búsqueda parcial de '{area}':")
                similar_titles = [title for title in job_titles_list if area.lower() in title.lower()]
                print(f"   Títulos similares: {similar_titles}")
        
        # Ver locations únicas (sin filtro para ver todas)
        locations = db.session.query(Salary.location).distinct().all()
        locations_list = [loc[0] for loc in locations if loc[0]]
        print(f"   Locations totales: {len(locations_list)}")
        print(f"   Algunas Locations: {locations_list[:10]}")
        
        # Verificar si la location existe exactamente
        if location:
            exact_match = location in locations_list
            print(f"🔍 ¿'{location}' existe exactamente en locations? {exact_match}")
            if not exact_match:
                print(f"🔍 Búsqueda parcial de '{location}':")
                similar_locations = [loc for loc in locations_list if location.lower() in loc.lower()]
                print(f"   Locations similares: {similar_locations}")
        
        # Ver experience levels únicos
        exp_levels = db.session.query(Salary.experience_level).distinct().all()
        exp_levels_list = [level[0] for level in exp_levels if level[0]]
        print(f"   Experience Levels: {exp_levels_list}")
        
        # Construir la consulta
        query = db.session.query(
            func.avg(Salary.salary_in_usd).label('average_salary'),
            func.count(Salary.id).label('sample_size')
        )
        
        # Aplicar filtros si se proporcionaron
        conditions_applied = []
        if area:
            query = query.filter(Salary.job_title == area)
            conditions_applied.append(f"job_title = '{area}'")
        if location:
            query = query.filter(Salary.location == location)
            conditions_applied.append(f"location = '{location}'")
        if experience_level_number:
            query = query.filter(Salary.experience_level == experience_level_number)
            conditions_applied.append(f"experience_level = {experience_level_number}")
        
        print(f"🔍 Condiciones aplicadas: {conditions_applied}")
        
        # Ejecutar la consulta
        result = query.first()
        
        average_salary = result.average_salary if result.average_salary else 0
        sample_size = result.sample_size if result.sample_size else 0
        
        print(f"📊 Resultado del cálculo: ${average_salary:.2f} USD (muestra: {sample_size} registros)")
        
        return jsonify({
            "averageSalary": round(float(average_salary), 2),
            "sampleSize": sample_size,
            "currency": "USD",
            "filters": {
                "jobTitle": area,
                "location": location,
                "experienceLevel": experience_level_text
            }
        })
        
    except Exception as e:
        print(f"❌ Error calculando promedio: {str(e)}")
        import traceback
        print(f"❌ Traceback: {traceback.format_exc()}")
        return jsonify({"error": str(e)}), 500

@salary_bp.route('/<int:id>', methods=['GET'])
def get_salary(id):
    """Obtiene y devuelve un registro de salario por su ID."""
    try:
        salary = Salary.query.get_or_404(id)
        return jsonify(salary.to_dict()), 200
    except Exception as e:
        return jsonify({'message': 'Salario no encontrado o error', 'error': str(e)}), 404

@salary_bp.route('/<int:id>', methods=['PUT'])
def update_salary(id):
    """Actualiza un registro de salario existente por su ID."""
    salary = Salary.query.get_or_404(id)
    data = request.get_json()
    
    try:
        if 'year' in data:
            salary.year = data['year']
        if 'salary_in_usd' in data:
            salary.salary_in_usd = data['salary_in_usd']
        if 'employment_type' in data:
            salary.employment_type = data['employment_type']
        if 'job_title' in data:
            salary.job_title = data['job_title']
        if 'location' in data:
            salary.location = data['location']
        if 'experience_level' in data:
            salary.experience_level = data['experience_level']
        salary.updated_date = db.func.current_timestamp()

        db.session.commit()
        return jsonify(salary.to_dict()), 200 
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Error al actualizar salario', 'error': str(e)}), 500

@salary_bp.route('/<int:id>', methods=['DELETE'])
def delete_salary(id):
    """Elimina un registro de salario por su ID."""
    salary = Salary.query.get_or_404(id)
    
    try:
        db.session.delete(salary)
        db.session.commit()
        return jsonify({'message': 'Salario eliminado exitosamente'}), 204 
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Error al eliminar salario', 'error': str(e)}), 500