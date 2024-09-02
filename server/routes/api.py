import os
from functools import wraps
from flask import Blueprint, jsonify, request

api = Blueprint('api', __name__)


def require_api_key(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get('API_KEY')
        API_KEY = os.getenv('DEFAULT_API_KEY')
        if api_key != API_KEY:
            return jsonify({
                "status": "error",
                "message": "Unauthorized"
            }), 401
        return f(*args, **kwargs)
    return decorated_function


@api.route('/products/overview')
@require_api_key
def get_all_product_overview():
    data = {
        "status": "success",
        "message": "Fetched all product overview.",
        "data": {
            "products": [
                {
                    "model": "Model 1",
                    "series": "Series A",
                    "productType": "AC",
                    "designCompletionDate": "2023-05-01T17:20+08:00"
                },
            ],
            "total": 2
        }
    }
    return jsonify(data), 200


@api.route('/products/overview/series/<sery_name>')
@require_api_key
def get_product_overview_by_sery_name(sery_name):
    data = {
        "status": "success",
        "message": f"Fetched product overview for series: {sery_name}",
        "data": {
            "products": [
                {
                    "model": "Model 1",
                    "series": sery_name,
                    "productType": "AC",
                    "designCompletionDate": "2023-05-01T17:20+08:00"
                },
            ],
            "total": 2
        }
    }
    return jsonify(data), 200


@api.route('/products/overview/models/<model_name>')
@require_api_key
def get_product_overview_by_model_name(model_name):
    data = {
        "status": "success",
        "message": f"Fetched product overview for model: {model_name}",
        "data": {
            "products": [
                {
                    "model": model_name,
                    "series": "Series C",
                    "productType": "AC",
                    "designCompletionDate": "2023-08-01T17:20+08:00"
                }
            ],
            "total": 1
        }
    }
    return jsonify(data), 200
