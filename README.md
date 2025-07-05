# Sistema de Gestión Hotelera - Entrega 2

## Descripción General
Este sistema es una aplicación de consola desarrollada en Python para la gestión integral de un hotel. Permite administrar huéspedes, habitaciones y reservas, con persistencia de datos en archivos JSON y un fuerte enfoque en la validación y robustez de los datos.

## ¿Qué hace el sistema?
- Permite **registrar, modificar, eliminar (baja lógica) y buscar huéspedes**.
- Permite **registrar, modificar, eliminar (baja lógica) y buscar habitaciones**.
- Permite **registrar y listar reservas** con validaciones estrictas de fechas, solapamientos y unicidad de IDs.
- Genera **informes automáticos** sobre operaciones, noches y montos por habitación, y cantidad de reservas por huésped.
- Realiza **backups automáticos** de los archivos antes de sobrescribirlos.
- Incluye un **script de conversión** para generar datos de prueba iniciales en formato JSON compatible.

## ¿Cómo funciona?
- El sistema se ejecuta desde consola y presenta un menú principal con opciones para gestionar huéspedes, habitaciones, reservas e informes.
- Todos los datos se almacenan y leen desde archivos JSON (`huespedes.json`, `habitaciones.json`, `reservas.json`).
- Antes de sobrescribir cualquier archivo, se crea una copia de seguridad automática con timestamp (`.YYYYMMDD_HHMMSS.bak`).
- El sistema valida todos los datos ingresados por el usuario en tiempo real, mostrando mensajes claros con emojis ante cualquier error.
- Las bajas de huéspedes y habitaciones son lógicas: no se eliminan físicamente, solo se marcan como inactivos.
- No se permite eliminar huéspedes o habitaciones con reservas activas o futuras.
- Las reservas solo pueden realizarse para los años 2025, 2026 y 2027, y nunca en fechas pasadas.
- Incluye sistema de ayuda contextual en cada menú para guiar al usuario.
- Manejo robusto de errores con opciones de restauración automática desde backups.

## Validaciones y robustez
- **IDs:** Todos los IDs (huéspedes, habitaciones, reservas) son únicos y cumplen con el formato requerido.
  - **IDs de huéspedes y habitaciones:** Entre 2 y 6 caracteres, solo letras y números, no pueden ser solo números.
  - **IDs de reservas:** Exactamente 9 caracteres con formato RSVxxxnnn (RSV + 3 dígitos + 3 letras).
- **Fechas:** Solo se aceptan reservas entre 2025 y 2027, y nunca en el pasado. Se valida que las fechas existan realmente (no 31 de febrero, etc.).
- **Solapamiento:** No se permite reservar una habitación en fechas ya ocupadas.
- **Campos de texto:** Se normalizan espacios y se validan longitudes mínimas y máximas.
- **Servicios incluidos:** Se validan y formatean correctamente, sin servicios vacíos ni cadenas largas.
- **Teléfonos:** Se permite el símbolo "+" solo al inicio si es internacional, y se valida la longitud.
- **Emails:** Se valida el formato con expresiones regulares estrictas.
- **Unicidad:** Se valida que emails, teléfonos, DNIs y números de habitación sean únicos entre entidades activas.
- **Backups:** Antes de sobrescribir cualquier archivo JSON, se crea un backup automático con timestamp.
- **Migración:** Incluye función para migrar reservas antiguas al nuevo formato de fechas.
- **Restauración:** Sistema de restauración automática desde backups en caso de archivos corruptos.

## Tecnología utilizada
- **Lenguaje:** Python 3.x
- **Persistencia:** Archivos JSON
- **Módulos estándar:** `datetime`, `json`, `re`, `random`, `string`, `shutil`
- **No se usan:** Clases, recursividad, ni instrucciones prohibidas (assert, class, global, lambda, nonlocal, yield, async)
- **Interfaz:** Consola (menús y listados tabulares)

## Archivos incluidos
- `Entrega2.py` - Sistema principal con todas las funcionalidades, validaciones y mejoras implementadas
- `Conversión_DICCIONARIO_a_ARCHIVO_JSON.py` - Script mejorado para generar datos de prueba iniciales en JSON con validaciones exhaustivas
- `huespedes.json` - Datos de huéspedes
- `habitaciones.json` - Datos de habitaciones
- `reservas.json` - Datos de reservas
- `*.YYYYMMDD_HHMMSS.bak` - Backups automáticos con timestamp

## Instrucciones de ejecución

### 1. Generar datos de prueba (opcional)
Si es la primera vez que ejecutas el sistema, puedes generar los archivos JSON de prueba ejecutando:
```bash
python Conversión_DICCIONARIO_a_ARCHIVO_JSON.py
```

### 2. Ejecutar el sistema principal
```bash
python Entrega2.py
```

### 3. Navegar por el menú
Sigue las instrucciones en pantalla para gestionar huéspedes, habitaciones, reservas e informes.

## Informes incluidos
- **Listado tabular de operaciones del mes en curso**
- **Resumen anual de cantidad de noches por habitación** (ingresando año en formato AA: 25, 26, 27)
- **Resumen anual de montos totales por habitación** (ingresando año en formato AA: 25, 26, 27)
- **Cantidad de reservas por huésped activo**

## Mejoras implementadas
- **Constantes centralizadas:** Todos los límites y opciones válidas están definidos como constantes para facilitar mantenimiento.
- **Validaciones mejoradas:** Validación de unicidad de emails, teléfonos, DNIs y números de habitación, mejor manejo de errores con mensajes descriptivos.
- **Validación de IDs específica:** 
  - IDs de huéspedes y habitaciones: 2-6 caracteres, solo letras y números, no solo números.
  - IDs de reservas: Exactamente 9 caracteres con formato RSVxxxnnn.
- **Validación de fechas robusta:** Verificación de fechas válidas, límites de tiempo (máximo 2 años en el futuro, máximo 30 días de reserva).
- **Validación de precios y números:** Límites razonables para precios (máximo $10,000), pisos (máximo 100), números de habitación (máximo 9999).
- **Validación de texto mejorada:** Prevención de espacios múltiples, caracteres problemáticos, y formatos incorrectos.
- **Validación de descuentos:** Rango de 0-100% con validación de porcentajes.
- **Backups con timestamp:** Los backups incluyen fecha y hora para evitar sobrescrituras.
- **Sistema de ayuda:** Cada menú incluye opción de ayuda contextual con formatos requeridos.
- **Manejo robusto de errores:** Restauración automática desde backups en caso de archivos corruptos.
- **Experiencia de usuario mejorada:** Mensajes con emojis, confirmaciones detalladas, y mejor presentación visual.
- **Validaciones exhaustivas:** El script de conversión incluye validaciones completas y reportes de errores.

## Notas importantes
- Todos los cambios se guardan automáticamente en los archivos JSON.
- El sistema es robusto ante errores de usuario y protege la integridad de los datos.
- Los backups automáticos con timestamp permiten recuperar información ante cualquier problema.
- El sistema está pensado para ser evaluado en términos de buenas prácticas, validaciones y robustez.
- Incluye sistema de ayuda contextual para facilitar el uso.

## Autor
Equipo 5 - Programación 1 (Viernes async) 