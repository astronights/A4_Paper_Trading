from datetime import date, timedelta, datetime

def get_today_str():
    return date.today().strftime('%Y-%m-%d')

def get_n_deltas_before_str(n):
    return (date.today() - timedelta(minutes=n)).strftime('%Y-%m-%d')

def convert_gmt_to_local(t):
    return t + (datetime.now() - datetime.utcnow())