from flask import Flask, render_template, request, jsonify
import json, logging, os, atexit
from ModeloInterseccionEq2 import *

app = Flask(__name__, static_url_path='')
model = ModelStreet(22,22)

def positionsToJSON(ps):
    posDICT = []
    for p in ps:
        pos = {
            "x" : p[0],
            "z" : p[1],
            "y" : p[2]
        }
        posDICT.append(pos)
    return json.dumps(posDICT)

port = int(os.getenv('PORT', 8000))

@app.route('/')
def root():
    return jsonify([{"message":"Hello World from IBM Cloud!"}])

@app.route('/multiagentes')
def multiagentes():
    positions = model.step()
    return positionsToJSON(positions)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=port, debug=True)