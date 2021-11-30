/*
 * TC2008B Modelacion de sistemas multiagentes con graficas computacionales (Gpo 301)
 * Autores:
 * Diego Alejandro Juarez Ruiz     A01379566
 * Edna Jacqueline Zavala Ortega   A01750480
 * Erick Alberto Bustos Cruz       A01378966
 * Luis Enrique Zamarripa Marin    A01379918
 * En conjunto con Sergio Ruiz Loza, PhD
 * Ultima modificacion: 30/11/21 
 */

// Importaciones
using System;
using System.Collections;
using System.Collections.Generic;
using UnityEditor;
using UnityEngine;
using UnityEngine.Networking;

/*
 * Clase que permite crear un objeto de tipo TrafficLightJSON para organizar
 * la informacion de los semaforos proveniente del modelo en la nube
 */
[Serializable]
public class TrafficLightJSON
{
    public string color;

    public static TrafficLightJSON CreateFromJSON(string jsonString)
    {
        return JsonUtility.FromJson<TrafficLightJSON>(jsonString);
    }
}

/*
 * Clase que permite crear un objeto de tipo CarJSON para organizar
 * la informacion de los automoviles proveniente del modelo en la nube
 */
[Serializable]
public class CarJSON
{
    public float x;
    public float y;
    public float z;
    public string orientation;
    public int id;
    public int destinationx;
    public int destinationy;

    public static CarJSON CreateFromJSON(string jsonString)
    {
        return JsonUtility.FromJson<CarJSON>(jsonString);
    }
}

/*
 * Clase WebClient que realiza las solicitudes al servidor para obtener
 * las nuevas posiciones de los autos y reiniciar la simulacion siempre
 * que se ejecute
 */
public class WebClient : MonoBehaviour
{
    // Inicializacion de diccionarios, listas y flotantes a utilizar
    
    // Diccionario en el que se asocia el id del automovil con la posicion actualizada
    // obtenida desde el modelo
    Dictionary<int, Vector3> positionsDict;
    // Diccionario en el que se asocia el id del automovil con la posicion previa (necesaria
    // para la interpolacion)
    Dictionary<int, Vector3> prevPositionsDict;
    // Diccionario en el que se asocia el id del automovil con el GameObject en la escena 
    Dictionary<int, GameObject> carsDict;
    // Diccionario en el que se asocia el id del automovil con su orientacion actual 
    Dictionary<int, string> orientationsDict;
    // Diccionario en el que se asocia el id del automovil con las coordenadas de su destino
    Dictionary<int, List<int>> destinationsDict;

    //public Material[] arrowMaterials;
    public List<GameObject> tls;
    public float simVel = 1;
    public List<String> trafficLights;
    public GameObject[] carsPrefabs;
    public float timeToUpdate = 1f;
    private float timer;
    public float dt;


    /*
     * Funcion que solicita que al servidor reinicie la simulacion
     * cada que se corre la simulacion de nuevo. Por ello, solo se
     * llama en el Start()
     */
    IEnumerator RestartSimulation(string data)
    {
         WWWForm form = new WWWForm();
        string urlRestart = "localhost:8000/restart";
        //string urlRestart = "https://multiagentsystemteam2.mybluemix.net/restart";
        using (UnityWebRequest www = UnityWebRequest.Post(urlRestart, form))
        {
            byte[] bodyRaw = System.Text.Encoding.UTF8.GetBytes(data);
            www.uploadHandler = (UploadHandler)new UploadHandlerRaw(bodyRaw);
            www.downloadHandler = (DownloadHandler)new DownloadHandlerBuffer();
            www.SetRequestHeader("Content-Type", "application/json");

            yield return www.SendWebRequest(); 

            if (www.isNetworkError || www.isHttpError)
            {
                Debug.Log(www.error);
            }
        }
    }

    /*
     * Funcion que solicita que solicita al servidor los datos de un nuevo paso del modelo,
     * recibe y procesa el JSON recibido para poder hacer uso de dichas variables en el
     * update.
     */
    IEnumerator SendData(string data)
    {
        WWWForm form = new WWWForm();
        // Link a la nube de IBM: https://multiagentsystemteam2.mybluemix.net/simulation
        string url = "localhost:8000/simulation";
        //string url = "https://multiagentsystemteam2.mybluemix.net/simulation";
        
        // Hacer request al servidor 
        using (UnityWebRequest www = UnityWebRequest.Post(url, form))
        {
            
            byte[] bodyRaw = System.Text.Encoding.UTF8.GetBytes(data);
            www.uploadHandler = (UploadHandler)new UploadHandlerRaw(bodyRaw);
            www.downloadHandler = (DownloadHandler)new DownloadHandlerBuffer();
            www.SetRequestHeader("Content-Type", "application/json");

            yield return www.SendWebRequest(); 

            // Si hay error, se pone en la consola
            if (www.isNetworkError || www.isHttpError)
            {
                Debug.Log(www.error);
            }
            else
            {
                prevPositionsDict = positionsDict;
                positionsDict = new Dictionary<int, Vector3>();
                string txt = www.downloadHandler.text;
                txt = txt.Replace('\'', '\"');
                txt = txt.TrimStart('[');
                txt = txt.TrimEnd(']');
                string[] strs = txt.Split(new string[] { "}, {" }, StringSplitOptions.None);

                // Procesar JSON 
                for (int i = 0; i < strs.Length; i++)
                {
                    // Quitar llaves
                    strs[i] = strs[i].Trim();
                    if (i == 0) strs[i] = strs[i] + '}';
                    else if (i == strs.Length - 1) strs[i] = '{' + strs[i];
                    else strs[i] = '{' + strs[i] + '}';
                    if (i <= 3)
                    {
                        // Agregar colores de los semaforos
                        TrafficLightJSON tl = TrafficLightJSON.CreateFromJSON(strs[i]);
                        trafficLights[i] = tl.color;

                    }
                    else
                    {
                        // Armar CarJSON con informacon recibida
                        CarJSON rumrun = CarJSON.CreateFromJSON(strs[i]);
                        
                        // Realizar ajustes para escalar las dimensiones de mesa a Unity
                        Vector3 position = new Vector3((rumrun.x*2)+1, rumrun.y ,(rumrun.z*2)+1);

                        // Agregar posicion del auto
                        positionsDict[rumrun.id] = position;

                        // Agregar orientacion del auto
                        orientationsDict[rumrun.id] = rumrun.orientation;

                        // Agregar del destino del auto
                        List<int> dest = new List<int>();
                        dest.Add(rumrun.destinationx* 2 + 1);
                        dest.Add(rumrun.destinationy * 2 + 1);
                        destinationsDict[rumrun.id] = dest;
                    }
                }
                
                // Iterar sobre los IDs de los autos que actualmente tienen posicion
                foreach(KeyValuePair<int, Vector3> kvp in positionsDict)
                {
                    // Si dicho auto no tiene un GameObject Asignado, crearlo
                    if(!carsDict.ContainsKey(kvp.Key))
                    {
                        // Escoger de manera aleatoria un modelo de auto
                        GameObject carGameO = Instantiate(carsPrefabs[UnityEngine.Random.Range(0, carsPrefabs.Length)]);
                        // Hacer visible el GameObject
                        carGameO.SetActive(true);
                        // Agregarlo al diccionario que mapea id a GameObject
                        carsDict.Add(kvp.Key,carGameO);
                    }
                }
            }
        }
    }
    
    /*
     *  Incicializacion de diccionarios a utlizar
     *  Se llama a las posiciones por primera vez con una posicion falsa
     *  Se manda a llamar la funcion SendData() para actualizar las posiciones
     *  Solo se corre una vez        
     */
    void Start()
    {
        // Lista de semaforos
        trafficLights = new List<String>()
        {
            "t",
            "e",
            "s",
            "t"
        };
        // Diccionario de posiciones [carID: Posicion]
        positionsDict = new Dictionary<int, Vector3>();
        // Diccionario de posiciones previas para interpolacion [carID: Posicion Previa]
        prevPositionsDict = new Dictionary<int, Vector3>();
        // Diccionario de orientaciones de los autos [carID: Orientacion]
        orientationsDict = new Dictionary<int, string>();
        // Diccionario de destinos de los autos [carID: Destino]
        destinationsDict = new Dictionary<int, List<int>>();
        // Diccionario de GameObjects de los autos [carID: GameObject]
        carsDict = new Dictionary<int, GameObject>();

#if UNITY_EDITOR
        Vector3 fakePos = new Vector3(3.44f, 0, -15.707f);
        string json = EditorJsonUtility.ToJson(fakePos);
        // Iniciar co-rutina para consumir la ruta que reinicia la simulacion
        StartCoroutine(RestartSimulation(json));
        // Iniciar co-rutina para solicitar los valores iniciales de la simulacion
        StartCoroutine(SendData(json));
        timer = timeToUpdate;
#endif
    }


    /*
     * Funcion que se actualiza con cada frame
     * Se actualiza el timer para volver a llamar las posiciones al servidor
     * Se actualizan todas las posiciones de todos los coches y si es que necesitan ser borrados
     */
    void Update()
    {
        Vector3 dir;
        Vector3 dir2;
        // Velocidad con la que se realizan actualizaciones a la simulacion
        timer -= simVel;
        dt = 1.0f - (timer / timeToUpdate);

        // Si el timer es menor a 0
        if(timer < 0)
        {
            
#if UNITY_EDITOR
            // Reiniciar el temporizador
            timer = timeToUpdate;
            
            Vector3 fakePos = new Vector3(3.44f, 0, -15.707f);

            // Si es necesario, se borran los automoviles que ya llegaron a su destino 
            foreach(KeyValuePair<int,Vector3> kvp in prevPositionsDict)
            {
                if(!positionsDict.ContainsKey(kvp.Key))
                {
                    if (carsDict.ContainsKey(kvp.Key))
                    {
                        // Destruir GameObject
                        Destroy(carsDict[kvp.Key]);
                        // Eliminar auto de los mapas
                        orientationsDict.Remove(kvp.Key);
                        destinationsDict.Remove(kvp.Key);
                        carsDict.Remove(kvp.Key);
                    }

                }
            }

            // Se vuelve a pedir posiciones al servidor
            string json = EditorJsonUtility.ToJson(fakePos);
            StartCoroutine(SendData(json));
#endif
            // Actualizacion de rotacion de cada automovil
            foreach(KeyValuePair<int, string> kvp in orientationsDict)
            { 
                // Si el automovil va hacia arriba
                if (orientationsDict[kvp.Key] == "Arriba")
                {
                    dir = new Vector3(0, 0, 2);
                }
                // Si el automovil va hacia derecha
                else if (orientationsDict[kvp.Key] == "Derecha")
                {
                    dir = new Vector3(2, 0, 0);
                }
                // Si el automovil va hacia izquierda
                else if (orientationsDict[kvp.Key] == "Izquierda")
                {
                    dir = new Vector3(-2, 0, 0);
                }
                // Si el automovil va hacia abajo
                else
                {
                    dir = new Vector3(0, 0, -2);
                }
                // Realizar la rotacion
                carsDict[kvp.Key].transform.rotation = Quaternion.LookRotation(dir);
            }

            // Actualizacion de rotacion de cada flecha
            foreach(KeyValuePair<int, GameObject> kvp in carsDict)
            {
                // Encontrar las coordenadas del destino
                List<int> destiny = destinationsDict[kvp.Key];
                
                // Crear un vector con los puntos del destino
                Vector3 destinyv = new Vector3(destiny[0], 0, destiny[1]);

                // Encontrar el vector de la posicion de la flecha
                Vector3 arrow = carsDict[kvp.Key].transform.Find("Arrow2").transform.position;
                
                // Cambiar el material de la flecha
                //carsDict[kvp.Key].transform.Find("Arrow2").gameObject.transform.GetChild(0).gameObject.GetComponent<Renderer>().material = arrowMaterials[UnityEngine.Random.Range(0, arrowMaterials.Length)];
                
                // Calcular el vector que representa la nueva posicion a donde debe apuntar la flecha
                Vector3 origin = new Vector3(arrow.x, arrow.y, arrow.z);
                dir2 = destinyv - origin;
                
                // Realizar la rotacion
                carsDict[kvp.Key].transform.Find("Arrow2").transform.rotation = Quaternion.LookRotation(dir2);
            }
        } 
        

        // Actualizar colores de los semaforos. Cada semaforo tiene GameObjects con los 3 colores
        // los cuales se desactivan segun sea el caso
        for (int tl = 0; tl < 4; tl++) 
        {
            if (trafficLights[tl] == "Verde")
            {
                tls[tl].gameObject.transform.GetChild(0).gameObject.SetActive(true);
                tls[tl].gameObject.transform.GetChild(1).gameObject.SetActive(false);
                tls[tl].gameObject.transform.GetChild(2).gameObject.SetActive(false);
            }
            else if (trafficLights[tl] == "Rojo")
            {
                tls[tl].gameObject.transform.GetChild(0).gameObject.SetActive(false);
                tls[tl].gameObject.transform.GetChild(1).gameObject.SetActive(true);
                tls[tl].gameObject.transform.GetChild(2).gameObject.SetActive(false);
            }
            else if(trafficLights[tl] == "Amarillo")
            {
                tls[tl].gameObject.transform.GetChild(0).gameObject.SetActive(false);
                tls[tl].gameObject.transform.GetChild(1).gameObject.SetActive(false);
                tls[tl].gameObject.transform.GetChild(2).gameObject.SetActive(true);
            }
        }



        if(positionsDict.Count > 0)
        {
            // Se itera en el diccionario actual para actualizar las posiciones de los automoviles
            foreach(KeyValuePair<int, Vector3> kvp in positionsDict)
            {
                // Revisar si la llave se encuentra en el diccionario previous, entonces se puede interpolar
                if(prevPositionsDict.ContainsKey(kvp.Key))
                {
                    Vector3 interpolated = Vector3.Lerp(prevPositionsDict[kvp.Key], positionsDict[kvp.Key], dt);
                    carsDict[kvp.Key].transform.localPosition = new Vector3(interpolated.x, carsDict[kvp.Key].transform.position.y ,interpolated.z);
                } 
                // Si no se encuentra, entonces solo se coloca el automovil en la coordenada correcta
                else
                {
                    carsDict[kvp.Key].transform.localPosition = new Vector3(positionsDict[kvp.Key].x,carsDict[kvp.Key].transform.position.y, positionsDict[kvp.Key].z);
                    // Si el automovil va hacia arriba
                    if (orientationsDict[kvp.Key] == "Arriba")
                    {
                        dir = new Vector3(0, 0, 2);
                    }
                    // Si el automovil va hacia derecha
                    else if (orientationsDict[kvp.Key] == "Derecha")
                    {
                        dir = new Vector3(2, 0, 0);
                    }
                    // Si el automovil va hacia izquierda
                    else if (orientationsDict[kvp.Key] == "Izquierda")
                    {
                        dir = new Vector3(-2, 0, 0);
                    }
                    // Si el automovil va hacia abajo
                    else
                    {
                        dir = new Vector3(0, 0, -2);
                    }
                    // Actualizacion de direccon
                    carsDict[kvp.Key].transform.rotation = Quaternion.LookRotation(dir);
                }
            }

            // Actualizacion de flecha
            foreach(KeyValuePair<int, GameObject> kvp in carsDict)
            {
                // Encontrar las coordenadas del destino
                List<int> destiny = destinationsDict[kvp.Key];
                
                // Crear un vector con los puntos del destino
                Vector3 destinyv = new Vector3(destiny[0], 0, destiny[1]);
                
                // Encontrar el vector de la posicion de la flecha
                Vector3 arrow = carsDict[kvp.Key].transform.Find("Arrow2").transform.position;
                
                // Calcular el vector que representa la nueva posicion a donde debe apuntar la flecha
                Vector3 origin = new Vector3(arrow.x, arrow.y, arrow.z);
                dir2 = destinyv - origin;
                
                // Realizar la rotacion
                carsDict[kvp.Key].transform.Find("Arrow2").transform.rotation = Quaternion.LookRotation(dir2);
            }

            // Se itera para desactivar los automoviles que llegan a su destino. Cuando se piden nuevas posiciones se destruye el objecto
            foreach(KeyValuePair<int,Vector3> kvp in prevPositionsDict)
            {
                if(!positionsDict.ContainsKey(kvp.Key))
                {
                    if (carsDict.ContainsKey(kvp.Key))
                    {
                        if (carsDict[kvp.Key].activeInHierarchy)
                        {
                            carsDict[kvp.Key].SetActive(false);
                        }
                    }
                }
            }
        }
    }
}