"""
- Resize image to appropriate aspect ratio
- Convert image format to png
- Zip image into sources archive
"""
import sys, zipfile, io
from PIL import Image

file = sys.argv[1]
archive = zipfile.ZipFile("assets/sources.zip", "a")

image = Image.open(file)
image = image.resize((150, 200))

image_bytes = io.BytesIO()
image.save(image_bytes, format="png")
image_bytes.seek(0)

file_png = ".".join(file.split(".")[:-1])+ ".png"
with archive.open(file_png, "w") as file:
    file.write(image_bytes.read())
    file.close()
archive.close()