from app import db

class Salary(db.Model):
    __tablename__ = 'salaries'
    id = db.Column(db.Integer, primary_key=True)
    year = db.Column(db.String(100))
    salary_in_usd = db.Column(db.Integer)
    employment_type = db.Column(db.Integer, db.ForeignKey('employment_types.id'))
    job_title = db.Column(db.Integer, db.ForeignKey('job_titles.id'))
    location = db.Column(db.Integer, db.ForeignKey('locations.id'))
    experience_level = db.Column(db.Integer, db.ForeignKey('experience_levels.id'))
    created_date = db.Column(db.DateTime)
    updated_date = db.Column(db.DateTime)

    employment_type_ref = db.relationship('EmploymentType', backref='salaries', lazy=True)
    job_title_type_ref = db.relationship('JobTitle', backref='salaries', lazy=True)
    location_type_ref = db.relationship('Location', backref='salaries', lazy=True)
    experience_level_type_ref = db.relationship('ExperienceLevel', backref='salaries', lazy=True)

    def to_dict(self):
        employment_type = self.employment_type_ref.employment_type if self.employment_type_ref else None
        job_title = self.job_title_type_ref.job_title if self.job_title_type_ref else None
        location = self.location_type_ref.location if self.location_type_ref else None
        experience_level = self.experience_level_type_ref.experience_level if self.experience_level_type_ref else None


        return {
            'id': self.id,
            'year': self.year,
            'salary_in_usd': self.salary_in_usd,
            'employment_type': employment_type,
            'job_title': job_title,
            'location': location,
            'experience_level': experience_level,
            'created_date': self.created_date.isoformat() if self.created_date else None,
            'updated_date': self.updated_date.isoformat() if self.updated_date else None
        }
