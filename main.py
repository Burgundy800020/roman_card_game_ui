import os,sys,socketio, threading
from kivymd.app import MDApp
from kivy.clock import Clock,mainthread
from kivy.metrics import dp
from kivy.core.window import Window
from kivy.lang import Builder
from kivymd.uix.dialog import MDDialog
from libs.utilities import thread

Window.size=(dp(1000),dp(600))
Window.minimum_width=dp(1000)
Window.minimum_height=dp(600)
os.environ["server"]="http://127.0.0.1:5000"
os.environ["root"]=getattr(sys,"_MEIPASS",os.path.dirname(os.path.abspath(__file__)))
for file in os.listdir(f"{os.environ['root']}/libs/kv"):Builder.load_file(f"{os.environ['root']}/libs/kv/{file}")

class Main(MDApp):
    @thread
    def connect(self):
        try:
            self.client.connect(os.environ["server"])
            if self.warningOpen:
                self.connectionWarning.dismiss()
                self.warningOPen = False
        except:
            if not self.warningOpen:
                mainthread(lambda:self.connectionWarning.open())()
                self.warningOpen=True
            Clock.schedule_once(lambda dt:self.connect(),5)        

    def build(self):
        self.title="Rome: Republic Legacy"
        self.icon=f"{os.environ['root']}/assets/images/logo.png"
        self.theme_cls.material_style="M3"
        self.theme_cls.primary_palette="Indigo"
        self.connectionWarning=MDDialog(
            title="Error",
            text="Cannot connect to server. Check your internet connection. We will keep trying.",
            radius=(dp(5),dp(5),dp(5),dp(5)),
            auto_dismiss=False,
        )
        self.warningOpen=False
        self.client=socketio.Client()
        self.connect()
        return Builder.load_string("""
#:import HomeScreen libs.baseclass.homescreen.HomeScreen
#:import JoinScreen libs.baseclass.joinscreen.JoinScreen
#:import PreGameScreen libs.baseclass.pregamescreen.PreGameScreen
#:import CharacterScreen libs.baseclass.characterscreen.CharacterScreen
#:import GameScreen libs.baseclass.gamescreen.GameScreen
#:import MDSlideTransition kivymd.uix.transition.transition.MDSlideTransition

MDScreenManager:
    transition:MDSlideTransition(direction="up")
    HomeScreen:
        name:"HomeScreen"
    PreGameScreen:
        name:"PreGameScreen"
    JoinScreen:
        name:"JoinScreen"
    CharacterScreen:
        name:"CharacterScreen"
    GameScreen:
        name:"GameScreen"
        """)
    
    def open_settings(self,*args):pass

    def on_stop(self):
        self.client.disconnect()

if __name__=="__main__":
    Main().run()