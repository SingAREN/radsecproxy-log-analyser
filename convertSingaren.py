import datetime
import csv
import os
import argparse


class ServerLoad:
    """Internal class used for checking the request load of the singAren eduroam server"""
    def __init__(self):
        """Initialises the accepted and rejected lists for 24 hours"""
        self.accepts = [0]*24
        self.rejects = [0]*24

    @staticmethod
    def update_hour_array(array, time):
        """Updates the list elements for every hour of the log to collect the number of requests for that time period"""
        time_array = time.split(":")
        try:
            hour = int(time_array[0])
            array[hour] += 1
        except ValueError:
            print('Malformed log line. Skipping...')

    def save_csv(self, filename, date):
        """Save the extracted data into a separate CSV file logging number of requests hourly"""
        csv_list = []
        month_words = date.strftime('%b')
        csv_date = date.strftime('%d%b%y')

        if os.path.isfile(filename+'.csv') and os.path.getsize(filename+'.csv') > 0:
        # Check if file is non-zero and exists, then open to get csv_list
            with open(filename+'.csv', 'r') as csv_file:
                reader = csv.reader(csv_file)
                print("Reading the {}.csv file".format(filename))
                for row in reader:
                    csv_list.append(row)
        else:
            with open(filename+'.csv', 'w') as csv_file:
                print("Creating new {}.csv file" .format(filename))
            csv_row = ["Date", "Month", "Hour", "Requests", "Category"]
            csv_list.append(csv_row)
        csv_list = [row for row in csv_list if row != []]
        last_checked = csv_list[-1:][0]
        # Check for duplicate entry and delete
        if not(csv_date != last_checked and last_checked == 'Date'):
            # Filter away the entries where the first element is the current date
            csv_list = [row for row in csv_list if csv_date not in row and row != []]
            print("Filtered!")
            print(self.accepts)

        for hour, count in enumerate(self.accepts):
            csv_list.append([csv_date, month_words, datetime.time(hour=hour).strftime("%X"), count, "Accepted"])

        for hour, count in enumerate(self.rejects):
            csv_list.append([csv_date, month_words, datetime.time(hour=hour).strftime("%X"), count, "Rejected"])

        # Then write back to csv file
        with open(filename+'.csv', 'w') as csv_file:
            writer = csv.writer(csv_file)
            writer.writerows(csv_list)
        print("Saved to Request Log CSV!")
        
    def log_extract(self, log_data):
        """ Defines the logic in extracting the information from the log file"""
        for line in log_data:
            # check if user access is accepted or rejected
            match_accept = 'Accept for user' in line
            match_reject = 'Reject for user' in line

            try:
                time = line.split()[2].strip()
            except IndexError:
                # Skips blank line
                continue

            if match_reject:
                # Access is rejected for the user
                self.update_hour_array(self.rejects, time)
            if match_accept:
                # Access is accepted for the user
                self.update_hour_array(self.accepts, time)


def server_load_analyser(start_date, end_date):
    """ Testing full program. Check and set the day for specific date"""
    ## Since datetime is a built-in module, can just use its properties to get previous day's date.
    # Comment below when you use batchfile sys.argv
    current_date = start_date
    while current_date <= end_date:
        year = current_date.strftime('%Y')
        file_date = current_date.strftime("%Y%m%d")
        # Comment below when using batchfile, check the filepath before running- IMPORTANT!
        # 1.Initialise serverLoad for checking number of authentication requests
        total = ServerLoad()
        # 2.Do Log Extract
        print("Opening radsecproxy.log-{}".format(file_date))
        try:
            with open("./logs/radsecproxy.log-{}".format(file_date), "r") as log_data:
                total.log_extract(log_data)
        except FileNotFoundError as error:
            print(error)
            current_date += datetime.timedelta(1)
            continue

        print("Number of accepted requests by hour: {}".format(total.accepts))
        print("Number of rejected requests by hour: {}".format(total.rejects))
        print("Total number of accepted requests: {}".format(sum(total.accepts)))
        print("Total number of rejected requests: {}".format(sum(total.rejects)))

        # 3. Save to CSV files
        total.save_csv("csv/ServerLoad{}".format(year), current_date)
        print("Saved to CSV!")
        current_date += datetime.timedelta(1)


def valid_date(date_input):
    try:
        return datetime.datetime.strptime(str(date_input), '%Y%m%d').date()
    except ValueError:
        print('Ignoring input as \'{}\' is not a valid date.'.format(date_input))
        return None


""" Allows execution of main convert function if run as a script"""    
if __name__ == '__main__':
    default_date = datetime.date.today() - datetime.timedelta(1)
    start = default_date
    end = default_date

    parser = argparse.ArgumentParser(prog='radsecproxy Server Load Analyser')
    parser.add_argument('--start_date', '-s', help='Start date in %Y%m%d format, e.g. 20190204', type=valid_date)
    parser.add_argument('--end_date', '-e', help='End date in %Y%m%d format, e.g. 20190228. '
                                                 'Use with --start_date flag.', type=valid_date)
    arguments = parser.parse_args()

    if arguments.start_date:
        start = arguments.start_date
    # Sets end date if valid date exists from parsed arguments and if said date is not in the future.
    if arguments.end_date:
        if not arguments.start_date:
            print('No start date provided... Setting end date as default date: {}'.format(default_date))
            end = default_date
        if arguments.end_date < default_date:
            end = arguments.end_date

    if start > end:
        raise ValueError('Start date is ahead of end date')

    server_load_analyser(start, end)
