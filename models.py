from datetime import datetime
from extensions import db

class Plant(db.Model): 
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    location = db.Column(db.String(50), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.now())

class PlantImage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    plant_id = db.Column(db.Integer, db.ForeignKey('plant.id'), nullable=False)
    image_path = db.Column(db.String(200), nullable=False)
    captured_at = db.Column(db.DateTime, default=datetime.now())

    plant = db.relationship('Plant', backref=db.backref('images', lazy=True))