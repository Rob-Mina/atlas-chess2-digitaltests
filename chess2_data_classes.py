from math import floor
import numpy as np

# condensed format: (1 byte = offset, 2 bytes=hit [2 unused bits]):
#     BIT[06:00] = ROW[6:0]
#     BIT[11:07] = COL[4:0]
#     BIT[12:12] = multihit
#     BIT[13:13] = valid
# the condensed tuple has shape: 
#                          3 (ASIC) x { N (=number non-zero entries) x 2 (offset,data) }
class condensed_event_data:

  def __init__(self, streamer_data): # streamer_data as bytearray, with header stripped
    # initialize each with max size to avoid resizing, then shrink to size at the end
    data_preshrink = [ np.empty( 256, dtype=[('offset','u1'),('hit','u2')] ),\
                       np.empty( 256, dtype=[('offset','u1'),('hit','u2')] ),\
                       np.empty( 256, dtype=[('offset','u1'),('hit','u2')] ) ]

    # read one 8-byte word at a time
    cnt_words = 0
    asic_nhits = [ 0, 0, 0 ]
    while (cnt_words < floor(len(streamer_data)/8)):
      theword = streamer_data[cnt_words*8:cnt_words*8+8]
      offset = np.uint8(cnt_words) # current word = the offset

      asic1_hit = np.uint16(theword[0] | (theword[1] << 8))
      if (asic1_hit != 0):
        data_preshrink[0][asic_nhits[0]] = ( offset, asic1_hit )
        asic_nhits[0] += 1

      asic2_hit = np.uint16(theword[2] | (theword[3] << 8))
      if (asic2_hit != 0):
        data_preshrink[1][asic_nhits[1]] = ( offset, asic2_hit )
        asic_nhits[1] += 1

      asic3_hit = np.uint16(theword[4] | (theword[5] << 8))
      if (asic3_hit != 0):
        data_preshrink[2][asic_nhits[2]] = ( offset, asic3_hit )
        asic_nhits[2] += 1

      cnt_words += 1

    self.data = ( data_preshrink[0][0:asic_nhits[0]],
                  data_preshrink[1][0:asic_nhits[1]],
                  data_preshrink[2][0:asic_nhits[2]] )
    self.asic_nhits = ( asic_nhits )
    self.data_words = cnt_words

  def _getData(self):
    return self.data
  def _getNhits(self):
    return self.asic_nhits
  def _getNwords(self):
    return self.data_words

# expanded format: 1 byte per data element (row,col,multihit,valid)
#                  offset is encoded as array index (0-255)
# struct has shape:
#                          { 3 (ASIC) x 256 (offset) x 4 (row, col, multihit, valid) }
class expanded_event_data:

  # initializing everything to 0 means we only need to overwrite the non-zero hits
  def __init__(self, condensed_data):
    self.condensed_data = condensed_data
    self.data = np.zeros( shape=(3,256,), dtype=[('row','u1'),('col','u1'),('multihit','b1'),('valid','b1')] )
    for i_asic in range(3):
      for entry in condensed_data._getData()[i_asic]:
        row = np.uint8(entry['hit'] & 0x7f) # first 7 bits
        col = np.uint8((entry['hit'] & 0xf80) >> 7) # next 5 bits
        multihit = np.bool_((entry['hit'] & 0x1000) >> 12) # next 1 bit
        valid = np.bool_((entry['hit'] & 0x2000) >> 13) # next 1 bit
        self.data[i_asic,entry['offset']] = ( row, col, multihit, valid )

  def _getData(self):
    return self.data
  def _getNhits(self):
    return self.condensed_data._getNhits()
  def _getNwords(self):
    return self.condensed_data._getNwords()

# wraps both a condensed and expanded data rep., along with the timestamp and header
class chess2_event:
  
  def __init__(self, streamer_packet):
    self.header = streamer_packet[0:32]
    self.condensed_data = condensed_event_data(streamer_packet[32:])
    self.timestamp_lower = np.uint32( self.header[12] | (self.header[13] << 8)  \
                                                      | (self.header[14] << 16) \
                                                      | (self.header[15] << 24) )
    self.timestamp_upper = np.uint32( self.header[16] | (self.header[17] << 8) \
                                                      | (self.header[18] << 16) \
                                                      | (self.header[19] << 24) )
    self.timestamp = np.uint64( self.timestamp_lower | (self.timestamp_upper << 32) )
    self.expanded = False
    self.expanded_data = None

  def expand_data(self):
    if self.expanded: return
    self.expanded_data = expanded_event_data(self.condensed_data)
    self.expanded = True

  def _getCondensedData(self):
    return self.condensed_data
  def _getTimestamp(self):
    return self.timestamp
  def _getExpandedData(self):
    if not self.expanded:
      self.expand_data()
    return self.expanded_data

# load a list of events from the pickle file and return it
import pickle
def load_from_pickle(pkl_fname):
  return pickle.load(open(pkl_fname,'rb'))
