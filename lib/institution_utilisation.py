import json
import csv
from lib.IHL import *


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


def results(ihl_array, file_name):
    """ Keep the results in a daily log file with date attached to it. """
    result = open(file_name, "w")
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
        result.write("Total number of unique users this month to %s : %d \n" % (ihl_array[ihl].name, ihl_array[ihl].get_unique_count_month()))
        result.write("Total number of rejectUnique users this month to %s : %d \n" % (ihl_array[ihl].name, ihl_array[ihl].get_reject_unique_count_month()))
        result.write("Total number of unique users this year to %s : %d \n" % (ihl_array[ihl].name, ihl_array[ihl].get_unique_count_year()))
        result.write("Total number of rejectUnique users this year to %s : %d \n\n" % (ihl_array[ihl].name, ihl_array[ihl].get_reject_unique_count_year()))
    
    for ihl in ihl_array:
        result.write("Total number of rejected from %s for the day: %d \n" % (ihl_array[ihl].name, ihl_array[ihl].get_reject_count()))
    result.close()
    print('Results.txt closed')


def is_non_zero_file(fpath):
    """Check if file exists and is not empty"""
    return True if os.path.isfile(fpath) and os.path.getsize(fpath) > 0 else False


def save_csv(ihl_array, file_name, interval, previous_date):
        """Save the extracted data into daily, monthly and yearly CSV files for data visualisation"""
        csv_list = []
        day = previous_date.strftime('%d')
        month_words = previous_date.strftime('%b')
        year = previous_date.strftime('%Y')
        year_2numbers = previous_date.strftime('%y')

        if is_non_zero_file(file_name):
            # Open the file first and get csv_list
            with open(file_name, 'r') as csv_file:
                reader = csv.reader(csv_file)
                print('Reading {} file'.format(file_name))
                for row in reader:
                    csv_list.append(row)
        else:
            with open(file_name, 'w') as csv_file:
                print("Creating new {} file".format(file_name))
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
                csv_list.append([date, ihl_array[ihl].name, ihl_array[ihl].get_reject_count(), "Rejected"])
        if interval == 'Month':
            # Check for duplicate month entry and delete
            if not(month_words != last_checked and last_checked == 'Month'):
                # Filter away the entries where the first element is the current month
                csv_list = [row for row in csv_list if month_words not in row]
            for ihl in ihl_array:
                csv_list.append([month_words, ihl_array[ihl].name, ihl_array[ihl].get_unique_count_month(),
                                 "Accepted"])
                csv_list.append([month_words, ihl_array[ihl].name, ihl_array[ihl].get_reject_unique_count_month(),
                                 "Rejected"])
        if interval == 'Year':
            # Check for duplicate year entry and delete
            if not(year != last_checked and last_checked == 'Year'):
                # Filter away the entries where the first element is the current year
                csv_list = [row for row in csv_list if year not in row]
            for ihl in ihl_array:
                csv_list.append([year, ihl_array[ihl].name, ihl_array[ihl].get_unique_count_year(), "Accepted"])
                csv_list.append([year, ihl_array[ihl].name, ihl_array[ihl].get_reject_unique_count_year(), "Rejected"])
        csv_list = [row for row in csv_list if row != []]
        # Then write back to csv file
        with open(file_name, 'w') as csv_file:
            writer = csv.writer(csv_file)
            writer.writerows(csv_list)


def analysis(statistics_directory, csv_directory, ihl_config_file_path, current_date):
    """
    Defines the main conversion process. Instantiates the class IHL for each institute
    nd calls the other functions for processing.
    :return:
    """

    month = current_date.strftime('%m')
    month_words = current_date.strftime('%b')
    year = current_date.strftime('%Y')
    file_date = current_date.strftime("%Y%m%d")

    # Load config file from ihlconfig.json which contains details of the IHLs.
    config = json.load(open(ihl_config_file_path))

    # Load Server name and IP Address for the Euro Top-Level RADIUS Servers
    etlr_server = config['etlr']['server']
    etlr_ip = config['etlr']['ip']
    
    # 1. Load the IHLs' details, their Unique Users file into unique Records
    ihl_array = dict()
    for institution in config:
        if institution != 'etlr':
            ihl_array[institution] = IHL(institution.upper(), config[institution]['ip'], config[institution]['server'])

    # Read UniqueUsers Files for all the IHLs
    for institution in ihl_array:
        ihl_array[institution].read_unique_user_files(month, year)
    print("Finished adding users from each uniqueUser file for each IHL")

    # Initialise localUsers from institution at other places and logExtract variables
    for institution in ihl_array:
        # 1 element for each institution in the stats for the institution's localUsersCount
        for ihl_name in config:
            ihl_array[institution].localUsersCount[ihl_name] = 0
        print("{}: {}".format(ihl_array[institution].name, ihl_array[institution].localUsersCount))
        
    # 2.Do Log Extract - Code logic at Line 8
    print("Opening radsecproxy.log-{}".format(file_date))
    with open("./logs/radsecproxy.log-{}".format(file_date), "r") as log_data:
        log_extract(log_data, ihl_array, etlr_server, etlr_ip)

    # 3. Writing back to uniqueUserFiles
    for institution in ihl_array:
        ihl_array[institution].write_unique_user_files(month, year)
    print("Finished writing to each uniqueUser file for all the IHLs")
    
    # 4. Write to results file - Code logic at line 80
    results(ihl_array, os.path.join(statistics_directory, 'results.log_{}'.format(file_date)))

    # 5. Save to CSV files(Daily, Monthly, Yearly) - saveCSV(FileInterval) Code logic at line 106
    daily_csv = os.path.join(csv_directory, 'Daily{}{}.csv'.format(month_words, year))
    monthly_csv = os.path.join(csv_directory, 'Monthly{}.csv'.format(year))
    yearly_csv = os.path.join(csv_directory, 'Yearly.csv')

    save_csv(ihl_array, daily_csv, 'Day', current_date)
    save_csv(ihl_array, monthly_csv, 'Month', current_date)
    save_csv(ihl_array, yearly_csv, 'Year', current_date)
    print("Saved to CSV files!")
