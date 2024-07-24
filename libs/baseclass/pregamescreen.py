import os,requests
from kivymd.app import MDApp
from kivy.clock import mainthread
from kivy.properties import StringProperty,BooleanProperty
from kivy.uix.screenmanager import Screen
from kivymd_extensions.sweetalert import SweetAlert
from libs.utilities import thread

app=MDApp.get_running_app()

class PreGameScreen(Screen):
    title=StringProperty()
    status=StringProperty()
    private=BooleanProperty()
    code=StringProperty()

    def __init__(self,**kwargs):
        super(PreGameScreen,self).__init__(**kwargs)
        app.client.on("establishPrivateConnection")(lambda data:self.establishPrivateConnection(data))

    def initialize(self,title,status,private):
        self.title=title
        self.status=status
        self.private=private
        self.code=""
        if private:self.createRoom("false")
        else:self.createRoom("true")
    
    @thread
    def cancel(self):
        mainthread(lambda:setattr(self.manager,"current","HomeScreen"))()
        requests.get(f"{os.environ['server']}/deleteRoom",data={"id":self.code})

    @thread
    def createRoom(self,public):
        try:
            response=requests.get(f"{os.environ['server']}/createRoom",data={"public":public},timeout=20 if public=="false" else 2000000)
            assert response.status_code==200
            if response.text=="FULL":
                self.cancel()
                mainthread(lambda:SweetAlert().fire("The server is now full. Try again later",type="failure"))()
            else:
                self.code=response.text
                app.client.emit("joinRoom",data={"id":self.code,"userName":""},callback=lambda reponse:None)
                if public=="false":self.updatePrivateRoom1(self.code)
                else:self.redirect(self.code)
        
        
        except Exception as e:
            print(e)
            self.cancel()
            mainthread(lambda:SweetAlert().fire("Cannot contact the server. Check your internet connection and try again.",type="failure"))()
    
        """
        except requests.exceptions.HTTPError as herr:
            self.cancel()
            mainthread(lambda:SweetAlert().fire("http error",type="failure"))()
        except requests.exceptions.ConnectionError as conerr:
            self.cancel()
            mainthread(lambda:SweetAlert().fire("Connection error",type="failure"))()
        except requests.exceptions.ReadTimeout as readerr:
            self.cancel()
            mainthread(lambda:SweetAlert().fire("Read error",type="failure"))()
        """
    @mainthread
    def updatePrivateRoom1(self,code):
        self.status="Waiting for connection..."
        self.code=code
    
    def establishPrivateConnection(self,data):
        self.redirect(self.code)
    
    @mainthread
    def redirect(self,code):
        self.status="Opening room..."
        self.manager.get_screen("CharacterScreen").initialize(code)
        self.manager.current="CharacterScreen"