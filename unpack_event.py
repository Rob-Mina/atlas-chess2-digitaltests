
import sys
import rogue.utilities
import rogue.utilities.fileio
import rogue.interfaces.stream
import pyrogue
import time
import pickle

from chess2_data_classes import *

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

def main(arg1,arg2):
  fileReader = rogue.utilities.fileio.StreamReader()
  eventReader = EventReader()

  pyrogue.streamConnect(fileReader, eventReader)

  fileReader.open(arg1)

  time.sleep(5)

#  print(len(eventReader._getEvents()))
#  condensed_data = []
#  expanded_data = []
  nhits = [ 0, 0, 0 ]
  events = eventReader._getEvents()
  for event in events:
    for i_asic in range(3):
      nhits[i_asic] += event._getCondensedData()._getNhits()[i_asic]
  print( "No. events = %d"%len(events) )
  print( "Total hits = %d,%d,%d"%(nhits[0],nhits[1],nhits[2]) )
  print( "Avg hits per event = %.3f,%.3f,%.3f"%(nhits[0]/len(events),nhits[1]/len(events),nhits[2]/len(events)) )


  pickle.dump(events, open(arg2,'wb'), pickle.HIGHEST_PROTOCOL)

if __name__ == '__main__':
  outfname = 'data.pkl'
  if len(sys.argv) < 3:
    outfname = sys.argv[1][:-3] + "pkl"
  else:
    outfname = sys.argv[2]
  main(sys.argv[1],outfname)

