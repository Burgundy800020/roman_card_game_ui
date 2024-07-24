from kivymd.app import MDApp
from kivy.properties import StringProperty,ListProperty,BooleanProperty,NumericProperty, ObjectProperty
from kivy.metrics import dp
from kivy.clock import Clock,mainthread
from kivy.graphics.texture import Texture
from kivy.uix.screenmanager import ScreenManager,Screen
from kivymd.uix.boxlayout import MDBoxLayout
from kivy.uix.modalview import ModalView
from kivymd.uix.widget import MDWidget
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.graphics import Rectangle, Color
from random import randint
import libs.engine as engine

app=MDApp.get_running_app()

#play_event
PLAY = 1
DISCARD = 2
DEFEND = 3
TESTUDO = 4
VETO = 5
CREDITOR = 101

#deploy_event
DEPLOY_MAIN = 11
DEPLOY_AUX = 12
BOOST = 13
AQUILIFER = 14
CAMP = 15
#destroy_event
BARBARIAN = 21
CONSULTUM = 22
EXILE = 301
TRIBAL = 302

#map event -> tutorial
Tutorial = {0:"", 1:"Select a card to play", 2:'', 3:"play [defend]?", 4:"play [testudo]?", 5:"play [veto]?",
            11:"Select a unit", 12:"Select a unit", 13:"Select a unit to boost", 14:"Select a unit to awake",
            15:"Select a unit to encamp",
            21:"Select an enemy unit to destroy", 22:"Do you obey to the Senate's final decree?",
            101:"Pay your debts towards Crassus",
            301:"use <<Exile>>? (Draw 3 cards and heal 1 hp. Skip the rest of your turn)",
            302:"use <<Tribal Alliance>>? (Lose 1 hp and add 1 attack pt to each of your Celtic Warriors and auxiliaries)"
            }


#map event -> event string
Event = {0:"", 1:"Playphase", 2:"Discard", 3:"Enemy Attack", 4:'Opponent Military', 5:'Opponent Political',
         11:'Main unit', 12:"Auxiliary unit", 13:"Booster", 14:'Aquilifer', 15:'Encampment',
         21:'Barbarian Invasion', 22:'Senatus Consultum Ultimum',
         101:"Creditor",
         301:'Exile',302:'Tribal Alliance'}

class EndGame(ModalView):
    homeCallback = ObjectProperty()
    def __init__(self,**kwargs):
        super(EndGame,self).__init__(**kwargs)
    
    def redirect(self, function):
        self.dismiss()
        function()

class LifeBar(MDBoxLayout):
    reversed=BooleanProperty(False)

    def __init__(self,**kwargs):
        super(LifeBar,self).__init__(**kwargs)
        Clock.schedule_once(lambda dt: self.on_state(10))
    
    def dot(self, color):
        return MDWidget(size_hint=(None,None),size=(dp(12),dp(12)),radius=dp(6),md_bg_color=(0,color,0,1))

    def on_state(self,state):
        self.clear_widgets()
        if self.reversed:
            self.add_widget(MDWidget())
            for life in range(10-state):
                self.add_widget(self.dot(0))
            for life in range(10-state, 10):
                self.add_widget(self.dot(1))
        else:
            for life in range(state):
                self.add_widget(self.dot(1))
            for life in range(state, 10):
                self.add_widget(self.dot(0))

class Quote(MDBoxLayout):
    side = StringProperty()
    def __init__(self, *args, **kargs):
        super(Quote, self).__init__(*args, **kargs)
        with self.canvas.before:
            Rectangle(size=self.size, pos=self.pos, 
                      source=f"libs/baseclass/Images/quotePlayer")

class Character(MDBoxLayout):
    button = None
    def setPortrait(self, name):
        but = Button(background_normal = f"assets/portraits/{name}.png",
                     size_hint_x = None,
                     color = (1, 0, 0, 1),
                     width = dp(93),
                     font_size = 20)
        self.add_widget(but)
        self.button = but
        
class GameScreen(Screen):
    code=StringProperty()

    playable = [False]*10
    deployable = [False]*3
    destroyable = [False]*3
    options = [None]*3

    dialogues_cnt = 0
    dialogues_max = 8
    
    def __init__(self,**kwargs):
        super(GameScreen,self).__init__(**kwargs)
        
        self.options[0] = lambda instance : self.choose(0)
        self.options[1] = lambda instance : self.choose(1)
        self.options[2] = lambda instance : self.choose(2)

        self.endgame = EndGame(homeCallback = self.returnHome)

        #sets display
        app.client.on("setCharacterName")(lambda data:self.setCharacterName(data))
        app.client.on("addDialogue")(lambda data:self.addDialogue(data))
        app.client.on("addQuote")(lambda data:self.addQuote(data))
        app.client.on("gameOver")(lambda data:self.gameOver(data))

        #update game state
        app.client.on("updateHand")(lambda data:self.updateHand(data))
        app.client.on("updateHp")(lambda data:self.updateHp(data))
        app.client.on("updateUnits")(lambda data:self.updateUnits(data))
        app.client.on("updateStates")(lambda data:self.updateStates(data))

        #input
        app.client.on("playInput")(lambda data:self.playInput(data))
        app.client.on("deployInput")(lambda data:self.deployInput(data))
        app.client.on("destroyInput")(lambda data:self.destroyInput(data))

    def initialize(self,code):
        self.code=code

    def returnHome(self):
        self.manager.current="HomeScreen"

    @mainthread
    def gameOver(self, data):
        self.endgame.open()

    def reset(self):
        self.ids["tutorial"].text = ""
        for i in range(10):
            self.playable[i] = False
            if i < 3:
                self.deployable[i] = False
                self.destroyable[i] = False
        self.ids["playerOptions"].clear_widgets()
    
    def updateOptions(self, choices):
        self.ids["playerOptions"].clear_widgets()
        if choices is not None:
            self.ids["playerOptions"].add_widget(MDWidget())
            for i in range(len(choices)):
                self.addOption(choices[i], self.options[i])
            self.ids["playerOptions"].add_widget(MDWidget())
    
    def addOption(self, name, fun):
        button = Button(text = name,
                        size_hint = (None, None),
                        size = (dp(180), dp(74)),
                        background_normal = "libs/baseclass/Images/button1.png")
        button.bind(on_press = fun)
        self.ids["playerOptions"].add_widget(button)

    def setTutorial(self, event):
        text = Event[event] + "\n" + Tutorial[event]
        self.ids['tutorial'].text = text

    @mainthread
    def playInput(self, data):
        event = data['event']
        choices = data['choices']
        self.setTutorial(event)
        self.updateOptions(choices)
        for i in data['n']:
            self.playable[i] = True

    @mainthread
    def deployInput(self, data):
        self.ids["tutorial"].text = Event[data['event']]
        choices = data['choices']
        self.updateOptions(choices)
        for i in data['n']:
            self.deployable[i] = True

    @mainthread
    def destroyInput(self, data):
        choices = data['choices']
        self.ids["tutorial"].text = Event[data['event']]
        self.updateOptions(choices)
        for i in data['n']:
            self.destroyable[i] = True

    @mainthread
    def play(self, i):
        if self.playable[i]:
            self.reset()
            app.client.emit(f"{self.code}/playListen",data={"i":i})
            
    @mainthread
    def deploy(self, i):
        if self.deployable[i]:
            self.reset()
            app.client.emit(f"{self.code}/deployListen",data={"i":i})

    @mainthread
    def destroy(self, i):
        if self.destroyable[i]:
            self.reset()
            app.client.emit(f"{self.code}/destroyListen",data={"i":i})
    
    @mainthread
    def choose(self, i):
        self.reset()
        app.client.emit(f"{self.code}/chooseListen",data={"i":i})


    @mainthread 
    def updateHp(self, data):
        for side in ("player", "opponent"):
            if f"{side}Hp" in data:
                self.ids[f"{side}Life"].on_state(int(data[f"{side}Hp"]))

    @mainthread
    def updateStates(self, data):
        for side in ("player", "opponent"):
            if side in data:
                text = ''
                for key, val in data[side].items():
                    if val:
                        text = text + key.upper() + '\n'
                self.ids[f'{side}Picture'].button.text = text

    @mainthread
    def updateHand(self, data):
        if "playerCards" in data:
            self.ids["playerCards"].ids["cards"].clear_widgets()
            for i in range(0, len(data["playerCards"])):
                card_name = data["playerCards"][i]["name"]
                button = Button(text = card_name,
                                color = (50, 0, 20, 1),
                                background_normal = "libs/baseclass/Images/card_f.png",
                                size_hint = (None, None),
                                size = (dp(90), dp(120)),
                                halign = "center",
                                valign = "center",
                                font_size = 20)
                button.text_size = button.size
                
                if i == 0:
                    fun = lambda instance: self.play(0)
                elif i == 1:
                    fun = lambda instance: self.play(1)
                elif i == 2:
                    fun = lambda instance: self.play(2)
                elif i == 3:
                    fun = lambda instance: self.play(3)
                elif i == 4:
                    fun = lambda instance: self.play(4)
                elif i == 5:
                    fun = lambda instance: self.play(5)
                elif i == 6:
                    fun = lambda instance: self.play(6)
                elif i == 7:
                    fun = lambda instance: self.play(7)
                elif i == 8:
                    fun = lambda instance: self.play(8)

                button.bind(on_press = fun)                
                self.ids["playerCards"].ids['cards'].add_widget(button)
            
        if "opponentCards" in data:
            self.ids["opponentCards"].ids['cards'].clear_widgets()
            for i in range(int(data["opponentCards"])):
                button = Button(background_normal = "libs/baseclass/Images/card.png",
                                size_hint = (None, None),
                                size = (dp(83), dp(120)))
                self.ids["opponentCards"].ids['cards'].add_widget(button)
    
    def addUnit(self,side, i, data):
        unit_name = data[side][i]["name"]
        state = data[side][i]["available"]
        ap = data[side][i]["ap"]
        button = Button(text = f'{unit_name} {ap}',
                        size_hint = (None, None),
                        color = (0, 1, 0, 1) if state else (1,1 , 0, 1),
                        size = (dp(120), dp(60)),
                        font_size = 26,
                        background_normal = "",
                        background_color = (.9,.1,.25, 1))
        if side == 'playerUnits':    
            if i == 0:
                fun = lambda instance: self.deploy(0)
            elif i == 1:
                fun = lambda instance: self.deploy(1)
            elif i == 2:
                fun = lambda instance: self.deploy(2)
        else:
            if i == 0:
                fun = lambda instance: self.destroy(0)
            elif i == 1:
                fun = lambda instance: self.destroy(1)
            elif i == 2:
                fun = lambda instance: self.destroy(2)
        button.bind(on_press = fun)
        self.ids[side].add_widget(button)

    @mainthread
    def updateUnits(self, data):
        if "playerUnits" in data:
            self.ids["playerUnits"].clear_widgets()
            for i in range(len(data["playerUnits"])):
                self.addUnit("playerUnits", i, data)
                
        if "opponentUnits" in data:
            self.ids["opponentUnits"].clear_widgets()
            for i in range(len(data["opponentUnits"])):
                self.addUnit("opponentUnits", i, data)
    
    @mainthread
    def quote_callback(self, side):
        self.ids[f"{side}Quote"].text = "" 
        self.ids[f"{side}Quote"].background_color = (0, 0, 0, 0) 


    @mainthread
    def addQuote(self, data):
        if "playerQuote" in data:
            text = data["playerQuote"]
            self.ids["playerQuote"].text = text 
            self.ids["playerQuote"].background_color = (1, 1, 1, 1)
            Clock.schedule_once(lambda dt:self.quote_callback("player"), 10)
        elif "opponentQuote" in data:
            text = data["opponentQuote"]
            self.ids["opponentQuote"].text = text
            self.ids["opponentQuote"].background_color = (1, 1, 1, 1)
            Clock.schedule_once(lambda dt:self.quote_callback("opponent"), 8)

    @mainthread
    def addDialogue(self, data):
        if self.dialogues_cnt == self.dialogues_max:
            self.dialogue.text = ""
            self.dialogues_cnt = 0
        self.dialogue.text = f"{self.dialogue.text}\n{data['text']}" 
        self.dialogues_cnt += 1

    @mainthread
    def setCharacterName(self, data):
        for side in ("player", "opponent"):
            self.ids[f"{side}Picture"].setPortrait(data[side])
            self.ids[f"{side}Name"].text = data[f"{side}Full"]
            

"""
    @mainthread
    def setCharacterName(self,data):
        for side in ("player","opponent"):
            image=engine.getImage(data[side])
            texture=Texture.create(size=(image.shape[1],image.shape[0]),colorfmt="rgba")
            texture.blit_buffer(image.tobytes(),bufferfmt="ubyte",colorfmt="rgba")
            self.ids[f"{side}Picture"].texture=texture
            self.ids[f"{side}Picture"].tooltip_text=data[side]
"""
    
    
    