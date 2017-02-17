import numpy as np
import matplotlib.pyplot as plt
import ROOT

from data_classes import *

def make_ROOT_event_display(ASIC,ASICNum,eventNum,saveAs):
  c = ROOT.TCanvas("name%i_%i"%(eventNum,ASICNum),"hist_e%i_a%i"%(eventNum,ASICNum),700,600)
  pad1 = ROOT.TPad("pad1_e%i_a%i"%(eventNum,ASICNum), "pad1_e%i_a%i"%(eventNum,ASICNum), 0, 0.305, 1, 1);
  #pad1.SetBottomMargin(0.1);
  #pad1.SetLogy()
  #pad1.SetGrid(1,1);

  pad1.Draw("same");

  pad2 = ROOT.TPad("pad2_e%i_%i"%(eventNum,ASICNum), "pad2%i_%i"%(eventNum,ASICNum), 0, 0.145, 1, 0.295);
  pad2.SetTopMargin(0);
  pad2.SetBottomMargin(0.3);
  #pad2.SetGrid(0,1);
  pad2.Draw("same");

  pad3 = ROOT.TPad("pad3_e%i_%i"%(eventNum,ASICNum), "pad3%i_%i"%(eventNum,ASICNum), 0, 0.001, 1, 0.135);
  pad3.SetTopMargin(0);
  pad3.SetBottomMargin(0.3);
  #pad3.SetGrid(0,1);
  pad3.Draw("same");
  pad1.cd()

  ASIC["pixelMap"].SetStats(ROOT.kFALSE)
  ASIC["pixelMap"].SetTitle('')
  ASIC["pixelMap"].SetMaximum(10)
  ASIC["pixelMap"].GetXaxis().SetTitle("Pixel Array")
  ASIC["pixelMap"].Draw("COLZ")

  pad2.cd()
  ASIC["isValidData"].SetStats(ROOT.kFALSE)
  ASIC["isValidData"].SetTitle('')
  ASIC["isValidData"].SetFillColor(ROOT.kBlue)
  ASIC["isValidData"].GetXaxis().SetTitle("Valid Hits")
  ASIC["isValidData"].GetXaxis().SetTitleSize(.15)
  ASIC["isValidData"].GetXaxis().SetLabelSize(.15)
  ASIC["isValidData"].GetYaxis().SetNdivisions(2)
  ASIC["isValidData"].Draw()
  pad3.cd()
  ASIC["isMultiHit"].SetStats(ROOT.kFALSE)
  ASIC["isMultiHit"].SetTitle('')
  ASIC["isMultiHit"].SetFillColor(ROOT.kBlue)
  ASIC["isMultiHit"].GetXaxis().SetTitle("MultiHit")
  ASIC["isMultiHit"].GetXaxis().SetTitleSize(.15)
  ASIC["isMultiHit"].GetXaxis().SetLabelSize(.15)
  ASIC["isMultiHit"].GetYaxis().SetNdivisions(2)
  ASIC["isMultiHit"].Draw()

  c.Print("%s_event%i_asic%i.png"%(saveAs,eventNum,ASICNum))

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
