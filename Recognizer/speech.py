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

# Initialize the recognizer
r = sr.Recognizer()

# This function uses the microphone to turn speech to text
def SpeechToText():
    # use the microphone as source for input.
    with sr.Microphone() as source2:

        # wait for a second to let the recognizer
        # adjust the energy threshold based on
        # the surrounding noise level
        r.adjust_for_ambient_noise(source2, duration=0.2)

        # listens for the user's input
        audio = r.listen(source2)
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

async def main():
    uri = "ws://127.0.0.1:2585/v1/messages"
    
    #starts the websocket
    async with websockets.connect(uri) as websocket:
        register = {
            "action": "REGISTER_LISTENER",
            "app": "recognizer",
            "eavesdrop": False,
        }
        
        deregister = {
            "action": "DEREGISTER_LISTENER",
            "app": "recognizer"
        }

        # Immediately register the listener with the dispatcher
        await websocket.send(json.dumps(register))

        # Loop infinitely for user to
        # speak

        while(1):

            # Exception handling to handle
            # exceptions at the runtime
            try:

                text = ''

                print('Say \"blue\" to input command from microphone, say "file" to input from command file')

                text = SpeechToText()

                print("-> "+text)

                # uses mic after activation phrase
                if text == 'blue':
                    print('activation phrase')
                    playStartSoundThread = threading.Thread(target=playStartSound)
                    playStartSoundThread.start()

                    command = SpeechToText()
                    print('Command heard: ' + command)
                    playEndSoundThread = threading.Thread(target=playEndSound)
                    playEndSoundThread.start()
                    command = json.dumps({
                        "action": "DISPATCH_COMMAND",
                        "command": command,
                    })
                    await websocket.send(command)
                # uses file to send command
                elif text == 'file':
                    # askes user for file name input
                    name = input('Input file name: ')
                    command = FileToText(name)
                    print('File command: ' + command)
                    command = json.dumps({
                        "action": "DISPATCH_COMMAND",
                        "command": command,
                    })
                    await websocket.send(command)

                # exit condition
                if text == 'exit':
                    deregister = {
                        "action": "DEREGISTER_LISTENER",
                        "app": "recognizer",
                    }
                    await websocket.send(json.dumps(deregister))
                    #time.sleep(0.5)
                    exit()

            except sr.RequestError as e:
                print("Could not request results; {0}".format(e))

            except KeyboardInterrupt:
                await websocket.send(json.dumps(deregister))
                print("Bye")
                sys.exit()

            except sr.UnknownValueError:
                print("unknown error occured")

#runs the main function as an async function
asyncio.get_event_loop().run_until_complete(main())