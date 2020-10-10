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

# Initialize the recognizer
r = sr.Recognizer()

#global checks, to pass be
exitFlag = False
listening = False
connected = False
# This function uses the microphone to turn speech to text

#setting up websocket
ws = websocket.WebSocket()

# setting up Widget
widget = tk.Tk()
widget.winfo_toplevel().title('Recognizer')
widget.iconbitmap('speaker.ico')
widget.geometry("300x540")
widget.lift()
widget.call('wm', 'attributes', '.', '-topmost', True)

# text on top of the widget
speakText = tk.Label(text='Say \"blue\" for commands, or alt+ctrl+v')
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
    with sr.Microphone() as source2:
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
                audio = r.listen(source2, timeout = 3)
            else:
                audio = r.listen(source2, timeout = 3, phrase_time_limit=3)
            micLabel.configure(image=micOffImage)
            micLabel.image = micOffImage
            # Using google to recognize audio
            text = r.recognize_google(audio)
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
uri = "ws://127.0.0.1:2585/v1/messages"



# send a command via text
def SendCommand():
    result = txtCommand.get("1.0", "end")
    payload = {
        "action": "DISPATCH_COMMAND",
        "command": result.strip(),
        "recipient": "desktop"
    }
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

            print(
                'Say \"blue\" to input command from microphone, say "file" to input from command file')

            text = SpeechToText()
            if exitFlag == True:
                exit()
            print("-> "+text)

            # uses mic after activation phrase
            if text == 'blue' and listening == False:
                # disables hot key
                keyboard.remove_hotkey('alt+ctrl+v')
                listening = True
                # changes speaker picture to active
                speakLabel.configure(image=speakImage)
                speakLabel.image = speakImage
                print('activation phrase')
                playStartSoundThread = threading.Thread(target=playStartSound)
                playStartSoundThread.start()

                command = SpeechToText()
                if exitFlag == True:
                    exit()
                print('Command heard: ' + command)
                playEndSoundThread = threading.Thread(target=playEndSound)
                playEndSoundThread.start()
                # changes speaker picture to inactive
                speakLabel.configure(image=noSpeakImage)
                speakLabel.image = noSpeakImage
                # placed new command in text box
                txtCommand.delete("1.0", "end")
                txtCommand.insert("1.0", command)
                # converts command to JSON
                command = json.dumps({
                    "action": "DISPATCH_COMMAND",
                    "command": command,
                })
                # send command
                ws.send(command)
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
    # sends command
    ws.send(command)


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

# makes sure to connect to dispatcher before starting widget
while(not connected):
    try:
        ws.connect(uri)
        connected = True
    except:
        e = sys.exc_info()[0]
        connected = False
        print('not connected: ' + str(e))
        time.sleep(1)

# checks connection while the program is runnuing
def checkConnection():
    # variables shared between threads
    global connected, ws
    errorConnected = connected
    # runs as long as the widget is running
    while not exitFlag:
        try:
            if not errorConnected:
                try:
                    # error reconncting
                    ws = None
                    ws = websocket.WebSocket()
                    ws.connect(uri)
                    errorConnected = True
                except:
                    print('Connecting')
                    time.sleep(1)
            # recieves messaged from dispatcher
            ws.settimeout(40)
            check = ws.recv()
            if(check):
                connected = True
                errorConnected = True
                print('check ' + check)
            else:
                print('not connected')
                connected = False
                errorConnected = True
                time.sleep(1)
        except:
            e = sys.exc_info()[0]
            errorConnected = False
            connected = False
            
            print('not connected: ' + str(e))
            time.sleep(1)

# sets up dispatcher check thread
dispatcherThread = threading.Thread(target=checkConnection)

# starting the program
ws.send(json.dumps(register))
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

# runs the main function as an async function
# asyncio.get_event_loop().run_until_complete(main())
