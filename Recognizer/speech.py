# Python program to translate
# speech to text


import speech_recognition as sr
import playsound as ps
import time


# Initialize the recognizer
r = sr.Recognizer()


# https://www.thepythoncode.com/article/using-speech-recognition-to-convert-speech-to-text-python

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

# Loop infinitely for user to
# speak

while(1):

    # Exception handling to handle
    # exceptions at the runtime
    try:

        text = ''

        file = input('Enter file name (*.wav) or 0 for microphone: ')

        # Decides to use file to text or mic to text
        if file != '0':
            text = FileToText(file)
        else:
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
