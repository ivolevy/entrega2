import json
import datetime

# Diccionarios originales copiados del main (Entrega2.py)
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

# Guardar los archivos JSON
with open('huespedes.json', 'w', encoding='utf-8') as f:
    json.dump(huespedes, f, ensure_ascii=False, indent=4)
with open('habitaciones.json', 'w', encoding='utf-8') as f:
    json.dump(habitaciones, f, ensure_ascii=False, indent=4)
with open('reservas.json', 'w', encoding='utf-8') as f:
    json.dump(reservas, f, ensure_ascii=False, indent=4)

print("Archivos JSON generados correctamente.") 