
from chess2_event_display import *

def print_event_stats(events): # a Python list of event_data objects
  nEvents = len(events)
  nWordsPerEvent = events[0]._getExpandedData()._getNwords()
  nDataValid = np.zeros(shape=(3,nEvents))
  nMultihits = np.zeros(shape=(3,nEvents))
#  figs = [ [], [], [] ]

  for i_evt, event in enumerate(events):
    evt_figs, evt_nDataValid, evt_nMultihits = make_event_display(event)

    for i_asic in range(3):
      nDataValid[i_asic,i_evt] = evt_nDataValid[i_asic]
      nMultihits[i_asic,i_evt] = evt_nMultihits[i_asic]
#      figs[i_asic].append(evt_figs[i_asic])
      plt.close('all') # close unused figures to reduce memory usage
      

  meanDataValid = np.mean(nDataValid/nWordsPerEvent, 1)
  meanMultihits = np.mean(nMultihits/nWordsPerEvent, 1)

  print('Mean Data Valid flags per readout: %f, %f, %f'%(meanDataValid[0],meanDataValid[1],meanDataValid[2]))
  print('Mean Multihit flags per readout: %f, %f, %f'%(meanMultihits[0],meanMultihits[1],meanMultihits[2]))

