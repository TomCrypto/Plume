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
from os.path import exists
import align, termutils
from time import time

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

ITEMSTATUS = {'new'  : ' ',
              'wip'  : colored('»', 'cyan',  attrs = ['bold']),
              'done' : colored('×', 'green', attrs = ['bold'])}

# The following functions do some generic user input error/type checking

def check_item(items, item):
    if not item in items:
        raise ValueError("Item '{0}' does not exist.".format(item))

def check_priority(priority):
    if not priority in PRIORITIES:
        raise ValueError("Invalid priority '{0}'.".format(priority))

def check_status(status):
    if not status in ITEMSTATUS:
        raise ValueError("Invalid status '{0}'".format(status))

def get_index(item):
    try:
        return str(int(item)) # ...
    except ValueError:
        raise ValueError("Invalid item '{0}'.".format(item))

# These functions are the ones that actually operate on the data file

def do_priority(items, item, priority):
    check_item(items, item)
    check_priority(priority)

    items[get_index(item)]["priority"] = priority
    items[get_index(item)]["modified"] = now()

def do_update(items, item, status):
    check_item(items, item)
    check_status(status)

    items[get_index(item)]["status"] = status
    items[get_index(item)]["modified"] = now()

def do_edit(items, item, summary):
    check_item(items, item)

    items[get_index(item)]["summary"] = summary
    items[get_index(item)]["modified"] = now()

def do_add(items, data, priority, summary):
    check_priority(priority)
    data['top'] += 1
   
    items[data['top']] = {"priority": priority,
                          "summary" : summary,
                          "status"  : 'new',
                          "modified": now(),
                          "created" : now()}

def do_rm(items, item):
    check_item(items, item)
    del items[item]

# The functions below do some pretty-printing for the terminal output

def to_date(timestamp):
    date = datetime.fromtimestamp(timestamp)
    if date.date() == datetime.today().date():
        return colored(date.strftime(" %H:%M:%S"), "white", attrs = ['bold'])
    else:
        return colored(date.strftime('%d %b %y'), 'white', attrs = ['bold'])

def to_item(index):
    prefix = colored('-' * (4 - len(str(index))), 'white', attrs = ['dark'])
    return prefix + ' ' + colored(str(index), 'magenta', attrs = ['bold'])

# This is the script, it does the argument parsing and most of the work

if __name__ == '__main__':
    args = argparse.ArgumentParser(description = "Plume - A Tiny Bugtracker")
    args.add_argument('-p', '--priority', nargs = 2) # Change item priority
    args.add_argument('-u', '--update',   nargs = 2) # Update existing item
    args.add_argument('-e', '--edit',     nargs = 2) # Edit a summary
    args.add_argument('-a', '--add',      nargs = 2) # Add a new item
    args.add_argument('-r', '--rm',       nargs = 1) # Delete an item
    arg = args.parse_args()
    colorama.init()

    if exists('.plume'):
        with open('.plume', 'r') as f:
            data = json.loads(f.read())
    else:
        data = {"top": 0, "entries": {}}

    items = data["entries"]

    try:
        if arg.priority: do_priority(items, arg.priority[0], arg.priority[1])
        if arg.update:   do_update(items, arg.update[0], arg.update[1])
        if arg.edit:     do_edit(items, arg.edit[0], arg.edit[1])
        if arg.add:      do_add(items, data, arg.add[0], arg.add[1])
        if arg.rm:       do_rm(items, arg.rm[0])
    except ValueError as e:
        raise SystemExit(e)

    output = json.dumps(data, indent = 2)
    with open('.plume', 'w') as f:
        f.write(output + '\n')

    print()

    if not items:
        print(" (no items at this time) ")
    else:
        for index in sorted(items.keys(), key = lambda k: -int(k)):
            width = term_width() - 45 # Takes up all the space
            item = items[index]

            summary = align.align_paragraph(item["summary"], width)

            if len(summary) == 1:
                print(" [{0}]  {1}  {2}  {3}  {4} {5}".format(
                      ITEMSTATUS[item[  "status"]],
                      PRIORITIES[item["priority"]],
                      summary[0].ljust(width),
                      to_date(item["created"]),
                      to_date(item["modified"]),
                      to_item(index)))
            else:
                for i, line in enumerate(summary):
                    if i == 0:
                        print(" [{0}]  {1}  {2}".format(
                              ITEMSTATUS[item[  "status"]],
                              PRIORITIES[item["priority"]],
                              line))
                    elif i == len(summary) - 1:
                        print(' ' * 16 + "{0}  {1}  {2} {3}".format(
                              line.ljust(width),
                              to_date(item["created"]),
                              to_date(item["modified"]),
                              to_item(index)))
                    else:
                        print(' ' * 16 + line)

    print()
