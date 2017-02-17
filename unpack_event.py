import sys
import rogue.utilities
import rogue.utilities.fileio
import rogue.interfaces.stream
import pyrogue
import time
import pickle
import ROOT
import argparse

from data_classes import *

class EventReader(rogue.interfaces.stream.Slave):

  def __init__(self):
    rogue.interfaces.stream.Slave.__init__(self)
    self.enable = True
    self.events = []

  def _acceptFrame(self, frame):
    if self.enable:
      channelNum = (frame.getFlags() >> 24)
      if (channelNum == 0x1) :
        # collect the data
        p = bytearray(frame.getPayload())
        frame.read(p, 0)
        # construct an event object
        event = chess2_event( p )
        self.events.append(event)

  def _getEvents(self):
    return self.events

# return a Python list of length 3*N_events where the elements are dictionaries
def generate_summary_histograms( events ):
  summary_hists = []
  for i_evt, event in enumerate(events):
    ASICList = []
    for asic in range(3):
      histDict = { }
      histDict["pixelMap"] = ROOT.TH2D("asic%i_%i"%(asic,i_evt),"asic%i_%i"%(asic,i_evt),32,0,31,128,0,127)
      histDict["isValidData"] = ROOT.TH1C("asic%i_%i"%(asic,i_evt),"asic%i_%i"%(asic,i_evt),256,0,255)
      histDict["isMultiHit"] = ROOT.TH1C("asic%i_%i"%(asic,i_evt),"asic%i_%i"%(asic,i_evt),256,0,255)
      ASICList.append(histDict)
    expandedData = event._getExpandedData()._getData()
    for timeSlice in range(256):
      for asic,histDict in enumerate(ASICList):
        ASICData = expandedData[asic][timeSlice]
        if (ASICData[3]):
          histDict["pixelMap"].Fill(ASICData[0],ASICData[1])
          histDict["isValidData"].Fill(timeSlice)
        if (ASICData[2]):
          histDict["isMultiHit"].Fill(timeSlice)
    summary_hists.append(ASICList[0])
    summary_hists.append(ASICList[1])
    summary_hists.append(ASICList[2])
  return summary_hists

def main( binFileName, verbose=False, pklFileName='', rootFileName='' ):
  fileReader = rogue.utilities.fileio.StreamReader()
  eventReader = EventReader()

  pyrogue.streamConnect(fileReader, eventReader)

  fileReader.open(binFileName)

  time.sleep(5)

  nhits = [ 0, 0, 0 ]
  events = eventReader._getEvents()

  # write condensed data first before processing
  if len(pklFileName) > 0:
    pickle.dump(events, open(pklFileName,'wb'), pickle.HIGHEST_PROTOCOL)

  for event in events:
    for i_asic in range(3):
      nhits[i_asic] += event._getCondensedData()._getNhits()[i_asic]
  print( "Filename = %s"%binFileName )
  print( "No. events = %d"%len(events) )
  print( "Total hits = %d,%d,%d"%(nhits[0],nhits[1],nhits[2]) )
  print( "Avg hits per event = %.3f,%.3f,%.3f"%(nhits[0]/len(events),nhits[1]/len(events),nhits[2]/len(events)) )

  if verbose or (len(rootFileName) > 0):
    summary_hists = generate_summary_histograms(events)
    if len(rootFileName) > 0:
      rootFile = ROOT.TFile(rootFileName, "RECREATE")
      rootFile.cd()
      for histDict in summary_hists:
        histDict["pixelMap"].Write()
        histDict["isValidData"].Write()
        histDict["isMultiHit"].Write()

if __name__ == '__main__':
  parser = argparse.ArgumentParser(description='CHESS2 raw data unpacker')
  parser.add_argument('--binFileName', action='store', dest='binFileName', default='None', help='Path to CHESS2 binary (raw) data')
  parser.add_argument('--pklFileName', action='store', dest='pklFileName', default='None', help='Path to pickle file to write structured data. Will contain a Python list of Chess2EventData objects. Leave blank to omit storing the data.')
  parser.add_argument('--rootFileName', action='store', dest='rootFileName', default='None', help='Path to ROOT file to write summary histograms. Will contain 9*(number of events) histograms with hitmaps, valid data maps, and multihit maps for each ASIC/event.')
  parser.add_argument('--verbosity', action='store', dest='verbosity', default='basic', help='Verbosity level [basic|extended]')

  options = parser.parse_args()

  binFileName = options.binFileName
  pklFileName = options.pklFileName
  rootFileName = options.rootFileName
  verbosity = options.verbosity

  if not binFileName:
    print("Cannot run without specifying binFileName.")
  else:
    main( binFileName, verbosity != 'basic', pklFileName if pklFileName else '', rootFileName if rootFileName else '' )

