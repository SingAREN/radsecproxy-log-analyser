import argparse
import datetime
from lib import users_and_institutions, server_load


def valid_date(date_input):
    try:
        return datetime.datetime.strptime(str(date_input), '%Y%m%d').date()
    except ValueError:
        print('Ignoring input as \'{}\' is not a valid date.'.format(date_input))
        return None


def main(start_date, end_date):
    """

    :param start_date:
    :param end_date:
    :return:
    """
    current_date = start_date
    while current_date <= end_date:
        try:
            server_load.analysis(current_date)
            users_and_institutions.analysis(current_date)
        except FileNotFoundError as error:
            print(error)

        current_date += datetime.timedelta(1)


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

    main(start, end)
