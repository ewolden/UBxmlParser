#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys, os
import xml.etree.ElementTree

import time
import threading

OUTPUT_SEPARATOR = '€'
VERSION = '0.04'

class Spinner:
  #Credit to Victor Moyseenko - https://stackoverflow.com/a/39504463/8376046
    busy = False
    delay = 0.2

    @staticmethod
    def spinning_cursor():
        while 1: 
            for cursor in '|/-\\': yield cursor

    def __init__(self, delay=None):
        self.spinner_generator = self.spinning_cursor()
        if delay and float(delay): self.delay = delay

    def spinner_task(self):
        while self.busy:
            sys.stdout.write(next(self.spinner_generator))
            sys.stdout.flush()
            time.sleep(self.delay)
            sys.stdout.write('\b')
            sys.stdout.flush()

    def start(self):
        self.busy = True
        threading.Thread(target=self.spinner_task).start()

    def stop(self):
        self.busy = False
        time.sleep(self.delay)

if len(sys.argv) != 2:
  print("\nMangler inputfil")
  print("Kjør scriptet slik:\n")
  print("python process.py inputfil\n\n")
  sys.exit()

print('XML decoder v.', VERSION)

inputfile = sys.argv[1]
filename = os.path.splitext(os.path.abspath(inputfile))[0]
print(filename)

print("- Leser XML fil")
spinner = Spinner()
spinner.start()
try:
  parser = xml.etree.ElementTree.XMLParser(encoding='utf-8')
  root = xml.etree.ElementTree.parse(inputfile, parser).getroot()
  spinner.stop()
except KeyboardInterrupt:
  spinner.stop()
except Exception as e:
  spinner.stop()
  print('Feil: ', e)
print("+ XML fil lest inn til minne\n")

count = 0
headers = []
finished_records = []
total_record_number = len(list(root))
ten_pcnt_records = round(total_record_number / 10)

print("- Starter utdrag fra XML objekt")
for record in root:
  processed_record = dict()
  processed_record["contents"] = [[] for _ in range(len(headers))]
  for controlfield in record.iter("controlfield"):
    processed_record["parent_name"] = controlfield.get("tag")
    if str(controlfield.get("tag")) in headers:
      processed_record["contents"][headers.index(str(controlfield.get("tag")))].append(str(controlfield.text))
    else:
      headers.append(str(controlfield.get("tag")))
      processed_record["contents"].append([str(controlfield.text)])
  for datafield in record.iter("datafield"):
    processed_record["parent_name"] = datafield.get("tag")
    for subfield in datafield:
      if str(processed_record["parent_name"] + "_" + subfield.get("code")) in headers:
        processed_record["contents"][headers.index(str(processed_record["parent_name"] + "_" + subfield.get("code")))].append(str(subfield.text))
      else:
        headers.append(str(processed_record["parent_name"] + "_" + subfield.get("code")))
        processed_record["contents"].append([str(subfield.text)])

  count = count + 1
  finished_records.append(processed_record["contents"])
  if count % ten_pcnt_records == 0:
  	print("  - " + str(round(count/total_record_number*100)) + "%, " + str(count) + " av " + str(total_record_number) + " objekter parset")
print("+ Relevant data hentet til nytt objekt\n")


print("- Etterprosseserer")
spinner.start()
try:

  afterprocessed = []
  for record in finished_records:
    tmp_record = ""
    for index, subrecord in enumerate(record):
      tmp_subrecord = ""
      if subrecord != [] and len(subrecord) > 1:
        tmp_subrecord = ("§").join(subrecord)
      elif subrecord != []:
        tmp_subrecord = subrecord[0]
      if tmp_record != "":
      	tmp_record = tmp_record + OUTPUT_SEPARATOR + tmp_subrecord
      else:
      	tmp_record = tmp_subrecord
    afterprocessed.append(tmp_record + "\n")
  spinner.stop()
except KeyboardInterrupt:
  spinner.stop()
except Exception as e:
  spinner.stop()
print("+ Ferdig med etterprossesring\n")

print("- Skriver til fil: " + filename + "_output.csv")
with open(filename + "_output.csv", "w", encoding="utf-8") as of:
  of.write(OUTPUT_SEPARATOR.join(headers) + "\n")
  for line in afterprocessed:
    of.write(line)
print("+ " +  str(len(afterprocessed)) + " linjer skrevet")
