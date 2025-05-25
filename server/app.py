#!/usr/bin/env python3

from models import db, Activity, Camper, Signup
from flask_restful import Api, Resource
from flask_migrate import Migrate
from flask import Flask, make_response, jsonify, request
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get(
    "DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

api = Api(app)

@app.route('/')
def home():
    return ''

class Campers(Resource):
    def get(self):
        camper_list = [c.to_dict() for c in Camper.query.all()]
        response = make_response(camper_list, 200,)
        return response
    
    def post(self):
        data = request.get_json()
        try:
            name = data.get('name')
            age = data.get('age')

            new_camper = Camper(name=name, age=age)
            db.session.add(new_camper)
            db.session.commit()
            response_dict = new_camper.to_dict()
            response = make_response(response_dict, 201)
            return response
        except (ValueError, TypeError) as e:
            return {"errors": ["validation errors"]}, 400

api.add_resource(Campers, '/campers')

class CamperByID(Resource):
    def get(self, id):
        camper = Camper.query.filter_by(id=id).first()
        if not camper:
            return {"error": "Camper not found"}, 404
        camper_dict = camper.to_dict(['name', 'age','signups'])
        response = make_response(camper_dict, 200)
        return response
    
    def patch(self, id):
        camper = Camper.query.filter_by(id=id).first()
        if not camper:
            return {"error": "Camper not found"}, 404
        data = request.get_json()
        try:
            if 'name' in data:
                camper.name = data['name']
            if 'age' in data:
                camper.age = data['age']
            db.session.commit()
            camper_dict = camper.to_dict(['name', 'age'])
            response = make_response(camper_dict, 202)
            return response
        except ValueError:
            return {"errors": ["validation errors"]}, 400

api.add_resource(CamperByID, '/campers/<int:id>')

class Activities(Resource):
    def get(self):
        activity_list = [a.to_dict() for a in Activity.query.all()]
        response = make_response(activity_list, 200,)
        return response

api.add_resource(Activities, '/activities')

class ActivityByID(Resource):
    def delete(self, id):
        activity = Activity.query.filter_by(id=id).first()
        if not activity:
            return {"error": "Activity not found"}, 404
        db.session.delete(activity)
        db.session.commit()
        response = make_response("", 204)
        return response

api.add_resource(ActivityByID, '/activities/<int:id>')

class Signups(Resource):
    def post(self):
        data = request.get_json()
        try:
            camper_id = data.get('camper_id')
            activity_id = data.get('activity_id')
            time = data.get('time')

            new_signup= Signup(camper_id=camper_id, activity_id=activity_id, time=time)
            db.session.add(new_signup)
            db.session.commit()
            response_dict = new_signup.to_dict()
            response = make_response(response_dict, 201)
            return response
        except (ValueError, TypeError) as e:
            return {"errors": ["validation errors"]}, 400

api.add_resource(Signups, '/signups')

if __name__ == '__main__':
    app.run(port=5555, debug=True)
