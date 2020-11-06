# Python program to translate
# speech to text
# Sound files such as end.wav and start.wav are from windows system sounds

import speech_recognition as sr
import playsound as ps
import time
import asyncio
import threading
from _thread import start_new_thread
import json
import sys
import tkinter as tk
from tkinter import filedialog
import websocket
import keyboard
import sys
import os

# volume change
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
import math

# trying pystray
import pystray



from PIL import Image, ImageDraw


#global checks, to pass be
exitFlag = False
listening = False
connected = False
micIndex = 0




# Get default audio device using PyCAW
devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(
    IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = cast(interface, POINTER(IAudioEndpointVolume))
# Get current volume 
#volume.SetMasterVolumeLevel(currentVolumeDb - 6.0, None)
#currentVolumeDb = volume.GetMasterVolumeLevel()
#print(currentVolumeDb)
# NOTE: -6.0 dB = half volume !


# Initialize the recognizer
r = sr.Recognizer()

#list of microphones
microphones = sr.Microphone.list_microphone_names()

# This function uses the microphone to turn speech to text

uri = "ws://127.0.0.1:2585/v1/messages"
#setting up websocket
ws = websocket.WebSocket(uri)

# setting up Widget
widget = tk.Tk()

widget.winfo_toplevel().title('Recognizer')
widget.iconbitmap('speaker.ico')
widget.geometry("300x540")
widget.lift()
widget.call('wm', 'attributes', '.', '-topmost', True)


# Add a grid
'''
mainframe = tk.Frame(widget)
mainframe.grid(column=0,row=0, sticky=(tk.N,tk.W,tk.E,tk.S) )
mainframe.columnconfigure(0, weight = 1)
mainframe.rowconfigure(0, weight = 1)
mainframe.pack()
'''
#adding the mic dropdown menu
tkvar = tk.StringVar(widget)
tkvar.set(microphones[0])

popupMenu = tk.OptionMenu(widget, tkvar, *microphones)
popupMenu.pack()
tk.Label(widget, text="Choose a mic")
#change dropdown menu
def change_dropdown(*args):
    global micIndex
    print( tkvar.get() )
    micIndex = microphones.index(tkvar.get())
    print('dropdown index ' + str(microphones.index(tkvar.get())))

tkvar.trace('w', change_dropdown)

# connection pic 
redDotImage = tk.PhotoImage(file='reddot.png')
greenDotImage = tk.PhotoImage(file='greendot.png')
connectionLabel = tk.Label(widget, image=redDotImage)
connectionLabel.pack()

# text on top of the widget
speakText = tk.Label(text='Say \"vicky\" for commands, or alt+ctrl+v')
speakText.pack()

# mic pitures
micOffImage = tk.PhotoImage(file='micoff.png')
micOnImage = tk.PhotoImage(file='micon.png')
micLabel = tk.Label(widget, image=micOffImage)
micLabel.pack()
#speaker pictures
speakImage = tk.PhotoImage(file='speak.png')
noSpeakImage = tk.PhotoImage(file='nospeak.png')
speakLabel = tk.Label(widget, image=noSpeakImage)
speakLabel.pack()

def SpeechToText():
    # use the microphone as source for input.
    print('Speech to text index ' + str(micIndex))
    with sr.Microphone(device_index = micIndex) as source2:
        micLabel.configure(image=micOnImage)
        micLabel.image = micOnImage

        # wait for a second to let the recognizer
        # adjust the energy threshold based on
        # the surrounding noise level
        r.adjust_for_ambient_noise(source2, duration=0.2)

        # listens for the user's input
        try:
            audio = None
            if listening:
                audio = r.listen(source2, timeout = 40)
            else:
                audio = r.listen(source2, phrase_time_limit=3, timeout = 10)
            micLabel.configure(image=micOffImage)
            micLabel.image = micOffImage
            # Using google to recognize audio
            try:
                text = r.recognize_google(audio)
            except:
                print('transulate error')
                return ''
            # converts all text to lower case
            text = text.lower()
            return text
        except sr.WaitTimeoutError:
            micLabel.configure(image=micOffImage)
            micLabel.image = micOffImage
            return ''

# This funtion uses a .wav file to turn speech to text


def FileToText(file):
    # use the microphone as source for input.
    with sr.AudioFile(file) as source2:

        # wait for a second to let the recognizer
        # adjust the energy threshold based on
        # the surrounding noise level
        r.adjust_for_ambient_noise(source2, duration=0.2)

        # listens for the user's input
        audio = r.record(source2)
        # Using google to recognize audio
        text = r.recognize_google(audio)
        # converts all text to lower case
        text = text.lower()
        return text

# Plays starting sound
def playStartSound():
    ps.playsound('start.wav')

# Plays ending sound
def playEndSound():
    ps.playsound('end.wav')


register = {
    "action": "REGISTER_LISTENER",
    "app": "recognizer",
    "eavesdrop": False,
}
deregister = {
    "action": "DEREGISTER_LISTENER",
    "app": "recognizer"
}




# send a command via text
def SendCommand():
    result = txtCommand.get("1.0", "end")
    payload = {
        "action": "DISPATCH_COMMAND",
        "command": result.strip(),
        "recipient": "desktop"
    }
    while not connected:
        time.sleep(1)
    ws.send(json.dumps(payload))

# Starts the Voice command thread
# Activates voice command feature with acticvation phrase
def VoiceCommand():
    # variables shared between threads
    global listening
    while True:
        # program end check
        if exitFlag == True:
            exit()
        try:

            text = ''
            commandFlag = False

            print(
                'Say \"blue\" to input command from microphone, say "file" to input from command file')

            text = SpeechToText()
            if exitFlag == True:
                exit()
            print("-> "+text)

            # uses mic after activation phrase
            tmp = text.find('vicky')
            if tmp != -1:
                commandFlag = True
                payload = json.dumps({
                    "action": "DISPATCH_COMMAND",
                    "command": text[tmp+5:len(text)],
                })
                txtCommand.delete("1.0", "end")
                txtCommand.insert("1.0", text[tmp+5:len(text)])
                while not connected:
                    time.sleep(1)
                # send command
                ws.send(payload)

            if commandFlag and listening == False:
                # disables hot key
                keyboard.remove_hotkey('alt+ctrl+v')
                listening = True
                # changes speaker picture to active
                speakLabel.configure(image=speakImage)
                speakLabel.image = speakImage
                exitPhrase = ''
                while not exitPhrase:
                    print('activation phrase')
                    playStartSoundThread = threading.Thread(target=playStartSound)
                    playStartSoundThread.start()

                    command = SpeechToText()
                    if exitFlag == True:
                        exit()
                    print('Command heard: ' + command)
                    playEndSoundThread = threading.Thread(target=playEndSound)
                    playEndSoundThread.start()
                    if command.find('vicky') != -1:
                        command = command[0:command.find('vicky')]
                        print(command)
                        exitPhrase = True
                    # placed new command in text box
                    txtCommand.delete("1.0", "end")
                    txtCommand.insert("1.0", command)
                    # converts command to JSON
                    
                    payload = json.dumps({
                        "action": "DISPATCH_COMMAND",
                        "command": command,
                    })
                    while not connected:
                        time.sleep(1)
                    # send command
                    ws.send(payload)

                # changes speaker picture to inactive
                speakLabel.configure(image=noSpeakImage)
                speakLabel.image = noSpeakImage
                listening = False
                # enables hot key
                keyboard.add_hotkey('alt+ctrl+v', hotKey)
        except sr.RequestError as e:
            print("Could not request results; {0}".format(e))

        except KeyboardInterrupt:
            ws.send(json.dumps(deregister))
            sys.exit()

        except sr.UnknownValueError:
            print("unknown error occured")

# hotkey function
def hotKey():
    # variables shared between threads
    global listening
    # diables hotkey
    keyboard.remove_hotkey('alt+ctrl+v')
    # checks if recognizer is listenning to a command
    if listening == False:
        listening = True
        # changes speaker picture to active
        speakLabel.configure(image=speakImage)
        speakLabel.image = speakImage
        playStartSoundThread = threading.Thread(target=playStartSound)
        playStartSoundThread.start()
        command = SpeechToText()
        # checks if program exited
        if exitFlag == True:
            exit()
        print('Command heard: ' + command)
        playEndSoundThread = threading.Thread(target=playEndSound)
        playEndSoundThread.start()
        # changes speaker picture to inactive
        speakLabel.configure(image=noSpeakImage)
        speakLabel.image = noSpeakImage
        # places new command in text box
        txtCommand.delete("1.0", "end")
        txtCommand.insert("1.0", command)
        # converts command to JSON for the dispatcher
        command = json.dumps({
            "action": "DISPATCH_COMMAND",
            "command": command,
        })
        while not connected:
            time.sleep(1)
        # sends command
        ws.send(command)
        listening = False
    # enables hot key
    keyboard.add_hotkey('alt+ctrl+v', hotKey)


keyboard.add_hotkey('alt+ctrl+v', hotKey)

# file to text button function
def FileToTextButton():
    # opens file navigator and returns path
    filename = filedialog.askopenfilename(
        initialdir="/", title="Select file", filetypes=[("wav files", "*.wav")])
    print(filename)
    # converts file to text given the path to the file
    text = FileToText(filename)
    # prepares command to be sent as JSON
    command = json.dumps({
        "action": "DISPATCH_COMMAND",
        "command": text,
    })
    while not connected:
        time.sleep(1)
    # sends command
    ws.send(command)

def SystemVolume():
    global listening, exitFlag
    while True and not exitFlag:
        currentVolume = volume.GetMasterVolumeLevelScalar()
        #print('Current volume: ' + str(currentVolume))
        if listening:
            if currentVolume > 0.2:
                volume.SetMasterVolumeLevelScalar(0.2, None)
                while listening:
                    time.sleep(0.2)
                volume.SetMasterVolumeLevelScalar(currentVolume, None)
        time.sleep(0.2)

# setting up VoiceCommand thread
voiceCommandThread = threading.Thread(target=VoiceCommand)

# text command textbox
txtCommand = tk.Text(widget, height=1)
txtCommand.pack( pady=15 )
# send button for text box
btnSend = tk.Button(widget, height=1, width=10,
                    text="Send", command=SendCommand)
btnSend.pack(pady=15)

# audio file text
audioText = tk.Label(text='Select and audio file to become a command')
audioText.pack(pady = 20)
# audio file button
fileButton = tk.Button(widget, height=1, width=20,
                       text="Select Audiofile", command=FileToTextButton)
fileButton.pack(pady=15)

# function that runs when widget is closed
def on_quit():
    # variables shared between threads
    global widget, exitFlag
    exitFlag = True
    widget.destroy()

# sets up on_quit for when the widget exits
widget.protocol("WM_DELETE_WINDOW", on_quit)

# adding the icon area notification
def create_image():
    # Generate an image and draw a pattern
    image = Image.open('speaker.ico')

    return image

def exitIcon(icon):
    global widget
    icon.stop()
    on_quit()


item = (pystray.MenuItem('Close', exitIcon))

icon = pystray.Icon('test name', menu = pystray.Menu(item))
icon.icon = create_image()

def setup(icon):
    icon.visible = True

def IconThread():
    icon.run(setup)

iconThread = threading.Thread(target=IconThread)
iconThread.start()


# checks connection while the program is runnuing
def checkConnection():
    # variables shared between threads
    global connected, ws
    errorConnected = connected
    #time.sleep(2)
    # runs as long as the widget is running
    while not exitFlag:
        try:
            while not connected:
                try:
                    # error reconncting
                    ws = None
                    ws = websocket.WebSocket()
                    ws.connect(uri)
                    ws.send(json.dumps(register))
                    connectionLabel.configure(image=greenDotImage)
                    connectionLabel.image = greenDotImage
                    errorConnected = True
                    connected = True
                except:
                    print('Connecting')
                    connectionLabel.configure(image=redDotImage)
                    connectionLabel.image = redDotImage
                    time.sleep(1)
            # recieves messaged from dispatcher
            check = ws.recv()
            if(check):
                connected = True
                errorConnected = True
                print('check ' + check)
                connectionLabel.configure(image=greenDotImage)
                connectionLabel.image = greenDotImage
            else:
                print('not connected')
                connected = False
                errorConnected = True
                connectionLabel.configure(image=redDotImage)
                connectionLabel.image = redDotImage
                time.sleep(1)
        except:
            e = sys.exc_info()[0]
            errorConnected = False
            connected = False
            
            print('not connected: ' + str(e))
            time.sleep(1)

# sets up dispatcher check thread
dispatcherThread = threading.Thread(target=checkConnection)
volumeThread = threading.Thread(target=SystemVolume)

# starting the program
#ws.send(json.dumps(register))
volumeThread.start()
dispatcherThread.start()
voiceCommandThread.start()

# starts the widget loop
widget.mainloop()

# exitting
# joins threads
voiceCommandThread.join()
dispatcherThread.join()
print('exit')
ws.send(json.dumps(deregister))
iconThread.join()
# runs the main function as an async function
# asyncio.get_event_loop().run_until_complete(main())
