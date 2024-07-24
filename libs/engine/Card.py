import zipfile, io
from random import randint
from PIL import Image
import numpy as np
from os.path import isdir
from os.path import dirname

"""
target = "assets/sources.zip"
if not isdir(dirname(target)):
    print('cannot create zipfile because target does not exists')
else:
    pass
    # create the zipfile
"""
archive = zipfile.ZipFile(r"assets/sources.zip", "r")

def readImage(name:str, source=archive) -> np.array:
    #fetch source archive for card image using class name
    #return image in bytes format
    try:data = io.BytesIO(source.read(f"{name}.png"))
    except:data = io.BytesIO(source.read("Soldier.png"))
    data.seek(0)
    
    #transform to numpy array
    image = Image.open(data).convert("RGBA")
    return np.flipud(np.array(image, dtype=np.uint8))

class Card:
    def __init__(self):
        self.numeral = randint(1, 6)
        self.available = True

    def toJson(self):
        #convert card into json format
        return {
            "type":self.type,
            "numeral":self.numeral,
            "available":self.available}
    
    def fromJson(self, data):
        #load card information from json data
        self.type = data["type"]
        self.numeral = data["numeral"]
        self.available = data["available"]

class CharacterCard:
    def __init__(self, character:str):
        self.name = character
        self.image = readImage(character)
        self.description = "This is a very very long string that is not that long finally to test text."

