# Sistema de Gestión Hotelera - Entrega 2

## Descripción
Sistema de gestión hotelera desarrollado en Python que permite administrar huéspedes, habitaciones y reservas con persistencia en archivos JSON.

## Archivos incluidos
- `Entrega2.py` - Sistema principal con todas las funcionalidades
- `huespedes.json` - Datos iniciales de huéspedes
- `habitaciones.json` - Datos iniciales de habitaciones  
- `reservas.json` - Datos iniciales de reservas

## Requisitos
- Python 3.x
- Módulos estándar: `datetime`, `json`, `re`

## Instrucciones de ejecución

### 1. Ejecutar el sistema
```bash
python Entrega2.py
```

### 2. Funcionalidades disponibles
El sistema incluye las siguientes opciones en el menú principal:

#### Gestión de Huéspedes
- [1] Ingresar huésped
- [2] Modificar huésped  
- [3] Eliminar huésped (baja lógica)
- [4] Listar huéspedes activos
- [5] Buscar huésped

#### Gestión de Habitaciones
- [1] Ingresar habitación
- [2] Modificar habitación
- [3] Eliminar habitación (baja lógica)
- [4] Listar habitaciones activas
- [5] Buscar habitación

#### Gestión de Reservas
- [1] Registrar reserva
- [2] Listar reservas

#### Informes
- [1] Listado tabular de operaciones del mes en curso
- [2] Resumen anual de cantidad de noches por habitación
- [3] Resumen anual de montos totales por habitación
- [4] Informe a elección: cantidad de reservas por huésped activo

## Características implementadas

### ✅ Requisitos técnicos cumplidos
- Código desarrollado en archivo `Entrega2.py`
- Diccionarios precargados comentados (no eliminados)
- Conversión a archivos JSON implementada
- Funciones CRUD ajustadas para leer/escribir archivos JSON
- Control de excepciones en todas las funciones
- Validación de email con expresiones regulares
- Patrón regex: `^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$`

### ✅ Restricciones respetadas
- No se usan módulos no vistos en clase
- No hay recursividad
- No se usan: continue, assert, class, global, lambda, nonlocal, yield, async

## Datos iniciales
El sistema incluye datos de prueba:
- **10 huéspedes** con información completa (H1-H10)
- **10 habitaciones** de diferentes tipos y precios (R1-R10)
- **10 reservas** del mes actual para demostrar funcionalidad

## Notas importantes
- Todos los cambios se guardan automáticamente en los archivos JSON
- El sistema valida fechas, emails y datos numéricos
- Las bajas son lógicas (campo "activo" = False)
- Los informes se generan a partir de los datos actuales en los archivos

## Autor
Equipo 5 - Programación 1 (Viernes async) 






Ya modificado y testeado
- Gestion de huespedes
    - ingresar huesped
    - modificar huesped
