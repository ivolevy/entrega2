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
import shutil
import time
import os

#----------------------------------------------------------------------------------------------
# CONSTANTES Y CONFIGURACIÓN
#----------------------------------------------------------------------------------------------
# Límites de validación
MIN_LENGTH_ID = 2
MAX_LENGTH_ID = 6  # Para IDs de huéspedes y habitaciones
MAX_LENGTH_ID_RESERVA = 9  # Para IDs de reserva (formato RSVxxxnnn)
MIN_LENGTH_NOMBRE = 2
MAX_LENGTH_NOMBRE = 20
MIN_LENGTH_DNI = 6
MAX_LENGTH_DNI = 8
MIN_LENGTH_TELEFONO = 7
MAX_LENGTH_TELEFONO = 15
MIN_LENGTH_DESCRIPCION = 5
MAX_LENGTH_DESCRIPCION = 25
MIN_LENGTH_SERVICIOS = 2
MAX_LENGTH_SERVICIOS = 50
MIN_LENGTH_NUMERO_HAB = 1
MAX_LENGTH_NUMERO_HAB = 6
MIN_LENGTH_PISO = 1
MAX_LENGTH_PISO = 3
MIN_LENGTH_PRECIO = 1
MAX_LENGTH_PRECIO = 8

# Formatos y rangos
ANIO_MIN = 25
ANIO_MAX = 27

# Opciones válidas
MEDIOS_DE_PAGO = ["Efectivo", "Tarjeta", "Transferencia", "Débito", "Crédito"]
TIPOS_HABITACION = ["Simple", "Doble", "Triple", "Suite", "Familiar"]
ESTADOS_HABITACION = ["Disponible", "Ocupada", "Mantenimiento"]
SERVICIOS_POSIBLES = ["WiFi", "TV", "Aire", "Frigobar", "Limpieza", "Desayuno"]

# Archivos
ARCHIVO_HUESPEDES = "huespedes.json"
ARCHIVO_HABITACIONES = "habitaciones.json"
ARCHIVO_RESERVAS = "reservas.json"

#----------------------------------------------------------------------------------------------
# FUNCIONES
#----------------------------------------------------------------------------------------------
def generar_id_reserva(reservas):
    """Genera un ID único tipo RSVxxxnnn para la reserva (exactamente 9 caracteres)."""
    while True:
        numeros = ''.join(random.choices(string.digits, k=3))
        letras = ''.join(random.choices(string.ascii_uppercase, k=3))
        rid = f"RSV{numeros}{letras}"
        # Verificar que tenga exactamente 9 caracteres
        if len(rid) != MAX_LENGTH_ID_RESERVA:
            continue
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
        # Permite un punto decimal.
        if dato.count('.') <= 1 and dato.replace('.', '', 1).isdigit():
            valor = float(dato)
            if valor < 0:
                print("❌ No se permiten valores negativos.")
                continue
            return valor
        
        print("❌ Ingrese un valor numérico positivo.")

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
        print(f"❌ Opción inválida. Opciones válidas: {', '.join(opciones)}")

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
    if len(email) > 254:  # RFC 5321 limit
        return False
    pat = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
    return re.match(pat, email) is not None

def validar_dni(dni):
    """Valida que el DNI tenga entre 6 y 8 caracteres numéricos."""
    if isinstance(dni, int):
        if dni < 0:
            return False
        dni = str(dni)
    elif isinstance(dni, str):
        if dni.startswith('-'):
            return False
    else:
        return False
    
    return dni.isdigit() and MIN_LENGTH_DNI <= len(dni) <= MAX_LENGTH_DNI

def validar_telefono(telefono):
    """Valida que el teléfono tenga el formato correcto."""
    telefono_str = str(telefono)
    # Permitir + solo al inicio, y solo si hay más de 7 dígitos después
    if telefono_str.startswith('+'):
        resto = telefono_str[1:]
        if not (resto.isdigit() and MIN_LENGTH_TELEFONO <= len(resto) <= MAX_LENGTH_TELEFONO):
            return False
        if len(resto) > 20:  # Máximo 20 dígitos después del +
            return False
    else:
        if not (telefono_str.isdigit() and MIN_LENGTH_TELEFONO <= len(telefono_str) <= MAX_LENGTH_TELEFONO):
            return False
        if len(telefono_str) > 20:  # Máximo 20 dígitos
            return False
    return True

def validar_id_huesped(idh):
    """Valida que el ID del huésped tenga entre 2 y 6 caracteres."""
    if not (MIN_LENGTH_ID <= len(idh) <= MAX_LENGTH_ID):
        return False
    # Verificar que solo contenga letras y números
    if not idh.isalnum():
        return False
    # Verificar que no sea solo números
    if idh.isdigit():
        return False
    return True

def validar_nombre_apellido(texto):
    """Valida que el nombre o apellido tenga entre 2 y 20 caracteres y solo contenga letras y espacios."""
    texto_limpio = texto.strip()
    if not (MIN_LENGTH_NOMBRE <= len(texto_limpio) <= MAX_LENGTH_NOMBRE):
        return False
    # Verificar que solo contenga letras y espacios
    for caracter in texto_limpio:
        if not (caracter.isalpha() or caracter.isspace()):
            return False
    # Verificar que no sea solo espacios
    if texto_limpio.replace(" ", "") == "":
        return False
    # Verificar que no tenga espacios múltiples consecutivos
    if "  " in texto_limpio:
        return False
    # Verificar que no empiece o termine con espacio
    if texto_limpio.startswith(" ") or texto_limpio.endswith(" "):
        return False
    return True

def validar_unicidad_email_telefono(huespedes, email, telefono, id_excluir=None):
    """Valida que el email y teléfono sean únicos entre huéspedes activos."""
    for idh, datos in huespedes.items():
        if idh == id_excluir:
            continue
        if datos["activo"]:
            if datos["email"] == email:
                return False, f"Email '{email}' ya existe en huésped {idh}"
            if str(datos["telefono"]) == str(telefono):
                return False, f"Teléfono '{telefono}' ya existe en huésped {idh}"
    return True, ""

def es_medio_pago_valido(medio):
    """Valida que el medio de pago sea válido."""
    return medio in MEDIOS_DE_PAGO

def es_tipo_habitacion_valido(tipo):
    """Valida que el tipo de habitación sea válido."""
    return tipo in TIPOS_HABITACION

def es_estado_habitacion_valido(estado):
    """Valida que el estado de habitación sea válido."""
    return estado in ESTADOS_HABITACION

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
    """Solicita un DNI por consola, validando la entrada."""
    while True:
        dni = input(msg).strip()
        if not dni.isdigit():
            print("❌ DNI inválido. Debe contener solo dígitos numéricos.")
            continue
        dni = int(dni)
        if dni < 0:
            print("❌ DNI inválido. No puede ser negativo.")
            continue
        if dni > 99999999:
            print("❌ DNI inválido. No puede exceder 99999999.")
            continue
        if not validar_dni(dni):
            print("❌ DNI inválido. Debe tener entre 6 y 8 dígitos numéricos.")
            continue
        return dni

def input_telefono(msg):
    """Solicita un teléfono válido por consola, validando la entrada."""
    while True:
        telefono = input(msg).strip()
        if validar_telefono(telefono):
            # Si tiene +, mantener como string, sino convertir a int
            if telefono.startswith('+'):
                return telefono
            else:
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
        print("❌ Email inválido. Debe contener @ y tener un formato válido.")

def input_medio_pago(msg):
    """Solicita un medio de pago válido de las opciones disponibles."""
    while True:
        medio = input(msg).strip()
        # Normalizar el input: convertir a minúsculas y remover acentos
        medio_normalizado = normalizar_texto(medio)
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
        
        if medio in MEDIOS_DE_PAGO:
            return medio
        elif medio_normalizado in mapeo_variaciones:
            return mapeo_variaciones[medio_normalizado]
        else:
            print(f"Medio de pago inválido. Opciones válidas: {', '.join(MEDIOS_DE_PAGO)}")

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

def limpiar_espacios(texto):
    """Elimina espacios dobles y espacios iniciales/finales de un texto."""
    partes = texto.strip().split()
    return ' '.join(partes)

def guardar_json_backup(ruta):
    """Hace un backup automático del archivo JSON antes de sobrescribirlo."""
    try:
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        backup_name = f"{ruta}.{timestamp}.bak"
        shutil.copy(ruta, backup_name)
        print(f"📋 Backup creado: {backup_name}")
    except Exception as e:
        print(f"⚠️  No se pudo crear backup de {ruta}: {e}")

def guardar_reservas(reservas, archivo=ARCHIVO_RESERVAS):
    guardar_json_backup(archivo)
    with open(archivo, mode='w', encoding='utf-8') as f:
        json.dump(reservas, f, ensure_ascii=False, indent=4)

def exportar_informe_a_archivo(contenido, nombre_archivo):
    """Exporta un informe a un archivo de texto."""
    try:
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        nombre_completo = f"{nombre_archivo}_{timestamp}.txt"
        with open(nombre_completo, 'w', encoding='utf-8') as f:
            f.write(contenido)
        print(f"✅ Informe exportado a: {nombre_completo}")
        return True
    except Exception as e:
        print(f"❌ Error al exportar informe: {e}")
        return False

def restaurar_desde_backup(archivo):
    """Intenta restaurar un archivo desde su backup más reciente."""
    try:
        # Buscar backups del archivo
        backups = []
        for f in os.listdir('.'):
            if f.startswith(archivo + '.') and f.endswith('.bak'):
                backups.append(f)
        
        if not backups:
            return False
        
        # Ordenar por timestamp (más reciente primero)
        backups.sort(reverse=True)
        backup_mas_reciente = backups[0]
        
        print(f"🔄 Restaurando desde backup: {backup_mas_reciente}")
        shutil.copy(backup_mas_reciente, archivo)
        print(f"✅ Archivo {archivo} restaurado exitosamente")
        return True
    except Exception as e:
        print(f"❌ Error al restaurar desde backup: {e}")
        return False

#----------------------------------------------------------------------------------------------
# CRUD HUESPEDES
#----------------------------------------------------------------------------------------------
def guardar_huespedes(huespedes, archivo="huespedes.json"):
    guardar_json_backup(archivo)
    with open(archivo, mode='w', encoding='utf-8') as f:
        json.dump(huespedes, f, ensure_ascii=False, indent=4)

def alta_huesped(huespedes_archivo=ARCHIVO_HUESPEDES):
    """Da de alta un huésped nuevo, persistiendo en archivo JSON."""
    print("\n--- Alta de huésped ---")
    try:
        with open(huespedes_archivo, mode='r', encoding='utf-8') as f:
            huespedes = json.load(f)
    except FileNotFoundError:
        huespedes = {}
    except OSError as detalle:
        print("❌ Error al intentar abrir archivo(s):", detalle, "¿Existe el archivo y tiene formato JSON válido?")
        return
    
    idh = input_id_huesped("ID del huésped: ")
    if not validar_id_huesped(idh):
        print(f"❌ ID inválido. Debe tener entre {MIN_LENGTH_ID} y {MAX_LENGTH_ID} caracteres, solo letras y números, y no puede ser solo números.")
        return
    if not validar_id_unico_huesped(huespedes, idh):
        print("❌ Ya existe un huésped con ese ID.")
        return
    
    nombre = input_nombre_apellido("Nombre: ")
    apellido = input_nombre_apellido("Apellido: ")
    dni = input_dni("DNI: ")
    if not validar_dni_unico(huespedes, dni):
        print("❌ Ya existe un huésped con ese DNI.")
        return
    email = input_email_validado("Email: ")
    telefono = input_telefono("Teléfono: ")
    
    # Solicitar medios de pago (pueden ser múltiples)
    while True:
        medios_input = input("Medios de pago (separados por coma): ").strip()
        medios_lista = [m.strip() for m in medios_input.split(',') if m.strip()]
        if len(medios_input) < 2 or len(medios_input) > 50:
            print("❌ Medios de pago inválidos. Debe tener entre 2 y 50 caracteres.")
        elif len(medios_lista) == 0 or '' in medios_lista:
            print("❌ Debe ingresar al menos un medio de pago válido, separados por coma y sin espacios vacíos.")
        elif len(medios_lista) != len(set(medios_lista)):
            print("❌ No puede haber medios de pago duplicados.")
        else:
            # Validar que todos los medios sean válidos usando la función normalizada
            medios_validos = []
            for medio in medios_lista:
                # Normalizar el medio de pago
                medio_normalizado = normalizar_texto(medio)
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
                
                if medio in MEDIOS_DE_PAGO:
                    medios_validos.append(medio)
                elif medio_normalizado in mapeo_variaciones:
                    medios_validos.append(mapeo_variaciones[medio_normalizado])
                else:
                    print(f"❌ Medio de pago '{medio}' no válido. Opciones: {', '.join(MEDIOS_DE_PAGO)}")
                    break
            else:
                medios = medios_validos
                break
    
    # Validar unicidad de email y teléfono
    valido, error = validar_unicidad_email_telefono(huespedes, email, telefono)
    if not valido:
        print(f"❌ {error}")
        return
    
    nombre = limpiar_espacios(nombre)
    apellido = limpiar_espacios(apellido)
    email = limpiar_espacios(email)
    
    huespedes[idh] = {
        "activo": True,
        "nombre": nombre,
        "apellido": apellido,
        "documento": dni,
        "email": email,
        "telefono": telefono,
        "mediosDePago": medios
    }
    
    guardar_huespedes(huespedes)
    print(f"✅ Huésped {nombre} {apellido} agregado correctamente.")

def modificar_huesped(huespedes_archivo=ARCHIVO_HUESPEDES):
    """Permite modificar todos los datos de un huésped activo, persistiendo en archivo JSON."""
    print("\n--- Modificar huésped ---")
    try:
        with open(huespedes_archivo, mode='r', encoding='utf-8') as f:
            huespedes = json.load(f)
    except FileNotFoundError:
        print("❌ El archivo de huéspedes no existe. No hay datos para modificar.")
        return
    except OSError as detalle:
        print("❌ Error al intentar abrir archivo(s):", detalle, "¿Existe el archivo y tiene formato JSON válido?")
        return
    
    idh = input_id_huesped("ID del huésped a modificar: ")
    if idh in huespedes and huespedes[idh]["activo"]:
        print("💡 Deje vacío para no modificar ese campo.")
        
        # Mostrar datos actuales
        print(f"\n📋 Datos actuales del huésped {idh}:")
        print(f"   Nombre: {huespedes[idh]['nombre']}")
        print(f"   Apellido: {huespedes[idh]['apellido']}")
        print(f"   DNI: {huespedes[idh]['documento']}")
        print(f"   Email: {huespedes[idh]['email']}")
        print(f"   Teléfono: {huespedes[idh]['telefono']}")
        print(f"   Medio de pago: {', '.join(huespedes[idh]['mediosDePago'])}")
        print()
        
        for campo in ["nombre", "apellido", "documento", "email", "telefono"]:
            actual = huespedes[idh][campo]
            while True:
                nuevo = input(f"Nuevo {campo} (actual: {actual}): ").strip()
                if not nuevo:  # Si está vacío, no modificar
                    break
                if campo in ["nombre", "apellido"]:
                    if validar_nombre_apellido(nuevo):
                        huespedes[idh][campo] = limpiar_espacios(nuevo)
                        break
                    else:
                        print("❌ Nombre/Apellido inválido. Debe tener entre 2 y 20 caracteres y solo contener letras.")
                elif campo == "email":
                    if validar_email_regex(nuevo):
                        huespedes[idh][campo] = limpiar_espacios(nuevo)
                        break
                    else:
                        print("❌ Email inválido. Debe contener @ y tener un formato válido.")
                elif campo == "documento":
                    if validar_dni(nuevo):
                        nuevo = int(nuevo)
                        if nuevo < 0:
                            print("❌ DNI inválido. No puede ser negativo.")
                            continue
                        huespedes[idh][campo] = nuevo
                        break
                    else:
                        print("❌ DNI inválido. Debe tener entre 6 y 8 dígitos numéricos.")
                elif campo == "telefono":
                    if validar_telefono(nuevo):
                        # Si tiene +, mantener como string, sino convertir a int
                        if nuevo.startswith('+'):
                            huespedes[idh][campo] = nuevo
                        else:
                            nuevo_int = int(nuevo)
                            if nuevo_int < 0:
                                print("❌ Teléfono inválido. No puede ser negativo.")
                                continue
                            huespedes[idh][campo] = nuevo_int
                        break
                    else:
                        print("❌ Teléfono inválido. Debe tener entre 7 y 15 dígitos numéricos.")
        
        # Validar unicidad de email y teléfono después de las modificaciones
        valido, error = validar_unicidad_email_telefono(huespedes, huespedes[idh]["email"], huespedes[idh]["telefono"], idh)
        if not valido:
            print(f"❌ {error}")
            return
        
        mp_actual = ', '.join(huespedes[idh]["mediosDePago"])
        while True:
            nuevo_mp_input = input(f"Nuevo medio de pago (actual: {mp_actual}, separados por coma): ").strip()
            if not nuevo_mp_input:  # Si está vacío, no modificar
                break
            # Procesar múltiples medios de pago separados por coma
            medios_lista = [m.strip() for m in nuevo_mp_input.split(',') if m.strip()]
            if len(nuevo_mp_input) < 2 or len(nuevo_mp_input) > 50:
                print("❌ Medios de pago inválidos. Debe tener entre 2 y 50 caracteres.")
            elif len(medios_lista) == 0 or '' in medios_lista:
                print("❌ Debe ingresar al menos un medio de pago válido, separados por coma y sin espacios vacíos.")
            elif len(medios_lista) != len(set(medios_lista)):
                print("❌ No puede haber medios de pago duplicados.")
            else:
                # Validar que todos los medios sean válidos usando la función normalizada
                medios_validos = []
                for medio in medios_lista:
                    # Normalizar el medio de pago
                    medio_normalizado = normalizar_texto(medio)
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
                    
                    if medio in MEDIOS_DE_PAGO:
                        medios_validos.append(medio)
                    elif medio_normalizado in mapeo_variaciones:
                        medios_validos.append(mapeo_variaciones[medio_normalizado])
                    else:
                        print(f"❌ Medio de pago '{medio}' no válido. Opciones: {', '.join(MEDIOS_DE_PAGO)}")
                        break
                else:
                    huespedes[idh]["mediosDePago"] = medios_validos
                    break
        
        guardar_huespedes(huespedes)
        print("✅ Huésped modificado correctamente.")
    else:
        print("❌ No existe un huésped activo con ese ID.")

def eliminar_huesped():
    """Realiza la baja lógica de un huésped solo si no tiene reservas activas o futuras."""
    print("\n--- Eliminar (baja lógica) huésped ---")
    
    # Cargar datos actualizados desde archivos JSON
    try:
        with open(ARCHIVO_HUESPEDES, 'r', encoding='utf-8') as f:
            huespedes = json.load(f)
        with open(ARCHIVO_RESERVAS, 'r', encoding='utf-8') as f:
            reservas = json.load(f)
    except (FileNotFoundError, OSError) as detalle:
        print("❌ Error al intentar abrir archivo(s):", detalle)
        return
    
    idh = input("ID huésped a eliminar: ").strip()
    if idh not in huespedes:
        print("❌ No existe un huésped con ese ID.")
        return
    if not huespedes[idh]["activo"]:
        print("❌ El huésped ya está inactivo.")
        return
    
    # Mostrar datos del huésped antes de eliminar
    print(f"\n📋 Datos del huésped a eliminar:")
    print(f"   ID: {idh}")
    print(f"   Nombre: {huespedes[idh]['nombre']} {huespedes[idh]['apellido']}")
    print(f"   DNI: {huespedes[idh]['documento']}")
    print(f"   Email: {huespedes[idh]['email']}")
    print(f"   Teléfono: {huespedes[idh]['telefono']}")
    
    # Verificar reservas activas o futuras
    reservas_activas = []
    for rid, datos in reservas.items():
        if datos["idhuesped"] == idh:
            # Si la reserva es futura o activa (no finalizada)
            if not datos.get("finalizada", False):
                reservas_activas.append(rid)
    
    if reservas_activas:
        print(f"\n❌ No se puede dar de baja: el huésped tiene {len(reservas_activas)} reservas activas o futuras:")
        for rid in reservas_activas:
            print(f"   - Reserva {rid}: {datos['fechaEntrada']} a {datos['fechaSalida']}")
        return
    
    confirm = input("\n⚠️  ¿Confirma la baja lógica del huésped? (s/n): ").strip().lower()
    if confirm == "s":
        huespedes[idh]["activo"] = False
        print("✅ Huésped dado de baja lógicamente.")
    else:
        print("❌ Operación cancelada.")
    
    guardar_huespedes(huespedes)

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
def guardar_habitaciones(habitaciones, archivo="habitaciones.json"):
    guardar_json_backup(archivo)
    with open(archivo, mode='w', encoding='utf-8') as f:
        json.dump(habitaciones, f, ensure_ascii=False, indent=4)

def alta_habitacion(habitaciones_archivo=ARCHIVO_HABITACIONES):
    """Da de alta una habitación nueva, persistiendo en archivo JSON."""
    print("\n--- Alta de habitación ---")
    try:
        with open(habitaciones_archivo, mode='r', encoding='utf-8') as f:
            habitaciones = json.load(f)
    except FileNotFoundError:
        habitaciones = {}
    except OSError as detalle:
        print("❌ Error al intentar abrir archivo(s):", detalle, "¿Existe el archivo y tiene formato JSON válido?")
        return
    
    # ID habitación
    while True:
        idh = input("ID habitación: ").strip()
        if not validar_id_habitacion(idh):
            print(f"❌ ID inválido. Debe tener entre {MIN_LENGTH_ID} y {MAX_LENGTH_ID} caracteres, solo letras y números, y no puede ser solo números.")
            continue
        if not validar_id_unico_habitacion(habitaciones, idh):
            print("❌ ID ya existe.")
            continue
        break
    # Número habitación
    while True:
        numero = input("Número de habitación: ").strip()
        if not (numero.isdigit() and MIN_LENGTH_NUMERO_HAB <= len(numero) <= MAX_LENGTH_NUMERO_HAB):
            print(f"❌ Número inválido. Debe tener entre {MIN_LENGTH_NUMERO_HAB} y {MAX_LENGTH_NUMERO_HAB} dígitos numéricos.")
            continue
        numero = int(numero)
        if numero < 0:
            print("❌ Número de habitación inválido. No puede ser negativo.")
            continue
        if numero > 9999:
            print("❌ Número de habitación inválido. No puede exceder 9999.")
            continue
        if not validar_numero_habitacion_unico(habitaciones, numero):
            print("❌ Ya existe una habitación con ese número.")
            continue
        break
    
    # Tipo habitación
    tipos_normalizados = [normalizar_texto(t) for t in TIPOS_HABITACION]
    while True:
        tipo = input(f"Tipo ({', '.join(TIPOS_HABITACION)}): ").strip()
        tipo_norm = normalizar_texto(tipo)
        if tipo_norm not in tipos_normalizados:
            print(f"❌ Tipo inválido. Opciones válidas: {', '.join(TIPOS_HABITACION)}.")
            continue
        tipo = TIPOS_HABITACION[tipos_normalizados.index(tipo_norm)]
        break
        # Descripción
    while True:
        descripcion = input("Descripción: ").strip()
        if not (MIN_LENGTH_DESCRIPCION <= len(descripcion) <= MAX_LENGTH_DESCRIPCION):
            print(f"❌ Descripción inválida. Debe tener entre {MIN_LENGTH_DESCRIPCION} y {MAX_LENGTH_DESCRIPCION} caracteres.")
            continue
        if not re.fullmatch(r'[a-zA-Z0-9,. ]+', descripcion):
            print("❌ Descripción inválida. Solo puede contener letras, números, comas, puntos y espacios.")
            continue
        # Verificar que no tenga espacios múltiples consecutivos
        if "  " in descripcion:
            print("❌ Descripción inválida. No puede tener espacios múltiples consecutivos.")
            continue
        # Verificar que no empiece o termine con espacio
        if descripcion.startswith(" ") or descripcion.endswith(" "):
            print("❌ Descripción inválida. No puede empezar o terminar con espacio.")
            continue
        break
    descripcion = limpiar_espacios(descripcion)
    
    # Precio por noche
    while True:
        precio = input("Precio por noche: ").strip()
        if not (precio.replace('.', '', 1).isdigit() and MIN_LENGTH_PRECIO <= len(precio) <= MAX_LENGTH_PRECIO):
            print(f"❌ Precio inválido. Debe ser numérico, entre {MIN_LENGTH_PRECIO} y {MAX_LENGTH_PRECIO} caracteres.")
            continue
        precio = float(precio)
        if precio < 0:
            print("❌ Precio inválido. No puede ser negativo.")
            continue
        if precio > 10000:
            print("❌ Precio inválido. No puede exceder $10,000 por noche.")
            continue
        break
    
    # Piso
    while True:
        piso = input("Piso: ").strip()
        if not (piso.isdigit() and MIN_LENGTH_PISO <= len(piso) <= MAX_LENGTH_PISO):
            print(f"❌ Piso inválido. Debe ser numérico, entre {MIN_LENGTH_PISO} y {MAX_LENGTH_PISO} caracteres.")
            continue
        piso = int(piso)
        if piso < 0:
            print("❌ Piso inválido. No puede ser negativo.")
            continue
        if piso > 100:
            print("❌ Piso inválido. No puede exceder 100.")
            continue
        break
    
    # Estado
    estados_normalizados = [normalizar_texto(e) for e in ESTADOS_HABITACION]
    while True:
        estado = input(f"Estado ({', '.join(ESTADOS_HABITACION)}): ").strip()
        estado_norm = normalizar_texto(estado)
        if estado_norm not in estados_normalizados:
            print(f"❌ Estado inválido. Opciones válidas: {', '.join(ESTADOS_HABITACION)}.")
            continue
        estado = ESTADOS_HABITACION[estados_normalizados.index(estado_norm)]
        break
    estado = limpiar_espacios(estado)
        # Servicios incluidos
    while True:
        servicios = input("Servicios incluidos (separados por coma): ").strip()
        serviciosIncluidos = limpiar_espacios(servicios)
        servicios_lista = [s.strip() for s in serviciosIncluidos.split(',') if s.strip()]
        if len(serviciosIncluidos) < MIN_LENGTH_SERVICIOS or len(serviciosIncluidos) > MAX_LENGTH_SERVICIOS:
            print(f"❌ Servicios inválidos. Debe tener entre {MIN_LENGTH_SERVICIOS} y {MAX_LENGTH_SERVICIOS} caracteres.")
        elif len(servicios_lista) == 0 or '' in servicios_lista:
            print("❌ Debe ingresar al menos un servicio válido, separados por coma y sin espacios vacíos.")
        elif len(servicios_lista) != len(set(servicios_lista)):
            print("❌ No puede haber servicios duplicados.")
        else:
            # Verificar que cada servicio no contenga caracteres problemáticos
            for servicio in servicios_lista:
                if not re.fullmatch(r'[a-zA-Z0-9,. ]+', servicio):
                    print(f"❌ Servicio '{servicio}' inválido. Solo puede contener letras, números, comas, puntos y espacios.")
                    break
                if "  " in servicio or servicio.startswith(" ") or servicio.endswith(" "):
                    print(f"❌ Servicio '{servicio}' inválido. No puede tener espacios múltiples o empezar/terminar con espacio.")
                    break
            else:
                serviciosIncluidos = ', '.join(servicios_lista)
                break
    
    habitaciones[idh] = {
        "activo": True,
        "numero": numero,
        "tipo": tipo,
        "descripcion": descripcion,
        "precioNoche": precio,
        "piso": piso,
        "estado": estado,
        "serviciosIncluidos": serviciosIncluidos
    }
    
    guardar_habitaciones(habitaciones)
    print(f"✅ Habitación {numero} agregada correctamente.")

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
                    while True:
                        nuevo = input("Nuevo valor para servicios incluidos (separados por coma): ").strip()
                        nuevo = limpiar_espacios(nuevo)
                        servicios_lista = [s.strip() for s in nuevo.split(',') if s.strip()]
                        if len(nuevo) < 2 or len(nuevo) > 50:
                            print("Servicios inválidos. Debe tener entre 2 y 50 caracteres.")
                        elif len(servicios_lista) == 0 or '' in servicios_lista:
                            print("Debe ingresar al menos un servicio válido, separados por coma y sin espacios vacíos.")
                        else:
                            habitaciones[idh][campo] = ', '.join(servicios_lista)
                            break
                nuevo = limpiar_espacios(nuevo)
                habitaciones[idh][campo] = nuevo
                break
        guardar_habitaciones(habitaciones)
        print("Habitación modificada correctamente.")
    else:
        print("No existe o está inactiva.")

def eliminar_habitacion():
    """Realiza la baja lógica de una habitación solo si no tiene reservas activas o futuras."""
    print("\n--- Eliminar (baja lógica) habitación ---")
    
    # Cargar datos actualizados desde archivos JSON
    try:
        with open("habitaciones.json", 'r', encoding='utf-8') as f:
            habitaciones = json.load(f)
        with open("reservas.json", 'r', encoding='utf-8') as f:
            reservas = json.load(f)
    except (FileNotFoundError, OSError) as detalle:
        print("Error al intentar abrir archivo(s):", detalle)
        return
    
    idh = input("ID habitación a eliminar: ").strip()
    if idh not in habitaciones:
        print("No existe una habitación con ese ID.")
        return
    if not habitaciones[idh]["activo"]:
        print("La habitación ya está inactiva.")
        return
    # Verificar reservas activas o futuras
    tiene_reservas = False
    for rid, datos in reservas.items():
        if datos["idhabitacion"] == idh:
            if not datos.get("finalizada", False):
                tiene_reservas = True
                break
    if tiene_reservas:
        print("No se puede dar de baja: la habitación tiene reservas activas o futuras.")
        return
    confirm = input("¿Confirma la baja lógica de la habitación? (s/n): ").strip().lower()
    if confirm == "s":
        habitaciones[idh]["activo"] = False
        print("Habitación dada de baja lógicamente.")
    else:
        print("Operación cancelada.")
    guardar_habitaciones(habitaciones)

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
            fe_existente_str = datos["fechaEntrada"]
            fs_existente_str = datos["fechaSalida"]
            if len(fe_existente_str) == 6 and len(fs_existente_str) == 6:
                try:
                    dia_e, mes_e, anio_e = int(fe_existente_str[:2]), int(fe_existente_str[2:4]), int(fe_existente_str[4:6])
                    dia_s, mes_s, anio_s = int(fs_existente_str[:2]), int(fs_existente_str[2:4]), int(fs_existente_str[4:6])
                    
                    # Validar que las fechas existan realmente
                    if not es_fecha_valida(dia_e, mes_e, 2000 + anio_e) or not es_fecha_valida(dia_s, mes_s, 2000 + anio_s):
                        continue  # Saltar reservas con fechas inválidas
                    
                    inicio_existente = datetime.datetime(2000 + anio_e, mes_e, dia_e)
                    fin_existente = datetime.datetime(2000 + anio_s, mes_s, dia_s)
                    if fecha_inicio_nueva < fin_existente and fecha_fin_nueva > inicio_existente:
                        return True
                except (ValueError, IndexError):
                    continue  # Saltar reservas con fechas mal formateadas
    return False

def registrar_reserva(huespedes, habitaciones, reservas):
    """
    Crea una reserva nueva. Pide los datos, valida que la habitación esté
    disponible en esas fechas y calcula bien las noches (incluso si cambia el año).
    Si está todo OK, la guarda.
    """
    print("\n--- Registrar reserva ---")
    print("IMPORTANTE: Solo se aceptan reservas entre los años 2025 y 2027 (inclusive).\nNo se permiten reservas en fechas pasadas (ni días anteriores al actual).\n")
    id_reserva = generar_id_reserva(reservas)
    # Validar ID huésped activo
    while True:
        h = input("ID huésped: ").strip()
        if h not in huespedes or not huespedes[h]["activo"]:
            print("Huésped inválido o inactivo. Ingrese un ID de huésped activo.")
        else:
            break
    # Validar ID habitación activa
    while True:
        r = input("ID habitación: ").strip()
        if r not in habitaciones or not habitaciones[r]["activo"]:
            print("Habitación inválida o inactiva. Ingrese un ID de habitación activa.")
        else:
            break
    # Validar fecha de entrada (DDMMAA, año entre 25 y 27)
    while True:
        fecha_entrada = input("Fecha de entrada (DDMMAA): ").strip()
        if not (len(fecha_entrada) == 6 and fecha_entrada.isdigit()):
            print("Formato inválido. Debe ser DDMMAA.")
            continue
        dia = int(fecha_entrada[:2])
        mes = int(fecha_entrada[2:4])
        anio = int(fecha_entrada[4:6])
        if not (1 <= dia <= 31):
            print("Día de entrada inválido. Debe estar entre 01 y 31.")
            continue
        if not (1 <= mes <= 12):
            print("Mes de entrada inválido. Debe estar entre 01 y 12.")
            continue
        if not (25 <= anio <= 27):
            print("Año inválido. Solo se permiten reservas entre 2025 y 2027.")
            continue
        try:
            fecha_ent = datetime.datetime(2000 + anio, mes, dia)
        except ValueError:
            print("Fecha inválida (p. ej. día 31 en un mes de 30 días).")
            continue
        hoy = datetime.datetime.now()
        if fecha_ent < hoy.replace(hour=0, minute=0, second=0, microsecond=0):
            print("❌ No se permiten reservas en el pasado.")
            continue
        # Verificar que no sea demasiado lejano en el futuro (máximo 2 años)
        fecha_maxima = hoy + datetime.timedelta(days=730)  # 2 años
        if fecha_ent > fecha_maxima:
            print("❌ No se permiten reservas más allá de 2 años en el futuro.")
            continue
        break
    # Validar fecha de salida (DDMMAA, año entre 25 y 27, posterior a entrada)
    while True:
        fecha_salida = input("Fecha de salida (DDMMAA): ").strip()
        if not (len(fecha_salida) == 6 and fecha_salida.isdigit()):
            print("Formato inválido. Debe ser DDMMAA.")
            continue
        dia_s = int(fecha_salida[:2])
        mes_s = int(fecha_salida[2:4])
        anio_s = int(fecha_salida[4:6])
        if not (1 <= dia_s <= 31):
            print("Día de salida inválido. Debe estar entre 01 y 31.")
            continue
        if not (1 <= mes_s <= 12):
            print("Mes de salida inválido. Debe estar entre 01 y 12.")
            continue
        if not (25 <= anio_s <= 27):
            print("Año inválido. Solo se permiten reservas entre 2025 y 2027.")
            continue
        try:
            fecha_sal = datetime.datetime(2000 + anio_s, mes_s, dia_s)
        except ValueError:
            print("Fecha inválida (p. ej. día 31 en un mes de 30 días).")
            continue
        if fecha_sal <= fecha_ent:
            print("❌ La fecha de salida debe ser posterior a la de entrada.")
            continue
        # Verificar que haya al menos 1 noche de diferencia
        if (fecha_sal - fecha_ent).days < 1:
            print("❌ La reserva debe ser de al menos 1 noche.")
            continue
        # Verificar que no sea demasiado larga (máximo 30 días)
        if (fecha_sal - fecha_ent).days > 30:
            print("❌ La reserva no puede exceder 30 días.")
            continue
        break
    # Calcular noches
    noches = (fecha_sal - fecha_ent).days
    # Solapamiento
    if solapa_reserva(reservas, r, fecha_ent, fecha_sal):
        print("La habitación ya está reservada en ese rango de fechas.")
        return
    # Validar descuento entre 0 y 99
    while True:
        descuento_str = input("Descuento: ").strip()
        if not descuento_str.isdigit():
            print("Ingrese un valor numérico entero para el descuento.")
            continue
        descuento = int(descuento_str)
        if not (0 <= descuento <= 100):
            print("❌ El descuento debe estar entre 0 y 100.")
            continue
        break
    # Limpiar espacios en campos de texto
    # Si hay campos de texto como observaciones, motivo, etc., aplicar limpiar_espacios antes de guardar
    reservas[id_reserva] = {
        "idhuesped": h,
        "idhabitacion": r,
        "fechaEntrada": fecha_entrada,
        "fechaSalida": fecha_salida,
        "cantidadNoches": noches,
        "descuento": descuento,
        "fechaHoraOperacion": datetime.datetime.now().strftime("%Y.%m.%d - %H:%M:%S")
    }
    guardar_reservas(reservas)
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
    encabezado = f"{'Fecha/Hora':<24} | {'Cliente':<20} | {'Producto':<14} | {'Cant.':>5} | {'Unit.':>12} | {'Total':>14}"
    print("-" * len(encabezado))
    print(encabezado)
    print("-" * len(encabezado))
    for rid, datos in reservas.items():
        fecha = datos['fechaHoraOperacion']
        if fecha[5:7] == mes_actual:
            h = huespedes.get(datos["idhuesped"], {"nombre": "-", "apellido": "-"})
            hab = habitaciones.get(datos["idhabitacion"], {"numero": "-", "tipo": "-", "precioNoche": 0})
            total = hab["precioNoche"] * datos["cantidadNoches"] * (1 - datos["descuento"]/100)
            print(f"{fecha:<24} | {h['apellido']+', '+h['nombre']:<20} | {hab['tipo']:<14} | {datos['cantidadNoches']:>5} | {hab['precioNoche']:>12.2f} | {total:>14.2f}")
            hay = True
    if not hay:
        print("No hay operaciones en el mes actual.")
    print("-" * len(encabezado))

def informe_matriz_cantidades(reservas, habitaciones):
    """Informe 2: Muestra la cantidad de noches reservadas por mes para cada habitación, con formato tabular alineado."""
    print("\n--- Resumen de cantidad de noches reservadas por mes ---")
    anio_str = input("Ingrese el año para el informe (AA, ej: 25, 26, 27): ").strip()
    if not (anio_str.isdigit() and len(anio_str) == 2 and anio_str in ["25", "26", "27"]):
        print("Año inválido. Solo se permiten 25, 26 o 27.")
        return
    anio = 2000 + int(anio_str)
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
    anio_str = input("Ingrese el año para el informe (AA, ej: 25, 26, 27): ").strip()
    if not (anio_str.isdigit() and len(anio_str) == 2 and anio_str in ["25", "26", "27"]):
        print("Año inválido. Solo se permiten 25, 26 o 27.")
        return
    anio = 2000 + int(anio_str)
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
    encabezado = f"{'Hab':<8}|" + ''.join([f"{nombre:>8}|" for nombre in nombres_mes])
    print("-" * len(encabezado))
    print(encabezado)
    print("-" * len(encabezado))
    for hab_id, meses in matriz.items():
        num_hab = habitaciones.get(hab_id, {}).get('numero', hab_id)
        linea = f"{str(num_hab):<8}|" + ''.join([f"{int(meses[mes]):8}|" for mes in range(1, 13)])
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

def migrar_reservas_ddmmaa(reservas):
    """Agrega el año '25' a las fechas de reservas antiguas en formato DDMM y elimina reservas con fechas inválidas."""
    for datos in reservas.values():
        if len(datos["fechaEntrada"]) == 4:
            datos["fechaEntrada"] += "25"
        if len(datos["fechaSalida"]) == 4:
            datos["fechaSalida"] += "25"
    
    # Validar fechas migradas
    reservas_invalidas = []
    for rid, datos in reservas.items():
        try:
            # Validar fecha de entrada
            if len(datos["fechaEntrada"]) == 6:
                dia = int(datos["fechaEntrada"][:2])
                mes = int(datos["fechaEntrada"][2:4])
                anio = int(datos["fechaEntrada"][4:6])
                if not es_fecha_valida(dia, mes, 2000 + anio):
                    reservas_invalidas.append(rid)
                    continue
            # Validar fecha de salida
            if len(datos["fechaSalida"]) == 6:
                dia = int(datos["fechaSalida"][:2])
                mes = int(datos["fechaSalida"][2:4])
                anio = int(datos["fechaSalida"][4:6])
                if not es_fecha_valida(dia, mes, 2000 + anio):
                    reservas_invalidas.append(rid)
                    continue
        except (ValueError, IndexError):
            reservas_invalidas.append(rid)
    # Remover reservas con fechas inválidas
    for rid in reservas_invalidas:
        if rid in reservas:
            del reservas[rid]
    if reservas_invalidas:
        print(f"⚠️  Se removieron {len(reservas_invalidas)} reservas con fechas inválidas después de la migración.")
    return reservas



#----------------------------------------------------------------------------------------------
# MENÚS
#----------------------------------------------------------------------------------------------
def mostrar_ayuda_huespedes():
    """Muestra ayuda contextual para la gestión de huéspedes."""
    print("\n📚 AYUDA - GESTIÓN DE HUÉSPEDES")
    print("=" * 50)
    print("📋 Formatos requeridos:")
    print("   • ID: 2-6 caracteres (letras y números)")
    print("   • Nombre/Apellido: 2-20 caracteres, solo letras y espacios")
    print("   • DNI: 6-8 dígitos numéricos")
    print("   • Email: formato válido con @ y dominio")
    print("   • Teléfono: 7-15 dígitos (puede empezar con +)")
    print("   • Medio de pago: Efectivo, Tarjeta, Transferencia, Débito, Crédito")
    print("     (acepta variaciones: efectivo, EFECTIVO, débito, etc.)")
    print("\n💡 Notas:")
    print("   • Los emails y teléfonos deben ser únicos")
    print("   • No se puede eliminar huéspedes con reservas activas")
    print("   • Las eliminaciones son lógicas (no se borran físicamente)")
    print("   • Los medios de pago se normalizan automáticamente")
    print("=" * 50)

def menu_huespedes():
    """Menú de gestión de huéspedes con persistencia en JSON."""
    while True:
        print("\n🏨 GESTIÓN DE HUÉSPEDES")
        print("[1] Ingresar huésped")
        print("[2] Modificar huésped")
        print("[3] Eliminar huésped")
        print("[4] Listar huéspedes activos")
        print("[5] Buscar huésped")
        print("[6] Ayuda")
        print("[0] Volver al menú principal")
        sub = input_opciones("Opción: ", ["1", "2", "3", "4", "5", "6", "0"])
        if sub == "1":
            alta_huesped()
        elif sub == "2":
            modificar_huesped()
        elif sub == "3":
            eliminar_huesped()
        elif sub == "4":
            listar_huespedes_activos()
        elif sub == "5":
            buscar_huespedes()
        elif sub == "6":
            mostrar_ayuda_huespedes()
        elif sub == "0":
            break

def mostrar_ayuda_habitaciones():
    """Muestra ayuda contextual para la gestión de habitaciones."""
    print("\n📚 AYUDA - GESTIÓN DE HABITACIONES")
    print("=" * 50)
    print("📋 Formatos requeridos:")
    print("   • ID: 2-6 caracteres (letras y números)")
    print("   • Número: 1-6 dígitos numéricos")
    print("   • Tipo: Simple, Doble, Triple, Suite, Familiar")
    print("   • Descripción: 5-25 caracteres (letras, números, comas, puntos, espacios)")
    print("   • Precio: número positivo, 1-8 caracteres")
    print("   • Piso: 1-3 dígitos numéricos")
    print("   • Estado: Disponible, Ocupada, Mantenimiento")
    print("   • Servicios: 2-50 caracteres, separados por coma")
    print("\n💡 Notas:")
    print("   • No se puede eliminar habitaciones con reservas activas")
    print("   • Las eliminaciones son lógicas (no se borran físicamente)")
    print("=" * 50)

def menu_habitaciones():
    """Menú de gestión de habitaciones con persistencia en JSON."""
    while True:
        print("\n🏨 GESTIÓN DE HABITACIONES")
        print("[1] Ingresar habitación")
        print("[2] Modificar habitación")
        print("[3] Eliminar habitación")
        print("[4] Listar habitaciones activas")
        print("[5] Buscar habitación")
        print("[6] Ayuda")
        print("[0] Volver al menú principal")
        sub = input_opciones("Opción: ", ["1", "2", "3", "4", "5", "6", "0"])
        if sub == "1":
            alta_habitacion()
        elif sub == "2":
            modificar_habitacion()
        elif sub == "3":
            eliminar_habitacion()
        elif sub == "4":
            listar_habitaciones_activas()
        elif sub == "5":
            buscar_habitaciones()
        elif sub == "6":
            mostrar_ayuda_habitaciones()
        elif sub == "0":
            break

def mostrar_ayuda_reservas():
    """Muestra ayuda contextual para la gestión de reservas."""
    print("\n📚 AYUDA - GESTIÓN DE RESERVAS")
    print("=" * 50)
    print("📋 Formatos requeridos:")
    print("   • ID Huésped: debe existir y estar activo")
    print("   • ID Habitación: debe existir y estar activa")
    print("   • Fecha Entrada: DDMMAA (años 25, 26, 27)")
    print("   • Fecha Salida: DDMMAA (posterior a entrada)")
    print("   • Descuento: 0-99%")
    print("\n💡 Notas:")
    print("   • Solo se permiten reservas entre 2025-2027")
    print("   • No se permiten reservas en fechas pasadas")
    print("   • No se permiten solapamientos de fechas")
    print("   • Los IDs se generan automáticamente")
    print("=" * 50)

def menu_reservas(huespedes, habitaciones, reservas):
    """Menú de gestión de reservas."""
    while True:
        print("\n🏨 GESTIÓN DE RESERVAS")
        print("[1] Registrar reserva")
        print("[2] Listar reservas")
        print("[3] Ayuda")
        print("[0] Volver al menú principal")
        sub = input_opciones("Opción: ", ["1", "2", "3", "0"])
        if sub == "1":
            registrar_reserva(huespedes, habitaciones, reservas)
        elif sub == "2":
            listar_reservas(reservas, huespedes, habitaciones)
        elif sub == "3":
            mostrar_ayuda_reservas()
        elif sub == "0":
            break

def mostrar_ayuda_informes():
    """Muestra ayuda contextual para los informes."""
    print("\n" + "=" * 70)
    print("📊 CENTRO DE AYUDA - SISTEMA DE INFORMES")
    print("=" * 70)
    print("🏨 Sistema de Gestión Hotelera - Módulo de Informes")
    print("📅 Generación de reportes y análisis de datos")
    print("=" * 70)
    
    print("\n📋 INFORMES DISPONIBLES:")
    print("─" * 50)
    
    print("\n🔹 1. OPERACIONES DEL MES EN CURSO")
    print("   ┌─────────────────────────────────────────────────┐")
    print("   │ • Muestra todas las reservas del mes actual     │")
    print("   │ • Incluye datos del cliente y habitación        │")
    print("   │ • Calcula cantidades, precios unitarios y total │")
    print("   │ • Formato tabular profesional y alineado        │")
    print("   └─────────────────────────────────────────────────┘")
    
    print("\n🔹 2. RESUMEN ANUAL - CANTIDAD DE NOCHES")
    print("   ┌─────────────────────────────────────────────────┐")
    print("   │ • Matriz de habitaciones vs meses del año       │")
    print("   │ • Muestra noches reservadas por habitación      │")
    print("   │ • Solicita año en formato AA (25, 26, 27)       │")
    print("   │ • Útil para análisis de ocupación               │")
    print("   └─────────────────────────────────────────────────┘")
    
    print("\n🔹 3. RESUMEN ANUAL - MONTOS TOTALES")
    print("   ┌─────────────────────────────────────────────────┐")
    print("   │ • Matriz de habitaciones vs meses del año       │")
    print("   │ • Muestra ingresos totales por habitación       │")
    print("   │ • Incluye descuentos aplicados                  │")
    print("   │ • Solicita año en formato AA (25, 26, 27)       │")
    print("   │ • Ideal para análisis financiero                │")
    print("   └─────────────────────────────────────────────────┘")
    
    print("\n🔹 4. RESERVAS POR HUÉSPED ACTIVO")
    print("   ┌─────────────────────────────────────────────────┐")
    print("   │ • Lista todos los huéspedes activos             │")
    print("   │ • Cuenta reservas realizadas por cada uno       │")
    print("   │ • Formato tabular claro y organizado            │")
    print("   │ • Útil para análisis de clientes frecuentes     │")
    print("   └─────────────────────────────────────────────────┘")
    
    print("\n💡 CONSEJOS DE USO:")
    print("─" * 30)
    print("   • Los informes se generan en tiempo real")
    print("   • Los datos provienen de los archivos JSON")
    print("   • Asegúrese de tener datos actualizados")
    print("   • Los años válidos son 25, 26 y 27")
    
    print("\n" + "=" * 70)
    print("✅ Para más información, consulte la documentación del sistema")
    print("=" * 70)

def menu_informes(reservas, huespedes, habitaciones):
    """Menú de informes con las 4 opciones requeridas."""
    while True:
        print("\n📊 MENÚ DE INFORMES")
        print("[1] Listado tabular de operaciones del mes en curso")
        print("[2] Resumen anual de cantidad de noches por habitación")
        print("[3] Resumen anual de montos totales por habitación")
        print("[4] Informe a elección del equipo")
        print("[5] Ayuda")
        print("[0] Volver al menú principal")
        op = input_opciones("Opción: ", ["1", "2", "3", "4", "5", "0"])
        if op == "1":
            informe_tabular_mes(reservas, huespedes, habitaciones)
        elif op == "2":
            informe_matriz_cantidades(reservas, habitaciones)
        elif op == "3":
            informe_matriz_montos(reservas, habitaciones)
        elif op == "4":
            informe_a_eleccion(reservas, huespedes, habitaciones)
        elif op == "5":
            mostrar_ayuda_informes()
        elif op == "0":
            break

#----------------------------------------------------------------------------------------------
# CUERPO PRINCIPAL
#----------------------------------------------------------------------------------------------
def main():
    """Función principal del sistema de gestión hotelera."""
    print("\n" + "=" * 60)
    print("🏨 SISTEMA DE GESTIÓN HOTELERA - ENTREGA 2")
    print("=" * 60)
    print("Bienvenido/a al Sistema de Gestión Hotelera")
    print("Desarrollado por: Equipo 5 - Programación 1 (Viernes async)")
    print("=" * 60)
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
        print("\n🏨 MENÚ PRINCIPAL")
        print("=" * 40)
        print("[1] Gestión de Huéspedes")
        print("[2] Gestión de Habitaciones")
        print("[3] Gestión de Reservas")
        print("[4] Informes")
        print("[0] Salir")
        print("=" * 40)
        op = input_opciones("Opción: ", ["1", "2", "3", "4", "0"])
        if op == "1":
            menu_huespedes()
        elif op == "2":
            menu_habitaciones()
        elif op == "3":
            # Leer datos actualizados de los archivos antes de operar
            try:
                with open(ARCHIVO_HUESPEDES, 'r', encoding='utf-8') as f:
                    huespedes = json.load(f)
                with open(ARCHIVO_HABITACIONES, 'r', encoding='utf-8') as f:
                    habitaciones = json.load(f)
                with open(ARCHIVO_RESERVAS, 'r', encoding='utf-8') as f:
                    reservas = json.load(f)
                reservas = migrar_reservas_ddmmaa(reservas)
            except FileNotFoundError as e:
                print("❌ Error: No se encontraron los archivos JSON necesarios.")
                print("💡 Ejecute primero el script de conversión para generar los archivos de datos:")
                print("   python Conversión_DICCIONARIO_a_ARCHIVO_JSON.py")
                continue
            except OSError as detalle:
                print(f"❌ Error al intentar abrir archivo(s): {detalle}")
                print("💡 Verifique que los archivos existan y tengan permisos de lectura")
                continue
            except json.JSONDecodeError as detalle:
                print(f"❌ Error en formato JSON: {detalle}")
                print("💡 Los archivos JSON pueden estar corruptos")
                respuesta = input("¿Desea intentar restaurar desde backup? (s/n): ").strip().lower()
                if respuesta == 's':
                    if restaurar_desde_backup(ARCHIVO_RESERVAS):
                        continue
                continue
            # Llamar a migrar_reservas_ddmmaa(reservas) al cargar reservas en main antes de operar.
            menu_reservas(huespedes, habitaciones, reservas)
        elif op == "4":
            try:
                with open(ARCHIVO_HUESPEDES, 'r', encoding='utf-8') as f:
                    huespedes = json.load(f)
                with open(ARCHIVO_HABITACIONES, 'r', encoding='utf-8') as f:
                    habitaciones = json.load(f)
                with open(ARCHIVO_RESERVAS, 'r', encoding='utf-8') as f:
                    reservas = json.load(f)
            except FileNotFoundError as e:
                print("❌ Error: No se encontraron los archivos JSON necesarios.")
                print("💡 Ejecute primero el script de conversión para generar los archivos de datos:")
                print("   python Conversión_DICCIONARIO_a_ARCHIVO_JSON.py")
                continue
            except OSError as detalle:
                print(f"❌ Error al intentar abrir archivo(s): {detalle}")
                print("💡 Verifique que los archivos existan y tengan permisos de lectura")
                continue
            except json.JSONDecodeError as detalle:
                print(f"❌ Error en formato JSON: {detalle}")
                print("💡 Los archivos JSON pueden estar corruptos")
                respuesta = input("¿Desea intentar restaurar desde backup? (s/n): ").strip().lower()
                if respuesta == 's':
                    if restaurar_desde_backup(ARCHIVO_RESERVAS):
                        continue
                continue
            menu_informes(reservas, huespedes, habitaciones)
        elif op == "0":
            print("\n" + "=" * 60)
            print("👋 ¡Gracias por usar el Sistema de Gestión Hotelera!")
            print("Desarrollado por: Equipo 5 - Programación 1 (Viernes async)")
            print("=" * 60)
            break

def validar_id_unico_huesped(huespedes, idh):
    """Valida que el ID del huésped sea único."""
    return idh not in huespedes

def validar_id_unico_habitacion(habitaciones, idh):
    """Valida que el ID de la habitación sea único."""
    return idh not in habitaciones

def validar_numero_habitacion_unico(habitaciones, numero):
    """Valida que el número de habitación sea único."""
    for datos in habitaciones.values():
        if datos["activo"] and datos["numero"] == numero:
            return False
    return True

def validar_dni_unico(huespedes, dni):
    """Valida que el DNI sea único entre huéspedes activos."""
    for datos in huespedes.values():
        if datos["activo"] and datos["documento"] == dni:
            return False
    return True

def validar_id_habitacion(idh):
    """Valida que el ID de la habitación tenga entre 2 y 6 caracteres."""
    if not (MIN_LENGTH_ID <= len(idh) <= MAX_LENGTH_ID):
        return False
    # Verificar que solo contenga letras y números
    if not idh.isalnum():
        return False
    # Verificar que no sea solo números
    if idh.isdigit():
        return False
    return True

def validar_id_reserva(rid):
    """Valida que el ID de reserva tenga exactamente 9 caracteres y formato RSVxxxnnn."""
    if len(rid) != MAX_LENGTH_ID_RESERVA:
        return False
    # Verificar formato: RSV + 3 dígitos + 3 letras
    if not rid.startswith("RSV"):
        return False
    if not rid[3:6].isdigit():
        return False
    if not rid[6:9].isalpha():
        return False
    return True

def validar_formato_id_reserva(rid):
    """Valida que el ID de reserva tenga el formato correcto RSVxxxnnn."""
    if len(rid) != MAX_LENGTH_ID_RESERVA:
        return False, f"ID de reserva debe tener exactamente {MAX_LENGTH_ID_RESERVA} caracteres"
    # Verificar formato: RSV + 3 dígitos + 3 letras
    if not rid.startswith("RSV"):
        return False, "ID de reserva debe empezar con 'RSV'"
    if not rid[3:6].isdigit():
        return False, "ID de reserva debe tener 3 dígitos después de 'RSV'"
    if not rid[6:9].isalpha():
        return False, "ID de reserva debe terminar con 3 letras"
    return True, ""

if __name__ == "__main__":
    main()