from kivymd.app import MDApp
from kivy.core.window import Window
from kivy.properties import NumericProperty,ObjectProperty
from kivy.metrics import dp
from kivy.animation import Animation
from kivy.uix.screenmanager import Screen
from kivy.uix.button import Button
from kivy.uix.modalview import ModalView
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.behaviors import HoverBehavior,MagicBehavior
from kivymd_extensions.sweetalert import SweetAlert
from kivy.clock import Clock,mainthread


class HomeButton(MagicBehavior,HoverBehavior,Button):
    posY=NumericProperty()

    def on_enter(self):Animation(size=(dp(180),dp(84)),x=Window.width-210,duration=0.1).start(self)
    def on_leave(self):Animation(size=(dp(160),dp(75)),x=Window.width-200,duration=0.1).start(self)

class AskOnlineGame(ModalView):
    createPrivateRoomCallback=ObjectProperty()
    createPublicRoomCallback=ObjectProperty()
    joinScreen=ObjectProperty()

    def __init__(self,**kwargs):
        super(AskOnlineGame,self).__init__(**kwargs)
        self.menu=MDDropdownMenu(
            caller=self.ids["createButton"],
            items=[
                {
                    "text":"Public room",
                    "secondary_text":"Play with anyone",
                    "height":dp(54),
                    "on_release":lambda:self.redirect(self.createPublicRoomCallback),
                    "viewclass":"TwoLineListItem"
                },
                {
                    "text":"Private room",
                    "secondary_text":"Play with your friend",
                    "height":dp(54),
                    "on_release":lambda:self.redirect(self.createPrivateRoomCallback),
                    "viewclass":"TwoLineListItem"
                }
            ],
            width_mult=3
        )
    
    def redirect(self,function):
        self.menu.dismiss()
        self.dismiss()
        function()

class HomeScreen(Screen):
    def __init__(self,**kwargs):
        super(HomeScreen,self).__init__(**kwargs)
        self.app=MDApp.get_running_app()
        self.askOnlineGame=AskOnlineGame(
            createPublicRoomCallback=self.createPublicRoom,
            createPrivateRoomCallback=self.createPrivateRoom,
            joinScreen=self.joinScreen
        )
    
    def joinScreen(self):
        if self.app.client.connected:self.manager.current="JoinScreen"
        else:SweetAlert().fire("Not connected to server.",type="failure")
    
    def createPublicRoom(self):
        if self.app.client.connected:
            self.manager.current="PreGameScreen"
            self.manager.get_screen("PreGameScreen").initialize("You will be matched to another player","Searching for other players...",False)
        else:
            SweetAlert().fire("Not connected to server.",type="failure")
            self.app.connect()

    def createPrivateRoom(self):
        if self.app.client.connected:
            self.manager.current="PreGameScreen"
            self.manager.get_screen("PreGameScreen").initialize("Share the room code below","Creating room...",True)
        else:SweetAlert().fire("Not connected to server.",type="failure")