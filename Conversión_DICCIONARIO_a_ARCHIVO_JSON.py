import json
import datetime
import random
import string
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
DIAS_MAX_POR_MES = 28  # Para evitar fechas inválidas

# Opciones válidas
TIPOS_HABITACION = ["Simple", "Doble", "Triple", "Suite", "Familiar"]
SERVICIOS_POSIBLES = ["WiFi", "TV", "Aire", "Frigobar", "Limpieza", "Desayuno"]
MEDIOS_DE_PAGO = ["Efectivo", "Tarjeta", "Transferencia", "Débito", "Crédito"]
ESTADOS_HABITACION = ["Disponible", "Ocupada", "Mantenimiento"]

# Archivos
ARCHIVO_HUESPEDES = 'huespedes.json'
ARCHIVO_HABITACIONES = 'habitaciones.json'
ARCHIVO_RESERVAS = 'reservas.json'

#----------------------------------------------------------------------------------------------
# FUNCIONES DE VALIDACIÓN
#----------------------------------------------------------------------------------------------
def validar_id(id_valor, tipo="general"):
    """Valida que un ID cumpla con los requisitos de longitud."""
    longitud = len(str(id_valor))
    
    # Para IDs de reserva (formato RSVxxxnnn), debe tener exactamente 9 caracteres
    if tipo == "ID de reserva" and longitud == MAX_LENGTH_ID_RESERVA:
        return True, ""
    
    # Para otros IDs, usar límites estándar (2-6 caracteres)
    if not (MIN_LENGTH_ID <= longitud <= MAX_LENGTH_ID):
        return False, f"ID debe tener entre {MIN_LENGTH_ID} y {MAX_LENGTH_ID} caracteres"
    
    return True, ""

def validar_nombre_apellido(texto, campo="texto"):
    """Valida que un nombre o apellido cumpla con los requisitos."""
    texto_limpio = texto.strip()
    if not (MIN_LENGTH_NOMBRE <= len(texto_limpio) <= MAX_LENGTH_NOMBRE):
        return False, f"{campo} debe tener entre {MIN_LENGTH_NOMBRE} y {MAX_LENGTH_NOMBRE} caracteres"
    
    # Verificar que solo contenga letras y espacios
    for caracter in texto_limpio:
        if not (caracter.isalpha() or caracter.isspace()):
            return False, f"{campo} solo puede contener letras y espacios"
    
    # Verificar que no sea solo espacios
    if texto_limpio.replace(" ", "") == "":
        return False, f"{campo} no puede ser solo espacios"
    
    return True, ""

def validar_dni(dni):
    """Valida que el DNI tenga el formato correcto."""
    dni_str = str(dni)
    if not (MIN_LENGTH_DNI <= len(dni_str) <= MAX_LENGTH_DNI):
        return False, f"DNI debe tener entre {MIN_LENGTH_DNI} y {MAX_LENGTH_DNI} dígitos"
    if not dni_str.isdigit():
        return False, "DNI debe contener solo dígitos numéricos"
    return True, ""

def validar_telefono(telefono):
    """Valida que el teléfono tenga el formato correcto."""
    telefono_str = str(telefono)
    
    # Permitir + solo al inicio, y solo si hay más de 7 dígitos después
    if telefono_str.startswith('+'):
        resto = telefono_str[1:]
        if not (resto.isdigit() and MIN_LENGTH_TELEFONO <= len(resto) <= MAX_LENGTH_TELEFONO):
            return False, f"Teléfono internacional debe tener entre {MIN_LENGTH_TELEFONO} y {MAX_LENGTH_TELEFONO} dígitos después del +"
    else:
        if not (telefono_str.isdigit() and MIN_LENGTH_TELEFONO <= len(telefono_str) <= MAX_LENGTH_TELEFONO):
            return False, f"Teléfono debe tener entre {MIN_LENGTH_TELEFONO} y {MAX_LENGTH_TELEFONO} dígitos"
    
    return True, ""

def validar_email(email):
    """Valida que el email tenga un formato básico válido."""
    if '@' not in email or '.' not in email.split('@')[1]:
        return False, "Email debe contener @ y un dominio válido"
    return True, ""

def validar_servicios(servicios_str):
    """Valida que los servicios cumplan con los requisitos."""
    if not (MIN_LENGTH_SERVICIOS <= len(servicios_str) <= MAX_LENGTH_SERVICIOS):
        return False, f"Servicios deben tener entre {MIN_LENGTH_SERVICIOS} y {MAX_LENGTH_SERVICIOS} caracteres"
    
    servicios_lista = [s.strip() for s in servicios_str.split(',') if s.strip()]
    if len(servicios_lista) == 0:
        return False, "Debe ingresar al menos un servicio válido"
    
    # Verificar que no haya servicios vacíos
    if '' in servicios_lista:
        return False, "No puede haber servicios vacíos"
    
    return True, ""

def validar_fecha_ddmmaa(fecha_str, tipo="fecha"):
    """Valida que una fecha en formato DDMMAA sea válida."""
    if not (len(fecha_str) == 6 and fecha_str.isdigit()):
        return False, f"Formato de {tipo} inválido. Debe ser DDMMAA"
    
    dia = int(fecha_str[:2])
    mes = int(fecha_str[2:4])
    anio = int(fecha_str[4:6])
    
    if not (1 <= dia <= 31):
        return False, f"Día de {tipo} inválido. Debe estar entre 01 y 31"
    if not (1 <= mes <= 12):
        return False, f"Mes de {tipo} inválido. Debe estar entre 01 y 12"
    if not (ANIO_MIN <= anio <= ANIO_MAX):
        return False, f"Año de {tipo} inválido. Solo se permiten años {ANIO_MIN} a {ANIO_MAX}"
    
    # Validar que la fecha existe realmente
    try:
        datetime.datetime(2000 + anio, mes, dia)
    except ValueError:
        return False, f"{tipo} inválida (ej: día 31 en un mes de 30 días)"
    
    return True, ""

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

#----------------------------------------------------------------------------------------------
# FUNCIONES DE GENERACIÓN DE DATOS
#----------------------------------------------------------------------------------------------
def generar_id_reserva(reservas):
    """Genera un ID único tipo RSVxxxnnn para la reserva (exactamente 9 caracteres)."""
    while True:
        numeros = ''.join(random.choices(string.digits, k=3))
        letras = ''.join(random.choices(string.ascii_uppercase, k=3))
        rid = f"RSV{numeros}{letras}"
        # Verificar que tenga exactamente 9 caracteres y formato correcto
        if len(rid) != MAX_LENGTH_ID_RESERVA:
            continue
        # Verificar formato
        valido, _ = validar_formato_id_reserva(rid)
        if not valido:
            continue
        if rid not in reservas:
            return rid

def generar_servicios_aleatorios():
    """Genera una lista aleatoria de servicios que cumple con las validaciones."""
    num_servicios = random.randint(2, 4)
    servicios = random.sample(SERVICIOS_POSIBLES, num_servicios)
    servicios_str = ", ".join(servicios)
    
    # Verificar que no exceda 50 caracteres
    while len(servicios_str) > MAX_LENGTH_SERVICIOS and len(servicios) > 2:
        servicios = servicios[:-1]  # Remover último servicio
        servicios_str = ", ".join(servicios)
    
    return servicios_str

def generar_huespedes():
    """Genera el diccionario de huéspedes con validaciones exhaustivas."""
    print("🔧 Generando huéspedes...")
    
    # Datos base de huéspedes
    datos_base = [
        {"nombre": "Ana", "apellido": "García", "documento": 30123456, "email": "ana.garcia@mail.com", "telefono": 1123456701, "mediosDePago": ["Efectivo"]},
        {"nombre": "Luis", "apellido": "Pérez", "documento": 31234567, "email": "luis.perez@mail.com", "telefono": 1123456702, "mediosDePago": ["Tarjeta"]},
        {"nombre": "María", "apellido": "López", "documento": 32345678, "email": "maria.lopez@mail.com", "telefono": 1123456703, "mediosDePago": ["Transferencia"]},
        {"nombre": "Carlos", "apellido": "Sánchez", "documento": 33456789, "email": "carlos.sanchez@mail.com", "telefono": 1123456704, "mediosDePago": ["Efectivo"]},
        {"nombre": "Lucía", "apellido": "Martínez", "documento": 34567890, "email": "lucia.martinez@mail.com", "telefono": 1123456705, "mediosDePago": ["Tarjeta"]},
        {"nombre": "Javier", "apellido": "Fernández", "documento": 35678901, "email": "javier.fernandez@mail.com", "telefono": 1123456706, "mediosDePago": ["Transferencia"]},
        {"nombre": "Sofía", "apellido": "Ruiz", "documento": 36789012, "email": "sofia.ruiz@mail.com", "telefono": 1123456707, "mediosDePago": ["Efectivo"]},
        {"nombre": "Diego", "apellido": "Torres", "documento": 37890123, "email": "diego.torres@mail.com", "telefono": 1123456708, "mediosDePago": ["Tarjeta"]},
        {"nombre": "Valentina", "apellido": "Ramírez", "documento": 38901234, "email": "valentina.ramirez@mail.com", "telefono": 1123456709, "mediosDePago": ["Transferencia"]},
        {"nombre": "Martín", "apellido": "Gómez", "documento": 39012345, "email": "martin.gomez@mail.com", "telefono": 1123456710, "mediosDePago": ["Efectivo"]}
    ]
    
    huespedes = {}
    errores = []
    
    for i, datos in enumerate(datos_base, 1):
        idh = f"H{i}"
        
        # Validar ID
        valido, error = validar_id(idh, "ID de huésped")
        if not valido:
            errores.append(f"Huésped {i}: {error}")
            continue
        
        # Validar nombre
        valido, error = validar_nombre_apellido(datos["nombre"], "Nombre")
        if not valido:
            errores.append(f"Huésped {idh}: {error}")
            continue
        
        # Validar apellido
        valido, error = validar_nombre_apellido(datos["apellido"], "Apellido")
        if not valido:
            errores.append(f"Huésped {idh}: {error}")
            continue
        
        # Validar DNI
        valido, error = validar_dni(datos["documento"])
        if not valido:
            errores.append(f"Huésped {idh}: {error}")
            continue
        
        # Validar email
        valido, error = validar_email(datos["email"])
        if not valido:
            errores.append(f"Huésped {idh}: {error}")
            continue
        
        # Validar teléfono
        valido, error = validar_telefono(datos["telefono"])
        if not valido:
            errores.append(f"Huésped {idh}: {error}")
            continue
        
        # Validar unicidad de email y teléfono
        valido, error = validar_unicidad_email_telefono(huespedes, datos["email"], datos["telefono"])
        if not valido:
            errores.append(f"Huésped {idh}: {error}")
            continue
        
        # Si todas las validaciones pasan, agregar el huésped
        huespedes[idh] = {
            "activo": True,
            "nombre": datos["nombre"],
            "apellido": datos["apellido"],
            "documento": datos["documento"],
            "email": datos["email"],
            "telefono": datos["telefono"],
            "mediosDePago": datos["mediosDePago"]
        }
    
    print(f"✅ Huéspedes generados: {len(huespedes)} exitosos, {len(errores)} errores")
    if errores:
        print("❌ Errores en huéspedes:")
        for error in errores:
            print(f"  - {error}")
    
    return huespedes, errores

def generar_habitaciones():
    """Genera el diccionario de habitaciones con validaciones exhaustivas."""
    print("🔧 Generando habitaciones...")
    
    habitaciones = {}
    errores = []
    
    for i in range(1, 11):
        idh = f"R{i}"
        
        # Validar ID
        valido, error = validar_id(idh, "ID de habitación")
        if not valido:
            errores.append(f"Habitación {i}: {error}")
            continue
        
        # Generar datos de la habitación
        tipo = TIPOS_HABITACION[i % len(TIPOS_HABITACION)]
        numero = 100 + i
        descripcion = "Vista al mar"
        precio_noche = 10000 + (i * 500)
        piso = i % 5 + 1
        estado = "Disponible"
        servicios_incluidos = generar_servicios_aleatorios()
        
        # Validar número de habitación
        if not (MIN_LENGTH_NUMERO_HAB <= len(str(numero)) <= MAX_LENGTH_NUMERO_HAB):
            errores.append(f"Habitación {idh}: Número debe tener entre {MIN_LENGTH_NUMERO_HAB} y {MAX_LENGTH_NUMERO_HAB} dígitos")
            continue
        
        # Validar descripción
        if not (MIN_LENGTH_DESCRIPCION <= len(descripcion) <= MAX_LENGTH_DESCRIPCION):
            errores.append(f"Habitación {idh}: Descripción debe tener entre {MIN_LENGTH_DESCRIPCION} y {MAX_LENGTH_DESCRIPCION} caracteres")
            continue
        
        # Validar precio
        if not (MIN_LENGTH_PRECIO <= len(str(precio_noche)) <= MAX_LENGTH_PRECIO):
            errores.append(f"Habitación {idh}: Precio debe tener entre {MIN_LENGTH_PRECIO} y {MAX_LENGTH_PRECIO} caracteres")
            continue
        
        # Validar piso
        if not (MIN_LENGTH_PISO <= len(str(piso)) <= MAX_LENGTH_PISO):
            errores.append(f"Habitación {idh}: Piso debe tener entre {MIN_LENGTH_PISO} y {MAX_LENGTH_PISO} caracteres")
            continue
        
        # Validar servicios
        valido, error = validar_servicios(servicios_incluidos)
        if not valido:
            errores.append(f"Habitación {idh}: {error}")
            continue
        
        # Si todas las validaciones pasan, agregar la habitación
        habitaciones[idh] = {
            "activo": True,
            "numero": numero,
            "tipo": tipo,
            "descripcion": descripcion,
            "precioNoche": precio_noche,
            "piso": piso,
            "estado": estado,
            "serviciosIncluidos": servicios_incluidos
        }
    
    print(f"✅ Habitaciones generadas: {len(habitaciones)} exitosas, {len(errores)} errores")
    if errores:
        print("❌ Errores en habitaciones:")
        for error in errores:
            print(f"  - {error}")
    
    return habitaciones, errores

def verificar_solapamiento_reserva(reservas, id_hab, fecha_entrada, fecha_salida):
    """Verifica si una nueva reserva se solapa con reservas existentes."""
    try:
        dia_ent = int(fecha_entrada[:2])
        mes_ent = int(fecha_entrada[2:4])
        anio_ent = int(fecha_entrada[4:6])
        dia_sal = int(fecha_salida[:2])
        mes_sal = int(fecha_salida[2:4])
        anio_sal = int(fecha_salida[4:6])
        
        fecha_ent = datetime.datetime(2000 + anio_ent, mes_ent, dia_ent)
        fecha_sal = datetime.datetime(2000 + anio_sal, mes_sal, dia_sal)
        
        for rid, datos in reservas.items():
            if datos["idhabitacion"] == id_hab:
                fe_existente = datos["fechaEntrada"]
                fs_existente = datos["fechaSalida"]
                
                if len(fe_existente) == 6 and len(fs_existente) == 6:
                    try:
                        dia_e_ex = int(fe_existente[:2])
                        mes_e_ex = int(fe_existente[2:4])
                        anio_e_ex = int(fe_existente[4:6])
                        dia_s_ex = int(fs_existente[:2])
                        mes_s_ex = int(fs_existente[2:4])
                        anio_s_ex = int(fs_existente[4:6])
                        
                        inicio_existente = datetime.datetime(2000 + anio_e_ex, mes_e_ex, dia_e_ex)
                        fin_existente = datetime.datetime(2000 + anio_s_ex, mes_s_ex, dia_s_ex)
                        
                        if fecha_ent < fin_existente and fecha_sal > inicio_existente:
                            return True
                    except (ValueError, IndexError):
                        continue
        return False
    except (ValueError, IndexError):
        return False

def generar_reservas(huespedes, habitaciones):
    """Genera el diccionario de reservas con validaciones exhaustivas."""
    print("🔧 Generando reservas...")
    
    reservas = {}
    errores = []
    
    # Generar reservas con fechas del mes actual en formato DDMMAA (año 25)
    hoy = datetime.datetime.now()
    mes_actual = hoy.strftime('%m')
    anio = "25"  # Año fijo 2025
    
    for i in range(10):
        # Generar ID de reserva único
        id_reserva = generar_id_reserva(reservas)
        
        # Validar ID
        valido, error = validar_id(id_reserva, "ID de reserva")
        if not valido:
            errores.append(f"Reserva {i+1}: {error}")
            continue
        
        # Validar formato del ID de reserva
        valido, error = validar_formato_id_reserva(id_reserva)
        if not valido:
            errores.append(f"Reserva {id_reserva}: {error}")
            continue
        
        # Generar fechas
        dia = str(i + 1).zfill(2)
        fecha_entrada = f"{dia}{mes_actual}{anio}"
        
        # Calcular fecha de salida válida (máximo 5 días después, sin exceder el mes)
        dia_salida = min(i + 5, DIAS_MAX_POR_MES)
        fecha_salida = f"{str(dia_salida).zfill(2)}{mes_actual}{anio}"
        
        # Validar fechas
        valido, error = validar_fecha_ddmmaa(fecha_entrada, "fecha de entrada")
        if not valido:
            errores.append(f"Reserva {id_reserva}: {error}")
            continue
        
        valido, error = validar_fecha_ddmmaa(fecha_salida, "fecha de salida")
        if not valido:
            errores.append(f"Reserva {id_reserva}: {error}")
            continue
        
        # Verificar que la fecha de salida sea posterior a la de entrada
        try:
            dia_ent = int(fecha_entrada[:2])
            mes_ent = int(fecha_entrada[2:4])
            anio_ent = int(fecha_entrada[4:6])
            dia_sal = int(fecha_salida[:2])
            mes_sal = int(fecha_salida[2:4])
            anio_sal = int(fecha_salida[4:6])
            
            fecha_ent = datetime.datetime(2000 + anio_ent, mes_ent, dia_ent)
            fecha_sal = datetime.datetime(2000 + anio_sal, mes_sal, dia_sal)
            
            if fecha_sal <= fecha_ent:
                errores.append(f"Reserva {id_reserva}: La fecha de salida debe ser posterior a la de entrada")
                continue
                
            cantidad_noches = (fecha_sal - fecha_ent).days
        except ValueError:
            errores.append(f"Reserva {id_reserva}: Error al calcular fechas")
            continue
        
        # Seleccionar huésped y habitación
        idh = f"H{(i % len(huespedes)) + 1}"
        idhab = f"R{(i % len(habitaciones)) + 1}"
        
        # Verificar que el huésped y la habitación existen
        if idh not in huespedes:
            errores.append(f"Reserva {id_reserva}: Huésped {idh} no existe")
            continue
        
        if idhab not in habitaciones:
            errores.append(f"Reserva {id_reserva}: Habitación {idhab} no existe")
            continue
        
        # Verificar que el huésped y la habitación están activos
        if not huespedes[idh]["activo"]:
            errores.append(f"Reserva {id_reserva}: Huésped {idh} está inactivo")
            continue
        
        if not habitaciones[idhab]["activo"]:
            errores.append(f"Reserva {id_reserva}: Habitación {idhab} está inactiva")
            continue
        
        # Verificar solapamiento
        if verificar_solapamiento_reserva(reservas, idhab, fecha_entrada, fecha_salida):
            errores.append(f"Reserva {id_reserva}: Solapamiento detectado con otra reserva")
            continue
        
        # Generar fecha/hora de operación
        fecha_hora = f"2025.{mes_actual}.{dia} - {str(10 + i).zfill(2)}:00:00"
        
        # Generar descuento
        descuento = (i % 4) * 5  # 0, 5, 10, 15
        
        # Si todas las validaciones pasan, agregar la reserva
        reservas[id_reserva] = {
            "idhuesped": idh,
            "idhabitacion": idhab,
            "fechaEntrada": fecha_entrada,
            "fechaSalida": fecha_salida,
            "cantidadNoches": cantidad_noches,
            "descuento": descuento,
            "fechaHoraOperacion": fecha_hora
        }
    
    print(f"✅ Reservas generadas: {len(reservas)} exitosas, {len(errores)} errores")
    if errores:
        print("❌ Errores en reservas:")
        for error in errores:
            print(f"  - {error}")
    
    return reservas, errores

#----------------------------------------------------------------------------------------------
# FUNCIONES DE PERSISTENCIA
#----------------------------------------------------------------------------------------------
def hacer_backup_archivo(ruta):
    """Hace un backup del archivo si existe."""
    if os.path.exists(ruta):
        try:
            import shutil
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"{ruta}.{timestamp}.bak"
            shutil.copy(ruta, backup_name)
            print(f"📋 Backup creado: {backup_name}")
            return True
        except Exception as e:
            print(f"⚠️  No se pudo crear backup de {ruta}: {e}")
            return False
    return True

def guardar_archivo_json(datos, archivo, descripcion):
    """Guarda datos en un archivo JSON con manejo de errores."""
    try:
        hacer_backup_archivo(archivo)
        with open(archivo, 'w', encoding='utf-8') as f:
            json.dump(datos, f, ensure_ascii=False, indent=4)
        print(f"✅ {descripcion} guardado en {archivo}")
        return True
    except Exception as e:
        print(f"❌ Error al guardar {archivo}: {e}")
        return False

#----------------------------------------------------------------------------------------------
# FUNCIONES DE VALIDACIÓN DE INTEGRIDAD
#----------------------------------------------------------------------------------------------
def validar_integridad_referencial(huespedes, habitaciones, reservas):
    """Valida la integridad referencial entre las entidades."""
    print("🔍 Validando integridad referencial...")
    
    errores = []
    
    # Verificar que todos los IDs de huéspedes en reservas existen
    for rid, reserva in reservas.items():
        if reserva['idhuesped'] not in huespedes:
            errores.append(f"Reserva {rid}: Huésped {reserva['idhuesped']} no existe")
        elif not huespedes[reserva['idhuesped']]['activo']:
            errores.append(f"Reserva {rid}: Huésped {reserva['idhuesped']} está inactivo")
        
        if reserva['idhabitacion'] not in habitaciones:
            errores.append(f"Reserva {rid}: Habitación {reserva['idhabitacion']} no existe")
        elif not habitaciones[reserva['idhabitacion']]['activo']:
            errores.append(f"Reserva {rid}: Habitación {reserva['idhabitacion']} está inactiva")
    
    # Verificar solapamientos de reservas
    for rid1, reserva1 in reservas.items():
        for rid2, reserva2 in reservas.items():
            if rid1 >= rid2:  # Evitar comparar consigo mismo y comparaciones duplicadas
                continue
            
            # Solo verificar solapamientos si es la misma habitación
            if reserva1['idhabitacion'] == reserva2['idhabitacion']:
                try:
                    # Convertir fechas a objetos datetime para comparación
                    fe1 = reserva1['fechaEntrada']
                    fs1 = reserva1['fechaSalida']
                    fe2 = reserva2['fechaEntrada']
                    fs2 = reserva2['fechaSalida']
                    
                    if len(fe1) == 6 and len(fs1) == 6 and len(fe2) == 6 and len(fs2) == 6:
                        dia_e1, mes_e1, anio_e1 = int(fe1[:2]), int(fe1[2:4]), int(fe1[4:6])
                        dia_s1, mes_s1, anio_s1 = int(fs1[:2]), int(fs1[2:4]), int(fs1[4:6])
                        dia_e2, mes_e2, anio_e2 = int(fe2[:2]), int(fe2[2:4]), int(fe2[4:6])
                        dia_s2, mes_s2, anio_s2 = int(fs2[:2]), int(fs2[2:4]), int(fs2[4:6])
                        
                        inicio1 = datetime.datetime(2000 + anio_e1, mes_e1, dia_e1)
                        fin1 = datetime.datetime(2000 + anio_s1, mes_s1, dia_s1)
                        inicio2 = datetime.datetime(2000 + anio_e2, mes_e2, dia_e2)
                        fin2 = datetime.datetime(2000 + anio_s2, mes_s2, dia_s2)
                        
                        # Verificar solapamiento
                        if inicio1 < fin2 and fin1 > inicio2:
                            errores.append(f"Solapamiento detectado: Reserva {rid1} ({fe1}-{fs1}) y {rid2} ({fe2}-{fs2}) en habitación {reserva1['idhabitacion']}")
                except (ValueError, IndexError) as e:
                    errores.append(f"Error al validar fechas de reservas {rid1} y {rid2}: {e}")
    
    if errores:
        print(f"❌ Se encontraron {len(errores)} errores de integridad:")
        for error in errores:
            print(f"  - {error}")
        return False
    else:
        print("✅ Integridad referencial validada correctamente")
        return True

def generar_resumen_estadisticas(huespedes, habitaciones, reservas):
    """Genera un resumen estadístico de los datos generados."""
    print("\n📊 RESUMEN ESTADÍSTICO")
    print("=" * 50)
    
    # Estadísticas de huéspedes
    huespedes_activos = sum(1 for h in huespedes.values() if h['activo'])
    print(f"👥 Huéspedes: {len(huespedes)} totales, {huespedes_activos} activos")
    
    # Estadísticas de habitaciones
    habitaciones_activas = sum(1 for h in habitaciones.values() if h['activo'])
    tipos_habitacion = {}
    for h in habitaciones.values():
        if h['activo']:
            tipo = h['tipo']
            tipos_habitacion[tipo] = tipos_habitacion.get(tipo, 0) + 1
    
    print(f"🏨 Habitaciones: {len(habitaciones)} totales, {habitaciones_activas} activas")
    print(f"   Tipos: {', '.join([f'{tipo}: {cant}' for tipo, cant in tipos_habitacion.items()])}")
    
    # Estadísticas de reservas
    print(f"📅 Reservas: {len(reservas)} totales")
    
    # Análisis de fechas de reservas
    anios_reservas = {}
    for r in reservas.values():
        anio = r['fechaEntrada'][4:6]
        anios_reservas[anio] = anios_reservas.get(anio, 0) + 1
    
    print(f"   Por año: {', '.join([f'{anio}: {cant}' for anio, cant in anios_reservas.items()])}")
    
    # Análisis de descuentos
    descuentos = {}
    for r in reservas.values():
        desc = r['descuento']
        descuentos[desc] = descuentos.get(desc, 0) + 1
    
    print(f"   Descuentos: {', '.join([f'{desc}%: {cant}' for desc, cant in descuentos.items()])}")
    
    print("=" * 50)

#----------------------------------------------------------------------------------------------
# FUNCIÓN PRINCIPAL
#----------------------------------------------------------------------------------------------
def main():
    """Función principal del script de conversión."""
    print("🚀 SISTEMA DE GENERACIÓN DE DATOS DE PRUEBA")
    print("=" * 60)
    print("Este script genera archivos JSON con datos de prueba para el sistema hotelero.")
    print("Los datos incluyen huéspedes, habitaciones y reservas con validaciones exhaustivas.")
    print("=" * 60)
    
    # Verificar si los archivos ya existen
    archivos_existentes = []
    for archivo in [ARCHIVO_HUESPEDES, ARCHIVO_HABITACIONES, ARCHIVO_RESERVAS]:
        if os.path.exists(archivo):
            archivos_existentes.append(archivo)
    
    if archivos_existentes:
        print(f"\n⚠️  Los siguientes archivos ya existen:")
        for archivo in archivos_existentes:
            print(f"   - {archivo}")
        
        respuesta = input("\n¿Desea sobrescribir los archivos existentes? (s/n): ").strip().lower()
        if respuesta != 's':
            print("Operación cancelada.")
            return
    
    print("\n🔄 Iniciando generación de datos...")
    
    # Generar datos
    huespedes, errores_huespedes = generar_huespedes()
    habitaciones, errores_habitaciones = generar_habitaciones()
    reservas, errores_reservas = generar_reservas(huespedes, habitaciones)
    
    # Validar integridad referencial
    integridad_ok = validar_integridad_referencial(huespedes, habitaciones, reservas)
    
    # Guardar archivos
    print("\n💾 Guardando archivos...")
    guardado_exitoso = True
    
    if huespedes:
        if not guardar_archivo_json(huespedes, ARCHIVO_HUESPEDES, "Huéspedes"):
            guardado_exitoso = False
    
    if habitaciones:
        if not guardar_archivo_json(habitaciones, ARCHIVO_HABITACIONES, "Habitaciones"):
            guardado_exitoso = False
    
    if reservas:
        if not guardar_archivo_json(reservas, ARCHIVO_RESERVAS, "Reservas"):
            guardado_exitoso = False
    
    # Generar resumen final
    if guardado_exitoso:
        generar_resumen_estadisticas(huespedes, habitaciones, reservas)
        
        total_errores = len(errores_huespedes) + len(errores_habitaciones) + len(errores_reservas)
        
        if total_errores == 0 and integridad_ok:
            print("\n🎉 ¡GENERACIÓN COMPLETADA EXITOSAMENTE!")
            print("✅ Todos los archivos JSON se generaron sin errores")
            print("✅ La integridad referencial es correcta")
            print("✅ Los datos están listos para usar en el sistema hotelero")
        else:
            print(f"\n⚠️  GENERACIÓN COMPLETADA CON ADVERTENCIAS")
            print(f"✅ Los archivos se generaron correctamente")
            print(f"⚠️  Se encontraron {total_errores} errores de validación")
            if not integridad_ok:
                print("⚠️  Se encontraron problemas de integridad referencial")
            print("💡 Los datos generados son funcionales pero revisa los errores")
    else:
        print("\n❌ ERROR EN LA GENERACIÓN")
        print("❌ No se pudieron guardar todos los archivos")
        print("💡 Verifica los permisos de escritura en el directorio")
    
    print("\n" + "=" * 60)
    print("📋 Archivos generados:")
    for archivo in [ARCHIVO_HUESPEDES, ARCHIVO_HABITACIONES, ARCHIVO_RESERVAS]:
        if os.path.exists(archivo):
            print(f"   ✅ {archivo}")
        else:
            print(f"   ❌ {archivo} (no se pudo crear)")
    
    print("\n🚀 Para usar el sistema hotelero, ejecuta: python Entrega2.py")

if __name__ == "__main__":
    main() 