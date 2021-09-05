import requests
import base64, io
from PIL import Image
import os
def test(img):
    files= {'img': img}
    headers={}
    res = requests.post("http://localhost:9000/align", headers=headers, json=files)
    aligned_str = res.json()['aligned_image']
    aligned_img = Image.open(io.BytesIO(base64.b64decode(aligned_str)))
    return aligned_img

for img_pth in os.listdir('inputs/'):
    input_img = 'inputs/' + img_pth
    with open(input_img, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read())
    output = test(encoded_string)
    output.save('outputs/' + img_pth)