from flask import Flask, request, jsonify
from flask_cors import CORS
from google.cloud import logging
from dataclasses import dataclass, fields
import redis
import json
import os
import signal
import sys

app = Flask(__name__)

pool = redis.ConnectionPool(
    host=os.environ.get('REDIS_HOST', '10.223.94.187'),
    port=os.environ.get('REDIS_PORT', 6379),
    decode_responses=True,
)
db = redis.Redis(connection_pool=pool)


@dataclass
class Product:
    product_id: int
    name: str
    description: str
    price: float
    categories: list[str]

product_fields = [field.name for field in fields(Product)]


@app.route('/cart/<int:user_id>', methods=['GET', 'POST', 'DELETE'])
def cart(user_id):
    if request.method == 'GET':
        items = db.lrange(user_id, 0, -1)
        return jsonify([json.loads(s) for s in items]), 200

    elif request.method == 'POST':
        product = request.get_json()
        if not product or set(product) != set(product_fields):
            return jsonify({"error": "Invalid data"}), 400

        db.lpush(user_id, json.dumps(product))
        return jsonify(product), 201

    elif request.method == 'DELETE':
        db.delete(user_id)
        return '', 204
        
    else:
        return jsonify({"error": "Invalid operation"}), 400


def disconnect_redis(signum, frame):
    print("Received SIGTERM/SIGINT. Closing Redis connection pool...", flush=True)
    pool.disconnect()
    print("Redis pool closed successfully. Exiting process.", flush=True)
    sys.exit(0)



if __name__ == '__main__':
    signal.signal(signal.SIGTERM, disconnect_redis)
    signal.signal(signal.SIGINT, disconnect_redis)

    CORS(app, origins=[
        os.environ.get('CORS_LOCALHOST', 'http://localhost:5173'),
        os.environ.get('CORS_URL', '')
    ])
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 8080)), debug=False)