import pytesseract
from PIL import Image

pytesseract.pytesseract.tesseract_cmd = r"C:\Users\user\AppData\Local\Programs\Tesseract-OCR"

text = pytesseract.image_to_string(Image.open("Vehicle-Inspection-Report-Template.jpg"))
print(text)
