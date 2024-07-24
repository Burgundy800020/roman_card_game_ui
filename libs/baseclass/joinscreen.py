from kivymd.app import MDApp
from kivy.clock import mainthread
from kivy.uix.screenmanager import Screen
from kivy.uix.modalview import ModalView
from kivymd_extensions.sweetalert import SweetAlert

app=MDApp.get_running_app()

class JoiningNotice(ModalView):
    def redirect(self,manager,key):
        self.open()
        manager.get_screen("CharacterScreen").initialize(key)
        manager.current="CharacterScreen"
        self.dismiss()


class JoinScreen(Screen):
    def __init__(self,**kwargs):
        super(JoinScreen,self).__init__(**kwargs)
        self.joiningNotice=JoiningNotice()

    def preJoinRoom(self):
        key=self.ids["keyEntry"].text
        app.client.emit("joinRoom",data={"id":key,"userName":""},callback=self.joinRoom)
    
    def joinRoom(self,response):
        if response=="ACCEPTED":self.redirect(response)
        elif response=="FULL":mainthread(lambda:SweetAlert().fire("The room is already full.",type="failure"))()
    
    @mainthread
    def redirect(self,key):
        self.joiningNotice.redirect(self.manager,key)