from flask import Flask, request, render_template, jsonify
import pytesseract
from PIL import Image, ImageOps
import os
from translatepy import Translator

# Set Tesseract OCR data path
os.environ['TESSDATA_PREFIX'] = r'C:\Program Files\Tesseract-OCR\tessdata'

app = Flask(__name__)

def extract_text(image_path, image_type='document', lang='eng'):
    preprocessed_image = preprocess_image(image_path, image_type)
    text = pytesseract.image_to_string(preprocessed_image, lang=lang)
    return text

def preprocess_image(image_path, image_type):
    image = Image.open(image_path)
    if image_type == 'document':
        image = image.convert('L')
        image = image.point(lambda p: 255 if p > 127 else 0)
    elif image_type == 'screenshot':
        image = image.convert('L')
        image = ImageOps.autocontrast(image)
        image = image.point(lambda p: 255 if p > 128 else 0)
    elif image_type == 'pic':
        image = image.convert('L')
    return image

def translate_text(text, dest_lang='en'):
    translator = Translator()
    translation = translator.translate(text, dest_lang)
    translated_text = translation.result
    return translated_text

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'})

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'})

    image_type = request.form.get('image_type', 'document')
    src_lang = request.form.get('src_lang', 'eng')

    file_path = os.path.join('uploads', file.filename)
    file.save(file_path)

    text = extract_text(file_path, image_type, lang=src_lang)
    translated_text = translate_text(text, dest_lang='en')

    return jsonify({'extracted_text': text, 'translated_text': translated_text})

if __name__ == '__main__':
    if not os.path.exists('uploads'):
        os.makedirs('uploads')
    app.run(debug=True)
