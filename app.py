from tkinter import *
from tkinter import messagebox

from plyer import notification

import requests

import sys
import os
import json

from pystray import Icon, MenuItem, Menu
from PIL import Image

import threading
from threading import Thread

import webbrowser

# API KEY
api_key = 'YOUR KEY' # <----------- Change this

# Window
window = Tk()
window['bg'] = '#6e91a1'
window.title('WeatherPulse')
window.geometry("300x385")
window.resizable(width=False, height=False)

# Icon
if hasattr(sys, '_MEIPASS'):
    icon_path = os.path.join(sys._MEIPASS, 'appicon.ico')
else:
    icon_path = "C:\\............\\WeatherPulse\\icon.ico" # <----- Write yout path!

window.iconbitmap(icon_path)


# -------- Settings -------- #

# Settings path and import
base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(sys.argv[0])))
settings_path = os.path.join(base_path, 'settings.json')

with open(settings_path, 'r') as file:
    app_settings = json.load(file)

# Variables
city = app_settings['city']
measurement = StringVar(value=app_settings['temp_unit'])

# Settings save function
def save():
    if not ent_city.get().strip():
        messagebox.showerror("Error!", "Please enter the city!")
        return
    
    app_settings['city'] = ent_city.get()
    app_settings['temp_unit'] = measurement.get()

    try:
        with open(settings_path, 'w') as file:
            json.dump(app_settings, file, indent=4)
        print("Settings saved.")
    except Exception as e:
        print(f"Saving error: {e}")

    global city
    city = app_settings['city']

    request()



# -------- Functions -------- #

### Notification ###
def send_notification(description, temp, humidity):
    if measurement.get() == 'fahrenheit':
        symbol = '°F'
    else:
        symbol = '°C'

    notification.notify(
    title="Weather!",
    message=f'It is {description} in {city} right now, temperature {temp}{symbol}. Humidity is {humidity}%.',
    timeout=10
    )


### Request ###

def request():
    if not city:
        messagebox.showerror("Error!", "Please enter the city and save settings!")
        return
    
    else:
        if measurement.get() == 'fahrenheit':
            url= f'http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=imperial'
            response = requests.get(url)

            if response.status_code == 200:
                data = response.json()

                temp_rn = data['main']['temp']
                description_rn = data['weather'][0]['description']
                humidity_rn = data['main']['humidity']

                final_text = f'{city}\n======================\nTemp: {temp_rn} °F\nConditions: {description_rn}\nHumidity: {humidity_rn}%'

                output.config(state=NORMAL)
                output.delete("1.0", END)
                output.insert(END, final_text)
                output.config(state=DISABLED)
                send_notification(description_rn, temp_rn, humidity_rn)

        else:
            url= f'http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric'
            response = requests.get(url)

            if response.status_code == 200:
                data = response.json()

                temp_rn = data['main']['temp']
                description_rn = data['weather'][0]['description']
                humidity_rn = data['main']['humidity']

                final_text = f'{city}\n======================\nTemp: {temp_rn} °C\nConditions: {description_rn}\nHumidity: {humidity_rn}%'
                output.config(state=NORMAL)
                output.delete("1.0", END)
                output.insert(END, final_text)
                output.config(state=DISABLED)
                send_notification(description_rn, temp_rn, humidity_rn)

    window.after(3600000, request)


# -------- UI -------- #

### Main ###
main = Frame(window)
main.pack(fill=BOTH, expand=True)

# Output field
output = Text(main, wrap=WORD, 
              font=("Microsoft New Tai Lue", 12))
output.place(relx=0.5, y=15, anchor='n', width=250, height=150)
output.config(state=DISABLED)

# CBK button
def github():
    webbrowser.open("https://github.com/pythonCBK/weatherpulse/")

btn_cbk = Button(main, text="by CBK",
                 relief='flat', highlightthickness=0, borderwidth=0,
                 font=("Microsoft New Tai Lue", 8, "underline"), command=github)
btn_cbk.place(relx=0.5, y=365, anchor='n')


### Settings ###

# Text <Settings>
txt_city = Label(main, text="Settings",
                 font=("Microsoft New Tai Lue", 14, "bold"))
txt_city.place(relx=0.5, y=180, anchor='n')

# Txt <Enter the city>
txt_city = Label(main, text="Enter the required city:",
                 font=("Microsoft New Tai Lue", 12))
txt_city.place(relx=0.5, y=215, anchor='n')

# City entry
ent_city = Entry(main, font=("Microsoft New Tai Lue", 11))
ent_city.place(relx=0.5, y=240, anchor='n')
ent_city.insert(0, city)

# Txt <Select the measurement>
txt_select = Label(main, text="Select measurement:",
                   font=("Microsoft New Tai Lue", 12))
txt_select.place(relx=0.5, y=275, anchor='n')

# Celsius
celsius = Radiobutton(main, text="Celsius",
                      font=("Microsoft New Tai Lue", 11), value="celsius", variable=measurement)
celsius.place(relx=0.32, y=300, anchor='n')

# Fahrenheit
fahrenheit = Radiobutton(main, text="Fahrenheit",
                         font=("Microsoft New Tai Lue", 11), value="fahrenheit",variable=measurement)
fahrenheit.place(relx=0.68, y=300, anchor='n')

# Save button
btn_save = Button(main, text="Save changes",
                  font=("Microsoft New Tai Lue", 12), command=save)
btn_save.place(relx=0.5, y=335, anchor='n', height=25)


# -------- Tray -------- #

# Icon
def tray_icon():
    icon = Icon("WeatherPulse")
    icon.icon = Image.open(icon_path)
    icon.menu = Menu(MenuItem("Quit", on_quit))
    icon.run()

# Quit
def on_quit(icon, item):
    icon.stop()
    window.quit()

# To tray
def to_tray():
    window.withdraw() 
    image = Image.open(icon_path)
    icon = Icon("WeatherPulse", image, menu=Menu(MenuItem("Open", restore_window), MenuItem("Exit", on_quit)))
    threading.Thread(target=icon.run).start()

# Restore window
def restore_window(icon, item):
    window.deiconify()
    icon.stop()



### On start up ###
request()



window.protocol("WM_DELETE_WINDOW", to_tray)
window.mainloop()
