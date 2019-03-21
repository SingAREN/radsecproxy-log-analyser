import os

class IHL(object):
    """ Defines a IHL with its constituent unique user files and properties like IP addresses etc"""
    def __init__(self, name, ipAddress=None,server=None, filepath="uniqueUsersFiles/"):
        self.name= name
        self.ipAddress= ipAddress
        self.server= server
        self.filepath= filepath
        self.userRecordsMonth=set()
        self.userRecordsYear=set()
        self.rejectRecordsMonth=set()
        self.rejectRecordsYear=set()
        ## Rejected and Accepted Count for the day
        self.reject_localUsers=0
        self.reject_visitors=0
        self.localUsers=0
        self.visitors=0
        # localUsersCount: contains localUsers of a ihl currently at each ihl and overseas
        # Example: localUsersCount={'eltr':12,'nie':2,'ntu':33,'nus':16} etc
        self.localUsersCount= dict()
        # localVisitors: contains the visitors from local IHLs accessing eduroam at the specific ihl
        self.localvisitors=0

    def readUniqueUserFiles(self, month, year):
        """ Open and read the unique user files associated with the IHL """
        self.userRecordsMonth= set(self.readFile(self.filepath+"UniqueUsers"+self.name+".log_"+month+year))
        print("Opened %s monthly unique user file" %(self.name))
        self.userRecordsYear= set(self.readFile(self.filepath+"UniqueUsers"+self.name+".log_"+year))
        print("Opened %s yearly unique user file" %(self.name))
        self.rejectRecordsMonth= set(self.readFile(self.filepath+"rejectUniqueUsers"+self.name+".log_"+month+year))
        print("Opened %s monthly rejectunique user file" %(self.name))
        self.rejectRecordsYear= set(self.readFile(self.filepath+"rejectUniqueUsers"+self.name+".log_"+year))
        print("Opened %s yearly rejectunique user file" %(self.name))

    def readFile(self, filename):
        """ Read a single unique user file, then save in records"""
        records=[]
        if(os.path.isfile(filename)):
            ## Open existing file and save its contents into records
            userfile= open(filename,'r')
            filelines=set(userfile.read().split('\n'))
            records= set(item.strip() for item in filelines if item !='')
        else:
            userfile=open(filename,'w')
        userfile.close()
        return records

    def writeUniqueUserFiles(self, month, year):
        """ Write all the associated unique users back to the unique user files"""
        self.writeFile(self.filepath+"UniqueUsers"+self.name+".log_"+month+year, self.userRecordsMonth)
        print("Written to %s monthly unique user file"%(self.name))
        self.writeFile(self.filepath+"UniqueUsers"+self.name+".log_"+year, self.userRecordsYear)
        print("Written to %s yearly unique user file"%(self.name))
        self.writeFile(self.filepath+"rejectUniqueUsers"+self.name+".log_"+month+year, self.rejectRecordsMonth)
        print("Written to %s monthly rejectunique user file"%(self.name))
        self.writeFile(self.filepath+"rejectUniqueUsers"+self.name+".log_"+year, self.rejectRecordsYear)
        print("Written to %s yearly rejectunique user file"%(self.name))

    def writeFile(self, filename, userRecords):
        """ Write userRecords into a single unique user file """
        userfile= open(filename, 'w')
        for user in userRecords:
            userfile.writelines(user+'\n')
        userfile.close()
    def getUniqueCountMonth(self):
        """ Get number of unique users from the IHL for the month"""
        return len(self.userRecordsMonth)
    def getUniqueCountYear(self):
        """ Get number of unique users from the IHL for the year"""
        return len(self.userRecordsYear)
    def getRejectUniqueCountMonth(self):
        """ Get number of reject unique users from the IHL for the month"""
        return len(self.rejectRecordsMonth)
    def getRejectUniqueCountYear(self):
        """ Get number of reject unique users from the IHL for the month"""
        return len(self.rejectRecordsYear)
    def getRejectCount(self):
        """ Get number of reject users from the IHL in total """
        return self.reject_localUsers+ self.reject_visitors
    def getLocalVisitors(self):
        """ Get the number of visitors from local IHLs accessing eduroam at this IHL"""
        return self.localvisitors