from mesa import Agent, Model
from mesa.time import RandomActivation
from mesa.space import MultiGrid

"""
EQUIPO 2.
Diego Alejandro Juárez Ruiz     A01379566
Edna Jacqueline Zavala Ortega   A01750480
Erick Alberto Bustos Cruz       A01378966
Luis Enrique Zamarripa Marín    A01379918

M1. ACTIVIDAD
Robot de limpieza reactivo.
Descripción: robot (VacuumAgent) dedicado a la limpieza de un determinado porcentaje de celdas
que contienen basura (TrashAgent) en celdas aleatorias. El robot es capaz de moverse hacia cualquiera
de las celdas aledañas en caso de que se encuentre en una celda limpia, de lo contrario, deberá
limpiar la basura. El programa se detiene hasta que el tiempo (steps) se agote o se hayan terminado de
limpiar las celdas.

Entrada:
* Habitación de MxN espacios.
* Número de agentes.
* Porcentaje de celdas inicialmente sucias.
* Tiempo máximo de ejecución (steps).

Salida:
* Tiempo necesario hasta que todas las celdas estén limpias (o se haya llegado al tiempo máximo).
* Porcentaje de celdas limpias después del termino de la simulación.
* Número de movimientos realizados por todos los agentes.

Fecha de creación/modificación: 11/11/2021
"""

def CreateGraph(model):
    return model.stepsTime


class TrashAgent(Agent):
    """
    Clase que representa la basura dentro de una celda
    """
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)

        
class VacuumAgent(Agent):
    """
    Clase que representa a una aspiradora.
    Su inicializador recibe una id única: unique_id, y el modelo al que pertenece
    """
    # Número de pasos realizados
    totalSteps = 0
    
    # Constructor
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
    
    def move(self):
        """
        Función que representa un movimiento de la aspiradora.
        Elige una posición vecina de manera aleatoria y mueve al agente.
        """
        
        # Se buscan las celdas vecinas a las que se puede mover el agente
        possible_steps = self.model.grid.get_neighborhood(
            self.pos,
            moore=True,
            include_center=False)
        
        # Se escoge una celda de manera aleatoria
        new_position = self.random.choice(possible_steps)
        
        # Se mueve al agente a dicha celda
        self.model.grid.move_agent(self, new_position)

    def clean(self, agent):
        """
        Función que permite eliminar basura de una celda sucia
        """
        self.model.grid.remove_agent(agent)
        self.model.cleanCells += 1

    def step(self): 
        """
        Función que modela el comportamiento de una aspiradora en cada paso
        del modelo. Debe limpiar una celda, o moverse.
        """
        # Se obtienen todos los agentes en la celda donde está la aspiradora
        gridContent = self.model.grid.get_cell_list_contents([self.pos])
        trash = False
        trashElement = None
        
        # Se busca basura en la celda
        for element in gridContent:
            if isinstance(element, TrashAgent):
                trash = True
                trashElement = element
        # Si no se encuentra basura mover al agente
        if not trash:
            VacuumAgent.totalSteps += 1
            self.move()
        # Si se encuentra basura, eliminarla
        else:
            self.clean(trashElement)

class ModelRoomba(Model):
    """
    Modelo que representa la simulación
    Recibe el número de agentes: numAgents, las dimensiones de la cuadrícula: m y n,
    el porcentaje de celdas sucias: dirty y el tiempo límite de la simulación: timeLimit
    
    """
    def __init__(self, numAgents, m, n, dirty, timeLimit):
        # Crear cuadrícula
        self.grid = MultiGrid(m, n, False)
        # Establecer el número de agentes
        self.numAgents = numAgents
        # Tiempo límite
        self.tle = timeLimit
        # Número de pasos transcurridos
        self.stepsTime = 0
        # Número de celdas sucias
        self.dirtyCells = int((dirty * (n*m)) / 100)
        # Número de celdas que han sido limpiadas
        self.cleanCells = 0
        # Schedule
        self.schedule = RandomActivation(self)
        # Estado de la simulación
        self.running = True
        # Bool que representa si ya se terminó de limpiar toda la basura
        self.cleanLimit = False
        
        # Creación de agentes aspiradoras
        for i in range(0,self.numAgents):
            # Crear agente y agregarlo al schedule
            a = VacuumAgent(i, self)
            self.schedule.add(a)
            
            # Colocar al agente en la posición (1,1)
            self.grid.place_agent(a, (1, 1))

        
        # Creación de celdas sucias por medio de un set
        dirtyCells = set()
        for t in range(self.numAgents+1,self.dirtyCells+self.numAgents+1):
            # Crear agente basura y agregarlo al schedule
            b = TrashAgent(t,self)
            self.schedule.add(b)
            VacuumAgent.totalSteps = 0
            # Establecer coordenadas aleatorias para la basura
            x = self.random.randrange(self.grid.width)
            y = self.random.randrange(self.grid.height)
            
            # Evitar poner doble basura en una misma celda
            while (x,y) in dirtyCells:
                x = self.random.randrange(self.grid.width)
                y = self.random.randrange(self.grid.height)
            dirtyCells.add((x,y))
                        
            # Colocar el agente en su posición
            self.grid.place_agent(b, (x, y))


    def step(self):
        """
        Representación de cada paso de la simulación
        """
        # Determinar si ya se limpiaron todas las celdas
        if(self.cleanCells == self.dirtyCells):
            self.cleanLimit = True

        # Imprimir la información solicitada sobre la corrida del modelo
        if(self.cleanLimit or self.tle == self.stepsTime):
                self.running = False

                if(self.cleanLimit):
                    print("\nTodas las celdas están limpias \n")
                else:
                    print("Se ha agotado el tiempo límite")

                print("Tiempo transcurrido: " + str(self.stepsTime) + " steps, Porcentaje de celdas limpiadas: " + str(int((self.cleanCells*100)/self.dirtyCells))+ "%")
                print("Número de movimientos: " + str(VacuumAgent.totalSteps))
        # Hacer que todos los agentes den un paso (determinado en sus respectivos modelos)
        else:
            self.stepsTime += 1
            self.schedule.step()



# Código utilizado para las gráficas

# fixed_params = {"n": 10,
#                "m": 10,
#                "dirty": 40,
#                "timeLimit":1000}

# variable_params = {"numAgents": range(1, 20)}

# batch_run = BatchRunner(ModelRoomba,
#                         variable_params,
#                         fixed_params,
#                         iterations=4,
#                         max_steps=1000,
#                         model_reporters={"CleanCells": CreateGraph})
# batch_run.run_all()

# run_data = batch_run.get_model_vars_dataframe()
# run_data.head()
# plt.scatter(run_data.numAgents,run_data.CleanCells)
# plt.title("Movimientos realizados por las aspiradoras contra el número de aspiradoras hasta limpiar el 100% de celdas sucias")
# plt.ylabel("Movimientos")
# plt.xlabel("Número de agentes")
# plt.grid(True)
# plt.xticks(range(min(run_data.numAgents),max(run_data.numAgents)+1,1))
# plt.show()

# fixed_params = {"n": 10,
#                "m": 10,
#                "dirty": 40,
#                "timeLimit":1000}

# variable_params = {"numAgents": range(1, 30)}

# batch_run = BatchRunner(ModelRoomba,
#                         variable_params,
#                         fixed_params,
#                         iterations=4,
#                         max_steps=1000,
#                         model_reporters={"CleanCells": CreateGraph})
# batch_run.run_all()

# run_data = batch_run.get_model_vars_dataframe()
# run_data.head()
# plt.scatter(run_data.numAgents,run_data.CleanCells)
# plt.title("Tiempo que se tarda en limpiar el 100% de celdas sucias con número de agentes variable")
# plt.ylabel("Tiempo")
# plt.xlabel("Número de agentes")
# plt.grid(True)
# plt.xticks(range(min(run_data.numAgents),max(run_data.numAgents)+1,1))
# plt.show()