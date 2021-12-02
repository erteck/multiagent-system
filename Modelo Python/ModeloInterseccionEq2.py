'''
TC2008B Modelacion de sistemas multiagentes con graficas computacionales (Gpo 301)
EQUIPO 2
Diego Alejandro Juarez Ruiz     A01379566
Edna Jacqueline Zavala Ortega   A01750480
Erick Alberto Bustos Cruz       A01378966
Luis Enrique Zamarripa Marin    A01379918

Modelo de una interseccion con semaforos inteligentes.

'''

# Importaciones
from mesa import Agent, Model, model
from mesa.time import RandomActivation
from mesa.space import Grid, SingleGrid
from mesa.space import MultiGrid
from collections import deque
import random
 

# Agente Automovil
class AgentCar(Agent):

    def __init__(self, unique_id, model, origen, orientation, trafficLight,color="black"):
        '''
        Inicializacion del agente Automovil. Se pasan como argumentos el ID, el modelo, el origen,
        la orientacion inicial, el semaforo que le corresponde y su color. 
        '''
        super().__init__(unique_id, model)
        self.previous = "Normal"
        self.curr = "Normal"
        self.origin = origen
        self.orientation = orientation
        self.trafficLight = trafficLight
        self.destination = self.setDestination(model)
        self.color = color
   
    def setDestination(self, model):
        '''
        Metodo seleccionar destino, este modelo excluye los origenes de destino para
        que no pueda dar vuelta en la calle que va, para esto utiliza el diccionario.
        Escoge de manera aleatoria el destino.
        '''
        exclude = {(11,0):(10,0),(21,11):(21,10),(10,21):(11,21),(0,10):(0,11)} # Diccionario de posibles salidas
        d = self.random.choice(model.possibleDestinations)
        while exclude.get(self.origin) == d:
             d = self.random.choice(model.possibleDestinations)
        return d
    
    def moveCar(self, cell):
        '''
        Metodo para mover el automovil. Recibe la celda de la nueva posicion como argumento
        Cambia la orientacion del automovil si es que es necesario
        '''
        # Aqui se mueve el auto
        self.model.grid.move_agent(self, cell)

        # Cambio de orientacion cuando una coordenada de la posicion llega a su destino
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
        '''
        Metodo que determina a que celda debe avanzar el auto y el si el auto puede avanzar a dicha celda.
        En ambos casos actualiza el tipo de celda en la que esta presente el auto.
        '''
        
        # Determinar la siguiente posicion
        nextPos = self.getNextPos()
        
        # Obtener los agentes presentes en dicha celda
        listAgents = self.model.grid.get_cell_list_contents(nextPos)
        
        # Si alguno de los agentes es otro auto no moverse 
        for a in listAgents:
            if isinstance(a, AgentCar):
                # Actualizar el tipo de celda en la que estoy y mi celda previa
                listAgents = self.model.grid.get_cell_list_contents(self.pos)
                for a in listAgents:
                    if isinstance(a, AgentCell):
                        self.previous = self.curr
                        self.curr = a.typeCell
                return
        
        # Si el paso esta libre, avanzar
        self.moveCar(nextPos)
        
        # Ya que el auto se movio actualizar el tipo de celda en la que estoy
        listAgents = self.model.grid.get_cell_list_contents(self.pos)
        for a in listAgents:
            if isinstance(a, AgentCell):
                self.previous = self.curr
                self.curr = a.typeCell
    
    def getNextPos(self):
        '''
        Metodo que permite incrementar o decrementar la coordenada correcta dependiendo
        de la orientacion que tendra el automovil.
        '''
        # Si el automovil se movera hacia arriba, incrementar uno en y en la coordenada actual
        if(self.orientation == "Arriba"):
            position = list(self.pos)
            position[1] += 1
            return tuple(position)
        # Si el automovil se movera hacia abajo, decrementar uno en y en la coordenada actual
        elif (self.orientation == "Abajo"):
            position = list(self.pos)
            position[1] -= 1
            return tuple(position)
        # Si el automovil se movera hacia la izquierda, decrementar uno en x en la coordenada actual
        elif (self.orientation == "Izquierda"):
            position = list(self.pos)
            position[0] -= 1
            return tuple(position)
        # Si el automovil se movera hacia la derecha, incrementar uno en x en la coordenada actual
        elif (self.orientation == "Derecha"):
            position = list(self.pos)
            position[0] += 1
            return tuple(position)

    def notifyTrafficLight(self):
        '''
        Metodo para notificar a un semaforo que ha llegado un automovil. Incrementa el contador
        de autos del semaforo
        '''
        listAgents = self.model.grid.get_cell_list_contents(self.pos)

        for a in listAgents:

            if isinstance(a, AgentCell):
                a.trafficLight.carArrived()
                a.trafficLight.carCount += 1
                return

    def findTrafficLight(self):
        '''
        Este metodo realiza una busqueda a la celda donde se encuentre el auto
        La celda regresa el atributo semaforo que contiene.
        '''
        listAgents = self.model.grid.get_cell_list_contents(self.pos)

        for a in listAgents:

            if isinstance(a, AgentCell):
                return a.trafficLight
    
    def delete(self):
        '''
        Este metodo elimina el agente automovil una vez que ya llego a su posicion
        destino. Se elimina del schedule y del grid
        '''
        if self.pos in [(10,0),(21,10),(11,21),(0,11)]:
            self.model.grid.remove_agent(self)
            self.model.schedule.remove(self)
            return True
        
    def step(self):
        '''
        Metodo step del automovil, se realiza cada paso del schedule
        '''
        # Si se ha eliminado al automovil, no se corre lo demas
        if self.delete():
            return

        # Si la posicion del automovil es su destino, se elimina y retorna
        if(self.pos == self.destination):
            self.model.grid.remove_agent(self)
            self.model.schedule.remove(self)
            return
        
        # Evita que el auto se pueda mover dos veces en el mismo step
        if not(self.previous == "Semaforo" and self.curr == "Semaforo"):
            self.checkMove()
        
        
        # Arq (1). Si tengo coche adelante, no avanzo (implicito)
        
        # Arq (2). Si estoy en una celda de Aviso y mi prev es normal 
        # Comunicarme con semaforo y avisarle que ya llegue
        if(self.previous == "Normal" and self.curr == "Aviso"):
            self.notifyTrafficLight()
            
        # Arq (3). Si estoy en una celda de semaforo y mi prev es una de aviso
        # Detenerse y cambiar la celda actual y previa
        elif(self.previous == "Aviso" and self.curr == "Semaforo"):
            self.previous = self.curr
            self.curr = "Semaforo"
            
            
        # Arq (4). Si estoy en una celda de aviso, y mi prev es de aviso
        # El auto se pregunta si su semaforo tiene un turno, si no, le vulve a avisar que se encuentra esperando
        elif(self.previous == "Aviso" and self.curr == "Aviso"):
            if(self.trafficLight.unique_id not in AgentTrafficLight.turns):
                AgentTrafficLight.turns.append(self.trafficLight.unique_id)

        
        # Si estoy en una celda de semaforo y mi prev es una celda de semaforo
        # Checar el color del semaforo (detenerse y moverse)
        elif(self.previous == "Semaforo" and self.curr == "Semaforo"):
            tl = self.findTrafficLight()
            # Arq (5). Si es verde el semaforo, intento avanzar
            if tl.color == "Verde":
                self.checkMove()
                return
            # Arq (6). Si es rojo, no me muevo
            elif tl.color == "Rojo":
                return

        # Arq (7). Si estoy en una celda normal y sali de la celda de interseccion
        # Se le resta al contador de autos del semaforo
        elif(self.curr == "Normal" and self.previous == "Interseccion"):
            self.trafficLight.carCount -= 1
            self.model.trafficFlow += 1

  
# Agente Celda en el Grid
class AgentCell(Agent):
    def __init__(self, unique_id, model, typeCell,trafficLight=None):
        '''
        Inicializacion de un Agente que representa a una celda.
        Se pasan como argumentos el ID, el modelo, el origen, el tipo de celda
        y en caso de que la celda este relacionada con un semaforo, el Agente
        correspondiente a dicho semaforo.
        '''
        super().__init__(unique_id, model)
        self.typeCell = typeCell
        self.trafficLight = trafficLight
    
    def step(self):
        pass
   
# Agente obstaculo     
class AgentObstacle(Agent):
    
    def __init__(self,unique_id,model):
        '''
        Inicializacion del obstaculo
        '''
        super().__init__(unique_id, model)
    
    def step(self):
        pass
    
# Agente semaforo
class AgentTrafficLight(Agent):

    turns = deque() # Pizaron 

    def __init__(self, unique_id, model):
        '''
        Inicializacion de un agente que representa a un semaforo.
        Recibe su id unico y el modelo al que pertenece.
        '''
        super().__init__(unique_id, model)
        # Determinar si hay un auto esperando
        self.carCount = 0
        # Semaforos inicializados en amarillo
        self.color = "Amarillo"
        # Es mi turno
        self.isMyTurn = False
        # Tiempo para estar en verde
        self.timeGreen = 10
    

    def carArrived(self):
        '''
        Metodo llamado por un auto cuando avisa que se aproxima a un cierto semaforo.
        Si el semaforo no tiene turno, pide uno en el pizarron.
        '''
        if(self.carCount == 0):
            if not self.isMyTurn:
                if self.unique_id not in AgentTrafficLight.turns:
                    # Agregar su turno
                    AgentTrafficLight.turns.append(self.unique_id)

    def stepTrafficLight(self):
        '''
        Metodo que representa el comportamiento del semaforo en cada paso del modelo.
        '''
        # Determinar en cada paso si es mi turno o no lo es
        if AgentTrafficLight.turns:
            self.isMyTurn = AgentTrafficLight.turns[0] == self.unique_id
        else:
            self.isMyTurn = False
        
        # Arq (1). Si no es mi turno, llega un coche y el contador de coches < 1, pide turno
        # Implementado en metodo carArrived
        
        # Arq (2). Si mi tiempo de turno acaba de terminar y mi contador de coches es mayor a 0
        # Cambiar a rojo, terminar con mi turno, pedir un turno nuevo y reiniciar mi contador de
        # luz verde
        if self.isMyTurn and self.timeGreen == 0 and self.carCount > 0:
            self.color = "Rojo"
            AgentTrafficLight.turns.popleft()
            AgentTrafficLight.turns.append(self.unique_id)
            self.timeGreen = 10

        # Arq (3). Si mi tiempo de turno acaba de terminar y mi contador de coches es igual 0
        # Cambiar a rojo, terminar con mi turno y reiniciar mi contador de luz verde
        elif self.isMyTurn and self.timeGreen == 0 and self.carCount <= 0:
            self.color = "Rojo"
            AgentTrafficLight.turns.popleft()
            self.timeGreen = 10

        # Arq (4). Si es mi turno y ya no hay mas autos, cambiar a rojo y terminar mi turno
        elif self.isMyTurn and self.carCount == 0:
            self.color = "Rojo"
            self.timeGreen = 10
            AgentTrafficLight.turns.popleft()

        # Arq (5). Si es mi turno, cambiar a verde y restar al contador de luz verde
        elif self.isMyTurn:
            self.color = "Verde"
            self.timeGreen -= 1

        # Arq (6). Si no hay autos en ningun semaforo, cambiar a amarillo
        elif not AgentTrafficLight.turns:
            self.color = "Amarillo"

        # Arq (7) Si no es mi turno,  permanecer en rojo
        elif not self.isMyTurn:
            self.color = "Rojo"
        
    
    def step(self):
        '''
        Step de semaforo, implementado en metodo stepTrafficLight para poder actualizar
        a todos los semaforos despues de los autos, evitando el orden de MESA.
        '''
        pass
        
# Modelo
class ModelStreet(Model):

    def __init__(self, width, length): # Matriz de 22 x 22 
        '''
        Inicializacion del agente Modelo. Se envia el ancho y largo del grid.
        Se inicializan los puntos de entrada y salida de la interseccion
        Se colocan las paredes de la interseccion
        Se inicializan y colocan los semaforos de la interseccion
        Se colocan las celdas normales, de aviso, de semaforo e interseccion 
        '''  
        # ID del modelo
        self.uniqueIDs = 1
        # Numero de Semaforos
        self.numTrafficLights = 4
        # Crear grid
        self.grid = MultiGrid(width,length,False)
        # Coordenadas de las entradas a la interseccion
        self.possibleStartingPoints = [(11,0),(21,11),(0,10),(10,21)]
        # Coordenadas de las salidas de la interseccion
        self.possibleDestinations = [(10,0),(21,10),(11,21),(0,11)]
        self.schedule = RandomActivation(self)
        self.running = True
        
        # Contador para conocer el flujo vial en un intervalo de tiempo
        self.trafficFlow = 0
        
        # Semaforos
        self.tl1 = None
        self.tl2 = None
        self.tl3 = None
        self.tl4 = None
            
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
        
        
        # Coordenadas de celdas de semaforo: (9,10) (10,12) (11,9) (12,11)
        # Colocar celdas de semaforo y sus respectivos semaforos
        tl1 = AgentTrafficLight(self.uniqueIDs,self)
        self.grid.place_agent(tl1, (8,8))
        self.uniqueIDs += 1
        tl2 = AgentTrafficLight(self.uniqueIDs,self)
        self.uniqueIDs += 1
        self.grid.place_agent(tl2, (8,13))
        tl3 = AgentTrafficLight(self.uniqueIDs,self)
        self.grid.place_agent(tl3, (13,8))
        self.uniqueIDs += 1
        tl4 = AgentTrafficLight(self.uniqueIDs,self)
        self.grid.place_agent(tl4, (13,13))
        self.uniqueIDs += 1
        
        # Asignar semaforos al modelo
        self.tl1 = tl1
        self.tl2 = tl2
        self.tl3 = tl3
        self.tl4 = tl4
       
        # Colocar celdas de semaforo ante cada semaforo
        cellS1 = AgentCell(self.uniqueIDs, self, "Semaforo", tl1)
        self.uniqueIDs += 1
        cellS2 = AgentCell(self.uniqueIDs, self, "Semaforo", tl2)
        self.uniqueIDs += 1
        cellS3 = AgentCell(self.uniqueIDs, self, "Semaforo", tl3)
        self.uniqueIDs += 1
        cellS4 = AgentCell(self.uniqueIDs, self, "Semaforo", tl4)
        self.uniqueIDs += 1
       

        # Agregar celdas al schedule
        self.schedule.add(cellS1)
        self.schedule.add(cellS2)
        self.schedule.add(cellS3)
        self.schedule.add(cellS4)
        
        # Agregar semaforos al schedule
        self.schedule.add(tl1)
        self.schedule.add(tl2)
        self.schedule.add(tl3)
        self.schedule.add(tl4)
        
        self.grid.place_agent(cellS1, (9,10))
        self.grid.place_agent(cellS2, (10,12))
        self.grid.place_agent(cellS3, (11,9))
        self.grid.place_agent(cellS4, (12,11))

                
        # Coordenadas de celdas aviso: (8,10) (11,8) (13,11) (10,13)
        # Colocar celdas de aviso
        cellA1 = AgentCell(self.uniqueIDs, self, "Aviso", tl1)
        self.uniqueIDs += 1
        cellA2 = AgentCell(self.uniqueIDs, self, "Aviso", tl3)
        self.uniqueIDs += 1
        cellA3 = AgentCell(self.uniqueIDs, self, "Aviso", tl4)
        self.uniqueIDs += 1
        cellA4 = AgentCell(self.uniqueIDs, self, "Aviso", tl2)
        self.uniqueIDs += 1
        self.schedule.add(cellA1)
        self.schedule.add(cellA2)
        self.schedule.add(cellA3)
        self.schedule.add(cellA4)
        self.grid.place_agent(cellA1, (8,10))
        self.grid.place_agent(cellA2, (11,8))
        self.grid.place_agent(cellA3, (13,11))
        self.grid.place_agent(cellA4, (10,13))
        self.trafficLights = [tl1,tl2,tl3,tl4]
        
        # Coordenadas celdas interseccion: (10,10) (11,10) (10,11) (11,11)
        # Colocar celdas de interseccion
        cellI1 = AgentCell(self.uniqueIDs, self, "Interseccion", tl1)
        self.uniqueIDs += 1
        cellI2 = AgentCell(self.uniqueIDs, self, "Interseccion", tl3)
        self.uniqueIDs += 1
        cellI3 = AgentCell(self.uniqueIDs, self, "Interseccion", tl2)
        self.uniqueIDs += 1
        cellI4 = AgentCell(self.uniqueIDs, self, "Interseccion", tl4)
        self.uniqueIDs += 1
        self.schedule.add(cellI1)
        self.schedule.add(cellI2)
        self.schedule.add(cellI3)
        self.schedule.add(cellI4)
        self.grid.place_agent(cellI1, (10,10))
        self.grid.place_agent(cellI2, (11,10))
        self.grid.place_agent(cellI3, (10,11))
        self.grid.place_agent(cellI4, (11,11))   

        # Coordenadas de celdas normales: (9,11) (10,9) (12,10) (11,12)
        # Colocar celdas normales
        cellN1 = AgentCell(self.uniqueIDs, self, "Normal")
        self.uniqueIDs += 1
        cellN2 = AgentCell(self.uniqueIDs, self, "Normal")
        self.uniqueIDs += 1
        cellN3 = AgentCell(self.uniqueIDs, self, "Normal")
        self.uniqueIDs += 1
        cellN4 = AgentCell(self.uniqueIDs, self, "Normal")
        self.uniqueIDs += 1
        cellN5 = AgentCell(self.uniqueIDs, self, "Normal")
        self.uniqueIDs += 1
        cellN6 = AgentCell(self.uniqueIDs, self, "Normal")
        self.uniqueIDs += 1
        cellN7 = AgentCell(self.uniqueIDs, self, "Normal")
        self.uniqueIDs += 1
        cellN8 = AgentCell(self.uniqueIDs, self, "Normal")
        self.uniqueIDs += 1
        self.schedule.add(cellN1)
        self.schedule.add(cellN2)
        self.schedule.add(cellN3)
        self.schedule.add(cellN4)
        self.schedule.add(cellN5)
        self.schedule.add(cellN6)
        self.schedule.add(cellN7)
        self.schedule.add(cellN8)
        self.grid.place_agent(cellN1, (9,11))
        self.grid.place_agent(cellN2, (10,9))
        self.grid.place_agent(cellN3, (12,10))
        self.grid.place_agent(cellN4, (11,12))
        self.grid.place_agent(cellN5, (8,11))
        self.grid.place_agent(cellN6, (10,8))
        self.grid.place_agent(cellN7, (13,10))
        self.grid.place_agent(cellN8, (11,13))     


    def addAgents(self):
        '''
        Metodo que permite anadir en cada iteracion, nuevas instancias de automoviles
        en coordenadas especificas definidas como puntos de origen solo si las celdas
        se encuentran disponibles.

        Se asocia el semaforo correspondiente considerando lo siguiente:
        - Si el coche parte de (11,0) -> tl3
        - Si el coche parte de (21,11) -> tl4
        - Si el coche parte de (10,21) -> tl2
        - Si el coche parte de (0,10) -> tl1 
        '''               
        # Se seleccionan de manera aleatoria cuatro booleanos para definir si apareceran automoviles
        b1,b2,b3,b4 = random.choices(population=[True,False], weights=[0.1, 0.9],k=4)
        
        # Si el primer booleano es verdadero, agregara un auto en la posicion (11,0)
        if(b1):
            cell = self.grid.get_cell_list_contents((11,0))
            if(not cell):
                b = AgentCar(self.uniqueIDs, self, (11,0), "Arriba",self.tl3,"purple")
                self.uniqueIDs += 1
                self.schedule.add(b)
                self.grid.place_agent(b, (11,0))
        
        # Si el segundo booleano es verdadero, agregara un auto en la posicion (21,11)
        if(b2):
            cell = self.grid.get_cell_list_contents((21,11))
            if(not cell):
                b = AgentCar(self.uniqueIDs, self, (21,11), "Izquierda",self.tl4)
                self.uniqueIDs += 1
                self.schedule.add(b)
                self.grid.place_agent(b, (21,11))
                
        # Si el tercer booleano es verdadero, agregara un auto en la posicion (0,10)
        if(b3):
            cell = self.grid.get_cell_list_contents((0,10))
            if(not cell):
                b = AgentCar(self.uniqueIDs, self, (0,10), "Derecha",self.tl1,"brown")
                self.uniqueIDs += 1
                self.schedule.add(b)
                self.grid.place_agent(b, (0,10))
                
        # Si el cuarto booleano es verdadero, agregara un auto en la posicion (10,21)
        if(b4):
            cell = self.grid.get_cell_list_contents((10,21))
            if(not cell):
                b = AgentCar(self.uniqueIDs, self, (10,21), "Abajo", self.tl2,"orange")
                self.uniqueIDs += 1
                self.schedule.add(b)
                self.grid.place_agent(b, (10,21))

    def step(self):
        '''
        Metodo step del modelo. Se realiza cada paso del schedule. Primer se realizan los steps
        de los automoviles y luego los steps de los semaforos
        '''  
        # Steps de agentes coche
        self.schedule.step()
        
        # Steps de agentes semaforos
        for lights in range(len(self.trafficLights)):
            self.trafficLights[lights].stepTrafficLight()
        self.addAgents()
        
        # Se mandan las visualizaciones
        positions = []
        for i in range(4):
            positions.append(self.trafficLights[i].color)
        
        # Se arman los arreglos de posiciones para mandar al servidor
        for pos in range(100,len(self.schedule.agents)):
            xy = self.schedule.agents[pos].pos
            p = [xy[0],xy[1],0, self.schedule.agents[pos].orientation, self.schedule.agents[pos].unique_id, self.schedule.agents[pos].destination, self.trafficFlow]
            positions.append(p)
        return positions