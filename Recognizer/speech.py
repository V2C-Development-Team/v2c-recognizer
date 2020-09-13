# Python program to translate
# speech to text and text to speech


import speech_recognition as sr
import playsound as ps
import time


# Initialize the recognizer
r = sr.Recognizer()


# https://www.thepythoncode.com/article/using-speech-recognition-to-convert-speech-to-text-python

def SpeechToText():
    # use the microphone as source for input.
    with sr.Microphone() as source2:

        # wait for a second to let the recognizer
        # adjust the energy threshold based on
        # the surrounding noise level
        r.adjust_for_ambient_noise(source2, duration=0.2)

        print('Say: !')
        # listens for the user's input
        audio = r.listen(source2)
        print('worked')
        # Using sphinx to recognize audio
        text = r.recognize_sphinx(audio)
        # converts all text to lower case
        text = text.lower()
        return text


# Loop infinitely for user to
# speak

while(1):

    # Exception handling to handle
    # exceptions at the runtime
    try:

        text = SpeechToText()

        print("-> "+text)

        if text == 'blue':
            print('activation phrase')
            ps.playsound('start.wav')
            command = SpeechToText()
            time.sleep(0.1)
            print('Sphnix heard: ' + command)

            ps.playsound('end.wav')

        if text == 'exit':
            exit()

    except sr.RequestError as e:
        print("Could not request results; {0}".format(e))

    except sr.UnknownValueError:
        print("unknown error occured")
