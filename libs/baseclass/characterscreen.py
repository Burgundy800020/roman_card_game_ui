import os,requests
from kivymd.app import MDApp
from kivy.clock import mainthread
from kivy.properties import StringProperty,ObjectProperty
from kivy.metrics import dp
from kivy.animation import Animation
from kivy.graphics.texture import Texture
from kivy.uix.screenmanager import Screen
from kivy.uix.modalview import ModalView
from kivymd.uix.boxlayout import MDBoxLayout
from kivy.uix.behaviors import ButtonBehavior
from kivymd.uix.behaviors import HoverBehavior
import libs.engine as engine
from libs.utilities import thread

app=MDApp.get_running_app()

class WaitingNotice(ModalView):
    pass

class CharacterBox(HoverBehavior,ButtonBehavior,MDBoxLayout):
    name=StringProperty()
    image=ObjectProperty()
    description=StringProperty()

    def on_enter(self):Animation(size=(dp(280),dp(390)),duration=.2).start(self);self.md_bg_color=(.2,.2,.2,.9)
    def on_leave(self):Animation(size=(dp(260),dp(360)),duration=.2).start(self);self.md_bg_color=(.2,.2,.2,.7)

    @mainthread
    def on_image(self,_,image):
        texture=Texture.create(size=(image.shape[1],image.shape[0]),colorfmt="rgba")
        texture.blit_buffer(image.tobytes(),bufferfmt="ubyte",colorfmt="rgba")
        self.ids["characterimage"].texture=texture

class CharacterScreen(Screen):
    code=StringProperty()

    def __init__(self,**kwargs):
        super(CharacterScreen,self).__init__(**kwargs)
        app.client.on("getCharacterChoices")(lambda data:self.getCharacterChoices(data))
        app.client.on("startGame")(lambda data:self.startGame())
        self.waitingNotice=WaitingNotice()

    def initialize(self,code):
        self.code=code
    
    @thread
    def cancel(self):
        mainthread(lambda:setattr(self.manager,"current","HomeScreen"))()
        requests.get(f"{os.environ['server']}/deleteRoom",data={"id":self.code})
    
    @mainthread
    def getCharacterChoices(self,data):
        data=data["characters"]
        for i in range(2):
            data[i]=engine.makeCharacterCard(data[i])
        for card,info in zip((self.ids["character1"],self.ids["character2"]),data):
            card.name=info.name
            card.image=info.image
            card.description=info.description
        
    def chooseCharacter(self,name):
        app.client.emit(f"{self.code}/setCharacterChoice",data={"character":name})
        self.waitingNotice.open()
    
    @mainthread
    def startGame(self):
        self.manager.get_screen("GameScreen").initialize(self.code)
        self.manager.current="GameScreen"
        self.waitingNotice.dismiss()