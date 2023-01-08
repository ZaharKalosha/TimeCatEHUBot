from datetime import datetime, timedelta, timezone
import math
import requests
import re


flag = 0


def get_flag():
    return flag


def set_flag(n):
    global flag
    flag = n


def get_time():
    delta = timedelta(hours=3, minutes=0)
    return datetime.now(timezone.utc) + delta


def my_round(i):
    return math.ceil(i) if math.modf(i)[0] == 0.5 else round(i)


def normalize(s) -> str:
    return str(s).replace('  ', '').replace('\n', '')


def auth_moodle(login, password) :
    url_domain = "https://moodle.ehu.lt"
    s = requests.Session()
    r_1 = s.get(url=url_domain + "/login/index.php")
    pattern_auth = '<input type="hidden" name="logintoken" value="\w{32}">'
    token = re.findall(pattern_auth, r_1.text)
    token = re.findall("\w{32}", token[0])[0]
    payload = {'anchor': '', 'logintoken': token, 'username': login, 'password': password, 'rememberusername': 1}
    r_2 = s.post(url=url_domain + "/login/index.php", data=payload)
    result = ''
    for i in r_2.text.splitlines():
        if "<title>" in i:
            # print(i[15:-8:])
            result = i[15:-8:]
            break
    counter = 0
    for i in r_2.text.splitlines():
        if "loginerrors" in i or (0 < counter <= 3):
            counter += 1
            print(i)
            result = i
    # return s
    return result


