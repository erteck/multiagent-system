// TC2008B Modelación de Sistemas Multiagentes con gráficas computacionales
// C# client to interact with Python server via GET
// Equipo 2
// Sergio Ruiz-Loza, Ph.D. March 2021

using System;
using System.Collections;
using System.Collections.Generic;
using UnityEditor;
using UnityEngine;
using UnityEngine.Networking;

[Serializable]
public class TrafficLightJSON
{
    public string color;

    public static TrafficLightJSON CreateFromJSON(string jsonString)
    {
        return JsonUtility.FromJson<TrafficLightJSON>(jsonString);
    }
}

[Serializable]
public class CarJSON
{
    public float x;
    public float y;
    public float z;
    public string orientation;
    public int id;

    public static CarJSON CreateFromJSON(string jsonString)
    {
        return JsonUtility.FromJson<CarJSON>(jsonString);
    }
}

public class WebClient : MonoBehaviour
{
    List<List<Vector3>> positions;

    Dictionary<int, Vector3> positionsDict;
    Dictionary<int, Vector3> prevPositionsDict;
    Dictionary<int, GameObject> carsDict;
    Dictionary<int, string> orientationsDict;


    public List<GameObject> cars;
    //public List<GameObject>

    public List<GameObject> tls;
   

    public List<String> trafficLights;

    public GameObject[] carsPrefabs;

    private List<List<String>> orientations;

    public float timeToUpdate = 2.0f; // 5
    private float timer;
    public float dt;

    private int prevLen = 0;

    // IEnumerator - yield return
    IEnumerator SendData(string data)
    {
        WWWForm form = new WWWForm();
        //string url = "https://multiagentsystemteam2.mybluemix.net/simulation";
        string url = "localhost:8000/simulation";
        //using (UnityWebRequest www = UnityWebRequest.Post(url, form))
        using (UnityWebRequest www = UnityWebRequest.Get(url))
        {
            byte[] bodyRaw = System.Text.Encoding.UTF8.GetBytes(data);
            www.uploadHandler = (UploadHandler)new UploadHandlerRaw(bodyRaw);
            www.downloadHandler = (DownloadHandler)new DownloadHandlerBuffer();
            www.SetRequestHeader("Content-Type", "application/json");

            yield return www.SendWebRequest();          // Talk to Python

            if (www.isNetworkError || www.isHttpError)
            {
                Debug.Log(www.error);
            }
            else
            {
                List<Vector3> newPositions = new List<Vector3>();
                List<String> orientationCars = new List<String>();
                string txt = www.downloadHandler.text;
                Debug.Log(txt);
                txt = txt.Replace('\'', '\"');
                txt = txt.TrimStart('[');
                txt = txt.TrimEnd(']');
                string[] strs = txt.Split(new string[] { "}, {" }, StringSplitOptions.None);
                for (int i = 0; i < strs.Length; i++)
                {
                    strs[i] = strs[i].Trim();
                    if (i == 0) strs[i] = strs[i] + '}';
                    else if (i == strs.Length - 1) strs[i] = '{' + strs[i];
                    else strs[i] = '{' + strs[i] + '}';
                    if (i <= 3)
                    {
                        TrafficLightJSON tl = TrafficLightJSON.CreateFromJSON(strs[i]);
                        trafficLights[i] = tl.color;

                    }
                    else
                    {
                        CarJSON rumrun = CarJSON.CreateFromJSON(strs[i]);
                        Vector3 position = new Vector3((rumrun.x*2)+1, rumrun.y ,(rumrun.z*2)+1);
                        positionsDict[rumrun.id] = position;
                        orientationsDict[rumrun.id] = rumrun.orientation;
                        newPositions.Add(position);

                        orientationCars.Add(rumrun.orientation);
                    }
                }
                
                foreach(KeyValuePair<int, Vector3> kvp in positionsDict)
                {
                    if(!carsDict.ContainsKey(kvp.Key))
                    {
                        // Agregar autos
                        int newCars = newPositions.Count - prevLen;
                        prevLen = prevLen + newCars;
                        GameObject carGameO = Instantiate(carsPrefabs[UnityEngine.Random.Range(0, carsPrefabs.Length)]);
                        carGameO.SetActive(true);
                        carsDict.Add(kvp.Key,carGameO);
                        // for(int c = 0; c < newCars; c++)f
                        // {
                        // //GameObject carGameO = Instantiate(carsPrefabs[1]);
                        // GameObject carGameO = Instantiate(carsPrefabs[UnityEngine.Random.Range(0, carsPrefabs.Length)]);
                        // carGameO.SetActive(true);
                        // cars.Add(carGameO);
                        // }
                    }
                }
            

                List<Vector3> poss = new List<Vector3>();
                //for (int s = 0; s < cars.Count; s++)
                for (int s = 0; s < newPositions.Count; s++)
                {
                    poss.Add(newPositions[s]);
                }
                positions.Add(poss);
                orientations.Add(orientationCars);
            }
        }
    
        if (positions.Count > 0){
            Debug.Log(positions[positions.Count - 1].Count);
        }

    }

    // Start is called before the first frame update
    void Start()
    {
        positions = new List<List<Vector3>>();
        orientations = new List<List<String>>();
        trafficLights = new List<String>()
        {
            "t",
            "e",
            "s",
            "t"
        };
        positionsDict = new Dictionary<int, Vector3>();
        prevPositionsDict = new Dictionary<int, Vector3>();
        orientationsDict = new Dictionary<int, string>();
        carsDict = new Dictionary<int, GameObject>();



#if UNITY_EDITOR
        Vector3 fakePos = new Vector3(3.44f, 0, -15.707f);
        string json = EditorJsonUtility.ToJson(fakePos);
        //StartCoroutine(SendData(call));
        StartCoroutine(SendData(json));
        timer = timeToUpdate;
#endif
    }




    // Update is called once per frame
    void Update()
    {
        timer -= Time.deltaTime;
        dt = 1.0f - (timer / timeToUpdate);

        if(timer < 0)
        {
            

#if UNITY_EDITOR
            timer = timeToUpdate; // reset the timer
            Vector3 fakePos = new Vector3(3.44f, 0, -15.707f);
            string json = EditorJsonUtility.ToJson(fakePos);
            StartCoroutine(SendData(json));
#endif
        }
        /*
        // Crear autos y agregarlos al vector de carss
            // Guardar siempre el len(cars) después de cada update y sacar el len al inicio
            // La diferencia es el número de autos que hay que agregar al vector s
        int newCars = positions[positions.Count-1].Count - 4 - prevLen;
        prevLen = newCars;

        for(int c = 0; c < newCars; c++){
            GameObject carGameO = Instantiate(carsPrefabs[1]);
            cars.Add(carGameO);
        }*/

        //  public List<String> trafficLights;
        // Actualizar colores de los semáforos
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



        if(positionsDict.Count > 1)
        {
            // Se itera en el diccionario actual para actualizar las posiciones de los automóviles
            foreach(KeyValuePair<int, Vector3> kvp in positionsDict)
            {
                // Revisar si la llave se encuentra en el diccionario previous, entonces se puede interpolar
                if(prevPositionsDict.ContainsKey(kvp.Key))
                {
                    Vector3 interpolated = Vector3.Lerp(prevPositionsDict[kvp.Key], positionsDict[kvp.Key], dt);
                    carsDict[kvp.Key].transform.localPosition = new Vector3(interpolated.x, prevPositionsDict[kvp.Key].y ,interpolated.z);
                } 
                // Si no se encuentra, entonces solo se coloca el automóvil en la coordenada correcta
                else
                {
                    carsDict[kvp.Key].transform.localPosition = new Vector3(positionsDict[kvp.Key].x,carsDict[kvp.Key].transform.position.y, positionsDict[kvp.Key].z);
                    // cars[s].transform.position.y
                }
            }
            // Se itera para eliminar los automóviles que salen
            foreach(KeyValuePair<int,Vector3> kvp in prevPositionsDict)
            {
                if(!positionsDict.ContainsKey(kvp.Key))
                {
                    Destroy(carsDict[kvp.Key]);
                    orientationsDict.Remove(kvp.Key);
                    carsDict.Remove(kvp.Key);
                }
            }
            prevPositionsDict = positionsDict;
            positionsDict = new Dictionary<int, Vector3>();
        }


        // // Actualizar posiciones de los autos
        // if (positions.Count > 1)
        // {
        //     // Actualiza las direcciones
        //     for (int s = 0; s < cars.Count; s++)
        //     {
        //         // longitud de positions[-1]
        //         // Positions [-2]
        //         // Get the last position for s

        //         if ( s <  positions[positions.Count - 2].Count)
        //         {
        //             List<Vector3> last = positions[positions.Count - 1];
        //             // Get the previous to last position for s
        //             List<Vector3> prevLast = positions[positions.Count - 2];
        //             // Interpolate using dt
        //             Vector3 interpolated = Vector3.Lerp(prevLast[s], last[s], dt);
        //             cars[s].transform.localPosition = new Vector3(interpolated.x,cars[s].transform.position.y,interpolated.z);
        //             Vector3 dir = last[s] - prevLast[s];
        //             cars[s].transform.rotation = Quaternion.LookRotation(dir);
        //         }
        //         else
        //         {
        //             Vector3 n = positions[positions.Count-1][s];
        //             cars[s].transform.localPosition = new Vector3(n.x,cars[s].transform.position.y,n.z);
        //         }
        //     }
        // }
        // if(positions.Count > 3)
        // {
        //     positions.RemoveAt(0);
        // }
    }
}
