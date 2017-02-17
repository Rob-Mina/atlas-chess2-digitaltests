import ROOT
import os, array
import argparse
import pickle


def makeHistDictionary(ASICNum,eventNum):
	hPixelMap = ROOT.TH2D("asic%i_%i"%(ASICNum,eventNum),"asic%i_%i"%(ASICNum,eventNum),32,0,31,128,0,127)
	hValidData= ROOT.TH1C("vasic%i_%i"%(ASICNum,eventNum),"vasic%i_%i"%(ASICNum,eventNum),256,0,255)
	hMultiHit = ROOT.TH1C("masic%i_%i"%(ASICNum,eventNum),"masic%i_%i"%(ASICNum,eventNum),256,0,255)

	histDict = {"pixelMap" : hPixelMap, "isValidData" : hValidData, "isMultiHit" : hMultiHit}

	return histDict


def makePlot(ASIC,ASICNum,eventNum,saveAs):
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

	c.SaveAs("%s_event%i_asic%i.png"%(saveAs,eventNum,ASICNum))


if __name__=="__main__":
	parser = argparse.ArgumentParser(description='CHESS2 Data Plotter using ROOT')

	parser.add_argument('--fileName', action="store", dest="fileName", default="None", help="Path + file of CHESS2 data")
	parser.add_argument('--maxEvents', action="store", dest="maxEvents", default="1", help="Max # events to plot")
	parser.add_argument('--saveAs', action="store", dest="saveAs", default="None", help="Path + file of image files to save")

	options = parser.parse_args()

	fileName  = options.fileName
	maxEvents = int(options.maxEvents)
	saveAs    = options.saveAs

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
					ASIC["pixelMap"].Fill(ASICData[0],ASICData[1])
					ASIC["isValidData"].Fill(timeSlice)
				if(ASICData[2]):
					ASIC["isMultiHit"].Fill(timeSlice)
		for iter,ASIC in enumerate(ASICList):
			makePlot(ASIC,iter+1,eventNum,saveAs)




		


