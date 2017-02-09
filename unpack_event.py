
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
#  for event in eventReader._getEvents():
#    print(event._getCondensedData()._getData())
#    condensed_data.append(event._getCondensedData()._getData())
#    expanded_data.append(event._getExpandedData()._getData())

  pickle.dump(eventReader._getEvents(), open(arg2,'wb'), pickle.HIGHEST_PROTOCOL)

if __name__ == '__main__':
  main(sys.argv[1],sys.argv[2])

