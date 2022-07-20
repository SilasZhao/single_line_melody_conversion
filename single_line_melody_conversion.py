'''
Author: Silas Zhao
Date: July 18, 2022
'''


from music21 import *
from music21 import note
import copy
import os
from tqdm import tqdm

'''
if the midi contains more than one part, seperate each part into different midi files
'''
def split_multi_instrument_midi(in_dirname,out_dirname):
  for (_,file_name) in tqdm(enumerate(os.listdir(in_dirname))):
    s = converter.parse(os.path.join(in_dirname,file_name))
    for i in range(len(s)):
      s[i].write('midi',out_dirname + "/"+file_name[:-4]+"_"+str(i)+".mid")


'''
takes in a chord and returns the note that has the highest pitch in the chord.
'''
def chord2note(chord):
  return note.Note(max([p.midi for p in chord.pitches]))

def is_valid_stream(v):
  # check if the stream has one TimeSignature
  if len(v.recurse().getElementsByClass(meter.TimeSignature)) != 1:
    return False
  # # check if the stream has one KeySignature
  # if len(v.recurse().getElementsByClass(key.KeySignature)) != 1:
  #   print("no keysignature")
  #   return False
  return True

'''
return true if:
      the stream have one or more voice(s) 
      the stream has one time signature
      the stream has key Signature
'''
def is_valid(s):
  if len(s.getElementsByClass(stream.Voice)) == 0:
    return is_valid_stream(s)
  else: 
    is_true = True
    for v in s.getElementsByClass(stream.Voice):
      if not is_valid_stream(v): 
        is_true = False
  return is_true
'''
make sure each voice contains no chords
'''
def clean_stream(s):
  newStream = stream.Stream()
  for el in s.recurse():
    t = el.offset
    d = el.duration.quarterLength
    if hasattr(el,"isChord"):
      if el.isChord:
        el = chord2note(el)
        el.duration.quarterLength = d
    if el.duration.quarterLength == 0.0:
      continue
    newStream.insert(t,el)
  return newStream
    
'''
assume every midi starts from just one part
'''
def clean_midi(in_dirname,out_dirname):
  # first layer is always start from "part" 
  invalid = set()
  for (_,file_name) in tqdm(enumerate(os.listdir(in_dirname))):
    # print(file_name)
    input_file = in_dirname + file_name
    c = converter.Converter()
    c.parseFile(input_file)
    s = c.stream
    if len(s) != 1:
      print(file_name)
      invalid.add(file_name)
      continue
    s = s[0]
    #make sure every voice has single time signature
    if len(s.recurse().getElementsByClass(stream.instrument)) > 0:
      # unpack each instrument's voices
      i = 0
      for ins in s.recurse().getElementsByClass(stream.instrument):
        #check if the stream is valid
        if not is_valid(s):
          invalid.add(file_name)
        else:
          # create a new stream to write to midi
          for v in ins.recurse().getElementsByClass(stream.Voice):
            newStream = clean_stream(v)
            newStream.write('midi',out_dirname + str(i) + "_voice_" + file_name)
            i += 1
            print(i)

        
    elif len(s.recurse().getElementsByClass(stream.Voice)) == 0:
      if not is_valid(s):
        invalid.add(file_name)
      else:
        i = 0
        newStream = clean_stream(s)
        # print(str(i) + "_voice_" + file_name)
        newStream.write('midi',out_dirname + str(i) + "_voice_" + file_name)
        i += 1


    else:
      # create a new stream to write to midi
      i = 0
      for v in s.recurse().getElementsByClass(stream.Voice):
        newStream = clean_stream(v)
        newStream.write('midi',out_dirname + str(i) + "_voice_" + file_name)
        i += 1
  print("number of invalid file: ",len(invalid))
  with open('invalid.txt', 'w') as f:
    for k in invalid:
      k = str(k) + "\n"
      f.write(k)

'''
check if the stream contains chord
'''
def hasChord(input):
  s = converter.parse(input)
  for el in s.recurse():
    if hasattr(el,"isChord"):
      if el.isChord:
        return True
  return False

def main():
  '''
  split different parts in a midi into different midis
  '''
  # in_dirname = "/content/gdrive/MyDrive/2022_Summer/MuseData"
  # out_dirname = "/content/gdrive/MyDrive/2022_Summer/MuseData_update"
  # split_multi_instrument_midi(in_dirname,out_dirname)
  '''
  clean the file
  '''
  in_dirname = "/content/gdrive/MyDrive/2022_Summer/MuseData_update/"
  out_dirname = "/content/gdrive/MyDrive/2022_Summer/MuseData_cleaned/"

  input = "/content/gdrive/MyDrive/2022_Summer/MuseData_update/bach.chorals.0379_midip_01_3.mid"
  clean_midi(in_dirname,out_dirname)
  # for (_,file_name) in tqdm(enumerate(os.listdir(in_dirname))):
  #   input_file = in_dirname + file_name
  # c = converter.Converter()
  # c.parseFile(input)
  # s = c.stream
  # for el in s.recurse():
  #   print(el.offset, el, el.duration)
  #   if el.duration.quarterLength > 4.0:
  #     print("------------------------------------------------------")
main()