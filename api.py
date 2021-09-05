import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from PIL import Image
import numpy as np
import logging
import base64, io
from align import alignment_correction

logging.basicConfig(level=logging.INFO)

# Initialize the Flask application
app = Flask(__name__)
CORS(app)

def pil_to_base64(img):
    im_file = io.BytesIO()
    img.save(im_file, format="JPEG")
    im_bytes = im_file.getvalue()  # im_bytes: image in binary format.
    im_b64 = base64.b64encode(im_bytes).decode('ascii')
    return im_b64

# Simple probe.
@app.route('/', methods=['GET'])
def hello():
    return 'Hello Alignment Correction!'


# Route http posts to this method
@app.route('/align', methods=['POST'])
def run():
    if 'img' not in request.json:
        return jsonify({'error': 'missing file param `img`'}), 400
    data = request.json['img']
    if not data:
        return jsonify({'error': 'empty image'}), 400
    input_img = Image.open(io.BytesIO(base64.b64decode(data)))
    img = np.array(input_img)
    img = img[:, :, ::-1].copy() 
    aligned_img = alignment_correction(img)
    pil_img = Image.fromarray(aligned_img)
    pil_encoded = pil_to_base64(pil_img)
    return jsonify({'aligned_image': pil_encoded}), 200

if __name__ == '__main__':
    port = 9000
    app.run(debug=False, host='0.0.0.0', port=port)
