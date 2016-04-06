from flask import Flask
from flask.json import dumps, jsonify
from models import Category, Restaurant, Location

API_ROOT = '/api'
API_URLS = {
    'category_url': '/api/category',
    'location_url': '/api/location',
    'restaurant_url': '/api/restaurant',
}

def add_api_routes(route):
    @route('/api')
    def api_root():
        "List all of our url end points"
        return jsonify(urls=API_URLS)

    # Restaurants
    @route('/api/restaurant')
    def api_list_restaurants():
        "List all of our restaurants"
        return jsonify(restaurantlist={i.id : i.__dict__ for i in Restaurant.query.all()})

    @route('/api/restaurant/<int:id>')
    def api_list_restaurants(id):
        "List a specific restaurant by specifying an id"
        return dumps(Restaurant.query.get(id).__dict__)

    @route('/api/restaurant?q=<filterstring>')
    def api_list_restaurants(filterstring):
        "List a specific restaurant by specifying an id"
        # TODO Parse filterstring and cop some info
        return dumps(Restaurant.query.filter_by(name="TODO parse the filterstring").__dict__)
