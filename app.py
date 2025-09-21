import os
import io
import base64
from flask import Flask, request, jsonify, render_template_string
from flask_restx import Api, Resource, fields
from werkzeug.datastructures import FileStorage
import google.generativeai as genai
import PyPDF2
from pdf2image import convert_from_bytes
from PIL import Image
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
api = Api(
    app,
    version='1.0',
    title='PDF Text Extractor API',
    description='API para extraer texto de archivos PDF usando Google Gemini AI',
    doc='/docs/'
)

ns = api.namespace('pdf', description='Operaciones de procesamiento de PDF')

genai.configure(api_key=os.getenv('GEMINI_API_KEY'))

def pdf_to_images(pdf_bytes):
    try:
        images = convert_from_bytes(pdf_bytes, dpi=200)
        return images
    except Exception as e:
        print(f"Error converting PDF to images: {e}")
        return []

def image_to_base64(image):
    buffer = io.BytesIO()
    image.save(buffer, format='PNG')
    img_str = base64.b64encode(buffer.getvalue()).decode()
    return img_str

def process_page_with_gemini(image):
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')

        prompt = """
        Analiza esta página de PDF y extrae todo el texto visible incluyendo:
        - Texto normal
        - Texto en tablas (preservando la estructura)
        - Texto en imágenes si es legible
        - Cualquier otro contenido textual

        Devuelve el solo el texto extraído de forma estructurada y legible, no incluyas comentarios ni razonamiento alguno. 
        """

        response = model.generate_content([prompt, image])
        return response.text
    except Exception as e:
        print(f"Error processing with Gemini: {e}")
        return f"Error processing page: {str(e)}"

upload_parser = api.parser()
upload_parser.add_argument('file', location='files', type=FileStorage, required=True, help='Archivo PDF a procesar')

page_text_model = api.model('PageText', {
    'page': fields.Integer(required=True, description='Número de página'),
    'text': fields.String(required=True, description='Texto extraído de la página')
})

pdf_response_model = api.model('PDFResponse', {
    'total_pages': fields.Integer(required=True, description='Número total de páginas procesadas'),
    'extracted_text': fields.List(fields.Nested(page_text_model), required=True, description='Texto extraído por página'),
    'full_text': fields.String(required=True, description='Todo el texto concatenado')
})

error_model = api.model('Error', {
    'error': fields.String(required=True, description='Mensaje de error')
})

health_model = api.model('Health', {
    'status': fields.String(required=True, description='Estado del servicio')
})

@ns.route('/process')
class ProcessPDF(Resource):
    @api.expect(upload_parser)
    @api.response(200, 'Éxito', pdf_response_model)
    @api.response(400, 'Error en la solicitud', error_model)
    @api.response(500, 'Error del servidor', error_model)
    @api.doc('process_pdf')
    def post(self):
        """Procesa un archivo PDF y extrae todo el texto usando Gemini AI"""
        args = upload_parser.parse_args()
        file = args['file']

        if not file:
            return {'error': 'No file provided'}, 400

        if file.filename == '':
            return {'error': 'No file selected'}, 400

        if not file.filename.lower().endswith('.pdf'):
            return {'error': 'File must be a PDF'}, 400

        try:
            pdf_bytes = file.read()

            images = pdf_to_images(pdf_bytes)
            if not images:
                return {'error': 'Could not convert PDF to images'}, 500

            extracted_text = []

            for i, image in enumerate(images):
                page_text = process_page_with_gemini(image)
                extracted_text.append({
                    'page': i + 1,
                    'text': page_text
                })

            result = {
                'total_pages': len(images),
                'extracted_text': extracted_text,
                'full_text': ' '.join([page['text'] for page in extracted_text])
            }

            return result

        except Exception as e:
            return {'error': f'Processing failed: {str(e)}'}, 500

@ns.route('/health')
class Health(Resource):
    @api.response(200, 'Servicio funcionando', health_model)
    @api.doc('health_check')
    def get(self):
        """Verifica el estado del servicio"""
        return {'status': 'healthy'}

@app.route('/')
def home():
    """Página de inicio"""
    return render_template_string('<h1>Herramientas para POC AERATION</h1>')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)