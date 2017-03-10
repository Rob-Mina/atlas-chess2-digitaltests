import ROOT
import os, array
import argparse
import pickle

from event_display import make_ROOT_event_display

ROOT.TH1.AddDirectory(ROOT.kFALSE)
ROOT.gROOT.SetBatch(ROOT.kTRUE)

def makeHistDictionary(ASICNum,eventNum):
  hPixelMap = ROOT.TH2D("asic%i_%i"%(ASICNum,eventNum),"asic%i_%i"%(ASICNum,eventNum),32,0,31,128,0,127)
  hValidData= ROOT.TH1C("vasic%i_%i"%(ASICNum,eventNum),"vasic%i_%i"%(ASICNum,eventNum),256,0,255)
  hMultiHit = ROOT.TH1C("masic%i_%i"%(ASICNum,eventNum),"masic%i_%i"%(ASICNum,eventNum),256,0,255)

  histDict = {"pixelMap" : hPixelMap, "isValidData" : hValidData, "isMultiHit" : hMultiHit}

  return histDict

def makePlotsFromPickle( fileName, maxEvents, saveAs ):
  CHESS2Events = pickle.load(open(fileName,'rb'))

  for eventNum, CHESS2Event in enumerate(CHESS2Events):
    if(eventNum > maxEvents): break
    expandedData = CHESS2Event._getExpandedData()._getData()
    ASICList = []
    ASICList.append(makeHistDictionary(1,eventNum))
    ASICList.append(makeHistDictionary(2,eventNum))
    ASICList.append(makeHistDictionary(3,eventNum))
    for timeSlice in range(256):
      for iter,ASIC in enumerate(ASICList):
        ASICData = expandedData[iter][timeSlice]
        if(ASICData[3]):
          ASIC["pixelMap"].Fill(ASICData[1],ASICData[0])
          ASIC["isValidData"].Fill(timeSlice)
        if(ASICData[2]):
          ASIC["isMultiHit"].Fill(timeSlice)
    for iter,ASIC in enumerate(ASICList):
      make_ROOT_event_display(ASIC,iter+1,eventNum,saveAs)

def makePlotsFromROOT( fileName, maxEvents, saveAs ):
  inFile = ROOT.TFile(fileName, 'read')
  # get the number of events = N_hists/9
  nEvts = int(len(inFile.GetListOfKeys())/9)
  for i_evt in range(nEvts):
    if (i_evt > maxEvents): break
    for i_asic in range(3):
      ASIC = { "pixelMap" : inFile.Get("asic%i_%i"%(i_asic+1,i_evt)),
               "isValidData" : inFile.Get("vasic%i_%i"%(i_asic+1,i_evt)),
                "isMultiHit" : inFile.Get("masic%i_%i"%(i_asic+1,i_evt)) }
      make_ROOT_event_display(ASIC,i_asic+1,i_evt,saveAs)
  inFile.Close()

if __name__=="__main__":
  parser = argparse.ArgumentParser(description='CHESS2 Data Plotter using ROOT')

  parser.add_argument('--fileName', action="store", dest="fileName", default="None", help="Path + file of CHESS2 data")
  parser.add_argument('--maxEvents', action="store", dest="maxEvents", default="1", help="Max # events to plot")
  parser.add_argument('--saveAs', action="store", dest="saveAs", default="None", help="Path + file of image files to save")

  options = parser.parse_args()

  fileName  = options.fileName
  maxEvents = int(options.maxEvents)
  saveAs    = options.saveAs

  if (fileName[-4:] == '.pkl'):
    makePlotsFromPickle( fileName, maxEvents, saveAs )
  elif (fileName[-4:] == 'root'):
    makePlotsFromROOT( fileName, maxEvents, saveAs )
  else:
    print("Unrecognized file extension: %s"%fileName)


