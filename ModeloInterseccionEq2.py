from mesa import Agent, Model, model
from mesa.time import RandomActivation
from mesa.space import Grid, SingleGrid
from mesa.space import MultiGrid
import random

class AgentCar(Agent):
    def __init__(self, unique_id, model, origen, orientation):
        super().__init__(unique_id, model)
        self.previous = "Normal"
        self.curr = "Normal"
        self.origin = origen
        self.orientation = orientation
        self.destination = self.setDestination(model)

    # Escoger de manera aleatoria un destino para el auto, exluyendo aquel que
    # Involucra una vuelta en U    
    def setDestination(self, model):
        exclude = {(11,0):(10,0),(21,10):(21,11),(11,21):(10,21),(0,10):(0,11)}
        d = self.random.choice(model.possibleDestinations)
        while exclude.get(self.origin) == d:
             d = self.random.choice(model.possibleDestinations)
        return d
    
    def moveCar(self, cell):
        # Aquí se mueve el auto
        self.model.grid.move_agent(self, cell)
        if self.orientation == "Arriba" or self.orientation == "Abajo":
            if self.pos[1] == self.destination[1]:
                if self.pos[0] < self.destination[0]:
                    self.orientation = "Derecha"
                elif self.pos[0] > self.destination[0]:
                    self.orientation = "Izquierda"
        elif self.orientation == "Izquierda" or self.orientation == "Derecha":
            if self.pos[0] == self.destination[0]:
                if self.pos[1] < self.destination[1]:
                    self.orientation = "Arriba"
                elif self.pos[1] > self.destination[1]:
                    self.orientation = "Abajo"
    
    def checkMove(self):
        # Avanza y luego checa si debe rotar
        nextPos = self.getNextPos()
        listAgents = self.model.grid.get_cell_list_contents(nextPos)
        
        for a in listAgents:
            if isinstance(a,AgentCar):
                return
        if(listAgents):
            self.previous = self.curr
            self.curr = listAgents[0].typeCell
        
        self.moveCar(nextPos)
    
    def getNextPos(self):
        if(self.orientation == "Arriba"):
            position = list(self.pos)
            position[1] += 1
            return tuple(position)
        elif (self.orientation == "Abajo"):
            position = list(self.pos)
            position[1] -= 1
            return tuple(position)
        elif (self.orientation == "Izquierda"):
            position = list(self.pos)
            position[0] -= 1
            return tuple(position)
        elif (self.orientation == "Derecha"):
            position = list(self.pos)
            position[0] += 1
            return tuple(position)

    # def notifytrafficLight(self):
    #     if out:
    #         sayBye()
    
    def step(self):
        # Si tengo coche adelante, no avanzo
        
        # Si estoy un una celda de aviso y mi prev es una normal 
        # Comunicarme con semáforo

        # Si estoy en una celda de semáforo y mi prev es una de aviso
        # Detenerse
        
        # Si estoy en una celda de semáforo y mi prev es una celda de semáforo
            # Si es verde el sem, intento avanzar
            # Si es rojo no me muevo
        
        # Si estoy en una celda de intersección y mi prev es una celda de semáforo
        # Llamar a move y restar a cars de semáforo
        
        # Si estoy en una celda de intersección y mi prev es una celda de intersección
        # moverme

        # Solo intentar mover el coche
        if(self.previous == "Normal" and self.curr == "Aviso"):
            # self.notifyTrafficLight
            pass
        elif(self.previous == "Aviso" and self.curr =="Semaforo"):
            pass

        self.checkMove()
        

    

class AgentCell(Agent):
    def __init__(self, unique_id, model, typeCell):
        super().__init__(unique_id, model)
        self.typeCell = typeCell
    
    def step(self):
        pass
        
class AgentObstacle(Agent):
    def __init__(self,unique_id,model):
        super().__init__(unique_id, model)
    
    def step(self):
        pass
    

class AgentTrafficLight(Agent):
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.carCount = 0
        self.colors = ["yellow","red","green"]
        self.color = "yellow"
        self.timeGreen = 30
    
    # def changeColor(self):
    #     if turn:
    #         change green
    #     elif not turn:
    #         change red
    #     elif turn list == empty:
    #         change yellow

    # def askTurn(self):
    #     if carCount != 0:
    #         add id to the turn list
            
    
    # def endTurn(self):
    #     remove turn id from turn list

    # def takeTurn(self):
    #     change color to green
    
    def step(self):
        pass
        


class ModelStreet(Model):
    def __init__(self,nCars, width, length): # Matriz de 22 x 22    
        # Número de Autos
        self.numCars = nCars
        self.uniqueIDs = 1
        # Número de Semáforos
        self.numTrafficLights = 4
        # Crear grid
        self.grid = MultiGrid(width,length,False)
        # Queue de turnos
        self.turns = []
        # Coordenadas de las entradas a la intersección
        self.possibleStartingPoints = [(11,0),(21,11),(0,10),(10,21)]
        # Coordenadas de las salidas de la intersección
        self.possibleDestinations = [(10,0),(21,10),(11,21),(0,11)]
        self.schedule = RandomActivation(self)
        self.running = True
        
        
        # Construir paredes
        for i in range(0,22):
            # Construir paredes verticales
            # En [9,0-9 y 12-21] y [12,0-9 y 12-21]
            if not(i > 9 and i < 12):
                a = AgentObstacle(self.uniqueIDs,self)
                self.uniqueIDs += 1
                b = AgentObstacle(self.uniqueIDs,self)
                self.uniqueIDs += 1
                self.schedule.add(a)
                self.schedule.add(b)
                self.grid.place_agent(a,(9,i))
                self.grid.place_agent(b,(12,i))
            # Construir paredes horizontales
            # En [0-8 y 13-21, 9] y [0-8 y 13-21, 12]
            if not(i > 8 and i < 13):
                a = AgentObstacle(self.uniqueIDs,self)
                self.uniqueIDs += 1
                b = AgentObstacle(self.uniqueIDs,self)
                self.uniqueIDs += 1
                self.schedule.add(a)
                self.schedule.add(b)
                self.grid.place_agent(a,(i,9))
                self.grid.place_agent(b,(i,12))

        # Coordenadas de celdas aviso (8,10) (11,8) (13,11) (10,13)
        # Colocar celdas de aviso
        cellA1 = AgentCell(self.uniqueIDs, self, "Aviso")
        self.uniqueIDs += 1
        cellA2 = AgentCell(self.uniqueIDs, self, "Aviso")
        self.uniqueIDs += 1
        cellA3 = AgentCell(self.uniqueIDs, self, "Aviso")
        self.uniqueIDs += 1
        cellA4 = AgentCell(self.uniqueIDs, self, "Aviso")
        self.uniqueIDs += 1
        self.schedule.add(cellA1)
        self.schedule.add(cellA2)
        self.schedule.add(cellA3)
        self.schedule.add(cellA4)
        self.grid.place_agent(cellA1, (8,10))
        self.grid.place_agent(cellA2, (11,8))
        self.grid.place_agent(cellA3, (13,11))
        self.grid.place_agent(cellA4, (10,13))
        
        
        
        # Coordenadas de celdas de semáforo (9,10) (10,12) (11,9) (12,11)
        # Colocar celdas de semáforo
        cellS1 = AgentCell(self.uniqueIDs, self, "Semaforo")
        self.uniqueIDs += 1
        cellS2 = AgentCell(self.uniqueIDs, self, "Semaforo")
        self.uniqueIDs += 1
        cellS3 = AgentCell(self.uniqueIDs, self, "Semaforo")
        self.uniqueIDs += 1
        cellS4 = AgentCell(self.uniqueIDs, self, "Semaforo")
        self.uniqueIDs += 1
        self.schedule.add(cellS1)
        self.schedule.add(cellS2)
        self.schedule.add(cellS3)
        self.schedule.add(cellS4)
        self.grid.place_agent(cellS1, (9,10))
        self.grid.place_agent(cellS2, (10,12))
        self.grid.place_agent(cellS3, (11,9))
        self.grid.place_agent(cellS4, (12,11))
        
        # Coordenadas intersección (10,10) (11,10) (10,11) (11,11)
        # Colocar celdas de intersección
        cellI1 = AgentCell(self.uniqueIDs, self, "Interseccion")
        self.uniqueIDs += 1
        cellI2 = AgentCell(self.uniqueIDs, self, "Interseccion")
        self.uniqueIDs += 1
        cellI3 = AgentCell(self.uniqueIDs, self, "Interseccion")
        self.uniqueIDs += 1
        cellI4 = AgentCell(self.uniqueIDs, self, "Interseccion")
        self.uniqueIDs += 1
        self.schedule.add(cellI1)
        self.schedule.add(cellI2)
        self.schedule.add(cellI3)
        self.schedule.add(cellI4)
        self.grid.place_agent(cellI1, (10,10))
        self.grid.place_agent(cellI2, (11,10))
        self.grid.place_agent(cellI3, (10,11))
        self.grid.place_agent(cellI4, (11,11))     



    def addAgents(self):
        """
        Para cada entrada a la intersección,
        checar si la celda está disponible,
        elegir de manera random entre True/False
        para decidir si agregar un nuevo agente
        """
        boolList = [self.random.choice([True, False]), self.random.choice([True, False]), self.random.choice([True, False]), self.random.choice([True, False])]

        if(boolList[0]):
            cell = self.grid.get_cell_list_contents((11,0))
            if(not cell):
                b = AgentCar(self.uniqueIDs, self, (11,0), "Arriba")
                self.uniqueIDs += 1
                self.schedule.add(b)
                self.grid.place_agent(b, (11,0))
        
        if(boolList[1]):
            cell = self.grid.get_cell_list_contents((21,11))
            if(not cell):
                b = AgentCar(self.uniqueIDs, self, (21,11), "Izquierda")
                self.uniqueIDs += 1
                self.schedule.add(b)
                self.grid.place_agent(b, (21,11))

        if(boolList[2]):
            cell = self.grid.get_cell_list_contents((0,10))
            if(not cell):
                b = AgentCar(self.uniqueIDs, self, (0,10), "Derecha")
                self.uniqueIDs += 1
                self.schedule.add(b)
                self.grid.place_agent(b, (0,10))
        
        if(boolList[3]):
            cell = self.grid.get_cell_list_contents((10,21))
            if(not cell):
                b = AgentCar(self.uniqueIDs, self, (10,21), "Abajo")
                self.uniqueIDs += 1
                self.schedule.add(b)
                self.grid.place_agent(b, (10,21))
        
    def step(self):
        self.addAgents()
        self.schedule.step()