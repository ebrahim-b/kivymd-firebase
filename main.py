from kivy.config import Config
Config.set('graphics', 'width', '480')
Config.set('graphics', 'height', '640')

from kivymd.app import MDApp
from kivy.lang.builder import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.floatlayout import FloatLayout
from kivymd.uix.tab import MDTabsBase
from kivy.uix.tabbedpanel import TabbedPanel 
from kivymd.uix.dialog import MDDialog
from kivy.uix.boxlayout import BoxLayout
from kivymd.uix.button import MDFlatButton

from kivymd.uix.list import OneLineListItem
from kivymd.uix.picker import MDDatePicker, MDTimePicker
from datetime import date
from datetime import time


import json
import requests


url = '' #Insert Database Address like https://sample.com/.json
auth_key = ''# insert Firebase Database secret in Project Setting > Service Account > Database Secret

class Tabs(FloatLayout, MDTabsBase):
    '''Class implementing content for a tab on home screen'''

class DialogContent(BoxLayout):

    def show_date_picker(self):
        date_dialog = MDDatePicker(callback=self.get_date)
        date_dialog.open()

    def get_date(self, date):
        self.ids.date_text.text = str(date)
        #print(date)

    def show_time_picker(self):
        picker = MDTimePicker()
        picker.bind(time=self.get_time)
        picker.open()

    def get_time(self,picker_widget, time):
        self.ids.time_text.text = str(time)
        #print(time)

class LoginScreen(Screen):
    #print(user_name)
    def login(self, uname, pword):        
        request = requests.get(url + '?auth=' + auth_key)
        users = request.json()
        #print(users)

        if uname in users and users[uname]["password"] == pword:
            global user_name 
            user_name = uname
            self.manager.current = "home"
        else:
            my_dialog = MDDialog(title="Error",text="UserName Or Password Is Wrong",
                                    size_hint=[.7,.5])
            my_dialog.open()

    def change_screen(self,name):
        self.manager.current = name


class MainScreen(Screen):
    dialog = None

    def show_text_list(self,instance):
        #print(instance.text)
        global task_id
        task_id = instance.text
        self.manager.current = "detailtask"

    def insert_data(self, uname):
        today = date.today()

        request = requests.get(url + '?auth=' + auth_key)
        users = request.json()
        if uname in users:
            row_data = users[uname]
            for i in row_data.keys():
                item = OneLineListItem(text=str(i))
                item.bind(on_press = self.show_text_list)
                if (row_data[i]["date"] == str(today)):
                    self.ids.container.add_widget(item)
                else:
                    self.ids.container_2.add_widget(item)

    def remove_widgets(self):
        self.ids.container.clear_widgets()
        self.ids.container_2.clear_widgets()

    def on_enter(self):
        self.remove_widgets()
        self.insert_data(user_name+"-task")

    def show_task_dialog(self):
        self.dialog = MDDialog(title="Create a new task", 
        type="custom", 
        content_cls=DialogContent(), 
        size_hint=[.95, .8],
        auto_dismiss=False,
        buttons=[
                    MDFlatButton(
                        text="CANCEL", on_release= self.close_dialog
                    ),
                    MDFlatButton(
                        text="SAVE", on_release=self.save_task
                    ),
                ],
        )
        self.dialog.open()

    def save_task(self, inst): 
        time_set = self.dialog.content_cls.children[0].children[0].text
        date_set = self.dialog.content_cls.children[0].children[1].text
        task = self.dialog.content_cls.children[1].children[2].text             
        if (time_set != '' and date_set != '' and task != ''):
            #print(task , time_set, date_set) 
            request = requests.get(url + '?auth=' + auth_key)
            users = request.json()
            task_set = dict()
            users_str = ""
            task_set = {
                task + "--" + date_set + "--" + time_set : {
                    "date": date_set,
                    "time": time_set,
                    "task": task,
                    "done": 0
                }
            }
            #print(task_set)
            if (user_name + "-task") in users:
                users[user_name + "-task"].update(task_set) 
            else:
                users[user_name + "-task"] = task_set

            users_str = str(json.dumps(users))
            #print(users_str)
            to_database = json.loads(users_str)
            requests.patch( url= url, json= to_database)
            self.remove_widgets()
            self.insert_data(user_name+"-task")
            self.close_dialog(self)

    def close_dialog(self, inst):
        self.dialog.dismiss()

    def change_screen(self,name):
        self.manager.current = name

class RegisterScreen(Screen):

    def change_screen(self,name):
        self.manager.current = name

    def add_user(self, uname, pword, bfriend):  

        request = requests.get(url + '?auth=' + auth_key)
        users = request.json()

        if uname not in users :      
            users = dict()
            users_str = ""
            users[uname] = {
                "username": uname,
                "password": pword,
                "bestfriend": bfriend
            }

            users_str = str(json.dumps(users))
            to_database = json.loads(users_str)
            requests.patch( url= url, json= to_database)

            self.ids.username.text = ''
            self.ids.password.text = ''
            self.ids.bestfriend.text = ''

            self.manager.current = "login"
        else:
            my_dialog = MDDialog(title="Error",text="Username Exists",
                                    size_hint=[.7,.5])
            my_dialog.open()

class ForgotScreen(Screen):

    def forgot_password(self, uname, pword, bfriend):
        request = requests.get(url + '?auth=' + auth_key)
        users = request.json()

        if uname in users and users[uname]["bestfriend"] == bfriend:
            users = dict()
            users_str = ""
            users[uname] = {
                "username": uname,
                "password": pword,
                "bestfriend": bfriend
            }

            users_str = str(json.dumps(users))
            to_database = json.loads(users_str)
            requests.patch( url= url, json= to_database)
            self.ids.username.text = ''
            self.ids.password.text = ''
            self.ids.bestfriend.text = ''

            self.manager.current = "login"


        else:
            my_dialog = MDDialog(title="Error",text="Some Information Is Wrong",
                                    size_hint=[.7,.5])
            my_dialog.open()


    def change_screen(self,name):
        self.manager.current = name

class DetailScreen(Screen):

    def delete_task(self):
        del_item = user_name + "-task" + "/" + task_id
        #print(del_item)
        requests.delete(url = url[:-5] + del_item + ".json")
        self.manager.current = "home"

    def on_enter(self):
        request = requests.get(url + '?auth=' + auth_key)
        users = request.json()
        if user_name+"-task" in users:
            row_data = users[user_name+"-task"][task_id]
            self.ids.task.text = 'Task: ' + row_data["task"] + '   '
            self.ids.date_time.text = 'Date: ' + row_data["date"] + '  Time: ' + row_data["time"]
    
    def change_screen(self,name):
        self.manager.current = name

sm = ScreenManager()
sm.add_widget(LoginScreen(name='login'))
sm.add_widget(MainScreen(name='main'))
sm.add_widget(RegisterScreen(name='register'))
sm.add_widget(ForgotScreen(name='forgot'))
sm.add_widget(DetailScreen(name='detailtask'))

class DemoApp(MDApp):        

    def build(self):
        self.title = "To-Do-List"
        screen = Builder.load_file('main.kv')
        return screen

    


DemoApp().run()
