'''
Created on Apr 2, 2010
@author: Chris

This program, along with the Actigram class, takes raw actigram data for each baby
and generates a spreadsheet file for that baby which contains a concatenation of 
those actigrams with a time- and date-stamp for each acceleration value, and the
z-score for that particular value based on the overall average of acceleration 
values for that baby alone. The activity watch used is also output into this
spreadsheet.

To run, make sure that the 'filePath' variable below is set to the folder containing 
all of the baby actigram folders. The file containing the Finnegan scores must 
also be at the same path and have a filename matching 'FinnFile' below. The
program will process all data put at this path properly provided that there is one
folder per baby, that the folder name is the babyID, and that the baby's .AWF actigram
files are stored in that folder.

The spreadsheets output from this program are written to the path specified by 'filePath'.

'''
from Actigram import Actigram
from os import listdir
from os.path import isdir
from xlwt import Workbook # this module is not native to Python and must be installed.
from xlrd import open_workbook,xldate_as_tuple # same with this module. http://www.python-excel.org/
from datetime import date,time,datetime

babies = [] # list to store Actigram objects for each baby
zeros = []

filePath = "C:/Users/Chris/Documents/Hayes lab/actigraphy/Actigraphy Summer 2009/Schizophrenia Actigraphy/Schizophrenics/"
#filePath = "C:/data/Actigraphy data/" # make sure this path goes to the spot where all of the raw actigram data for each baby are stored.
#filePath = "C:/data/actigram/" # make sure this path goes to the spot where all of the raw actigram data for each baby are stored.
FinnFile = "Finnegan data only.xls"

''' main calls all actigram methods '''
def main():    
    dirNames = getDirnames(filePath) # returns list of paths to all directories in filePath
#    fList = getFinnegansfromExcel() # 

    for d in range(len(dirNames)):
#        thisBabyFinnegans()
        babyActs = Actigram(dirNames[d]) # creates new actigram object and passes thisDir to name it        
#        babyActs.printBinLists() # writes results of actigraphy data analysis to a .CSV file  
        zeros.append((babyActs.babyID, babyActs.zeroCount))
        #babies.append(babyActs) # stores the new actigram object into a list
    writeZeros(zeros)
    print "DONE"
    

def getFinnegansfromExcel(): 
    # better version of this function will take dirNames as argument and
    # only pull out babyIDs that match those in dirNames
    Finnegans = open_workbook(filePath+FinnFile)
    f = Finnegans.sheet_by_index(0)
    lastRow = f.nrows        
    fArray = []
    
    for r in range(1,lastRow): # pulls date, time and the associated Finnigan from each row (i.e. - each observation)
        d = date(*xldate_as_tuple(f.cell(r,1).value, Finnegans.datemode)[:3])
        t = time(*xldate_as_tuple(f.cell(r,2).value, Finnegans.datemode)[3:])
        dt = datetime.combine(d,t)        
        fArray.append(((f.cell(r,0).value),dt))
    return fArray

    

''' getDirnames returns a list of all the directory names in the specified path '''
def getDirnames(filePath): # this function generates a list of paths for all directories found at the path passed to it 
    dirNames = []
    contents = listdir(filePath)
    for f in range(len(contents)):
        thisItem = filePath+contents[f]
        if isdir(thisItem) == True: dirNames.append(thisItem) # filters out any non-directory contents
        # IMPORTANT NOTE: the above line assumes that only folders with babyIDs will be in target path
    return dirNames

def writeZeros(zeros):
    f = open(filePath+"percentZeros.csv","w")
    binNum = len(zeros)        
        
    for r in range(binNum): # loop that writes processed actigram data to CSV
        thisLine = str(zeros[r][0])+","+str(zeros[r][1])+"\n"
        f.write(thisLine)
    f.close()



''' printIntervals takes a list of actigrams and writes them to an Excel spreadsheet 
    as long as no more than 65536 rows are written '''
def  printIntervals(list): # this function is only used to put actigram data into a format that can be processed using C.Richard's M.S. thesis software
    upperLimit = 5000
    wb = Workbook()
    ws = wb.add_sheet('INTERVALS') # labels worksheet as 'INTERVALS' 
    flagID = 0.0003 # translates into food pellet delivery event for use in meal analysis VBA     
    for c in range(len(list)): # c is for columns, cookie monster is incorrect
        ws.row(0).write(c,list[c][0])
        ws.row(1).write(c,list[c][1])             
        for r in range(2,len(list[c])): # r is row index
            val = int(list[c][r]) + flagID # val is inter-event interval length value
            ws.row(r).write(c,val)
    fname = "INTERVALS-upperlimit="+str(upperLimit)+".xls" # fname = filename 
    wb.save(filePath+fname)

#    addc = 0
#    modr = 0
#    wb = Workbook()
#    ws = wb.add_sheet('BINS') # labels worksheet as 'BINS' 
#    print len(list)," ",len(list[0])
#    for r in range(len(list)):
#        if r > 65535:
#            modr = r - 65535
#            addc = addc + 4
#        else: modr = r
#        for c in range(len(list[r])):
##            print list[r][c]
#            if c == 0:
#                ws.row(modr).set_cell_date(c+addc,list[r][c])          
#            else:
#                ws.row(modr).write(c+addc,list[r][c])
#
#    fname = "BINS-upperlimit="+str(upperLimit)+".xls" # fname = filename 
#    wb.save(filePath+fname)


main()
        
#if __name__ == '__main__':
#    pass