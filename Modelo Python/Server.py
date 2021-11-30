'''
TC2008B Modelacion de sistemas multiagentes con graficas computacionales (Gpo 301)
EQUIPO 2
Diego Alejandro Juarez Ruiz     A01379566
Edna Jacqueline Zavala Ortega   A01750480
Erick Alberto Bustos Cruz       A01378966
Luis Enrique Zamarripa Marin    A01379918

Servidor para establecer comunicacion entre IBM Cloud, modelo de MESA y Unity

'''

# Importaciones
from flask import Flask, render_template, request, jsonify
import json, logging, os, atexit
from ModeloInterseccionEq2 import *

# Modelo y app de Flask
app = Flask(__name__, static_url_path='')
model = ModelStreet(22,22)

def positionsToJSON(ps):
    '''
    Recibe un vector ps, toma los elementos que hay dentro del mismo
    y los ingresa dentro de un JSON, el cual regresa.
    '''
    posDICT = []
    for p in range(len(ps)):
        if(p > 3):
            pos = {
                "x" : ps[p][0],
                "z" : ps[p][1],
                "y" : ps[p][2],
                "orientation": ps[p][3],
                "id": ps[p][4],
                "destinationx": ps[p][5][0],
                "destinationy": ps[p][5][1]
            }
        else:
            pos = {
                "color": ps[p]
            }
        posDICT.append(pos)
        
    return json.dumps(posDICT)

port = int(os.getenv('PORT', 8000)) # Puerto

@app.route('/')
def root():
    '''
    Mensaje de bienvenda con ruta raiz
    '''
    return jsonify([{"message":"Welcome to IBM Cloud from Team 2 we hope you like our work!"}])


@app.route('/restart',methods= ['GET','POST'])
def restart():
    '''
    Ruta para reiniciar el modelo
    '''
    global model
    model = ModelStreet(22,22)
    return jsonify([{"message":"Restablecido"}])

@app.route('/simulation',methods= ['GET','POST'])
def multiagentes():
    '''
    Ruta para recibir la informacion del modelo en formato JSON
    '''
    positions = model.step()
    return positionsToJSON(positions)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=port, debug=True) #Inicializacion