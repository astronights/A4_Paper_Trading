from datetime import date, timedelta, datetime

"""Function to get current date in format YYYY-MM-DD"""
def get_today_str():
    return date.today().strftime('%Y-%m-%d')

"""Function to get minutes before current date in format YYYY-MM-DD"""
def get_n_deltas_before_str(n):
    return (date.today() - timedelta(minutes=n)).strftime('%Y-%m-%d')

"""Function to convert GMT time to local time"""
def convert_gmt_to_local(t):
    return t + (datetime.now() - datetime.utcnow())