from AspiradorasModel import *
from mesa.visualization.modules import CanvasGrid
from mesa.visualization.ModularVisualization import ModularServer

"""
EQUIPO 2.
Diego Alejandro Juárez Ruiz     A01379566
Edna Jacqueline Zavala Ortega   A01750480
Erick Alberto Bustos Cruz       A01378966
Luis Enrique Zamarripa Marín    A01379918

M1. ACTIVIDAD
Simulación de Aspiradoras Model.
"""

# Representación gráfica de los agentes
def agent_portrayal(agent):
    portrayal = {"Shape": "circle",
                 "Filled": "true",
                 "r":0.6}

    # Distinción entre agente Aspiradora y Basura
    if isinstance(agent, VacuumAgent):
        portrayal["Color"] = "blue"
        portrayal["Layer"] = 0.2
    else:
        portrayal["Color"] = "grey"
        portrayal["Layer"] = 0.5
        portrayal["r"] = 0.4
    return portrayal

# Parámetros de simulación
n = 15
m = 15
numAgents = 8
dirty = 40
timeLimit = 200


# Crear instancia del servidor con el modelo
grid = CanvasGrid(agent_portrayal, n, m, 750, 750)
server = ModularServer(ModelRoomba,
                       [grid],
                       "Model aspiradoras",
                       {"n": n,
                        "m": m,
                        "numAgents": numAgents,
                        "dirty": dirty,
                        "timeLimit": timeLimit})
server.port = 8521 # Puerto default
server.launch()

