# Python program to translate
# speech to text
# Sound files such as end.wav and start.wav are from windows system sounds

import speech_recognition as sr
import playsound as ps
import time
import asyncio
import websockets
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

exitFlag = False
listening = False
connected = False
# This function uses the microphone to turn speech to text

#setting up websocket
ws = websocket.WebSocket()
widget = tk.Tk()
widget.winfo_toplevel().title('Recognizer')
widget.iconbitmap('speaker.ico')
widget.geometry("300x540")
widget.lift()
widget.call('wm', 'attributes', '.', '-topmost', True)

speakText = tk.Label(text='Say \"blue\" for commands, or alt+ctrl+v')
speakText.pack()

micOffImage = tk.PhotoImage(file='micoff.png')
micOnImage = tk.PhotoImage(file='micon.png')
micLabel = tk.Label(widget, image=micOffImage)
micLabel.pack()
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
        audio = r.listen(source2)
        micLabel.configure(image=micOffImage)
        micLabel.image = micOffImage
        # Using google to recognize audio
        text = r.recognize_google(audio)
        # converts all text to lower case
        text = text.lower()
        return text

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


# setting up
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




def SendCommand():
    result = txtCommand.get("1.0", "end")
    payload = {
        "action": "DISPATCH_COMMAND",
        "command": result.strip(),
        "recipient": "desktop"
    }
    ws.send(json.dumps(payload))


def VoiceCommand():
    global listening
    while True:
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
                keyboard.remove_hotkey('alt+ctrl+v')
                listening = True
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
                speakLabel.configure(image=noSpeakImage)
                speakLabel.image = noSpeakImage
                txtCommand.delete("1.0", "end")
                txtCommand.insert("1.0", command)
                command = json.dumps({
                    "action": "DISPATCH_COMMAND",
                    "command": command,
                })
                ws.send(command)
                listening = False
                keyboard.add_hotkey('alt+ctrl+v', hotKey)
        except sr.RequestError as e:
            print("Could not request results; {0}".format(e))

        except KeyboardInterrupt:
            ws.send(json.dumps(deregister))
            sys.exit()

        except sr.UnknownValueError:
            print("unknown error occured")


def hotKey():
    global listening
    keyboard.remove_hotkey('alt+ctrl+v')
    if listening == False:
        listening = True
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
        speakLabel.configure(image=noSpeakImage)
        speakLabel.image = noSpeakImage
        txtCommand.delete("1.0", "end")
        txtCommand.insert("1.0", command)
        command = json.dumps({
            "action": "DISPATCH_COMMAND",
            "command": command,
        })
        ws.send(command)
        listening = False
        keyboard.add_hotkey('alt+ctrl+v', hotKey)


keyboard.add_hotkey('alt+ctrl+v', hotKey)


def FileToTextButton():
    filename = filedialog.askopenfilename(
        initialdir="/", title="Select file", filetypes=[("wav files", "*.wav")])
    print(filename)
    text = FileToText(filename)
    command = json.dumps({
        "action": "DISPATCH_COMMAND",
        "command": text,
    })
    ws.send(command)


# setting up threads
voiceCommandThread = threading.Thread(target=VoiceCommand)

txtCommand = tk.Text(widget, height=1)
txtCommand.pack( pady=15, )
btnSend = tk.Button(widget, height=1, width=10,
                    text="Send", command=SendCommand)


btnSend.pack(pady=15)


speakText = tk.Label(text='Select and audio file to become a command')
speakText.pack(pady = 20)

fileButton = tk.Button(widget, height=1, width=20,
                       text="Select Audiofile", command=FileToTextButton)
fileButton.pack(pady=15)


def on_quit():
    global widget, exitFlag
    exitFlag = True
    widget.destroy()


widget.protocol("WM_DELETE_WINDOW", on_quit)


while(not connected):
    try:
        ws.connect(uri)
        connected = True
    except:
        e = sys.exc_info()[0]
        connected = False
        print('not connected: ' + str(e))
        time.sleep(1)

def checkConnection():
    global connected, ws
    errorConnected = connected
    while not exitFlag:
        try:
            if not errorConnected:
                try:
                    ws = None
                    ws = websocket.WebSocket()
                    ws.connect(uri)
                    errorConnected = True
                except:
                    print('Connecting')
                    time.sleep(1)
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


dispatcherThread = threading.Thread(target=checkConnection)

# starting the program
ws.send(json.dumps(register))
dispatcherThread.start()
voiceCommandThread.start()

widget.mainloop()

# exitting

voiceCommandThread.join()
dispatcherThread.join()
print('exit')
ws.send(json.dumps(deregister))

# runs the main function as an async function
# asyncio.get_event_loop().run_until_complete(main())
