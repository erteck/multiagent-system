'''
TC2008B Modelacion de sistemas multiagentes con graficas computacionales (Gpo 301)
EQUIPO 2
Diego Alejandro Juarez Ruiz     A01379566
Edna Jacqueline Zavala Ortega   A01750480
Erick Alberto Bustos Cruz       A01378966
Luis Enrique Zamarripa Marin    A01379918

Visualizacion del modelo de una interseccion con semaforos inteligentes.

'''

# Importaciones
from ModeloInterseccionEq2 import *
from mesa.visualization.modules import CanvasGrid
from mesa.visualization.ModularVisualization import ModularServer

def agent_portrayal(agent):
    # Apariencia por defecto de los agentes
    portrayal = {"Shape": "circle",
                 "Filled": "true",
                 "Layer": 1,
                 "Color": "white",
                 "r": 0.5}
    '''
    # Visualizacion de las celdas auxiliares            
    if (isinstance(agent, AgentCell)):
        if (agent.typeCell == "Aviso"):
            portrayal["Color"] = "#6A5ACD" # purple
            portrayal["Layer"] = 1
            portrayal["r"] = 0.5
        elif (agent.typeCell == "Semaforo"):
            portrayal["Color"] = "#B22222" #red
            portrayal["Layer"] = 1
            portrayal["r"] = 0.5
        elif (agent.typeCell == "Interseccion"):
            portrayal["Color"] = "orange" 
            portrayal["Layer"] = 1
            portrayal["r"] = 0.5
        elif (agent.typeCell == "Normal"):
            portrayal["Color"] = "yellow" 
            portrayal["Layer"] = 1
            portrayal["r"] = 0.5'''

    # Visualizacion de los agentes obstaculo (acera)
    if (isinstance(agent, AgentObstacle)):
        portrayal["Color"] = "#191970" # blue HTML
        portrayal["Layer"] = 1
        portrayal["r"] = 0.1
    
    # Visualizacion de los agentes automoviles
    if (isinstance(agent,AgentCar)):
        portrayal["Color"] = agent.color
        portrayal["Layer"] = 10
        portrayal["r"] = 0.4    
        
    # Visualizacion de los agentes semaforo
    if(isinstance(agent,AgentTrafficLight)):
        if agent.color == "Amarillo":
            portrayal["Color"] = "yellow"
        elif agent.color == "Rojo":
            portrayal["Color"] = "red"
        elif agent.color == "Verde":
            portrayal["Color"] = "green"
        portrayal["Layer"] = 10
        portrayal["r"] = 0.4
    return portrayal

# Configuracion del grid
grid = CanvasGrid(agent_portrayal, 22, 22, 880, 880)
server = ModularServer(ModelStreet,
                       [grid],
                       "ModelStreet",
                       {"width":22, "length":22})
server.port = 8521 # The default
server.launch()

