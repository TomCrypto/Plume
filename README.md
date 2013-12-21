Plume
=====

Minimalist Todo List/Bugtracker
-------------------------------

This little Python 3 tool lets you manage a simple console-based todo list, which also doubles up as a rudimentary bugtracker. This tool is intended for small prototype projects with little infrastructure in place, with typically only one or two developers. Larger code bases will prefer a full-fledged solution.

### Features

 - non-intrusive: the tool generates a single `.plume` file in the root directory of your project, and can then be run from any location inside your project;
 
 - simple: the commands are straightforward, and we use JSON to store a human-readable data file, should you ever need to delve into it;
 
 - good-looking: colors are extensively used in order to give a quick overview of the bugs which most need addressing, and those which have been fixed;

 - easy to tweak: the main script is less than 200 lines long and can easily be extended;

 - portable: all major operating systems are supported;

### Install

It is recommended to symlink the script to a location on your `PATH`, so that you can just call `plume`. This can easily be done on Windows as well, at least on NTFS file systems.

### Usage

First create a `.plume` file in your project's root folder by running the tool once in it with no arguments. From this point on you can run the tool from any folder inside your project, it will autodetect the existing data file.

You can now add bugs or desired features (issues) easily using `--add`:

    $ plume --add [feature/minor/major/etc] "description"

The new issue is then assigned a unique number which identifies it. The set of bugs (priorities) available is by default `feature`, `trivial`, `minor`, `major`, and `critical`, but other ones can be trivially added to the script.

If you made a typo, or otherwise need to change the description, you can use the `--edit` command, which takes the issue number:

    $ plume --edit 14 "amended description for issue 14"

You can remove issues by using the `--rm` command, though this should be avoided - unless in error, issues should be preserved for history. You can also change the priority of an issue as needed, using `--priority`. Finally, you can change the status of an issue using `--update`:

    $ plume --update 14 [new/wip/done]

New issues are automatically set to the status `new`. The user interface is as follows:

![Plume UI](http://imgur.com/u5uQE7O.png)

Note the first date/time is the time the issue was created, and the second one is the last time it was modified (updated, edited, had its priority changed). The number on the far right is the issue number.

Once you start having a lot of issues, the list might start taking up quite a bit of space. Use the `--succint` (or `-s`) flag to hide issues which have been marked `done`.
