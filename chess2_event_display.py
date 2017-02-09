import numpy as np
import matplotlib.pyplot as plt

from chess2_data_classes import *

# the_event is a chess2_event object
# stack_hits determines if we will count the hits in each pixel (if True)
#             or just display the first readout (if False)
# return a tuple with:
#          -the pyplot figures generated
#          -count of data valid flags
#          -count of multihit flags
def make_event_display(the_event, stack_hits=True):
  expanded_data = the_event._getExpandedData()._getData()
  nValidReadouts = the_event._getExpandedData()._getNwords()
  if not stack_hits:
    nValidReadouts = 1

  rows = range(128)
  cols = range(32)

  data_valid = np.zeros( shape=(3,1,nValidReadouts) )
  multihit = np.zeros( shape=(3,1,nValidReadouts) )

  display_data = np.zeros( shape=(3,128,32) ) # 3 ASICs x 128 rows x 32 cols

  nDataValid = np.zeros(3) # valid readouts per ASIC
  nMultihits = np.zeros(3) # multihits per ASIC

  # fill data to display - there's probably a more efficient way to do this
  for i in range(nValidReadouts):
    for i_asic in range(3):
      if expanded_data[i_asic,i]['valid']:
        data_valid[i_asic,0,i] = 1
        nDataValid[i_asic] += 1
        display_data[i_asic, expanded_data[i_asic,i][0], expanded_data[i_asic,i][1]]+=1
      if expanded_data[i_asic,i]['multihit']:
        multihit[i_asic,0,i] = 1
        nMultihits[i_asic] += 1

  # suppress 0,0
#  for i_asic in range(3):
#    display_data[i_asic, 0, 0] = 0

  figs = []

  for i_asic in range(3):
    figure, subplots = plt.subplots(3, gridspec_kw={'height_ratios':[15,1,1]})
    subplots[0].pcolormesh(display_data[i_asic])
    subplots[0].set_title('ASIC %d Hitmap'%(i_asic+1))
    subplots[1].pcolormesh(data_valid[i_asic], vmin=0, vmax=1)
    subplots[1].set_title('Data Valid')
    subplots[2].pcolormesh(multihit[i_asic], vmin=0, vmax=1)
    subplots[2].set_title('Multihit')
    figs.append(figure)
  
  return (figs, nDataValid, nMultihits)
