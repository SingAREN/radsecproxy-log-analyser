import datetime
import csv
import os
import sys

class serverLoad:
    """Internal class used for checking the request load of the singAren eduroam server"""
    def __init__(self):
        """Initialises the accepted and rejected lists for 24 hours"""
        self.accepts=[0]*24
        self.rejects=[0]*24
    def update(self,array,time):
        """Updates the list elements for every hour of the log to collect the number of requests for that time period"""
        timeArray= time.split(":")
        try:
            hour=int(timeArray[0])
            array[hour]+=1
        except ValueError:
            print('Malformed log line. Skipping...')

    def saveCSV(self,filename,date):
        """Save the extracted data into a separate CSV file logging number of requests hourly"""
        csvlist=[]
        day= date.strftime('%d')
        month= date.strftime('%m')
        month_words= date.strftime('%b')
        year= date.strftime('%Y')
        year_2numbers=date.strftime('%y')
        if (os.path.isfile(filename+'.csv') and os.path.getsize(filename+'.csv') > 0):
        #Check if file is non-zero and exists, then open to get csv_list
            with open(filename+'.csv','r') as csvfile:
                reader = csv.reader(csvfile)
                print("Reading the "+filename+".csv file")
                for row in reader:
                    csvlist.append(row)
        else:
            with open(filename+'.csv','w') as csvfile:
                print("Creating new "+filename+".csv file")
            csvrow=["Date","Month","Hour","Requests","Category"]
            csvlist.append(csvrow)
        csvlist=[row for row in csvlist if row!=[]]
        last_checked=csvlist[-1:][0]
        date="".join([day,month_words,year_2numbers])
        #Check for duplicate entry and delete
        if not(date != last_checked and last_checked=='Date'):
            #Filter away the entries where the first element is the current date
            csvlist=[row for row in csvlist if date not in row and row!=[]]
            print("Filtered!")
        for i in range(len(self.accepts)):
            csvlist.append([date,month_words,datetime.time(hour=i).strftime("%X"),self.accepts[i],"Accepted"])
        for i in range(len(self.rejects)):    
            csvlist.append([date,month_words,datetime.time(hour=i).strftime("%X"),self.rejects[i],"Rejected"])
        #Then write back to csv file
        with open(filename+'.csv', 'w') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerows(csvlist)    
        print("Saved to Request Log CSV!")
        
    def logExtract(self,logData):
        """ Defines the logic in extracting the information from the log file"""
        for line in logData:
            ## check if user access is accepted or rejected, re.I ignores cases, re.M goes from start of string to end of string(multiline)
            match_accept = 'Accept for user' in line
            match_reject = 'Reject for user' in line
            time = line.split()[2].strip()

            if matchReject:
                ## Access is rejected for the user
                self.update(self.rejects, time)
            if matchAccept:
                ## Access is accepted for the user
                self.update(self.accepts, time)
            
def main():                
    """ Testing full program. Check and set the day for specific date"""
    ## Since datetime is a built-in module, can just use its properties to get previous day's date.
    #Comment below when you use batchfile sys.argv
    #previous_date= datetime.date(day=12, month=6, year=2015)
    previous_date = datetime.date.today() - datetime.timedelta(1)
    #previous_date = datetime.date(year=2015, month=6, day=1)
    ####uncomment below for use with batchfile only. Example arg: 021215 ### 
    # log_file = open("radsecproxy.log_"+str(sys.argv[1]),"r")
    # print ("radsecproxy.log_"+str(sys.argv[1]))
    # datestring=str(sys.argv[1])
    # previous_date= datetime.date(day=int(datestring[0:2]),month=int(datestring[2:4]),year=(2000+int(datestring[4:6])))
    
    year = previous_date.strftime('%Y')
    file_date = previous_date.strftime("%Y%m%d")
    ## Comment below when using batchfile, check the filepath before running- IMPORTANT!
    log_file = open("./logs/radsecproxy.log-{}".format(file_date),"r")
    print ("Opening radsecproxy.log-{}".format(file_date))
    
    #Save all info from log file into a list of lines named logData(for LogExtract)
    logData = log_file.readlines()
    log_file.close()
    ## 1.Initialise serverLoad for checking number of authentication requests
    total = serverLoad()
    ## 2.Do Log Extract
    total.logExtract(logData)
    print("Number of accepted requests by hour: {}".format(total.accepts))
    print("Number of rejected requests by hour: {}".format(total.rejects))
    print("Total number of accepted requests: {}".format(sum(total.accepts)))
    print("Total number of rejected requests: {}".format(sum(total.rejects)))

    ## 3. Save to CSV files
    total.saveCSV("csv/ServerLoad"+year,previous_date)
    print("Saved to CSV!")


""" Allows execution of main convert function if run as a script"""    
if __name__ == '__main__':
    main()
