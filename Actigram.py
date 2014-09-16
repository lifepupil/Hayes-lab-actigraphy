'''
Created on May 25, 2010
@author: Chris
for Hayes lab

An Actigram object is created for each baby.
Actigram methods are for the processing of 
that baby's raw actigram files.
'''

from os import listdir
from os.path import basename,dirname
from datetime import datetime,date,time,timedelta
from math import sqrt

class Actigram:
    ''' classdocs '''
    
    def __init__(self,dirPath):
        ''' constructor '''
        self.babyID = basename(dirPath) # pulls baby ID (directory name) from path
        self.sex = "" 
        self.dirPath = dirPath # full path to this baby's directory
        self.upDir = dirname(self.dirPath) # one directory level up from dirPath
        
        self.AWFpaths = [] # a list of full paths for each .AWF file in the directory  
        self.rawValues = [] # list of activity magnitude values used for storage and to get average and stdev
        self.timeStamps = [] # list of time stamps for time bins
        self.watchUsed = [] # list of activity magnitude values and actiwatch used
        self.zscores = [] # stores z-scores for each time bin in actigram
        self.FinneganScores = [] # stores Finnegan scores and associated timestamps
        self.overallAvg = 0
        self.sd = 0
        self.zeroCount = 0
        
        self.processedActigram = [] # used to hold tuples of actigram list data for writing to spreadsheet
        self.actigramIntervals = [] # event-delimited interval list converted from bin data
        
        ''' commands ''' 
        self.getAWFnames() # creates list of all .AWF files in this baby's directory
        self.processActigrams() # takes raw .AWF and creates time-stamped version, 
                                # generates actigram interval data from bin data, then
                                # calculates overall average and standard deviation for entire actigram
        self.createProcessedActigram()
        print self.babyID
        
    ''' getAWFnames function allows for multiple file processing '''
    def getAWFnames(self):
        # this function generates a list of paths to each file
        # containing actigraphy data (.AWF files) from a baby-specific directory. 
        # this function then returns a list used to open and process 
        # each of these files automatically, i.e. without user having to 
        # provide the name of each individual file to process. 
        fileNames = listdir(self.dirPath)
        fileNum = len(fileNames)
        fileExt = [".awf",".AWF",".AWD",".awd"]
        i = 0    
        while i < fileNum:
            thisExt = fileNames[i][-4:]
            if thisExt != fileExt[0] and \
            thisExt != fileExt[1] and \
            thisExt != fileExt[2] and \
            thisExt != fileExt[3]: # if file is NOT an .AWF file       
                del fileNames[i]
                fileNum = len(fileNames)
            else: # if file IS an .AWF file that has not already been added 
                fileNames[i] = self.dirPath + "/" + fileNames[i]
                if self.AWFpaths.count(fileNames[i]) == 0: # returns number of times fileNames[i] appears in path list
                    self.AWFpaths.append(fileNames[i])
                i = i + 1

    '''
    processActigrams creates list of tuples containing time stamp, activity magnitude and watch used,
    and also converts time-binned values into event-delimited time intervals. First calculates the 
    overall average magnitude and standard deviation in order to calculate z-scores for each time bin. 
    '''
    def processActigrams(self):        
        magnitudeSums = 0 # will be numerator for overall average
        totalBins = 0 # will be denominator for overall average
        zeroCount = 0
        headerItems = 6 # last element containing header information before actual data starts appearing        
        timeIncrement = timedelta(seconds=2) # used to add 2 seconds to current datetime object
        months = {'Jan':1,'Feb':2,'Mar':3,'Apr':4,'May':5,'Jun':6,'Jul':7,'Aug':8,'Sep':9,'Oct':10,'Nov':11,'Dec':12}
        
        # data are read out of files into various arrays for later processing in this FOR loop
        for thisAWF in range(len(self.AWFpaths)):
            file = open(self.AWFpaths[thisAWF],'r')            
            lineCounter = 0
            thisTime = 0
            
            print self.AWFpaths[thisAWF]
            for line in file:
                line = line.strip() # remove leading and trailing characters
                if lineCounter <= headerItems: # extracts useful information from actigram header                    
                    if lineCounter == 1: # date when actigram recording begins
                        if line != "":
                            dateParts = line.split('-')
                            yr = int(dateParts[2])
                            mon = int(months[dateParts[1]])
                            day = int(dateParts[0])
                            d = date(yr,mon,day)
                        else: d = date(1970,1,1)
                    elif lineCounter == 2: # time when actigram recording begins
                        if line != "":                        
                            timeParts = line.split(':')
                            hr = int(timeParts[0])
                            min = int(timeParts[1])
                            t = time(hr,min)
                            thisTime = datetime.combine(d,t)
                        else: thisTime = datetime.combine(d,time(0,0))
                    elif lineCounter == 5:# actiwatch used to gather actigram data
                        watch = line
                    elif lineCounter == 6: # sex of baby (may not be accurate and will overwrite if different)
                        self.sex = line
                    lineCounter = lineCounter + 1
                    
                else: # for lines that are passed the header
                    if line[-1] == "M": line = line[:-1]                        
                    value = int(line)
                    if value == 0: zeroCount = zeroCount + 1 # used to calculate the percentage of zeros in actigram
                    self.rawValues.append(value) # temporary storage for magnitudes found in raw actigram data file
                    magnitudeSums = magnitudeSums + value # for use generating average, stdev and z-scores
                    self.timeStamps.append(thisTime) # temporary storage for time stamps
                    thisTime = thisTime + timeIncrement # adds 2 seconds to current time stamp
                    self.watchUsed.append(watch)
                    
        totalBins = len(self.rawValues)
        if totalBins != 0: self.overallAvg = (magnitudeSums * 1.0) / totalBins
        if totalBins != 0: self.zeroCount = (zeroCount * 1.0) / totalBins
        
        sums = 0.0
        for s in range(totalBins): # loop for calculating standard deviation
            sums = sums + (self.rawValues[s] - self.overallAvg)**2
        self.sd = sqrt(float(sums / totalBins))
    
        for z in range(totalBins): # loop for calculating z-scores and writing all data to permanent arrays
            thisZ = (self.rawValues[z] - self.overallAvg) / self.sd
            self.zscores.append(thisZ)
            
        

    ''' createProcessedActigram collects processed actigram data into a single list '''
    def createProcessedActigram(self):
        for thisBin in range(len(self.rawValues)):
            self.processedActigram.append((self.timeStamps[thisBin],self.rawValues[thisBin],self.zscores[thisBin],self.watchUsed[thisBin]))
        

    ''' printBinLists takes a list of actigrams and writes them to an Excel spreadsheet, or at least a .CSV '''
    def  printBinLists(self):
        f = open(self.upDir+"/"+self.babyID+".csv","w")
        pA = self.processedActigram
        binNum = len(pA)        
        labels = "date,time,magnitude,z-score,actiwatch,zeros\n"
        
        f.write(labels)        
        for r in range(binNum): # loop that writes processed actigram data to CSV
            thisLine = str(pA[r][0].date())+","+str(pA[r][0].time())+","+str(pA[r][1])+","+str(pA[r][2])+","+str(pA[r][3])+"\n"
            f.write(thisLine)
        f.close()
                
    '''
    getActigramIntervals creates list of event-delimited intervals from time-binned actigraphy data
    '''                         
    def getActigramIntervals(self):
        upperLimit = 5000 # used as a filter for magnitudes too large to be from the baby (set at 5000 = no filtering)       
        binDuration = 2 # bin sizes are 2 seconds long
        intervalSum = 1 # used to store inter-event interval size in bin counts
        
        for thisBin in range(len(self.rawValues)):
            value = self.rawValues[thisBin] # magnitude recorded during this bin that was stored in this line
            if value == 0 or value > upperLimit: # part of magnitude filter to generate event-delimited time interval list 
                intervalSum = intervalSum + 1 # no activity recorded in this line so inter-event interval increases
            elif value > 0: # activity event was recorded
                self.intervals.append((intervalSum*binDuration)) 
                intervalSum = 1 # reinitializes interval length
                
                
            