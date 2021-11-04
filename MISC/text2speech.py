"""
Note: ssml must be well-formed according to:
    https://www.w3.org/TR/speech-synthesis/
"""

# I use this for creating IVR menu prompts instead of using professional services
# You will need to sign up for a cloud google account to use this feature
# You will need pip install PySimpleGUI for this to work
# you will need pip install google-cloud-texttospeech
# Menu will ask for file name, text to convert to speech, and a language (EN or FR)
# There's other voices and languages you can use.  Just go google "google text to speech api" or "google text to speech api python"

# Helpful links
# https://cloud.google.com/text-to-speech has a demo box that you can look at drop downs for languages and voices
# https://cloud.google.com/text-to-speech/docs/libraries 

from google.cloud import texttospeech
import os
from dotenv import load_dotenv
load_dotenv()
import PySimpleGUI as sg
import sys

os.environ["GOOGLE_APPLICATION_CREDENTIALS"]=os.getenv('googlePath')
client = texttospeech.TextToSpeechClient()

# Sets break condition if menu is exited or canceled 
TTS='0'

# Sets the theme
sg.theme('Material1')     
  
# Build the layout of your window
layout = [
    [sg.Text('Enter your file name:', size =(15, 1)), sg.InputText()],
    [sg.Text('Enter your text to speech in the box below')],
    [sg.Multiline('', size=(65,15), k='-MLINE-')],
    [sg.Text('Select Your Language')],
    [sg.Combo(values=('English', 'French Canadian', 'French French'), default_value='English', readonly=True, k='-COMBO1-')],
    [sg.Text('')],
    [sg.Submit(), sg.Cancel()]
]

# Runs the window applying the layout
window = sg.Window('Google Text to Speech!', layout)
while True:
    event, values = window.read()
    if event=="Cancel" or event==sg.WIN_CLOSED:
        break
    elif event=='Submit':
        fileName=values[0]
        TTS=values['-MLINE-']
        if values['-COMBO1-'] == 'English':
            langOutput='en-US'
            langName='en-US-Wavenet-F'
        elif values['-COMBO1-'] == 'French Canadian':
            langOutput='fr-CA'
            langName='fr-CA-Wavenet-F'
        else:
            langOutput='fr-FR'
            langName='fr-FR-Wavenet-F'
        window.close()

if TTS == '0':
    sys.exit()

# Set the text input to be synthesized
synthesis_input = texttospeech.SynthesisInput(text=TTS) 

# Build the voice request, select the language code ("fr-CA") and the ssml
voice = texttospeech.VoiceSelectionParams(
    language_code=(langOutput), name=(langName)
)

# Select the type of audio file you want returned
audio_config = texttospeech.AudioConfig(
    audio_encoding=texttospeech.AudioEncoding.MP3,
)

# Perform the text-to-speech request on the text input with the selected
# voice parameters and audio file type
response = client.synthesize_speech(
    input=synthesis_input, voice=voice, audio_config=audio_config
)

# Write the response to the output file.
with open("c:/pythonoutput/" + fileName + '.mp3', "wb") as out:
    out.write(response.audio_content)
    print('Audio content written to file c:/pythonoutput/' + fileName + '.mp3') # You can modify the path to output here