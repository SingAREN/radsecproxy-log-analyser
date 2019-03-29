import datetime
import csv
import os


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

    def save_csv(self, file_path, date):
        """Save the extracted data into a separate CSV file logging number of requests hourly"""
        csv_list = []
        month_words = date.strftime('%b')
        csv_date = date.strftime('%d%b%y')

        if os.path.isfile(file_path) and os.path.getsize(file_path) > 0:
            # Check if file is non-zero and exists, then open to get csv_list
            with open(file_path, 'r') as csv_file:
                reader = csv.reader(csv_file)
                print("Reading {} file".format(file_path))
                for row in reader:
                    csv_list.append(row)
        else:
            with open(file_path, 'w') as csv_file:
                print("Creating new {} file" .format(file_path))
            csv_row = ["Date", "Month", "Hour", "Requests", "Category"]
            csv_list.append(csv_row)
        csv_list = [row for row in csv_list if row != []]
        last_checked = csv_list[-1:][0]
        # Check for duplicate entry and delete
        if not(csv_date != last_checked and last_checked == 'Date'):
            # Filter away the entries where the first element is the current date
            csv_list = [row for row in csv_list if csv_date not in row and row != []]
            print("Filtered!")

        for hour, count in enumerate(self.accepts):
            csv_list.append([csv_date, month_words, datetime.time(hour=hour).strftime("%X"), count, "Accepted"])

        for hour, count in enumerate(self.rejects):
            csv_list.append([csv_date, month_words, datetime.time(hour=hour).strftime("%X"), count, "Rejected"])

        # Then write back to csv file
        with open(file_path, 'w') as csv_file:
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


def analysis(csv_file_path, current_date):
    """ Testing full program. Check and set the day for specific date"""
    year = current_date.strftime('%Y')
    file_date = current_date.strftime("%Y%m%d")
    # Comment below when using batchfile, check the filepath before running- IMPORTANT!
    # 1.Initialise serverLoad for checking number of authentication requests
    total = ServerLoad()
    # 2.Do Log Extract
    print("Opening radsecproxy.log-{}".format(file_date))

    with open("./logs/radsecproxy.log-{}".format(file_date), "r") as log_data:
        total.log_extract(log_data)

    print("Number of accepted requests by hour: {}".format(total.accepts))
    print("Number of rejected requests by hour: {}".format(total.rejects))
    print("Total number of accepted requests: {}".format(sum(total.accepts)))
    print("Total number of rejected requests: {}".format(sum(total.rejects)))

    # 3. Save to CSV files
    csv_file = os.path.join(csv_file_path, 'ServerLoad{}.csv'.format(year))
    total.save_csv(csv_file, current_date)
    print("Saved to CSV!")
