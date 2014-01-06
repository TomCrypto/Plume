#! /usr/bin/env python3
# -*- coding: utf-8 -*-

# plume - small todo list/bugtracker
# TomCrypto (contact: github)
# Header written 21 Dec 2013
# Last update on 01 Dec 2014

# Installation:
# -------------
# sudo apt-get install python3 python3-pip
# sudo pip3 install termcolor colorama (or pip-3.2)

from __future__ import print_function

from termcolor import colored
from colorama import init

import termutils
import align

from datetime import datetime
from time import time
import argparse
import os.path
import json
import os


def now():
    return int(time())


def term_width():
    return termutils.getTerminalSize()[0]


def open_file(path):
    if os.path.exists(path):
        with open(path, 'r') as f:
            return json.loads(f.read())
    else:
        return {'top': 0, 'entries': {}}


# These are the available priorities and status (feel free to add some!)

PRIORITIES = {'feature':  colored('feature ', 'green'),
              'trivial':  colored('trivial ', 'cyan'),
              'minor':    colored('minor   ', 'yellow'),
              'major':    colored('major   ', 'red'),
              'critical': colored('critical', 'red', attrs=['bold'])}

# TEMPORARY (cmd.exe does not support unicode)
if os.name == 'nt':
    ISSUE_STATUS = {'new':  ' ',
                    'wip':  colored('>', 'cyan',  attrs=['bold']),
                    'done': colored('x', 'green', attrs=['bold'])}
else:
    ISSUE_STATUS = {'new':  ' ',
                    'wip':  colored('»', 'cyan',  attrs=['bold']),
                    'done': colored('×', 'green', attrs=['bold'])}


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
        return str(int(issue))  # ...
    except ValueError:
        raise ValueError("Invalid issue '{0}'.".format(issue))


# These functions are the ones that actually operate on the data file

def do_priority(issues, issue, priority):
    check_issue(issues, issue)
    check_priority(priority)

    issues[get_index(issue)]['priority'] = priority
    issues[get_index(issue)]['modified'] = now()


def do_update(issues, issue, status):
    check_issue(issues, issue)
    check_status(status)

    issues[get_index(issue)]['status'] = status
    issues[get_index(issue)]['modified'] = now()


def do_edit(issues, issue, summary):
    check_issue(issues, issue)

    issues[get_index(issue)]['summary'] = summary
    issues[get_index(issue)]['modified'] = now()


def do_add(issues, data, priority, summary):
    check_priority(priority)
    data['top'] += 1

    issues[data['top']] = {'priority': priority,
                           'summary':  summary,
                           'status':   'new',
                           'modified': now(),
                           'created':  now()}


def do_rm(issues, issue):
    check_issue(issues, issue)
    del issues[issue]


# The functions below do some pretty-printing for the terminal output

def to_date(timestamp, color=True):
    date = datetime.fromtimestamp(timestamp)
    if date.date() == datetime.today().date():
        s = date.strftime(" %H:%M:%S")
    else:
        s = date.strftime('%d %b %y')

    if color:
        return colored(s, "white", attrs=['bold'])
    else:
        return s


def to_issue(index):
    prefix = colored('-' * (4 - len(str(index))), 'white', attrs=['dark'])
    return prefix + ' ' + colored(str(index), 'magenta', attrs=['bold'])


def print_as_html(issues):
    print('<table border="1">')
    print('<tr>')
    print('<th>Status</th>')
    print('<th>Priority</th>')
    print('<th>Description</th>')
    print('<th>Creation Date</th>')
    print('<th>Last Modified</th>')
    print('<th>Issue Number</th>')
    print('</tr>')

    for index in sorted(issues.keys(), key=lambda k: int(k)):
        issue = issues[index]
        print("<tr>"
              "<td>{0}</td>"
              "<td>{1}</td>"
              "<td>{2}</td>"
              "<td>{3}</td>"
              "<td>{4}</td>"
              "<td>{5}</td>"
              "</tr>".format(
            issue['status'],
            issue['priority'],
            issue['summary'],
            to_date(issue['created'], False),
            to_date(issue['modified'], False),
            index))

    print('</table>')


# This is the script, it does the argument parsing and most of the work

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Plume - A Tiny Bugtracker")
    parser.add_argument('-p', '--priority', nargs=2)  # Change issue priority
    parser.add_argument('-u', '--update',   nargs=2)  # Update existing issue
    parser.add_argument('-e', '--edit',     nargs=2)  # Edit a summary
    parser.add_argument('-a', '--add',      nargs=2)  # Add a new issue
    parser.add_argument('-r', '--rm')                 # Delete an issue
    parser.add_argument('-s', '--short',  action='store_true')
    parser.add_argument('-m', '--html',   action='store_true')
    parser.add_argument('-f', '--path')
    args = vars(parser.parse_args())
    init()

    if args['path']:
        path = args['path']
        data = open_file(path)
    else:
        search = '.'
        while True:
            path = os.path.join(search, '.plume')

            if os.path.exists(path):
                data = open_file(path)
                break

            parent = os.path.join(search, os.pardir)
            if os.path.abspath(parent) == os.path.abspath(search):
                data = {'top': 0, 'entries': {}}
                path = '.plume'
                break
            else:
                search = parent

    issues = data['entries']

    try:
        if args['priority']:
            do_priority(issues, *args['priority'])
        if args['update']:
            do_update(issues, *args['update'])
        if args['edit']:
            do_edit(issues, *args['edit'])
        if args['add']:
            do_add(issues, data, *args['add'])
        if args['rm']:
            do_rm(issues, *args['rm'])
    except ValueError as e:
        raise SystemExit(e)

    output = json.dumps(data, indent=2)
    with open(path, 'w') as f:
        f.write(output + '\n')

    if args['html']:
        print_as_html(issues)
    else:
        print('')

        if not issues:
            print(" (no issues at this time) ")
        else:
            for index in sorted(issues.keys(), key=lambda k: int(k)):
                width = term_width() - 45  # Takes up all the space
                issue = issues[index]

                if args['short'] and issue['status'] == 'done':
                    continue

                summary = align.align_paragraph(issue['summary'], width)

                if len(summary) == 1:
                    print(" [{0}]  {1}  {2}  {3}  {4} {5}".format(
                          ISSUE_STATUS[issue['status']],
                          PRIORITIES[issue['priority']],
                          summary[0].ljust(width),
                          to_date(issue['created']),
                          to_date(issue['modified']),
                          to_issue(index)))
                else:
                    for i, line in enumerate(summary):
                        if i == 0:
                            print(" [{0}]  {1}  {2}".format(
                                  ISSUE_STATUS[issue['status']],
                                  PRIORITIES[issue['priority']],
                                  line))
                        elif i == len(summary) - 1:
                            print(' ' * 16 + "{0}  {1}  {2} {3}".format(
                                  line.ljust(width),
                                  to_date(issue['created']),
                                  to_date(issue['modified']),
                                  to_issue(index)))
                        else:
                            print(' ' * 16 + line)

        print('')
