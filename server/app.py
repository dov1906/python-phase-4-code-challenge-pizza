#!/usr/bin/env python3
from models import db, Restaurant, RestaurantPizza, Pizza
from flask_migrate import Migrate
from flask import Flask, request, jsonify, make_response
from flask_restful import Api, Resource
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get("DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.json.compact = False

migrate = Migrate(app, db)
db.init_app(app)
api = Api(app)

@app.route("/")
def index():
    return "<h1>Code challenge</h1>"

@app.route("/restaurants", methods=["GET"])
def get_restaurants():
    restaurants = Restaurant.query.all()
    return jsonify([restaurant.to_dict() for restaurant in restaurants])

@app.route("/restaurants/<int:id>", methods=["GET", "DELETE"])
def restaurant_detail(id):
    restaurant = Restaurant.query.get(id)
    if not restaurant:
        return make_response(jsonify({"error": "Restaurant not found"}), 404)

    if request.method == "DELETE":
        db.session.delete(restaurant)
        db.session.commit()
        return make_response("", 204)

    return jsonify(restaurant.to_dict_with_pizzas())

@app.route("/pizzas", methods=["GET"])
def get_pizzas():
    pizzas = Pizza.query.all()
    return jsonify([pizza.to_dict() for pizza in pizzas])

@app.route("/restaurant_pizzas", methods=["POST"])
def create_restaurant_pizza():
    data = request.get_json()
    try:
        # Validate price
        price = data.get("price")
        if not (1 <= price <= 30):
            raise ValueError("Price must be between 1 and 30")

        restaurant_pizza = RestaurantPizza(
            price=price,
            restaurant_id=data["restaurant_id"],
            pizza_id=data["pizza_id"]
        )
        db.session.add(restaurant_pizza)
        db.session.commit()

        # Include pizza and restaurant details in the response
        response_data = restaurant_pizza.to_dict()
        response_data["pizza"] = restaurant_pizza.pizza.to_dict()
        response_data["restaurant"] = restaurant_pizza.restaurant.to_dict()
        return jsonify(response_data), 201

    except ValueError:
        return make_response(jsonify({"errors": ["validation errors"]}), 400)
    except Exception as e:
        return make_response(jsonify({"error": str(e)}), 400)

if __name__ == "__main__":
    app.run(port=5555, debug=True)
