from ModeloInterseccionEq2 import *
from mesa.visualization.modules import CanvasGrid
from mesa.visualization.ModularVisualization import ModularServer

def agent_portrayal(agent):
    portrayal = {"Shape": "circle",
                 "Filled": "true",
                 "Layer": 1,
                 "Color": "red",
                 "r": 0.5}
                 
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
            portrayal["r"] = 0.5

    if (isinstance(agent, AgentObstacle)):
        portrayal["Color"] = "#191970" # blue HTML
        portrayal["Layer"] = 1
        portrayal["r"] = 0.5
        
    if (isinstance(agent,AgentCar)):
        portrayal["Color"] = "red"
        portrayal["Layer"] = 10
        portrayal["r"] = 0.5      
    return portrayal

grid = CanvasGrid(agent_portrayal, 22, 22, 660, 660)
server = ModularServer(ModelStreet,
                       [grid],
                       "ModelStreet",
                       {"nCars":3, "width":22, "length":22})
server.port = 8521 # The default
server.launch()

