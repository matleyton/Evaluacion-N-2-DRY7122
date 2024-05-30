import requests
import urllib.parse

geocode_url = "https://graphhopper.com/api/1/geocode?"
route_url = "https://graphhopper.com/api/1/route?"
key = "e35861dd-b8d6-4808-bf37-1f835a44cf05"  # Reemplaza esto con tu clave API

def geocoding(location, key):
    url = geocode_url + urllib.parse.urlencode({"q": location, "limit": "1", "key": key})
    
    try:
        replydata = requests.get(url)
        replydata.raise_for_status()  # Verificar si la solicitud fue exitosa
        json_data = replydata.json()

        if 'hits' in json_data and len(json_data['hits']) > 0:
            lat = json_data["hits"][0]["point"]["lat"]
            lng = json_data["hits"][0]["point"]["lng"]
            return 200, lat, lng
        else:
            print(f"No se encontraron resultados para {location}.")
            return 404, None, None
    except requests.exceptions.RequestException as e:
        print(f"Error en la solicitud HTTP: {e}")
        return 500, None, None

def calcular_distancia_duracion_indicaciones(origen, destino, key):
    # Geocodificar origen y destino
    orig_status, orig_lat, orig_lng = geocoding(origen, key)
    dest_status, dest_lat, dest_lng = geocoding(destino, key)

    if orig_status != 200 or dest_status != 200:
        print("Error en la geocodificación. No se puede calcular la distancia y duración.")
        return None, None, None

    print(f"Coordenadas de origen: latitud {orig_lat}, longitud {orig_lng}")
    print(f"Coordenadas de destino: latitud {dest_lat}, longitud {dest_lng}")

    # Construir la URL de la ruta entre origen y destino
    route_params = {
        "point": [f"{orig_lat},{orig_lng}", f"{dest_lat},{dest_lng}"],
        "vehicle": "car",  # Modo de transporte: coche
        "key": key,
        "instructions": "true",  # Incluir instrucciones detalladas
        "locale": "es"  # Instrucciones en español
    }
    
    try:
        route_response = requests.get(route_url, params=route_params)
        route_response.raise_for_status()
        route_data = route_response.json()

        if 'paths' not in route_data or len(route_data['paths']) == 0:
            print("No se encontró una ruta válida entre los puntos.")
            return None, None, None

        # Extraer la distancia y duración de la ruta
        distance_meters = route_data['paths'][0]['distance']
        duration_seconds = route_data['paths'][0]['time'] / 1000  # Convertir de milisegundos a segundos
        instrucciones = route_data['paths'][0]['instructions']  # Instrucciones de la ruta
        
        distance_km = distance_meters / 1000  # Convertir a kilómetros
        duration_hms = convertir_duracion(duration_seconds)
        
        return distance_km, duration_hms, instrucciones
    except requests.exceptions.RequestException as e:
        print(f"Error en la solicitud HTTP para la ruta: {e}")
        return None, None, None

def convertir_duracion(segundos):
    horas = int(segundos // 3600)
    minutos = int((segundos % 3600) // 60)
    segundos = int(segundos % 60)
    return f"{horas:02}:{minutos:02}:{segundos:02}"

def generar_narrativa(origen, destino, distancia, duracion, instrucciones):
    narrativa = (f"El viaje desde {origen} hasta {destino} cubre una distancia de aproximadamente {distancia:.2f} kilómetros. "
                 f"La duración estimada del viaje es de {duracion} (horas:minutos:segundos). "
                 "Aquí están las indicaciones detalladas:\n")
    for instruccion in instrucciones:
        distancia_instruccion = instruccion['distance'] / 1000  # Convertir a kilómetros
        narrativa += f"{instruccion['text']} durante {distancia_instruccion:.2f} kilómetros.\n"
    return narrativa

def calcular_consumo_combustible(kilometros_recorridos, litros_por_100km=10):
    consumo_combustible = (kilometros_recorridos / 100) * litros_por_100km
    return consumo_combustible

def generar_narrativa_consumo(consumo_combustible):
    return f"Consumo de combustible estimado para el viaje: {consumo_combustible:.2f} litros."

# Bucle principal para solicitar origen y destino hasta que el usuario escriba "q"
while True:
    origen = input("Ingrese el origen (o escriba 'q' para terminar): ")
    if origen.lower() == "q":
        break
    destino = input("Ingrese el destino (o escriba 'q' para terminar): ")
    if destino.lower() == "q":
        break

    # Calcular la distancia, duración y obtener las indicaciones entre el origen y el destino proporcionados por el usuario
    distancia, duracion, instrucciones = calcular_distancia_duracion_indicaciones(origen, destino, key)

    if distancia is not None and duracion is not None and instrucciones is not None:
        narrativa = generar_narrativa(origen, destino, distancia, duracion, instrucciones)
        print(narrativa)
        
        # Calcular y mostrar el consumo de combustible
        consumo_combustible = calcular_consumo_combustible(distancia)
        narrativa_consumo = generar_narrativa_consumo(consumo_combustible)
        print(narrativa_consumo)