import datetime
import json
import csv
from IHL import *


def log_extract(log_data, ihl_array, euro_tlr_server, euro_tlr_ip):
    """ Defines the logic in extracting the information from the log file"""
    daily_accept_records = set()
    daily_reject_records = set()
    # ihl_name_list: List of institutes of higher learning (IHL) in the within the logs
    ihl_name_list = list(ihl_array.keys())

    for line in log_data:
        # Checks for either Access-Accept or Access-Reject RADIUS Response logs
        match_accept = 'Access-Accept for user' in line
        match_reject = 'Access-Reject for user' in line

        # Continues to next log line if no Accept/Reject matches are found
        if not match_accept and not match_reject:
            continue

        tokens = line.split()
        # Extracts specific info from the logfile, coming_from - identity provider, going_to - service provider
        user, coming_from, going_to = [tokens[tokens.index(value) + 1] for value in ['user', 'from', 'to']]

        if match_reject:
            # Access is rejected for the user
            if user not in daily_reject_records:
                daily_reject_records.add(user)
                # visitors TRAFFIC FOR ALL IHL
                # Overseas users using their accounts in IHL
                if coming_from in euro_tlr_server:
                    for ihl in ihl_array:
                        if going_to in ihl_array[ihl].ipAddress:
                            ihl_array[ihl].reject_visitors += 1
                            ihl_array[ihl].rejectRecordsMonth.add(user)
                            ihl_array[ihl].rejectRecordsYear.add(user)

                # Handle all the local IHLs
                else:
                    for ihl in ihl_array:
                        # Coming from any IHL and going to etlr1 or etlr2
                        if coming_from in ihl_array[ihl].server:
                            if not (going_to in ihl_array[ihl].ipAddress):
                                ihl_array[ihl].reject_localUsers += 1
                                ihl_array[ihl].rejectRecordsMonth.add(user)
                                ihl_array[ihl].rejectRecordsYear.add(user)
            continue

        # Access-Accept for the user
        if user not in daily_accept_records:
            daily_accept_records.add(user)
            # visitors TRAFFIC FOR ALL IHL
            # Overseas users using their accounts in IHL
            if coming_from in euro_tlr_server:
                for ihl in ihl_array:
                    if going_to in ihl_array[ihl].ipAddress:
                        ihl_array[ihl].visitors += 1
                        ihl_array[ihl].userRecordsMonth.add(user)
                        ihl_array[ihl].userRecordsYear.add(user)
            # Handle all the local IHLs
            else:
                for ihl in ihl_array:
                    if coming_from in ihl_array[ihl].server:
                        if not (going_to in ihl_array[ihl].ipAddress):
                            ihl_array[ihl].userRecordsMonth.add(user)
                            ihl_array[ihl].userRecordsYear.add(user)
                            if going_to in euro_tlr_ip:
                                ihl_array[ihl].localUsersCount['etlr'] += 1
                            else:
                                for i in ihl_name_list:
                                    if going_to in ihl_array[i].ipAddress:
                                        ihl_array[ihl].localUsersCount[i] += 1
                                        ihl_array[i].localvisitors += 1

    # Get total count of local users and visitors for each ihl
    for ihl in ihl_array:
        ihl_array[ihl].localUsers = sum(ihl_array[ihl].localUsersCount.values())
        ihl_array[ihl].visitors = ihl_array[ihl].visitors + ihl_array[ihl].localvisitors
        print("{}: {}".format(ihl_array[ihl].name, ihl_array[ihl].localUsersCount))


def results(ihl_array, filename):
    """ Keep the results in a daily log file with date attached to it. """
    result = open(filename, "w")
    print("Writing to Results.txt")
    # ihl_name_list: List of institutes of higher learning (IHL) in the within the logs

    ihl_name_list = list(ihl_array.keys())
    for ihl in ihl_array:
        result.write("Total number of localUsers from %s who are abroad : %d \n" % (ihl_array[ihl].name, ihl_array[ihl].localUsersCount['etlr']))
        for i in ihl_name_list:
            if i != ihl:
                result.write("Total number of localUsers from %s in %s : %d \n" % (ihl_array[ihl].name, i.upper(), ihl_array[ihl].localUsersCount[i]))
        result.write("Total number of localUsers from %s in total: %d \n \n" % (ihl_array[ihl].name, ihl_array[ihl].localUsers))
        result.write("Total number of visitors to %s : %d \n \n" % (ihl_array[ihl].name, ihl_array[ihl].visitors))
    for ihl in ihl_array:
        result.write("Total number of unique users this month to %s : %d \n" % (ihl_array[ihl].name, ihl_array[ihl].getUniqueCountMonth()))
        result.write("Total number of rejectUnique users this month to %s : %d \n" % (ihl_array[ihl].name, ihl_array[ihl].getRejectUniqueCountMonth()))
        result.write("Total number of unique users this year to %s : %d \n" % (ihl_array[ihl].name, ihl_array[ihl].getUniqueCountYear()))
        result.write("Total number of rejectUnique users this year to %s : %d \n\n" % (ihl_array[ihl].name, ihl_array[ihl].getRejectUniqueCountYear()))
    
    for ihl in ihl_array:
        result.write("Total number of rejected from %s for the day: %d \n" % (ihl_array[ihl].name, ihl_array[ihl].getRejectCount()))
    result.close()
    print('Results.txt closed')


def is_non_zero_file(fpath):
    """Check if file exists and is not empty"""
    return True if os.path.isfile(fpath) and os.path.getsize(fpath) > 0 else False


def save_csv(ihl_array, filename, interval, previous_date):
        """Save the extracted data into daily, monthly and yearly CSV files for data visualisation"""
        csv_list = []
        day = previous_date.strftime('%d')
        month_words = previous_date.strftime('%b')
        year = previous_date.strftime('%Y')
        year_2numbers = previous_date.strftime('%y')

        if is_non_zero_file(filename+'.csv'):
            # Open the file first and get csv_list
            with open(filename+'.csv', 'r') as csv_file:
                reader = csv.reader(csv_file)
                print("Reading the "+filename+".csv file")
                for row in reader:
                    csv_list.append(row)
        else:
            with open(filename+'.csv', 'w') as csv_file:
                print("Creating new {}.csv file".format(filename))
            csv_row = []
            if interval == 'Day':
                csv_row = ["Date", "IHL", "Users", "Category"]
            if interval == 'Month':
                csv_row = ["Month", "IHL", "UniqueUsers", "Category"]
            if interval == 'Year':
                csv_row = ["Year", "IHL", "UniqueUsers", "Category"]
            csv_list.append(csv_row)
        last_checked = csv_list[-1:][0]
        if interval == 'Day':
            date = day+month_words+year_2numbers
            # Check for duplicate daily entry and delete
            if not(date != last_checked and last_checked == 'Date'):
                # Filter away the entries where the first element is the current month
                csv_list = [row for row in csv_list if date not in row]
            for ihl in ihl_array:
                csv_list.append([date, ihl_array[ihl].name, ihl_array[ihl].localUsers, "LocalUsers"])
                csv_list.append([date, ihl_array[ihl].name, ihl_array[ihl].visitors, "Visitors"])
                csv_list.append([date, ihl_array[ihl].name, ihl_array[ihl].getRejectCount(), "Rejected"])
        if interval == 'Month':
            # Check for duplicate month entry and delete
            if not(month_words != last_checked and last_checked=='Month'):
                # Filter away the entries where the first element is the current month
                csv_list = [row for row in csv_list if month_words not in row]
            for ihl in ihl_array:
                csv_list.append([month_words, ihl_array[ihl].name, ihl_array[ihl].getUniqueCountMonth(),
                                 "Accepted"])
                csv_list.append([month_words, ihl_array[ihl].name, ihl_array[ihl].getRejectUniqueCountMonth(),
                                 "Rejected"])
        if interval == 'Year':
            # Check for duplicate year entry and delete
            if not(year != last_checked and last_checked == 'Year'):
                # Filter away the entries where the first element is the current year
                csv_list = [row for row in csv_list if year not in row]
            for ihl in ihl_array:
                csv_list.append([year, ihl_array[ihl].name, ihl_array[ihl].getUniqueCountYear(), "Accepted"])
                csv_list.append([year, ihl_array[ihl].name, ihl_array[ihl].getRejectUniqueCountYear(), "Rejected"])
        csv_list = [row for row in csv_list if row != []]
        # Then write back to csv file
        with open(filename+'.csv', 'w') as csv_file:
            writer = csv.writer(csv_file)
            writer.writerows(csv_list)


def main():
    """
    Defines the main conversion process. Instantiates the class IHL for each institute
    nd calls the other functions for processing.
    :return:
    """
    # Since datetime is a built-in module, can just use its properties to get previous day's date.
    # Comment the previous_date below when you use batchfile sys.argv
    previous_date = datetime.date.today() - datetime.timedelta(1)
    # previous_date = datetime.date(day=1, month=6, year=2015)
    
    # uncomment !SS! below for use with batchfile only. Example arg: 021215 ###
    # !SS!log_file = open("/home/eduroam_stat/old-stat/radsecproxy.log_"+str(sys.argv[1]),"r")
    # !SS!print ("radsecproxy.log_"+str(sys.argv[1]))
    # !SS!datestring=str(sys.argv[1])
    # !SS!previous_date = datetime.date(day=int(datestring[0:2]),month=int(datestring[2:4]),year=2000+int(datestring[4:6]))

    day = previous_date.strftime('%d')
    month = previous_date.strftime('%m')
    month_words = previous_date.strftime('%b')
    year = previous_date.strftime('%Y')
    year_2numbers = previous_date.strftime('%y')
    file_date = previous_date.strftime("%Y%m%d")

    # Comment below when using batchfile, check the filepath before running- IMPORTANT!
    log_file = open("./logs/radsecproxy.log-{}".format(file_date), "r")
    print("Opening radsecproxy.log-{}".format(file_date))
    
    # Save all info from log file into a list of lines named log_data(for LogExtract)
    log_data = log_file.readlines()
    log_file.close()
    # Load config file from ihlconfig.json which contains details of the IHLs.
    config = json.load(open('./ihlconfig.json'))
    # Load Server name and IP Address for the Euro Top-Level RADIUS Servers
    etlr_server = config['etlr']['server']
    etlr_ip = config['etlr']['ip']
    
    # 1. Load the IHLs' details, their Unique Users file into unique Records
    ihl_array = dict()
    for ihl in config:
        if ihl != 'etlr':
            ihl_array[ihl] = IHL(ihl.upper(), config[ihl]['ip'], config[ihl]['server'])
    # Read UniqueUsers Files for all the IHLs
    for ihl in ihl_array:
        ihl_array[ihl].readUniqueUserFiles(month,year_2numbers)
    print("Finished adding users from each uniqueUser file for each IHL")
    # Initialise localUsers from ihl at other places and logExtract variables
    for ihl in ihl_array:
        # 1 element for each ihl in the stats for the ihl's localUsersCount
        for ihl_name in config:
            ihl_array[ihl].localUsersCount[ihl_name] = 0
        print("{}: {}".format(ihl_array[ihl].name, ihl_array[ihl].localUsersCount))
        
    # 2.Do Log Extract - Code logic at Line 8
    log_extract(log_data, ihl_array, etlr_server, etlr_ip)

    # 3. Writing back to uniqueUserFiles
    for ihl in ihl_array:
        ihl_array[ihl].writeUniqueUserFiles(month, year_2numbers)
    print("Finished writing to each uniqueUser file for all the IHLs")
    
    # 4. Write to results file - Code logic at line 80
    results(ihl_array, "Stats_results/results.log_"+day+month+year_2numbers)

    # 5. Save to CSV files(Daily, Monthly, Yearly) - saveCSV(FileInterval) Code logic at line 106
    save_csv(ihl_array, 'csv/Daily' + month_words + year, 'Day', previous_date)
    save_csv(ihl_array, 'csv/Monthly' + year, 'Month', previous_date)
    save_csv(ihl_array, 'csv/Yearly', 'Year', previous_date)
    print("Saved to CSV files!")


""" Allows execution of main convert function if run as a script"""    
if __name__ == '__main__':
    main()
