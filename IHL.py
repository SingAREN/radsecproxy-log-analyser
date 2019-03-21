import os


class IHL:
    """ Defines a IHL with its constituent unique user files and properties like IP addresses etc"""
    def __init__(self, name, ip_address=None, server=None, file_path="uniqueUsersFiles/"):
        self.name = name
        self.ipAddress = ip_address
        self.server = server
        self.filepath = file_path
        self.userRecordsMonth = set()
        self.userRecordsYear = set()
        self.rejectRecordsMonth = set()
        self.rejectRecordsYear = set()
        # Rejected and Accepted Count for the day
        self.reject_localUsers = 0
        self.reject_visitors = 0
        self.localUsers = 0
        self.visitors = 0
        # localUsersCount: contains localUsers of a ihl currently at each ihl and overseas
        # Example: localUsersCount={'eltr':12,'nie':2,'ntu':33,'nus':16} etc
        self.localUsersCount = dict()
        # localVisitors: contains the visitors from local IHLs accessing eduroam at the specific ihl
        self.localvisitors = 0

    def read_unique_user_files(self, month, year):
        """ Open and read the unique user files associated with the IHL """
        self.userRecordsMonth = set(self.read_file(self.filepath + "UniqueUsers" + self.name + ".log_" + month + year))
        print("Opened %s monthly unique user file" % self.name)
        self.userRecordsYear = set(self.read_file(self.filepath + "UniqueUsers" + self.name + ".log_" + year))
        print("Opened %s yearly unique user file" % self.name)
        self.rejectRecordsMonth = set(self.read_file(self.filepath + "rejectUniqueUsers" + self.name + ".log_" + month + year))
        print("Opened %s monthly rejectunique user file" % self.name)
        self.rejectRecordsYear = set(self.read_file(self.filepath + "rejectUniqueUsers" + self.name + ".log_" + year))
        print("Opened %s yearly rejectunique user file" % self.name)

    @staticmethod
    def read_file(filename):
        """ Read a single unique user file, then save in records"""
        records = []
        if os.path.isfile(filename):
            # Open existing file and save its contents into records
            user_file = open(filename, 'r')
            file_lines = set(user_file.read().split('\n'))
            records = set(item.strip() for item in file_lines if item != '')
        else:
            user_file = open(filename, 'w')
        user_file.close()
        return records

    def write_unique_user_files(self, month, year):
        """ Write all the associated unique users back to the unique user files"""
        self.write_file(self.filepath + "UniqueUsers" + self.name + ".log_" + month + year, self.userRecordsMonth)
        print("Written to %s monthly unique user file" % self.name)
        self.write_file(self.filepath + "UniqueUsers" + self.name + ".log_" + year, self.userRecordsYear)
        print("Written to %s yearly unique user file" % self.name)
        self.write_file(self.filepath + "rejectUniqueUsers" + self.name + ".log_" + month + year, self.rejectRecordsMonth)
        print("Written to %s monthly rejectunique user file" % self.name)
        self.write_file(self.filepath + "rejectUniqueUsers" + self.name + ".log_" + year, self.rejectRecordsYear)
        print("Written to %s yearly rejectunique user file" % self.name)

    @staticmethod
    def write_file(file_name, user_records):
        """ Write user_records into a single unique user file """
        user_file = open(file_name, 'w')
        for user in user_records:
            user_file.writelines(user+'\n')
        user_file.close()

    def get_unique_count_month(self):
        """ Get number of unique users from the IHL for the month"""
        return len(self.userRecordsMonth)

    def get_unique_count_year(self):
        """ Get number of unique users from the IHL for the year"""
        return len(self.userRecordsYear)

    def get_reject_unique_count_month(self):
        """ Get number of reject unique users from the IHL for the month"""
        return len(self.rejectRecordsMonth)

    def get_reject_unique_count_year(self):
        """ Get number of reject unique users from the IHL for the month"""
        return len(self.rejectRecordsYear)

    def get_reject_count(self):
        """ Get number of reject users from the IHL in total """
        return self.reject_localUsers + self.reject_visitors

    def get_local_visitors(self):
        """ Get the number of visitors from local IHLs accessing eduroam at this IHL"""
        return self.localvisitors
