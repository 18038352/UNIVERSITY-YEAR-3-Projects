import re

from kivy.metrics import dp
from kivyauth.google_auth import initialize_google, login_google, logout_google
from kivy.lang import Builder
from kivymd.app import MDApp
from kivy.core.window import Window
from kivymd.uix.snackbar import Snackbar
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.properties import StringProperty
import datetime
from datetime import date
from kivymd.uix.behaviors import FakeRectangularElevationBehavior
from kivymd.uix.floatlayout import MDFloatLayout
from kivy.core.audio import SoundLoader
from kivy.uix.videoplayer import VideoPlayer
from kivy.uix.scrollview import ScrollView
from kivy.clock import Clock
import mysql.connector


Window.size = (350, 600)

class Scroll(ScrollView):
    pass

class ToDoCard(FakeRectangularElevationBehavior, MDFloatLayout):
    title = StringProperty()
    description = StringProperty()

class NavBar(FakeRectangularElevationBehavior, MDFloatLayout):
    pass


class Feel_Good(MDApp):
    global database
    database = mysql.connector.Connect(host="localhost", user="root", password="Nakupo12", database="loginform") #define DB stuff
    login_reg = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b' #expression to validate email
    cursor = database.cursor()
    cursor.execute("select * from logindata")
    for i in cursor.fetchall():
        print(i[0], i[1])

    def build(self):

        client_id = open("clientID.txt")
        client_secret = open("clientSec.txt")
        initialize_google(self.after_login, self.error_listener, client_id.read(), client_secret.read())
        global screen_manager
        screen_manager = ScreenManager()
        screen_manager.add_widget(Builder.load_file("WelcomePage.kv"))
        screen_manager.add_widget(Builder.load_file("login.kv"))
        screen_manager.add_widget(Builder.load_file("signup.kv"))
        screen_manager.add_widget(Builder.load_file("HomeScreen.kv"))
        screen_manager.add_widget(Builder.load_file("ToDoScreen.kv"))
        screen_manager.add_widget(Builder.load_file("AddingToDo.kv"))
        screen_manager.add_widget(Builder.load_file("BrainFeeder.kv"))
        screen_manager.add_widget(Builder.load_file("BodyPositivity.kv"))
        screen_manager.add_widget(Builder.load_file("meditateFocus.kv"))
        screen_manager.add_widget(Builder.load_file("AnxietyDepression.kv"))
        screen_manager.add_widget(Builder.load_file("betterSleep.kv"))
        screen_manager.add_widget(Builder.load_file("UserGuide.kv"))
        screen_manager.add_widget(Builder.load_file("motivation_images.kv"))

        return screen_manager

    #to-do-list
    def on_start(self):
        todays = date.today()
        weekdays = date.weekday(todays)
        alldays = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        years = str(datetime.datetime.now().year)
        months = str(datetime.datetime.now().strftime("%b"))
        days = str(datetime.datetime.now().strftime("%d"))
        screen_manager.get_screen("ToDoScreen").date.text = f"{alldays[weekdays]}, {days} {months} {years}"
        screen_manager.get_screen("ToDoScreen").todo_list.clear_widgets()


    def on_complete(self, checkbox, value, description, bar, title):
        if value:
            description_original = description.text
            description.text = f"[s]{description.text}[/s]"
            cursor = database.cursor()
            cursor.execute('delete from todolist where email="' + current_email + '" and title="' + title.text + '" and description="' + description_original + '"')
            screen_manager.get_screen("ToDoScreen").todo_list.clear_widgets()
            cursor.execute('select * from todolist where email = "' + current_email + '"')
            for todolist_item in cursor.fetchall():
                screen_manager.get_screen("ToDoScreen").todo_list.add_widget(
                    ToDoCard(title=todolist_item[1], description=todolist_item[2]))

        else:
            clear = ["[s]", "[/s]"]
            for num in clear:
                description.text = description.text.replace(num, "")


    def add_list(self, title, description):
        if title != "" and description != "" and len(title) < 30 and len(description) < 70:
            cursor = database.cursor()
            cursor.execute('insert into todolist (email, title, description) values ("' + current_email + '","' + title + '","' + description + '")')
            screen_manager.current = "ToDoScreen"
            screen_manager.transition.direction = "right"
            cursor.execute('select * from todolist where email = "'+ current_email + '"')
            screen_manager.get_screen("ToDoScreen").todo_list.clear_widgets()

            for todolist_item in cursor.fetchall():
                screen_manager.get_screen("ToDoScreen").todo_list.add_widget(ToDoCard(title=todolist_item[1], description=todolist_item[2]))

            screen_manager.get_screen("AddingTodo").description.text = ""
        elif title == "":
            Snackbar(text="Please Enter a Task/Goal!", snackbar_x="12dp", size_hint_y=.07, size_hint_x=(Window.width - (dp(11) * 2)) / Window.width, bg_color=(147/255, 233/255, 202/255, 1), font_size="16sp").open()
        elif description == "":
            Snackbar(text="Please Enter a Description!", snackbar_x="12dp", size_hint_y=.07, size_hint_x=(Window.width - (dp(11) * 2)) / Window.width, bg_color=(147/255, 233/255, 202/255, 1), font_size="16sp").open()
        elif len(title) > 30:
            Snackbar(text="Title should be < 30 characters", snackbar_x="12dp", size_hint_y=.07, size_hint_x=(Window.width - (dp(11) * 2)) / Window.width, bg_color=(147/255, 233/255, 202/255, 1), font_size="16sp").open()
        elif len(description) > 30:
            Snackbar(text="Description should be < 70 characters", snackbar_x="12dp", size_hint_y=.07, size_hint_x=(Window.width - (dp(11) * 2)) / Window.width, bg_color=(147/255, 233/255, 202/255, 1), font_size="16sp").open()

###################################################
    def after_login(self, name, email, photo_uri):
        self.root.ids.label.text = f"Logged in as {name}"
        self.root.transition.direction = "left"
        self.root.current = "HomeScreen"

    def error_listener(self):
        print("Login failed")

    def login(self):
        login_google()

    def logout(self):
        logout_google(self.after_logout())

    def after_logout(self):
        self.root.ids.label.text = ""
        self.root.transition.direction = "right"
        self.root.current = "login"

######################################################
#sql data fetching for login

    def send_login(self, email, password):
        if re.fullmatch(self.login_reg, email.text): #returns a match object if and only if the entire string matches the pattern
            self.cursor.execute(f"insert into logindata values('{email.text}', '{password.text}')")
            database.commit() #insert query to database
            email.text = ""
            password.text = ""

    def retrieve_data(self, email, password):
        self.cursor.execute("select * from logindata")
        email_data = []

        for i in self.cursor.fetchall(): #fetches all the rows of a query result.
            email_data.append(i[0])
        if email.text in email_data and email.text != "":
            self.cursor.execute(f"select password from logindata where email='{email.text}'")
            for j in self.cursor:
                if password.text == j[0]:
                    global current_email
                    current_email = email.text
                    print("Successfully logged in!")
                    if current_email is not None or current_email is not "":
                        screen_manager.get_screen("ToDoScreen").todo_list.clear_widgets()
                        cursor = database.cursor()
                        cursor.execute('select * from todolist where email = "' + current_email + '"')
                        for todolist_item in cursor.fetchall():
                            screen_manager.get_screen("ToDoScreen").todo_list.add_widget(ToDoCard(title=todolist_item[1], description=todolist_item[2]))
                else:
                    Snackbar(text="Incorrect Password!", snackbar_x="12dp", size_hint_y=.07, size_hint_x=(Window.width - (dp(11) * 2)) / Window.width, bg_color=(147 / 255, 200/255, 202/260, 1), font_size="16sp").open()
                    screen_manager.current = "login"
                    screen_manager.transition.direction = "right"

        else:
            Snackbar(text="Incorrect Email!", snackbar_x="12dp", size_hint_y=.07, size_hint_x=(Window.width - (dp(11) * 2)) / Window.width, bg_color=(147/255, 200/255, 202/260, 1), font_size="16sp").open()
            screen_manager.current = "login"
            screen_manager.transition.direction = "right"

######################################################

    #Sleep MusicPlayer
    def play_btn(self):
        self.musicSleep = SoundLoader.load("SleepMusic.mp3")
        if self.musicSleep:
            self.musicSleep.play()


    def stop_btn(self):
        if self.musicSleep:
            self.musicSleep.stop()
        else:
            pass


############################################################

    #Anxiety and depression tracks
    def anxiety_btn(self):
        self.musicAnxiety = SoundLoader.load("Anxiety Track.mp3")
        if self.musicAnxiety:
            self.musicAnxiety.play()

    def anxiety_stop_btn(self):
        if self.musicAnxiety:
            self.musicAnxiety.stop()
        else:
            pass

    def anxiety_btn2(self):
        self.musicAnxiety2 = SoundLoader.load("Anxiety Track 2.mp3")
        if self.musicAnxiety2:
            self.musicAnxiety2.play()

    def anxiety_stop_btn2(self):
        if self.musicAnxiety2:
            self.musicAnxiety2.stop()
        else:
            pass

    def depression_btn(self):
        self.musicDepression = SoundLoader.load("depression track.mp3")
        if self.musicDepression:
            self.musicDepression.play()

    def depression_stop_btn(self):
        if self.musicDepression:
            self.musicDepression.stop()
        else:
            pass

    def depression_btn2(self):
        self.musicDepression2 = SoundLoader.load("depression track 2.mp3")
        if self.musicDepression2:
            self.musicDepression2.play()

    def depression_stop_btn2(self):
        if self.musicDepression2:
            self.musicDepression2.stop()
        else:
            pass


##################################################################

    #meditation music
#self love track
    def meditate_btn(self):
        self.musicMeditate = SoundLoader.load("self love track.mp3")
        if self.musicMeditate:
            self.musicMeditate.play()

    def meditate_stop_btn(self):
        if self.musicMeditate:
            self.musicMeditate.stop()
        else:
            pass
#spiritual track
    def meditate_btn2(self):
        self.musicMeditate2 = SoundLoader.load("spiritual tack.mp3")
        if self.musicMeditate2:
            self.musicMeditate2.play()

    def meditate_stop_btn2(self):
        if self.musicMeditate2:
            self.musicMeditate2.stop()
        else:
            pass
#focused meditation
    def meditate_btn3(self):
        self.musicMeditate3 = SoundLoader.load("focus track.mp3")
        if self.musicMeditate3:
            self.musicMeditate3.play()

    def meditate_stop_btn3(self):
        if self.musicMeditate3:
            self.musicMeditate3.stop()
        else:
            pass
#mindfulness
    def meditate_btn4(self):
        self.musicMeditate4 = SoundLoader.load("mindfulness track.mp3")
        if self.musicMeditate4:
            self.musicMeditate4.play()

    def meditate_stop_btn4(self):
        if self.musicMeditate4:
            self.musicMeditate4.stop()
        else:
            pass

#walking
    def meditate_walk(self):
        self.musicWalk = SoundLoader.load("walking meditation.mp3")
        if self.musicWalk:
            self.musicWalk.play()

    def meditate_stop_walk(self):
        if self.musicWalk:
            self.musicWalk.stop()
        else:
            pass


######################################################################
    #brain-feeder - timer plus music buttons


    #get time
    def get_time(self, instance, time):
        #self.root.ids.study_timer.text = str(time)
        print(time)

    #stop timer
    def stop_timer(self, instance, time):
        self.root.ids.study_timer.text = "You stopped time"

    def learning_timer(self):
        from kivymd.uix.picker import MDTimePicker
        timer_dialogue = MDTimePicker()
        timer_dialogue.bind(on_cancel=self.stop_timer, time=self.get_time)
        timer_dialogue.open()




#Music study

    def nature_btn(self):
        self.musicNature = SoundLoader.load("nature_study.mp3")
        if self.musicNature:
            self.musicNature.play()

    def piano_btn(self):
        self.musicPiano = SoundLoader.load("piano_study.mp3")
        if self.musicPiano:
            self.musicPiano.play()

    def lofi_btn(self):
        self.musicLofi = SoundLoader.load("lofi_study.mp3")
        if self.musicLofi:
            self.musicLofi.play()

    def jazz_btn(self):
        self.musicJazz = SoundLoader.load("jazz_study.mp3")
        if self.musicJazz:
            self.musicJazz.play()

    def stop_nature(self):
        if self.musicNature:
            self.musicNature.stop()
    def stop_piano(self):
        if self.musicPiano:
            self.musicPiano.stop()
    def stop_lofi(self):
        if self.musicLofi:
            self.musicLofi.stop()
    def stop_jazz(self):
        if self.musicJazz:
            self.musicJazz.stop()





######################################################################
#exercise

    def meditate_btn5(self):
        self.vidplayer = VideoPlayer(source="full_exercise_1.mp4")
        if self.vidplayer:
            return "full_exercise_1.mp4"

######################################################################




if __name__ == "__main__":
    Feel_Good().run()
