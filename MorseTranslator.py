import wave
import numpy as np
from scipy.io import wavfile
import matplotlib.pyplot as plot

FREQ = 1000
THRESHOLD = 128
WPM = 5
NOISE_FACTOR = 0.01
AUDIO_FILENAME = 'sara.wav'
letter_to_morse = {
	"a" : ".-",	"b" : "-...",	"c" : "-.-.",
	"d" : "-..",	"e" : ".",	"f" : "..-.",
	"g" : "--.",	"h" : "....",	"i" : "..",
	"j" : ".---",	"k" : "-.-",	"l" : ".-..",
	"m" : "--",	"n" : "-.",	"o" : "---",
	"p" : ".--.",	"q" : "--.-",	"r" : ".-.",
	"s" : "...",	"t" : "-",	"u" : "..-",
	"v" : "...-",	"w" : ".--",	"x" : "-..-",
	"y" : "-.--",	"z" : "--..",	"1" : ".----",
	"2" : "..---",	"3" : "...--",	"4" : "....-",
	"5" : ".....", 	"6" : "-....",	"7" : "--...",
	"8" : "---..",	"9" : "----.",	"0" : "-----",	
	" " : " "}
morse_to_letters = dict([(value, key) for key, value in letter_to_morse.items()])


def digitize(snd_data):
  sampled = np.asarray(snd_data).copy()
  if sampled[0] == THRESHOLD:
    sampled[0] = 0
  else: sampled[0] = 1
  for i in range(1, len(snd_data)-1):
    if snd_data[i]>THRESHOLD + 4 or snd_data[i]<THRESHOLD-4:
      sampled[i] = 1
    elif snd_data[i-1]<THRESHOLD+4 and snd_data[i-1]>THRESHOLD-4 and snd_data[i+1]<THRESHOLD+4 and snd_data[i+1]>THRESHOLD-4:
      sampled[i] = 0
    else:
      sampled[i] = 1
  sampled[-1] = sampled[-2]
  return np.asarray(sampled)

def preprocess(AUDIO_FILENAME):
  wav_file = wave.open(AUDIO_FILENAME)
  fs, data = wavfile.read(AUDIO_FILENAME)
  data = data
  data = digitize(data)
  length = data.shape[0] / fs
  time = np.linspace(0., length, data.shape[0])
  return time, data

def tone_separator(AUDIO_FILENAME):
  time, data = preprocess(AUDIO_FILENAME)
  c1 = 0
  c2 = 0
  c3 = 0
  c4 = 0
  tone_sep = []
  rising_edge = 0
  falling_edge = 0
  for i in range(1, len(time)):
    if data[i] == 1:
      if data[i-1] == 0:
        c1 = time[i]
        c4 = time[i]
        rising_edge = 1
    elif data[i] == 0:
      if data[i-1] == 1:
        c2 = time[i]
        c3 = time[i]
        falling_edge = 1
    if c1 != 0 and c2 != 0:
      tone_sep.append((c2-c1, falling_edge))
      rising_edge = 0
      falling_edge = 0
      c1 = 0
      c2 = 0
    if c3 != 0 and c4 != 0 and c4>c3:
      tone_sep.append((c4-c3, falling_edge))
      c3 = 0
      c4 = 0
  tone_sep = filter_tones(tone_sep)
  tone_sep = np.asarray(tone_sep)
  tone_sep = np.round(tone_sep, 3)
  return tone_sep

def filter_tones(tone_list):
  tone_list = [s for s in tone_list if s[0]>NOISE_FACTOR]
  return tone_list

def normalize_time(tone_list):  ##normaloze the values of the tones, 1 = '.', 2= '-', 3 = letter separation, 4= word separation
  normalized = []
  for x in tone_list:
    if x[0] < 0.1:
        normalized.append((1, x[1]))
    elif x[0] > 1 and x[0] <4 :
        normalized.append((3, x[1]))
    elif x[0] > 4:
       normalized.append((4, x[1]))
    else:
      normalized.append((2, x[1]))
  normalized.append((3,0.0))
  return normalized

def encode(Tones): #convert the resultant audio into text morse (dots & dashes)
  scentence=[]
  letter = ''
  for tone in Tones:
      if tone[0] == 1 and tone[1] == 1:
        letter+='.'
      elif tone[0] == 2:
        letter += '-'
      elif tone[0] == 3:
        scentence.append(letter)
        letter=''
      elif tone[0] == 4:
        scentence.append(letter)
        scentence.append(' ')
        letter = ''
  return scentence

def decode(morse): #convert the text morse into english letters 
  scentence = ''
  for e in morse:
    scentence += morse_to_letters[e]
  return scentence

def Translate_Morse(AUDIO_FILENAME):
  tones = tone_separator(AUDIO_FILENAME)
  tones = normalize_time(tones)
  Morse = encode(tones)
  translation = decode(Morse)
  return translation

translated = Translate_Morse(AUDIO_FILENAME)
print(translated)