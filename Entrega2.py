"""
-----------------------------------------------------------------------------------------------
Título: Sistema de gestión hotelera - Entrega 2
Fecha: 03/07/2025
Autor: Equipo 5

Descripción:
Este programa permite gestionar huéspedes, habitaciones y reservas en un hotel.
Incluye operaciones de alta, baja lógica y modificación de datos, así como la generación 
de informes, todo a través de menús multinivel intuitivos.
Los datos se persisten en archivos JSON con control de excepciones y validación
de email mediante expresiones regulares.

IMPORTANTE: Los archivos huespedes.json, habitaciones.json y reservas.json deben estar 
presentes en la misma carpeta que este archivo para que el sistema funcione correctamente.
-----------------------------------------------------------------------------------------------
"""

#----------------------------------------------------------------------------------------------
# MÓDULOS
#----------------------------------------------------------------------------------------------
import datetime
import json
import re
import random
import string

#----------------------------------------------------------------------------------------------
# FUNCIONES
#----------------------------------------------------------------------------------------------
def generar_id_reserva(reservas):
    """Genera un ID único tipo RSVxxxnnn para la reserva."""
    while True:
        numeros = ''.join(random.choices(string.digits, k=3))
        letras = ''.join(random.choices(string.ascii_uppercase, k=3))
        rid = f"RSV{numeros}{letras}"
        if rid not in reservas:
            return rid

def input_int(msg):
    """Solicita un entero por consola, validando la entrada."""
    while True:
        dato = input(msg)
        if dato.isdigit():
            return int(dato)
        print("Ingrese un número válido.")

def input_float(msg):
    """Solicita un número flotante por consola, validando la entrada."""
    while True:
        dato = input(msg).strip()
        # Permite un signo negativo opcional y un punto decimal.
        temp_dato = dato
        if dato.startswith('-'):
            temp_dato = dato[1:]
        
        if temp_dato.count('.') <= 1 and temp_dato.replace('.', '', 1).isdigit():
            return float(dato)
        
        print("Ingrese un valor numérico.")

def input_email(msg):
    """Solicita un email por consola, validando su formato básico."""
    while True:
        email = input(msg).strip()
        # Validación simple: contiene un '@' y al menos un '.' después del '@'.
        partes = email.split('@')
        if len(partes) == 2 and partes[0] and partes[1] and '.' in partes[1]:
            return email
        print("Ingrese un email válido.")

def input_opciones(msg, opciones):
    """Solicita una opción válida de un conjunto dado."""
    while True:
        op = input(msg)
        if op in opciones:
            return op
        print(f"Opción inválida. Opciones válidas: {', '.join(opciones)}")

def es_fecha_valida(dia, mes, anio):
    """Chequea si una fecha es válida (ej: que no sea 31 de abril)."""
    if not (1 <= mes <= 12):
        return False
    
    dias_por_mes = [0, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    
    # Manejo de año bisiesto
    if (anio % 4 == 0 and anio % 100 != 0) or (anio % 400 == 0):
        dias_por_mes[2] = 29
        
    if not (1 <= dia <= dias_por_mes[mes]):
        return False
        
    return True

def validar_email_regex(email):
    """Valida el email usando una expresión regular estricta."""
    pat = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
    return re.match(pat, email) is not None

def validar_dni(dni):
    """Valida que el DNI tenga entre 6 y 8 caracteres numéricos."""
    if isinstance(dni, int):
        dni = str(dni)
    return dni.isdigit() and 6 <= len(dni) <= 8

def validar_telefono(telefono):
    """Valida que el teléfono tenga entre 7 y 15 caracteres numéricos."""
    if isinstance(telefono, int):
        telefono = str(telefono)
    return telefono.isdigit() and 7 <= len(telefono) <= 15

def validar_id_huesped(idh):
    """Valida que el ID del huésped tenga entre 2 y 6 caracteres."""
    return 2 <= len(idh) <= 6

def validar_nombre_apellido(texto):
    """Valida que el nombre o apellido tenga entre 2 y 20 caracteres y solo contenga letras y espacios."""
    texto_limpio = texto.strip()
    if not (2 <= len(texto_limpio) <= 20):
        return False
    # Verificar que solo contenga letras y espacios
    for caracter in texto_limpio:
        if not (caracter.isalpha() or caracter.isspace()):
            return False
    # Verificar que no sea solo espacios
    if texto_limpio.replace(" ", "") == "":
        return False
    return True

def input_id_huesped(msg):
    """Solicita un ID de huésped válido por consola, validando la entrada."""
    while True:
        idh = input(msg).strip()
        if validar_id_huesped(idh):
            return idh
        print("ID inválido. Debe tener entre 2 y 6 caracteres.")

def input_nombre_apellido(msg):
    """Solicita un nombre o apellido válido por consola, validando la entrada."""
    while True:
        texto = input(msg).strip()
        if validar_nombre_apellido(texto):
            return texto
        print("Nombre/Apellido inválido. Debe tener entre 2 y 20 caracteres y solo contener letras.")

def input_dni(msg):
    """Solicita un DNI válido por consola, validando la entrada."""
    while True:
        dni = input(msg).strip()
        if validar_dni(dni):
            dni_int = int(dni)
            if dni_int < 0:
                print("DNI inválido. No puede ser negativo.")
                continue
            return dni_int
        print("DNI inválido. Debe tener entre 6 y 8 dígitos numéricos.")

def input_telefono(msg):
    """Solicita un teléfono válido por consola, validando la entrada."""
    while True:
        telefono = input(msg).strip()
        if validar_telefono(telefono):
            telefono_int = int(telefono)
            if telefono_int < 0:
                print("Teléfono inválido. No puede ser negativo.")
                continue
            return telefono_int
        print("Teléfono inválido. Debe tener entre 7 y 15 dígitos numéricos.")

def input_email_validado(msg):
    """Solicita un email válido por consola, validando su formato con regex."""
    while True:
        email = input(msg).strip()
        if validar_email_regex(email):
            return email
        print("Email inválido. Debe contener @ y tener un formato válido.")

def input_medio_pago(msg):
    """Solicita un medio de pago válido de las opciones disponibles."""
    opciones_validas = ["Efectivo", "Tarjeta", "Transferencia", "Débito", "Crédito"]
    while True:
        medio = input(msg).strip()
        # Normalizar el input: convertir a minúsculas y remover acentos
        medio_normalizado = medio.lower()
        # Mapeo de variaciones comunes sin acentos
        mapeo_variaciones = {
            "efectivo": "Efectivo",
            "tarjeta": "Tarjeta", 
            "transferencia": "Transferencia",
            "debito": "Débito",
            "débito": "Débito",
            "credito": "Crédito",
            "crédito": "Crédito"
        }
        
        if medio in opciones_validas:
            return medio
        elif medio_normalizado in mapeo_variaciones:
            return mapeo_variaciones[medio_normalizado]
        else:
            print(f"Medio de pago inválido. Opciones válidas: {', '.join(opciones_validas)}")

def normalizar_texto(texto):
    """Normaliza texto removiendo acentos y convirtiendo a minúsculas."""
    mapeo_acentos = {
        'á': 'a', 'é': 'e', 'í': 'i', 'ó': 'o', 'ú': 'u', 'ü': 'u', 'ñ': 'n',
        'Á': 'A', 'É': 'E', 'Í': 'I', 'Ó': 'O', 'Ú': 'U', 'Ü': 'U', 'Ñ': 'N'
    }
    texto_normalizado = texto
    for acento, sin_acento in mapeo_acentos.items():
        texto_normalizado = texto_normalizado.replace(acento, sin_acento)
    return texto_normalizado.lower()

#----------------------------------------------------------------------------------------------
# CRUD HUESPEDES
#----------------------------------------------------------------------------------------------
def alta_huesped(huespedes_archivo="huespedes.json"):
    """Da de alta un huésped nuevo, persistiendo en archivo JSON."""
    print("\n--- Alta de huésped ---")
    try:
        with open(huespedes_archivo, mode='r', encoding='utf-8') as f:
            huespedes = json.load(f)
    except FileNotFoundError:
        huespedes = {}
    except OSError as detalle:
        print("Error al intentar abrir archivo(s):", detalle, "¿Existe el archivo y tiene formato JSON válido?")
        return
    idh = input_id_huesped("ID del huésped: ")
    if idh in huespedes:
        print("Ya existe ese ID.")
        return
    nombre = input_nombre_apellido("Nombre: ")
    apellido = input_nombre_apellido("Apellido: ")
    documento = input_dni("DNI: ")
    email = input_email_validado("Email: ")
    telefono = input_telefono("Teléfono: ")
    medio_pago = input_medio_pago("Medio de pago: ")
    huespedes[idh] = {
        "activo": True,
        "nombre": nombre,
        "apellido": apellido,
        "documento": documento,
        "email": email,
        "telefono": telefono,
        "mediosDePago": [medio_pago]
    }
    try:
        with open(huespedes_archivo, mode='w', encoding='utf-8') as f:
            json.dump(huespedes, f, ensure_ascii=False, indent=4)
        print(f"Huésped {nombre} {apellido} agregado correctamente.")
    except (FileNotFoundError, OSError) as detalle:
        print("Error al intentar guardar archivo(s):", detalle)

def modificar_huesped(huespedes_archivo="huespedes.json"):
    """Permite modificar todos los datos de un huésped activo, persistiendo en archivo JSON."""
    print("\n--- Modificar huésped ---")
    try:
        with open(huespedes_archivo, mode='r', encoding='utf-8') as f:
            huespedes = json.load(f)
    except FileNotFoundError:
        print("El archivo de huéspedes no existe. No hay datos para modificar.")
        return
    except OSError as detalle:
        print("Error al intentar abrir archivo(s):", detalle, "¿Existe el archivo y tiene formato JSON válido?")
        return
    idh = input_id_huesped("ID del huésped a modificar: ")
    if idh in huespedes and huespedes[idh]["activo"]:
        print("Deje vacío para no modificar ese campo.")
        for campo in ["nombre", "apellido", "documento", "email", "telefono"]:
            actual = huespedes[idh][campo]
            while True:
                nuevo = input(f"Nuevo {campo} (actual: {actual}): ").strip()
                if not nuevo:  # Si está vacío, no modificar
                    break
                if campo in ["nombre", "apellido"]:
                    if validar_nombre_apellido(nuevo):
                        huespedes[idh][campo] = nuevo
                        break
                    else:
                        print("Nombre/Apellido inválido. Debe tener entre 2 y 20 caracteres y solo contener letras.")
                elif campo == "documento":
                    if validar_dni(nuevo):
                        nuevo = int(nuevo)
                        if nuevo < 0:
                            print("DNI inválido. No puede ser negativo.")
                            continue
                        huespedes[idh][campo] = nuevo
                        break
                    else:
                        print("DNI inválido. Debe tener entre 6 y 8 dígitos numéricos.")
                elif campo == "telefono":
                    if validar_telefono(nuevo):
                        nuevo = int(nuevo)
                        if nuevo < 0:
                            print("Teléfono inválido. No puede ser negativo.")
                            continue
                        huespedes[idh][campo] = nuevo
                        break
                    else:
                        print("Teléfono inválido. Debe tener entre 7 y 15 dígitos numéricos.")
                elif campo == "email":
                    if validar_email_regex(nuevo):
                        huespedes[idh][campo] = nuevo
                        break
                    else:
                        print("Email inválido. Debe contener @ y tener un formato válido.")
        mp_actual = ', '.join(huespedes[idh]["mediosDePago"])
        while True:
            nuevo_mp = input(f"Nuevo medio de pago (actual: {mp_actual}): ").strip()
            if not nuevo_mp:  # Si está vacío, no modificar
                break
            opciones_validas = ["Efectivo", "Tarjeta", "Transferencia", "Débito", "Crédito"]
            # Normalizar el input: convertir a minúsculas y remover acentos
            nuevo_mp_normalizado = nuevo_mp.lower()
            # Mapeo de variaciones comunes sin acentos
            mapeo_variaciones = {
                "efectivo": "Efectivo",
                "tarjeta": "Tarjeta", 
                "transferencia": "Transferencia",
                "debito": "Débito",
                "débito": "Débito",
                "credito": "Crédito",
                "crédito": "Crédito"
            }
            
            if nuevo_mp in opciones_validas:
                huespedes[idh]["mediosDePago"] = [nuevo_mp]
                break
            elif nuevo_mp_normalizado in mapeo_variaciones:
                huespedes[idh]["mediosDePago"] = [mapeo_variaciones[nuevo_mp_normalizado]]
                break
            else:
                print(f"Medio de pago inválido. Opciones válidas: {', '.join(opciones_validas)}.")
        try:
            with open(huespedes_archivo, mode='w', encoding='utf-8') as f:
                json.dump(huespedes, f, ensure_ascii=False, indent=4)
            print("Huésped modificado correctamente.")
        except (FileNotFoundError, OSError) as detalle:
            print("Error al intentar guardar archivo(s):", detalle)
    else:
        print("No existe o está inactivo.")

def inactivar_huesped(huespedes_archivo="huespedes.json"):
    """Realiza la baja lógica de un huésped activo, persistiendo en archivo JSON."""
    print("\n--- Eliminar (baja lógica) huésped ---")
    try:
        with open(huespedes_archivo, mode='r', encoding='utf-8') as f:
            huespedes = json.load(f)
    except FileNotFoundError:
        print("El archivo de huéspedes no existe. No hay datos para modificar.")
        return
    except OSError as detalle:
        print("Error al intentar abrir archivo(s):", detalle, "¿Existe el archivo y tiene formato JSON válido?")
        return
    idh = input_id_huesped("ID del huésped a inactivar: ")
    if idh not in huespedes:
        print("No existe un huésped con ese ID.")
        return
    if not huespedes[idh]["activo"]:
        print("El huésped ya está inactivo.")
        return
    nombre = huespedes[idh]['nombre'] + ' ' + huespedes[idh]['apellido']
    confirm = input_opciones(f"¿Está seguro de inactivar a {nombre}? (s/n): ", ["s", "n"])
    if confirm == "s":
        huespedes[idh]["activo"] = False
        try:
            with open(huespedes_archivo, mode='w', encoding='utf-8') as f:
                json.dump(huespedes, f, ensure_ascii=False, indent=4)
            print("Huésped inactivado.")
        except (FileNotFoundError, OSError) as detalle:
            print("Error al intentar guardar archivo(s):", detalle)
    else:
        print("Operación cancelada.")

def listar_huespedes_activos(huespedes_archivo="huespedes.json"):
    """Lista todos los huéspedes activos leyendo desde archivo JSON, con formato tabular alineado."""
    print("\n--- Lista de huéspedes activos ---")
    try:
        with open(huespedes_archivo, mode='r', encoding='utf-8') as f:
            huespedes = json.load(f)
    except FileNotFoundError:
        print("El archivo de huéspedes no existe. No hay datos para mostrar.")
        return
    except OSError as detalle:
        print("Error al intentar abrir archivo(s):", detalle, "¿Existe el archivo y tiene formato JSON válido?")
        return
    encabezado = f"{'ID':<4} | {'Nombre':<12} | {'Apellido':<12} | {'DNI':<9} | {'Email':<35} | {'Teléfono':<12} | {'Pago':<15}"
    print("-" * len(encabezado))
    print(encabezado)
    print("-" * len(encabezado))
    hay_activos = False
    for idh, datos in huespedes.items():
        if datos["activo"]:
            print(f"{idh:<4} | {datos['nombre']:<12} | {datos['apellido']:<12} | {str(datos['documento']):<9} | {datos['email']:<35} | {str(datos['telefono']):<12} | {', '.join(datos['mediosDePago']):<15}")
            hay_activos = True
    if not hay_activos:
        print("No hay huéspedes activos.")
    print("-" * len(encabezado))

def buscar_huespedes(huespedes_archivo="huespedes.json"):
    print("\n--- Buscar huésped por nombre o apellido ---")
    try:
        with open(huespedes_archivo, mode='r', encoding='utf-8') as f:
            huespedes = json.load(f)
    except FileNotFoundError:
        print("El archivo de huéspedes no existe. No hay datos para buscar.")
        return
    except OSError as detalle:
        print("Error al intentar abrir archivo(s):", detalle, "¿Existe el archivo y tiene formato JSON válido?")
        return
    termino = input("Ingrese nombre o apellido a buscar: ").strip()
    termino_normalizado = normalizar_texto(termino)
    encontrados = []
    for idh, d in huespedes.items():
        if d["activo"]:
            nombre_normalizado = normalizar_texto(d["nombre"])
            apellido_normalizado = normalizar_texto(d["apellido"])
            if (termino_normalizado in nombre_normalizado or 
                termino_normalizado in apellido_normalizado):
                encontrados.append((idh, d))
    if encontrados:
        encabezado = f"{'ID':<4} | {'Nombre':<12} | {'Apellido':<12} | {'DNI':<35} | {'Email':<35} | {'Teléfono':<12} | {'Pago':<15}"
        print("-" * len(encabezado))
        print(encabezado)
        print("-" * len(encabezado))
        for idh, datos in encontrados:
            print(f"{idh:<4} | {datos['nombre']:<12} | {datos['apellido']:<12} | {str(datos['documento']):<35} | {datos['email']:<35} | {str(datos['telefono']):<12} | {', '.join(datos['mediosDePago']):<15}")
        print("-" * len(encabezado))
    else:
        print("No se encontraron huéspedes con ese nombre o apellido.")

#----------------------------------------------------------------------------------------------
# CRUD HABITACIONES
#----------------------------------------------------------------------------------------------
def alta_habitacion(habitaciones_archivo="habitaciones.json"):
    """Da de alta una habitación nueva, persistiendo en archivo JSON."""
    print("\n--- Alta de habitación ---")
    try:
        with open(habitaciones_archivo, mode='r', encoding='utf-8') as f:
            habitaciones = json.load(f)
    except FileNotFoundError:
        habitaciones = {}
    except OSError as detalle:
        print("Error al intentar abrir archivo(s):", detalle, "¿Existe el archivo y tiene formato JSON válido?")
        return
    # ID habitación
    while True:
        idh = input("ID habitación: ").strip()
        if not (2 <= len(idh) <= 6 and idh.isalnum()):
            print("ID inválido. Debe tener entre 2 y 6 caracteres, solo letras y números.")
            continue
        if idh in habitaciones:
            print("ID ya existe.")
            continue
        break
    # Número habitación
    while True:
        numero = input("Número de habitación: ").strip()
        if not (numero.isdigit() and 1 <= len(numero) <= 6):
            print("Número inválido. Debe tener entre 1 y 6 dígitos numéricos.")
            continue
        numero = int(numero)
        if numero < 0:
            print("Número de habitación inválido. No puede ser negativo.")
            continue
        break
    # Tipo habitación
    tipos_validos = ["Simple", "Doble", "Triple", "Suite", "Familiar"]
    tipos_normalizados = [normalizar_texto(t) for t in tipos_validos]
    while True:
        tipo = input(f"Tipo ({', '.join(tipos_validos)}): ").strip()
        tipo_norm = normalizar_texto(tipo)
        if tipo_norm not in tipos_normalizados:
            print(f"Tipo inválido. Opciones válidas: {', '.join(tipos_validos)}.")
            continue
        tipo = tipos_validos[tipos_normalizados.index(tipo_norm)]
        break
    # Descripción
    while True:
        descripcion = input("Descripción: ").strip()
        if not (5 <= len(descripcion) <= 25):
            print("Descripción inválida. Debe tener entre 5 y 25 caracteres.")
            continue
        if not re.fullmatch(r'[a-zA-Z0-9,. ]+', descripcion):
            print("Descripción inválida. Solo puede contener letras, números, comas, puntos y espacios.")
            continue
        break
    # Precio por noche
    while True:
        precio = input("Precio por noche: ").strip()
        if not (precio.replace('.', '', 1).isdigit() and 1 <= len(precio) <= 8):
            print("Precio inválido. Debe ser numérico, entre 1 y 8 caracteres.")
            continue
        precio = float(precio)
        if precio < 0:
            print("Precio inválido. No puede ser negativo.")
            continue
        break
    # Piso
    while True:
        piso = input("Piso: ").strip()
        if not (piso.isdigit() and 1 <= len(piso) <= 3):
            print("Piso inválido. Debe ser numérico, entre 1 y 3 caracteres.")
            continue
        piso = int(piso)
        if piso < 0:
            print("Piso inválido. No puede ser negativo.")
            continue
        break
    # Estado
    estados_validos = ["Disponible", "Ocupada", "Mantenimiento"]
    estados_normalizados = [normalizar_texto(e) for e in estados_validos]
    while True:
        estado = input(f"Estado ({', '.join(estados_validos)}): ").strip()
        estado_norm = normalizar_texto(estado)
        if estado_norm not in estados_normalizados:
            print(f"Estado inválido. Opciones válidas: {', '.join(estados_validos)}.")
            continue
        estado = estados_validos[estados_normalizados.index(estado_norm)]
        break
    # Servicios incluidos
    while True:
        servicios = input("Servicios incluidos (separados por coma): ").strip()
        if not (2 <= len(servicios) <= 50):
            print("Servicios inválidos. Debe tener entre 2 y 50 caracteres.")
            continue
        break
    habitaciones[idh] = {
        "activo": True,
        "numero": numero,
        "tipo": tipo,
        "descripcion": descripcion,
        "precioNoche": precio,
        "piso": piso,
        "estado": estado,
        "serviciosIncluidos": servicios
    }
    try:
        with open(habitaciones_archivo, mode='w', encoding='utf-8') as f:
            json.dump(habitaciones, f, ensure_ascii=False, indent=4)
        print(f"Habitación {numero} agregada correctamente.")
    except (FileNotFoundError, OSError) as detalle:
        print("Error al intentar guardar archivo(s):", detalle)

def modificar_habitacion(habitaciones_archivo="habitaciones.json"):
    """Permite modificar todos los datos de una habitación activa, persistiendo en archivo JSON."""
    print("\n--- Modificar habitación ---")
    try:
        with open(habitaciones_archivo, mode='r', encoding='utf-8') as f:
            habitaciones = json.load(f)
    except FileNotFoundError:
        print("El archivo de habitaciones no existe. No hay datos para modificar.")
        return
    except OSError as detalle:
        print("Error al intentar abrir archivo(s):", detalle, "¿Existe el archivo y tiene formato JSON válido?")
        return
    idh = input("ID habitación a modificar: ").strip()
    if idh in habitaciones and habitaciones[idh]["activo"]:
        print("Deje vacío para no modificar ese campo.")
        for campo in ["numero", "tipo", "descripcion", "precioNoche", "piso", "estado", "serviciosIncluidos"]:
            actual = habitaciones[idh][campo]
            while True:
                nuevo = input(f"Nuevo {campo} (actual: {actual}): ").strip()
                if not nuevo:
                    break
                if campo == "numero":
                    if not (nuevo.isdigit() and 1 <= len(nuevo) <= 6):
                        print("Número inválido. Debe tener entre 1 y 6 dígitos numéricos.")
                        continue
                    nuevo = int(nuevo)
                    if nuevo < 0:
                        print("Número de habitación inválido. No puede ser negativo.")
                        continue
                elif campo == "tipo":
                    tipos_validos = ["Simple", "Doble", "Triple", "Suite", "Familiar"]
                    tipos_normalizados = [normalizar_texto(t) for t in tipos_validos]
                    tipo_norm = normalizar_texto(nuevo)
                    if tipo_norm not in tipos_normalizados:
                        print(f"Tipo inválido. Opciones válidas: {', '.join(tipos_validos)}.")
                        continue
                    nuevo = tipos_validos[tipos_normalizados.index(tipo_norm)]
                elif campo == "descripcion":
                    if not (5 <= len(nuevo) <= 25):
                        print("Descripción inválida. Debe tener entre 5 y 25 caracteres.")
                        continue
                    if not re.fullmatch(r'[a-zA-Z0-9,. ]+', nuevo):
                        print("Descripción inválida. Solo puede contener letras, números, comas, puntos y espacios.")
                        continue
                elif campo == "precioNoche":
                    if not (nuevo.replace('.', '', 1).isdigit() and 1 <= len(nuevo) <= 8):
                        print("Precio inválido. Debe ser numérico, entre 1 y 8 caracteres.")
                        continue
                    nuevo = float(nuevo)
                    if nuevo < 0:
                        print("Precio inválido. No puede ser negativo.")
                        continue
                elif campo == "piso":
                    if not (nuevo.isdigit() and 1 <= len(nuevo) <= 3):
                        print("Piso inválido. Debe ser numérico, entre 1 y 3 caracteres.")
                        continue
                    nuevo = int(nuevo)
                    if nuevo < 0:
                        print("Piso inválido. No puede ser negativo.")
                        continue
                elif campo == "estado":
                    estados_validos = ["Disponible", "Ocupada", "Mantenimiento"]
                    estados_normalizados = [normalizar_texto(e) for e in estados_validos]
                    estado_norm = normalizar_texto(nuevo)
                    if estado_norm not in estados_normalizados:
                        print(f"Estado inválido. Opciones válidas: {', '.join(estados_validos)}.")
                        continue
                    nuevo = estados_validos[estados_normalizados.index(estado_norm)]
                elif campo == "serviciosIncluidos":
                    if not (2 <= len(nuevo) <= 50):
                        print("Servicios inválidos. Debe tener entre 2 y 50 caracteres.")
                        continue
                habitaciones[idh][campo] = nuevo
                break
        try:
            with open(habitaciones_archivo, mode='w', encoding='utf-8') as f:
                json.dump(habitaciones, f, ensure_ascii=False, indent=4)
            print("Habitación modificada correctamente.")
        except (FileNotFoundError, OSError) as detalle:
            print("Error al intentar guardar archivo(s):", detalle)
    else:
        print("No existe o está inactiva.")

def inactivar_habitacion(habitaciones_archivo="habitaciones.json"):
    """Realiza la baja lógica de una habitación activa, persistiendo en archivo JSON."""
    print("\n--- Eliminar (baja lógica) habitación ---")
    try:
        with open(habitaciones_archivo, mode='r', encoding='utf-8') as f:
            habitaciones = json.load(f)
    except FileNotFoundError:
        print("El archivo de habitaciones no existe. No hay datos para modificar.")
        return
    except OSError as detalle:
        print("Error al intentar abrir archivo(s):", detalle, "¿Existe el archivo y tiene formato JSON válido?")
        return
    idh = input("ID habitación a inactivar: ").strip()
    if idh not in habitaciones:
        print("No existe una habitación con ese ID.")
        return
    if not habitaciones[idh]["activo"]:
        print("La habitación ya está inactiva.")
        return
    numero = habitaciones[idh]['numero']
    confirm = input_opciones(f"¿Está seguro de inactivar la habitación {numero}? (s/n): ", ["s", "n"])
    if confirm == "s":
        habitaciones[idh]["activo"] = False
        try:
            with open(habitaciones_archivo, mode='w', encoding='utf-8') as f:
                json.dump(habitaciones, f, ensure_ascii=False, indent=4)
            print("Habitación inactivada.")
        except (FileNotFoundError, OSError) as detalle:
            print("Error al intentar guardar archivo(s):", detalle)
    else:
        print("Operación cancelada.")

def listar_habitaciones_activas(habitaciones_archivo="habitaciones.json"):
    """Lista todas las habitaciones activas leyendo desde archivo JSON, con formato tabular alineado."""
    print("\n--- Lista de habitaciones activas ---")
    try:
        with open(habitaciones_archivo, mode='r', encoding='utf-8') as f:
            habitaciones = json.load(f)
    except FileNotFoundError:
        print("El archivo de habitaciones no existe. No hay datos para mostrar.")
        return
    except OSError as detalle:
        print("Error al intentar abrir archivo(s):", detalle, "¿Existe el archivo y tiene formato JSON válido?")
        return
    encabezado = f"{'ID':<12} | {'Nro':<8} | {'Tipo':<10} | {'Piso':<4} | {'Estado':<12} | {'Precio':<10} | {'Servicios':<20}"
    print("-" * len(encabezado))
    print(encabezado)
    print("-" * len(encabezado))
    hay_activas = False
    for idh, datos in habitaciones.items():
        if datos["activo"]:
            print(f"{idh:<12} | {str(datos['numero']):<8} | {datos['tipo']:<10} | {str(datos['piso']):<4} | {datos['estado']:<12} | ${datos['precioNoche']:<9.2f} | {datos['serviciosIncluidos']:<20}")
            hay_activas = True
    if not hay_activas:
        print("No hay habitaciones activas.")
    print("-" * len(encabezado))

def buscar_habitaciones(habitaciones_archivo="habitaciones.json"):
    print("\n--- Buscar habitación por tipo o estado ---")
    try:
        with open(habitaciones_archivo, mode='r', encoding='utf-8') as f:
            habitaciones = json.load(f)
    except FileNotFoundError:
        print("El archivo de habitaciones no existe. No hay datos para buscar.")
        return
    except OSError as detalle:
        print("Error al intentar abrir archivo(s):", detalle, "¿Existe el archivo y tiene formato JSON válido?")
        return
    termino = input("Ingrese tipo o estado a buscar: ").strip().lower()
    encontrados = [ (idh, d) for idh, d in habitaciones.items() if d["activo"] and (termino in d["tipo"].lower() or termino in d["estado"].lower()) ]
    if encontrados:
        encabezado = f"{'ID':<12} | {'Nro':<8} | {'Tipo':<10} | {'Piso':<4} | {'Estado':<12} | {'Precio':<10} | {'Servicios':<20}"
        print("-" * len(encabezado))
        print(encabezado)
        print("-" * len(encabezado))
        for idh, datos in encontrados:
            print(f"{idh:<12} | {str(datos['numero']):<8} | {datos['tipo']:<10} | {str(datos['piso']):<4} | {datos['estado']:<12} | ${datos['precioNoche']:<9.2f} | {datos['serviciosIncluidos']:<20}")
        print("-" * len(encabezado))
    else:
        print("No se encontraron habitaciones con ese tipo o estado.")

#----------------------------------------------------------------------------------------------
# TRANSACCIONES - RESERVAS
#----------------------------------------------------------------------------------------------
def solapa_reserva(reservas, id_hab, fecha_inicio_nueva, fecha_fin_nueva):
    """
    Revisa si una habitación ya está reservada en un rango de fechas.
    Compara la nueva reserva con las existentes para evitar solapamientos.
    Devuelve True si se solapa, False si está libre.
    """
    for datos in reservas.values():
        if datos["idhabitacion"] == id_hab:
            # Reconstruir fechas de la reserva existente a partir del formato 'DDMM'
            fe_existente_str = datos["fechaEntrada"]
            fs_existente_str = datos["fechaSalida"]
            
            # Obtener el año de la fecha de operación para contextualizar la fecha de la reserva
            anio_op_str = datos["fechaHoraOperacion"][:4]
            if not anio_op_str.isdigit():
                pass  # Omitir si el dato es inválido
            else:
                anio_op = int(anio_op_str)
                dia_e, mes_e = int(fe_existente_str[:2]), int(fe_existente_str[2:])
                dia_s, mes_s = int(fs_existente_str[:2]), int(fs_existente_str[2:])
                anio_e = anio_op
                anio_s = anio_op
                if mes_s < mes_e:
                    anio_s = anio_op + 1
                inicio_existente = datetime.datetime(anio_e, mes_e, dia_e)
                fin_existente = datetime.datetime(anio_s, mes_s, dia_s)
                if fecha_inicio_nueva < fin_existente and fecha_fin_nueva > inicio_existente:
                    return True
    return False

def registrar_reserva(huespedes, habitaciones, reservas):
    """
    Crea una reserva nueva. Pide los datos, valida que la habitación esté
    disponible en esas fechas y calcula bien las noches (incluso si cambia el año).
    Si está todo OK, la guarda.
    """
    print("\n--- Registrar reserva ---")
    id_reserva = generar_id_reserva(reservas)
    # Validar ID huésped activo
    while True:
        h = input("ID huésped: ").strip()
        if h not in huespedes or not huespedes[h]["activo"]:
            print("Huésped inválido o inactivo. Ingrese un ID de huésped activo.")
            continue
        break
    # Validar ID habitación activa
    while True:
        r = input("ID habitación: ").strip()
        if r not in habitaciones or not habitaciones[r]["activo"]:
            print("Habitación inválida o inactiva. Ingrese un ID de habitación activa.")
            continue
        break
    # Validar fecha de entrada (exactamente 4 dígitos numéricos, día y mes válidos)
    while True:
        fe_str = input("Fecha entrada (DDMM): ").strip()
        if not (fe_str.isdigit() and len(fe_str) == 4):
            print("Fecha de entrada inválida. Debe estar en formato DDMM y ser numérica, exactamente 4 dígitos.")
            continue
        dia_entrada = int(fe_str[:2])
        mes_entrada = int(fe_str[2:])
        if dia_entrada < 1 or dia_entrada > 31:
            print("Día de entrada inválido. Debe estar entre 01 y 31.")
            continue
        if mes_entrada < 1 or mes_entrada > 12:
            print("Mes de entrada inválido. Debe estar entre 01 y 12.")
            continue
        break
    # Validar fecha de salida (exactamente 4 dígitos numéricos, día y mes válidos)
    while True:
        fs_str = input("Fecha salida (DDMM): ").strip()
        if not (fs_str.isdigit() and len(fs_str) == 4):
            print("Fecha de salida inválida. Debe estar en formato DDMM y ser numérica, exactamente 4 dígitos.")
            continue
        dia_salida = int(fs_str[:2])
        mes_salida = int(fs_str[2:])
        if dia_salida < 1 or dia_salida > 31:
            print("Día de salida inválido. Debe estar entre 01 y 31.")
            continue
        if mes_salida < 1 or mes_salida > 12:
            print("Mes de salida inválido. Debe estar entre 01 y 12.")
            continue
        break

    # Calcular fechas correctamente usando el año actual y manejando el cruce de año
    hoy = datetime.datetime.now()
    anio_actual = hoy.year

    anio_entrada = anio_actual
    anio_salida = anio_actual
    # Si la fecha de salida es "menor" a la de entrada, es porque cambió el año.
    if mes_salida < mes_entrada or (mes_salida == mes_entrada and dia_salida <= dia_entrada):
        anio_salida = anio_actual + 1

    if not es_fecha_valida(dia_entrada, mes_entrada, anio_entrada) or not es_fecha_valida(dia_salida, mes_salida, anio_salida):
        print("Fecha inválida (p. ej. día 31 en un mes de 30 días).")
        return

    fecha_entrada_obj = datetime.datetime(anio_entrada, mes_entrada, dia_entrada)
    fecha_salida_obj = datetime.datetime(anio_salida, mes_salida, dia_salida)

    if fecha_salida_obj <= fecha_entrada_obj:
        print("La fecha de salida debe ser posterior a la de entrada.")
        return
        
    noches = (fecha_salida_obj - fecha_entrada_obj).days

    if solapa_reserva(reservas, r, fecha_entrada_obj, fecha_salida_obj):
        print("La habitación ya está reservada en ese rango de fechas.")
        return
    # Validar descuento entre 0 y 99
    while True:
        descuento_str = input("Descuento: ").strip()
        if not descuento_str.isdigit():
            print("Ingrese un valor numérico entero para el descuento.")
            continue
        descuento = int(descuento_str)
        if not (0 <= descuento <= 99):
            print("El descuento debe estar entre 0 y 99.")
            continue
        break
    reservas[id_reserva] = {
        "idhuesped": h,
        "idhabitacion": r,
        "fechaEntrada": fe_str,
        "fechaSalida": fs_str,
        "cantidadNoches": noches,
        "descuento": descuento,
        "fechaHoraOperacion": datetime.datetime.now().strftime("%Y.%m.%d - %H:%M:%S")
    }
    print(f"Reserva registrada con ID: {id_reserva}")

def listar_reservas(reservas, huespedes, habitaciones):
    """Muestra una lista con todas las reservas que se hicieron, con formato tabular alineado y una sola línea por reserva."""
    print("\n--- Lista de reservas ---")
    if not reservas:
        print("No hay reservas registradas.")
        return
    encabezado = f"{'ID':<12} | {'Fecha/Hora':<24} | {'Huésped':<18} | {'Habitación':<10} | {'Entrada':<8} | {'Salida':<8} | {'Noches':<6} | {'Desc.':<5}"
    print("-" * len(encabezado))
    print(encabezado)
    print("-" * len(encabezado))
    for rid, datos in reservas.items():
        h = huespedes.get(datos["idhuesped"], {"nombre": "-", "apellido": "-"})
        hab = habitaciones.get(datos["idhabitacion"], {"numero": "-"})
        print(f"{rid:<12} | {datos['fechaHoraOperacion']:<24} | {(h['nombre'] + ' ' + h['apellido']):<18} | {str(hab['numero']):<10} | {datos['fechaEntrada']:<8} | {datos['fechaSalida']:<8} | {str(datos['cantidadNoches']):<6} | {str(datos['descuento']):<5}")
    print("-" * len(encabezado))

#----------------------------------------------------------------------------------------------
# INFORMES
#----------------------------------------------------------------------------------------------
def informe_tabular_mes(reservas, huespedes, habitaciones):
    """Informe 1: Muestra un listado con las reservas del mes actual, con formato tabular alineado."""
    print("\n--- Listado de operaciones del mes en curso ---")
    hoy = datetime.datetime.now()
    mes_actual = hoy.strftime("%m")
    hay = False
    encabezado = f"{'Fecha/Hora':<20} | {'Cliente':<20} | {'Producto':<20} | {'Cant.':>5} | {'Unit.':>8} | {'Total':>10}"
    print("-" * len(encabezado))
    print(encabezado)
    print("-" * len(encabezado))
    for rid, datos in reservas.items():
        fecha = datos['fechaHoraOperacion']
        if fecha[5:7] == mes_actual:
            h = huespedes.get(datos["idhuesped"], {"nombre": "-", "apellido": "-"})
            hab = habitaciones.get(datos["idhabitacion"], {"numero": "-", "tipo": "-", "precioNoche": 0})
            total = hab["precioNoche"] * datos["cantidadNoches"] * (1 - datos["descuento"]/100)
            print(f"{fecha:<20} | {h['apellido']+', '+h['nombre']:<20} | {hab['tipo']:<20} | {datos['cantidadNoches']:>5} | {hab['precioNoche']:>8.2f} | {total:>10.2f}")
            hay = True
    if not hay:
        print("No hay operaciones en el mes actual.")
    print("-" * len(encabezado))

def informe_matriz_cantidades(reservas, habitaciones):
    """Informe 2: Muestra la cantidad de noches reservadas por mes para cada habitación, con formato tabular alineado."""
    print("\n--- Resumen de cantidad de noches reservadas por mes ---")
    anio_str = input("Ingrese el año para el informe (AAAA): ")
    if not (anio_str.isdigit() and len(anio_str) == 4):
        print("Año inválido.")
        return
    anio = int(anio_str)
    nombres_mes = ['Ene','Feb','Mar','Abr','May','Jun','Jul','Ago','Sep','Oct','Nov','Dic']
    matriz = {
        hab_id: {mes: 0 for mes in range(1, 13)} 
        for hab_id, datos in habitaciones.items() if datos["activo"]
    }
    for datos in reservas.values():
        hab_id = datos["idhabitacion"]
        if hab_id in matriz:
            fecha_op_str = datos["fechaHoraOperacion"]
            if fecha_op_str[:4].isdigit() and fecha_op_str[5:7].isdigit():
                reserva_anio = int(fecha_op_str[:4])
                reserva_mes = int(fecha_op_str[5:7])
                if reserva_anio == anio:
                    matriz[hab_id][reserva_mes] += datos["cantidadNoches"]
    encabezado = f"{'Habitación':<12} |" + ''.join([f" {nombre:>6} |" for nombre in nombres_mes])
    print("-" * len(encabezado))
    print(encabezado)
    print("-" * len(encabezado))
    for hab_id, meses in matriz.items():
        num_hab = habitaciones.get(hab_id, {}).get('numero', hab_id)
        linea = f"{str(num_hab):<12} |" + ''.join([f" {meses[mes]:6} |" for mes in range(1, 13)])
        print(linea)
    print("-" * len(encabezado))

def informe_matriz_montos(reservas, habitaciones):
    """Informe 3: Muestra la plata total facturada por mes para cada habitación, con formato tabular compacto."""
    print("\n--- Resumen de montos totales por mes ---")
    anio_str = input("Ingrese el año para el informe (AAAA): ")
    if not (anio_str.isdigit() and len(anio_str) == 4):
        print("Año inválido.")
        return
    anio = int(anio_str)
    nombres_mes = ['Ene','Feb','Mar','Abr','May','Jun','Jul','Ago','Sep','Oct','Nov','Dic']
    matriz = {
        hab_id: {mes: 0.0 for mes in range(1, 13)} 
        for hab_id, datos in habitaciones.items() if datos["activo"]
    }
    for datos in reservas.values():
        hab_id = datos["idhabitacion"]
        if hab_id in matriz and "precioNoche" in habitaciones[hab_id]:
            fecha_op_str = datos["fechaHoraOperacion"]
            if fecha_op_str[:4].isdigit() and fecha_op_str[5:7].isdigit():
                reserva_anio = int(fecha_op_str[:4])
                reserva_mes = int(fecha_op_str[5:7])
                if reserva_anio == anio:
                    monto = habitaciones[hab_id]["precioNoche"] * datos["cantidadNoches"] * (1 - datos["descuento"]/100)
                    matriz[hab_id][reserva_mes] += monto
    encabezado = f"{'Hab':<8}|" + ''.join([f"{nombre:>6}|" for nombre in nombres_mes])
    print("-" * len(encabezado))
    print(encabezado)
    print("-" * len(encabezado))
    for hab_id, meses in matriz.items():
        num_hab = habitaciones.get(hab_id, {}).get('numero', hab_id)
        linea = f"{str(num_hab):<8}|" + ''.join([f"{int(meses[mes]):6}|" for mes in range(1, 13)])
        print(linea)
    print("-" * len(encabezado))

def informe_a_eleccion(reservas, huespedes, habitaciones):
    """Informe a elección: cantidad de reservas por huésped activo, con formato tabular alineado."""
    print("\n--- Informe: Cantidad de reservas por huésped activo ---")
    conteo = {idh: 0 for idh, datos in huespedes.items() if datos["activo"]}
    for datos in reservas.values():
        h = datos["idhuesped"]
        if h in conteo:
            conteo[h] += 1
    encabezado = f"{'ID':<5} {'Nombre':<20} {'Reservas':<8}"
    print("-" * len(encabezado))
    print(encabezado)
    print("-" * len(encabezado))
    for idh, cant in conteo.items():
        nombre = huespedes[idh]["nombre"] + ' ' + huespedes[idh]["apellido"]
        print(f"{idh:<5} {nombre:<20} {cant:<8}")
    print("-" * len(encabezado))

#----------------------------------------------------------------------------------------------
# MENÚS
#----------------------------------------------------------------------------------------------
def menu_huespedes():
    """Menú de gestión de huéspedes con persistencia en JSON."""
    while True:
        print("\n[1] Ingresar huésped\n[2] Modificar huésped\n[3] Eliminar huésped\n[4] Listar huéspedes activos\n[5] Buscar huésped\n[0] Volver al menú principal")
        sub = input_opciones("Opción: ", ["1", "2", "3", "4", "5", "0"])
        if sub == "1":
            alta_huesped()
        elif sub == "2":
            modificar_huesped()
        elif sub == "3":
            inactivar_huesped()
        elif sub == "4":
            listar_huespedes_activos()
        elif sub == "5":
            buscar_huespedes()
        elif sub == "0":
            break

def menu_habitaciones():
    """Menú de gestión de habitaciones con persistencia en JSON."""
    while True:
        print("\n[1] Ingresar habitación\n[2] Modificar habitación\n[3] Eliminar habitación\n[4] Listar habitaciones activas\n[5] Buscar habitación\n[0] Volver al menú principal")
        sub = input_opciones("Opción: ", ["1", "2", "3", "4", "5", "0"])
        if sub == "1":
            alta_habitacion()
        elif sub == "2":
            modificar_habitacion()
        elif sub == "3":
            inactivar_habitacion()
        elif sub == "4":
            listar_habitaciones_activas()
        elif sub == "5":
            buscar_habitaciones()
        elif sub == "0":
            break

def menu_reservas(huespedes, habitaciones, reservas):
    """Menú de gestión de reservas."""
    while True:
        print("\n[1] Registrar reserva\n[2] Listar reservas\n[0] Volver al menú principal")
        sub = input_opciones("Opción: ", ["1", "2", "0"])
        if sub == "1":
            registrar_reserva(huespedes, habitaciones, reservas)
        elif sub == "2":
            listar_reservas(reservas, huespedes, habitaciones)
        elif sub == "0":
            break

def menu_informes(reservas, huespedes, habitaciones):
    """Menú de informes con las 4 opciones requeridas."""
    while True:
        print("\n--- MENÚ DE INFORMES ---\n[1] Listado tabular de operaciones del mes en curso\n[2] Resumen anual de cantidad de noches por habitación\n[3] Resumen anual de montos totales por habitación\n[4] Informe a elección del equipo\n[0] Volver al menú principal")
        op = input_opciones("Opción: ", ["1", "2", "3", "4", "0"])
        if op == "1":
            informe_tabular_mes(reservas, huespedes, habitaciones)
        elif op == "2":
            informe_matriz_cantidades(reservas, habitaciones)
        elif op == "3":
            informe_matriz_montos(reservas, habitaciones)
        elif op == "4":
            informe_a_eleccion(reservas, huespedes, habitaciones)
        elif op == "0":
            break

#----------------------------------------------------------------------------------------------
# CUERPO PRINCIPAL
#----------------------------------------------------------------------------------------------
def main():
    """Función principal del sistema de gestión hotelera."""
    print("\nBienvenido/a al Sistema de Gestión Hotelera\n")
    """
    huespedes = {
        "H1": {"activo": True, "nombre": "Ana", "apellido": "García", "documento": 30123456, "email": "ana.garcia@mail.com", "telefono": 1123456701, "mediosDePago": ["Efectivo"]},
        "H2": {"activo": True, "nombre": "Luis", "apellido": "Pérez", "documento": 31234567, "email": "luis.perez@mail.com", "telefono": 1123456702, "mediosDePago": ["Tarjeta"]},
        "H3": {"activo": True, "nombre": "María", "apellido": "López", "documento": 32345678, "email": "maria.lopez@mail.com", "telefono": 1123456703, "mediosDePago": ["Transferencia"]},
        "H4": {"activo": True, "nombre": "Carlos", "apellido": "Sánchez", "documento": 33456789, "email": "carlos.sanchez@mail.com", "telefono": 1123456704, "mediosDePago": ["Efectivo"]},
        "H5": {"activo": True, "nombre": "Lucía", "apellido": "Martínez", "documento": 34567890, "email": "lucia.martinez@mail.com", "telefono": 1123456705, "mediosDePago": ["Tarjeta"]},
        "H6": {"activo": True, "nombre": "Javier", "apellido": "Fernández", "documento": 35678901, "email": "javier.fernandez@mail.com", "telefono": 1123456706, "mediosDePago": ["Transferencia"]},
        "H7": {"activo": True, "nombre": "Sofía", "apellido": "Ruiz", "documento": 36789012, "email": "sofia.ruiz@mail.com", "telefono": 1123456707, "mediosDePago": ["Efectivo"]},
        "H8": {"activo": True, "nombre": "Diego", "apellido": "Torres", "documento": 37890123, "email": "diego.torres@mail.com", "telefono": 1123456708, "mediosDePago": ["Tarjeta"]},
        "H9": {"activo": True, "nombre": "Valentina", "apellido": "Ramírez", "documento": 38901234, "email": "valentina.ramirez@mail.com", "telefono": 1123456709, "mediosDePago": ["Transferencia"]},
        "H10": {"activo": True, "nombre": "Martín", "apellido": "Gómez", "documento": 39012345, "email": "martin.gomez@mail.com", "telefono": 1123456710, "mediosDePago": ["Efectivo"]}
    }
    habitaciones = {f"R{i}": {"activo": True, "numero": 100+i, "tipo": "Doble", "descripcion": "Vista al mar", "precioNoche": 10000+(i*500), "piso": i%5+1, "estado": "Disponible", "serviciosIncluidos": "WiFi"} for i in range(1, 11)}
    # Generar reservas con fechas del mes actual
    hoy = datetime.datetime.now()
    mes_actual = hoy.strftime('%m')
    anio_actual = hoy.strftime('%Y')
    reservas = {}
    for i in range(10):
        dia = str(i+1).zfill(2)
        idh = f"H{i+1}"
        idhab = f"R{i+1}"
        fecha_entrada = f"{dia}{mes_actual}"
        fecha_salida = f"{str(i+5).zfill(2)}{mes_actual}"
        fecha_hora = f"{anio_actual}.{mes_actual}.{dia} - {str(10+i).zfill(2)}:00:00"
        reservas[fecha_hora] = {
            "idhuesped": idh,
            "idhabitacion": idhab,
            "fechaEntrada": fecha_entrada,
            "fechaSalida": fecha_salida,
            "cantidadNoches": 4,
            "descuento": (i%4)*5,  # 0,5,10,15
            "fechaHoraOperacion": fecha_hora
        }
    """
    while True:
        print("\n--- MENU PRINCIPAL ---")
        print("[1] Gestión de Huéspedes")
        print("[2] Gestión de Habitaciones")
        print("[3] Gestión de Reservas")
        print("[4] Informes")
        print("[0] Salir")
        op = input_opciones("Opción: ", ["1", "2", "3", "4", "0"])
        if op == "1":
            menu_huespedes()
        elif op == "2":
            menu_habitaciones()
        elif op == "3":
            # Leer datos actualizados de los archivos antes de operar
            try:
                with open("huespedes.json", 'r', encoding='utf-8') as f:
                    huespedes = json.load(f)
                with open("habitaciones.json", 'r', encoding='utf-8') as f:
                    habitaciones = json.load(f)
                with open("reservas.json", 'r', encoding='utf-8') as f:
                    reservas = json.load(f)
            except (FileNotFoundError, OSError) as detalle:
                print("Error al intentar abrir archivo(s):", detalle)
                pass
            menu_reservas(huespedes, habitaciones, reservas)
        elif op == "4":
            try:
                with open("huespedes.json", 'r', encoding='utf-8') as f:
                    huespedes = json.load(f)
                with open("habitaciones.json", 'r', encoding='utf-8') as f:
                    habitaciones = json.load(f)
                with open("reservas.json", 'r', encoding='utf-8') as f:
                    reservas = json.load(f)
            except (FileNotFoundError, OSError) as detalle:
                print("Error al intentar abrir archivo(s):", detalle)
                pass
            menu_informes(reservas, huespedes, habitaciones)
        elif op == "0":
            print("Gracias por usar el sistema. ¡Hasta luego!")
            break

if __name__ == "__main__":
    main()