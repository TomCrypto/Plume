#! /usr/bin/env python3
# -*- coding: utf-8 -*-

# plume - small bugtracker/todo list
# TomCrypto (contact: github)
# Header written 21 Dec 2013
# Last update on 21 Dec 2013

# Installation:
# -------------
# sudo apt-get install python3 python3-pip
# sudo pip-3.2 termcolor colorama (or pip3)

import json, argparse, colorama
from termcolor import colored
from datetime import datetime
import align, termutils
from time import time
import os, os.path

def now():
    return int(time())

def term_width():
    return termutils.getTerminalSize()[0]

# These are the available priorities and status (feel free to add some!)

PRIORITIES = {'feature'  : colored('feature ', 'green'                ),
              'trivial'  : colored('trivial ', 'cyan'                 ),
              'minor'    : colored('minor   ', 'yellow'               ),
              'major'    : colored('major   ', 'red'                  ),
              'critical' : colored('critical', 'red', attrs = ['bold'])}

ISSUE_STATUS = {'new'  : ' ',
                'wip'  : colored('»', 'cyan',  attrs = ['bold']),
                'done' : colored('×', 'green', attrs = ['bold'])}

# The following functions do some generic user input error/type checking

def check_issue(issues, issue):
    if not issue in issues:
        raise ValueError("Issue '{0}' does not exist.".format(issue))

def check_priority(priority):
    if not priority in PRIORITIES:
        raise ValueError("Invalid priority '{0}'.".format(priority))

def check_status(status):
    if not status in ISSUE_STATUS:
        raise ValueError("Invalid status '{0}'".format(status))

def get_index(issue):
    try:
        return str(int(issue)) # ...
    except ValueError:
        raise ValueError("Invalid issue '{0}'.".format(issue))

# These functions are the ones that actually operate on the data file

def do_priority(issues, issue, priority):
    check_issue(issues, issue)
    check_priority(priority)

    issues[get_index(issue)]["priority"] = priority
    issues[get_index(issue)]["modified"] = now()

def do_update(issues, issue, status):
    check_issue(issues, issue)
    check_status(status)

    issues[get_index(issue)]["status"] = status
    issues[get_index(issue)]["modified"] = now()

def do_edit(issues, issue, summary):
    check_issue(issues, issue)

    issues[get_index(issue)]["summary"] = summary
    issues[get_index(issue)]["modified"] = now()

def do_add(issues, data, priority, summary):
    check_priority(priority)
    data['top'] += 1
   
    issues[data['top']] = {"priority": priority,
                           "summary" : summary,
                           "status"  : 'new',
                           "modified": now(),
                           "created" : now()}

def do_rm(issues, issue):
    check_issue(issues, issue)
    del issues[issue]

# The functions below do some pretty-printing for the terminal output

def to_date(timestamp):
    date = datetime.fromtimestamp(timestamp)
    if date.date() == datetime.today().date():
        return colored(date.strftime(" %H:%M:%S"), "white", attrs = ['bold'])
    else:
        return colored(date.strftime('%d %b %y'), 'white', attrs = ['bold'])

def to_issue(index):
    prefix = colored('-' * (4 - len(str(index))), 'white', attrs = ['dark'])
    return prefix + ' ' + colored(str(index), 'magenta', attrs = ['bold'])

# This is the script, it does the argument parsing and most of the work

if __name__ == '__main__':
    args = argparse.ArgumentParser(description = "Plume - A Tiny Bugtracker")
    args.add_argument('-p', '--priority', nargs = 2) # Change issue priority
    args.add_argument('-u', '--update',   nargs = 2) # Update existing issue
    args.add_argument('-e', '--edit',     nargs = 2) # Edit a summary
    args.add_argument('-a', '--add',      nargs = 2) # Add a new issue
    args.add_argument('-r', '--rm',       nargs = 1) # Delete an issue
    args.add_argument('-s', '--succint',  action = 'store_true')
    arg = args.parse_args()
    colorama.init()

    search = '.'
    while True:
        path = os.path.join(search, '.plume')
        if os.path.exists(path):
            with open(path, 'r') as f:
                data = json.loads(f.read())
                break
        
        parent = os.path.join(search, os.pardir)
        if os.path.abspath(parent) == os.path.abspath(search):
            data = {"top": 0, "entries": {}}
            path = '.plume'
            break
        else:
            search = parent

    issues = data["entries"]

    try:
        if arg.priority:
            do_priority(issues, arg.priority[0], arg.priority[1])
        if arg.update:
            do_update(issues, arg.update[0], arg.update[1])
        if arg.edit:
            do_edit(issues, arg.edit[0], arg.edit[1])
        if arg.add:
            do_add(issues, data, arg.add[0], arg.add[1])
        if arg.rm:
            do_rm(issues, arg.rm[0])
    except ValueError as e:
        raise SystemExit(e)

    output = json.dumps(data, indent = 2)
    with open(path, 'w') as f:
        f.write(output + '\n')

    print()

    if not issues:
        print(" (no issues at this time) ")
    else:
        for index in sorted(issues.keys(), key = lambda k: int(k)):
            width = term_width() - 45 # Takes up all the space
            issue = issues[index]
            
            if arg.succint and issue["status"] == 'done':
                continue

            summary = align.align_paragraph(issue["summary"], width)

            if len(summary) == 1:
                print(" [{0}]  {1}  {2}  {3}  {4} {5}".format(
                      ISSUE_STATUS[issue[  "status"]],
                      PRIORITIES[issue["priority"]],
                      summary[0].ljust(width),
                      to_date(issue["created"]),
                      to_date(issue["modified"]),
                      to_issue(index)))
            else:
                for i, line in enumerate(summary):
                    if i == 0:
                        print(" [{0}]  {1}  {2}".format(
                              ISSUE_STATUS[issue[  "status"]],
                              PRIORITIES[issue["priority"]],
                              line))
                    elif i == len(summary) - 1:
                        print(' ' * 16 + "{0}  {1}  {2} {3}".format(
                              line.ljust(width),
                              to_date(issue["created"]),
                              to_date(issue["modified"]),
                              to_issue(index)))
                    else:
                        print(' ' * 16 + line)

    print()
