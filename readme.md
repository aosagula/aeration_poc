# PDF Text Extractor with Gemini AI

API endpoint que procesa archivos PDF para extraer texto usando Google Gemini AI. Procesa cada página individualmente para extraer texto de contenido normal, tablas e imágenes.

## Características

- Extracción de texto de PDFs con texto, imágenes y tablas
- Procesamiento página por página con Gemini AI
- API REST con Flask
- Contenedor Docker con Alpine Linux
- Respuesta JSON estructurada

## Configuración

1. Clona el repositorio
2. Crea un archivo `.env` basado en `.env.example`:
   ```
   GEMINI_API_KEY=tu_clave_api_gemini
   ```

## Uso con Docker

### Construir y ejecutar
```bash
docker build -t pdf-processor .
docker run -p 5000:5000 --env-file .env pdf-processor
```

### Con Docker Compose
```bash
docker-compose up --build
```

## API Endpoints

### POST /process-pdf

Procesa un archivo PDF y extrae todo el texto utilizando Google Gemini AI. Convierte cada página del PDF a imagen y las procesa individualmente para extraer texto de contenido normal, tablas e imágenes.

**URL:** `http://localhost:5000/process-pdf`

**Método:** POST

**Headers:**
- `Content-Type: multipart/form-data`

**Parámetros:**
- `file` (required): Archivo PDF a procesar
  - Tipo: File
  - Formatos soportados: .pdf
  - Tamaño máximo: Limitado por configuración del servidor

**Request Example:**
```bash
curl -X POST \
  -F "file=@document.pdf" \
  http://localhost:5000/process-pdf
```

**Response Success (200):**
```json
{
  "total_pages": 3,
  "extracted_text": [
    {
      "page": 1,
      "text": "Texto extraído de la página 1 incluyendo contenido de tablas y texto en imágenes..."
    },
    {
      "page": 2,
      "text": "Texto extraído de la página 2..."
    },
    {
      "page": 3,
      "text": "Texto extraído de la página 3..."
    }
  ],
  "full_text": "Todo el texto concatenado de todas las páginas..."
}
```

**Response Fields:**
- `total_pages` (integer): Número total de páginas procesadas
- `extracted_text` (array): Array de objetos con el texto extraído por página
  - `page` (integer): Número de página (empezando en 1)
  - `text` (string): Texto extraído de la página
- `full_text` (string): Todo el texto concatenado en un solo string

**Error Responses:**

**400 Bad Request - No file provided:**
```json
{
  "error": "No file provided"
}
```

**400 Bad Request - No file selected:**
```json
{
  "error": "No file selected"
}
```

**400 Bad Request - Invalid file format:**
```json
{
  "error": "File must be a PDF"
}
```

**500 Internal Server Error - PDF conversion failed:**
```json
{
  "error": "Could not convert PDF to images"
}
```

**500 Internal Server Error - Processing failed:**
```json
{
  "error": "Processing failed: [error details]"
}
```

### GET /health

Endpoint de verificación de estado del servicio.

**URL:** `http://localhost:5000/health`

**Método:** GET

**Headers:** Ninguno requerido

**Parámetros:** Ninguno

**Request Example:**
```bash
curl -X GET http://localhost:5000/health
```

**Response Success (200):**
```json
{
  "status": "healthy"
}
```

**Response Fields:**
- `status` (string): Estado del servicio ("healthy" cuando funciona correctamente)

## Documentación Swagger

La API incluye documentación interactiva Swagger/OpenAPI disponible en:

**URL:** `http://localhost:5000/docs/`

Esta interfaz permite:
- Explorar todos los endpoints disponibles
- Ver esquemas de request/response
- Probar los endpoints directamente desde el navegador
- Descargar archivos PDF y ver los resultados en tiempo real

### Nuevas rutas con Swagger:
- `POST /pdf/process` - Endpoint para procesar PDFs
- `GET /pdf/health` - Endpoint de verificación de estado
- `GET /docs/` - Documentación Swagger interactiva

## Testing

```bash
# Instalar dependencias de testing
pip install requests

# Ejecutar tests
python test_endpoint.py
```

## Uso del API

### Con curl (rutas originales siguen funcionando):
```bash
# Procesar PDF
curl -X POST \
  -F "file=@document.pdf" \
  http://localhost:5000/pdf/process

# Verificar estado
curl -X GET http://localhost:5000/pdf/health
```

### Con Swagger UI:
1. Abre `http://localhost:5000/docs/` en tu navegador
2. Expande el endpoint `/pdf/process`
3. Haz clic en "Try it out"
4. Selecciona tu archivo PDF
5. Haz clic en "Execute"
6. Ve los resultados directamente en la interfaz
