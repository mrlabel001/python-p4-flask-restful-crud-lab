#!/usr/bin/env python3

from flask import Flask, jsonify, request, make_response
from flask_migrate import Migrate
from flask_restful import Api, Resource

from models import db, Plant

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///plants.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)
db.init_app(app)

api = Api(app)


class Plants(Resource):

    def get(self):
        plants = [plant.to_dict() for plant in Plant.query.all()]
        return make_response(jsonify(plants), 200)

    def post(self):
        data = request.get_json()

        new_plant = Plant(
            name=data['name'],
            image=data['image'],
            price=data['price'],
        )

        db.session.add(new_plant)
        db.session.commit()

        return make_response(new_plant.to_dict(), 201)


api.add_resource(Plants, '/plants')


class PlantByID(Resource):

    def get(self, id):
        plant = Plant.query.filter_by(id=id).first().to_dict()
        return make_response(jsonify(plant), 200)


api.add_resource(PlantByID, '/plants/<int:id>')

@app.route('/plants/<int:id>', methods=['PATCH'])
def update_plant(id):
    # Retrieve the plant by id
    plant = db.session.get(Plant, id)

    # Check if the plant exists
    if not plant:
        return jsonify({'error': 'Plant not found'}), 404

    # Update the plant attributes based on the request body
    data = request.json
    if 'is_in_stock' in data:
        plant.is_in_stock = data['is_in_stock']

    # Commit the changes to the database
    db.session.commit()

    # Return the updated plant as JSON response
    return jsonify({
        'id': plant.id,
        'name': plant.name,
        'image': plant.image,
        'price': plant.price,
        'is_in_stock': plant.is_in_stock
    })

@app.route('/plants/<int:id>', methods=['DELETE'])
def delete_plant(id):
    plant = Plant.query.get(id)

    if not plant:
        return jsonify({'error': 'Plant not found'}), 404

    db.session.delete(plant)
    db.session.commit()

    return '', 204


if __name__ == '__main__':
    app.run(port=5555, debug=True)
