import datetime as dt
import os
import sys
import unicodedata

from contextlib import redirect_stdout

import requests


#Global
global OS_NAME 
OS_NAME = os.name


def add_zero(num):

    if num < 10:
        str_num = '0' + str(num)

    else:
        str_num = str(num)

    return str_num


def check_shift(hour_list):

    length = len(hour_list)
    today = 256
    tomorrow = 256

    for i in range(length - 1):
        
        tmp = i + 1

        if hour_list[i] > hour_list[tmp]:

            if len(hour_list[:i]) < len(hour_list[i:]):
                today = i
                break

            else:
                tomorrow = i
                break

    return (today, tomorrow)


def check_timezone():

    TIMEZONE_PATH = 'text/timezone'

    with open(TIMEZONE_PATH, 'r') as f:
        timezone = f.read().replace('\n', '')

    return timezone


def get_index_list(members_list):

    JA_LIST = get_all_members_list()

    index_list = tuple([JA_LIST.index(member.replace("サブ", "")) for member in members_list])

    return index_list


def eval_argv(argv):

    valid_options_list = {'--help', '--eng', '--date', '--tomorrow', '--all', '--title'}

    #Options that is not available with other options
    special_options = {'--help', '--date'}

    #Options that is available to use other non special option at the same time
    non_special_options = {'--eng', '--tomorrow', '--all', 'title'}

    s_flag = 0
    n_flag = False

    for option in argv:

        if not option in valid_options_list:
            return None

        if option in special_options:
            s_flag += 1 

        if option in non_special_options:
            n_flag = True

        if s_flag and n_flag or s_flag > 1:

            return None

    return argv


def fetch_title(url_list):

    title_list = []

    for url in url_list:
        
        #Check if the stream url is YouTube url
        if not "youtube" in url:
            title_list.append("")
            continue

        else:

            tmp = requests.get('https://www.youtube.com/oembed?url={}&format=json'.format(url))
            try:
                title = str(eval(tmp.text)['title'])
            except:
                title_list.append("")
                continue

            if unicodedata.east_asian_width(title[0]) != 'W':
                title = ' ' + title

            title_list.append(title)

    return title_list


def get_en_list():

    EN_FILE_PATH = 'text/hololive_members_en.txt'

    with open(EN_FILE_PATH, 'r') as f:

        #Ignore the message of the first row
        en_list = f.readlines()[1].split(',')

    #Delete break symbol
    en_list[-1] = en_list[-1].replace('\n', '')

    return tuple(en_list)


def get_all_members_list():

    MEMBER_FILE_PATH = 'text/hololive_members.txt'

    with open(MEMBER_FILE_PATH, 'r') as f:

        #Ignore the message of the first row
        all_members_list = f.readlines()[1].split(',')

    #Delete break symbol
    all_members_list[-1] = all_members_list[-1].replace('\n', '')

    return all_members_list


def get_now_time():

    #Get the current time in JST(UTC+9)
    JST = dt.timezone(dt.timedelta(hours=+9), 'JST')
    now = dt.datetime.now(JST)

    month = now.month
    date = now.day

    return (month, date)


def get_tomorrow():

    #Get the tomorrow date in JST
    JST = dt.timezone(dt.timedelta(hours=+9), 'JST')
    tomorrow = dt.datetime.now() + dt.timedelta(days=1)

    month = tomorrow.month
    date = tomorrow.day

    return (month, date)


def move_current_directory():

    #Move to the directory that has main.py
    #Change directory delimiter by OS

    #Windows
    if OS_NAME == 'nt':
        path = __file__.replace(r'\src\util.py', '')
        os.chdir(path)

    #POSIX
    else:
        path = __file__.replace('/src/util.py', '')
        os.chdir(path)


def option_check(options):

    eng_flag = False
    tomorrow_flag = False
    all_flag = False
    title_flag = False

    if '--help' in options:
        show_help()
        sys.exit()

    if '--date' in options:
        show_date()
        sys.exit()

    if '--eng' in options:
        eng_flag = True

    if '--tomorrow' in options:
        tomorrow_flag = True

    if '--all' in options:
        all_flag = True

    if '--title' in options:
        title_flag = True

    return (eng_flag, tomorrow_flag, all_flag, title_flag)
        

def remove_emoji(title):
    
    #Redirect to null in order not display 
    with redirect_stdout(open(os.devnull, 'w')):
        tmp = []
        for i in list(title):
            try:
                print(i)
                tmp.append(i)
            except UnicodeEncodeError:
                pass
    title = ''.join(tmp)
    if len(title) == 0:
        title.append(' ')
    return title
    

def replace_name(member):

    member = member.replace('Sub','サブ')

    return member

def show_date():

    JST = dt.timezone(dt.timedelta(hours=+9), 'JST')
    now = dt.datetime.now(JST)

    month = now.month
    date = now.day
    hours = add_zero(now.hour)
    minutes = add_zero(now.minute)

    print('{}/{} {}:{} (JST)'.format(month, date, hours, minutes))


def show_help():

    with open('text/help', 'r') as f:
        
        l = f.read().split('\n')

        #Remove the top message
        l.pop(0)

        for line in l:
            print(line)


def timezone_convert(time_list, timezone):
    import pytz

    new_date_list = []

    JST = pytz.timezone('Asia/Tokyo')
    now = dt.datetime.now(JST)
    year = now.year
    month = now.month
    day = now.day

    new_date_list = [dt.datetime.strptime(t, '%H:%M').replace(year=year, month=month, day=day) for t in time_list]
    new_date_list = list(map(lambda x: JST.localize(x), new_date_list))

    try:
        new_timezone = pytz.timezone(timezone)
    except:
        sys.exit('Invalid timezone')

    new_date_list = tuple(map(lambda x: x.astimezone(new_timezone), new_date_list))
    new_time_list = tuple([d.strftime("%H:%M") for d in new_date_list])

    return new_time_list
