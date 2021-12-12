#!/usr/bin/env python3

'''
OPS435 Assignment 2 - Winter 2021
Program: assignment2.py
Author: AHMED MAQSOOD
The python code in this file assignment2.py is original work written by
"Student Name". No code in this file is copied from any other source 
including any person, textbook, or on-line resource except those provided
by the course instructor. I have not shared this python file with anyone
or anything except for submission for grading.  
I understand that the Academic Honesty Policy will be enforced and violators 
will be reported and appropriate action will be taken.
'''

import os
import sys
import time
import argparse
import subprocess
from datetime import datetime, timedelta

args = object()  # arguments will be returned here from parse_command_args()

def parse_command_args():  # provided
    parser = argparse.ArgumentParser(description="Usage Report based on the last command",epilog="Copyright 2021 - Ahmed Maqsood")
    parser.add_argument("-l", "--list", type=str, choices=['user','host'], help="generate user name or remote host IP from the given files")
    parser.add_argument("-r", "--rhost", help="usage report for the given remote host IP")  # this even used? no, I think we will remove it
    parser.add_argument("-d","--date", type=str, help="specify date for report")
    parser.add_argument("-u", "--user", help="usage report for the given user name")  # this is another to lose
    parser.add_argument("-v","--verbose", action="store_true",help="turn on output verbosity")
    parser.add_argument("files", type=str, nargs='?',help="file to be processed, if blank, will call last")
    parser.add_argument("-t", "--time", type=str, choices=['daily','weekly'], help="type of report: day or week")
    args=parser.parse_args()
    if args.verbose:
        print('Files to be processed:',args.files)
        print('Type of args for files',type(args.files))
        if args.user:
            print('usage report for user:',args.user)
        if args.rhost:
            print('usage report for remote host:',args.rhost)
        if args.time:
            print('usage report type:',args.time)
    return args

def open_file_list():  # provided?
    output = []
    filename = args.files
    if filename == None:
        p = subprocess.Popen(['last', '-Fiw'], stdout=subprocess.PIPE)
        stdout = p.communicate()
        stdout = stdout[0].decode('utf-8')
        output =  stdout.split('\n')
    else:
        f = open(filename, 'r')
        output = f.read().split('\n')
        f.close()
    return output

def parse_for_user(file_line_list, date=None):  # provided
    "take list of lines from file, return list of users" # UNUSED
    users = process(file_line_list,0,'users')            # ONLY HERE
    users = sorted(list(dict.fromkeys(users)))           # BECAUSE OF CHECK SCRIPT
    return users          

def datestr_to_obj(datestr):
    "A string in YYYY-MM-DD from argparse gets converted into datetime object"
    fmt = "%Y-%m-%d"
    try:
        obj = datetime.strptime(datestr, fmt)
    except:
        print("Date not recognized. Use YYYY-MM-DD format.")
        sys.exit(1)
    return obj

def process(file_line_list,target,request):
    '''
    process function accepts list(output),target(target data in list 0 for user and 2 for host),request(requested list can be users and hosts)
    process function filters the list line by line and returns a list of data containing users or hosts depending on request"
    '''
    datas = []                              
    for item in file_line_list[:]:          
        if item != '':                      
           data = item.split(' ')           
           data1 = list(filter(None, data)) 
           datas.append(data1[target])     
    if request == 'users':                        
       datas = sorted(list(dict.fromkeys(datas))) 
    elif request == 'hosts':                       
       f=lambda n:sorted(set(n),key=n.count)[::-1] 
       datas = sorted(f(datas))                    
    return datas

def dateprocess(file_line_list,date,target):
    '''
    dateprocess function accepts list(output),date(from args.date) and target(target data from list 0 for users and 2 for hosts)
    dateprocess function checks the list line by line and retrieve a data base on the date given argument and returns a list of users or host base on target argument
    '''
    datedata = []                           
    for item in file_line_list[:]:          
        if item != '':                      
           user = item.split(' ')           
           user1 = list(filter(None, user)) 
           try:
               if date == user1[10]+'-'+user1[11]+'-'+user1[13]:      
                   datedata.append(user1[target])                     
               elif date == user1[4]+'-'+user1[5]+'-'+user1[7]:       
                   datedata.append(user1[target])                     
           except:
                   pass
    return datedata 

def timediff(file_line_list,user,target,time):
    '''
    Timediff function arguments are: File_line_list(output) ,user(can be args.user or args.rhost), target(target data from list users or hosts) and time(weekly or daily)
    Timediff function checks all the lines from file_line_list and retrieves all the lines from specific user and calculates their daily/weekly usages and returns a dictionary containing date as key and usage time as value.
    '''
    datas = {}                              
    timeformat = '%Y-%b-%d %H:%M:%S'        
    for item in file_line_list[:]:          
        if item != '':                      
           data = item.split(' ')           
           data1 = list(filter(None, data)) 
           if data1[target] == user:        
                 starttime = str(data1[7]+'-'+data1[4]+'-'+data1[5]+' '+data1[6])                         
                 endtime = str(data1[13]+'-'+data1[10]+'-'+data1[11]+' '+data1[12])                       
                 diff = datetime.strptime(endtime, timeformat) - datetime.strptime(starttime, timeformat) 
                 monthnum = data1[4]                           
                 monthnum = datetime.strptime(monthnum, "%b")  
                 monthnum = str(monthnum.month).zfill(2)       
                 if time == 'daily':                                                            
                    date = str(data1[5]+'/'+monthnum+'/'+data1[7])                             
                 elif time == 'weekly':                                                         
                    date = datetime(int(data1[7]), int(monthnum), int(data1[5])).strftime("%V")
                    date = int(date)-1                                                          
                    date = str(date).zfill(2)                                                   
                    date = str(str(data1[7]+' '+str(date)))                                    
                 if date not in datas:                   
                    datas.update({date:diff.seconds})    
                 elif date in datas:                    
                    x = datas.get(date)                  
                    datas.update({date:x+diff.seconds})  
    datas.update({'Total':sum(datas.values())})          
    for key,values in datas.items():  
        conv = timecalculator(values) 
        datas.update({key:conv})      
    return datas

def timecalculator(seconds):
    ''' 
    timecalculator accepts seconds and convert it into hour,min and remaining seconds
    '''
    minutes = seconds // 60  
    hours = minutes // 60    
    while seconds >= 60:     
          seconds -= 60      
    return "%2d:%02d:%02d" % (hours, minutes % 60, seconds % 60)    

def outputform(var1,var2): 
    '''
    outputform takes variables to be formatted into a proper output
    '''
    if var2 == None:                                        
       var2 = 'last -Fiw'                                   
    equals = []                                             
    equal = 0                                               
    try:
        out = str(var1.capitalize()) + ' list for ' + str(var2) 
    except:
        out = str(var1) + ' list for ' + str(var2)              
    if var2 == args.time and args.user != None:
           out = str(var2.capitalize()) + ' Usage Report for ' + str(args.user) 
    elif var2 == args.time and args.rhost !=None:
           out = str(var2.capitalize()) + ' Usage Report for ' + args.rhost     
    while equal != len(out):                                
       equals.append('=')                                   
       equal += 1                                           
    return out+'\n'+''.join(equals)                         

if __name__ == "__main__":
    args = parse_command_args()
    output = open_file_list()
    if args.files == None:  
       output = output[:-2] 

    if args.list == 'user' and args.date == None:
         "For user list"
         print(outputform(args.list , args.files)) 
         for user in process(output,0,'users'):     
               print(user)                         

    elif args.list == 'host' and args.date == None:
         "For host list"
         print(outputform(args.list , args.files))  
         for host in process(output,2,'hosts'):     
              print(host)                           

    elif args.list == 'user' and args.date != None:
         "For user list and date"            
         y = datestr_to_obj(args.date)                        
         formdate = y.strftime("%b-%d-%Y")                    
         print(outputform(args.list , args.files))            
         for userdate in dateprocess(output,formdate,0):      
              print(userdate)                                 

    elif args.list == 'host' and args.date != None:
         "For host list and date"           
         y = datestr_to_obj(args.date)                        
         formdate = y.strftime("%b-%d-%Y")                    
         print(outputform(args.list , args.files))            
         for hostdate in dateprocess(output,formdate,2):      
              print(hostdate)                                 
    
    elif args.user != None and args.time == 'daily':
         "For daily user usage"           
         print(outputform(args.user, args.time))
         dic = timediff(output,args.user,0,args.time)
         print('Date'.ljust(10)+'Usage'.rjust(15))
         for date,time in dic.items():
             print(date.ljust(10)+time.rjust(15))

    elif args.rhost != None and args.time == 'daily':
         "For daily rhost usage"
         print(outputform(args.rhost, args.time))
         dic = timediff(output,args.rhost,2,args.time)
         print('Date'.ljust(10)+'Usage'.rjust(15))
         for date,time in dic.items():
             print(date.ljust(10)+time.rjust(15))

    elif args.user != None and args.time == 'weekly':
         "For weekly user usage"
         print(outputform(args.user, args.time))
         dic = timediff(output,args.user,0,args.time)
         print('Date'.ljust(10)+'Usage'.rjust(15))
         for date,time in dic.items():
             print(date.ljust(10)+time.rjust(15))

    elif args.rhost != None and args.time == 'weekly':
         "For weekly rhost usage"
         print(outputform(args.rhost, args.time))
         dic = timediff(output,args.rhost,2,args.time)
         print('Date'.ljust(10)+'Usage'.rjust(15))
         for date,time in dic.items():
             print(date.ljust(10)+time.rjust(15))
