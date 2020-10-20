
'''
Date         : 2020-09-17 11:04:12
LastEditors  : LiZhenglin
LastEditTime : 2020-09-17 14:08:18
FilePath     : \SSHConnectRunCommand\Tools.py
'''

from sys import exit

def findInStrList(target, lst):
    for string in lst:
        if target in string:
            return True
    return False


def list2string(list):
    s = ''
    for string in list:
        s += string
    return s


def checkSame(str_list_1, str_list_2):
    if list2string(str_list_1) == list2string(str_list_2):
        return True
    else:
        return False

def exitWithPress(): 
    input("Press Enter to continue...")
    exit(0)
