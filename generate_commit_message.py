#!/usr/bin/python
"""Generate a commit message from an app.yaml file.

Takes the path to a .yaml file, and the path to a version file as
command line arguments.  Optionally, a third `summary` argument can be
supplied.

The version file will be created or overwritten, then populated with
relevant information from the yaml file.  If a `summary` argument is
included, that will be included in the version file as well.

The version file should be plain text.

usage: vfile-yaml <yaml file path> OPTIONS...
       vfile-yaml --help | -h

OPTIONS:
    (-V | --version-file) path_to_version_file
        Use a custom version file, not 'version.txt'

    (-s | --summary) summary_message
        Add a summary message to the file.  A summary may be added
        later by editing the file.
"""
__version__ = "1.0"
__author__ = "Alexander Otavka (zotavka@gmail.com)"


import sys
import os
import re

from multi_key_dict import multi_key_dict


__all__ = []


VERSION_REGEX = (
    "version: "
    "(?P<major>\d+)-(?P<minor>\d+)-(?P<state>.+)-(?P<revision>\d+)")
STATE = multi_key_dict({
    ('a', '0'): "Alpha",
    ('b', '1'): "Beta",
    ('rc', '2'): "Release Candidate",
    ('r', '3'): "Release",
    })
args = multi_key_dict({
    ("-V", "--version-file", 0): "VERSION",
    ("-s", "--summary", 1): "summary.",
    })
TEMPLATE = """V{version}, {summary}

CHANGES:
    - none

BUG FIXES:
    - none
"""


# Read and parse command line arguments
try:
    if (sys.argv[1] == "--help" or
        sys.argv[1] == "-h"):
        print __doc__
        exit()
    yaml_file_path = sys.argv[1]
except IndexError:
    print __doc__
    raise TypeError("requires at least 1 argument: path to .yaml file")
for i, arg in enumerate(sys.argv):
    if i >= 2 and args.has_key(arg):
        try:
            args[arg] = sys.argv[i + 1]
            print "debug", sys.argv[2:]
        except IndexError:
            # they have the argument tag but no argument
            raise
    else:
        # they are using the wrong tag
        pass
version_file_path = args[0]
summary = args[1]

#try:
#    version_file_path = sys.argv[2]
#except IndexError:
#    print "[INFO] No version file given, using default."
#    version_file_path = "version.txt"
#try:
#    summary = sys.argv[3]
#except IndexError:
#    print "[INFO] No summary given, using default."
#    summary = "summary"

# Parse the version from the .yaml file
with open(yaml_file_path) as f:
    for line in f:
        if re.match(VERSION_REGEX, line) is not None:
            version = line
            break
try:
    m = re.search(VERSION_REGEX, version).groupdict()
except:
    print "There was a problem finding the version information:"
    raise
m["state"] = STATE[m["state"]]
version = "{major}.{minor} ({state} {revision})".format(**m)

# Load the version text file
version_file = None
try:
    with open(version_file_path, "r") as f:
        print "[INFO] Old Contents of " + version_file_path + ":"
        print "\"\"\"\n" + f.read() + "\n\"\"\""
except IOError:
    os.mknod(version_file_path, 420)
version_file = open(version_file_path, "w")

# Warn if first line is over 60 characters
out = TEMPLATE.format(version=version, summary=summary)
first_line_len = len(out.split('\n', 1)[0])
if first_line_len > 60:
    print ("[WARN] The first line exceeds 60 characters.\n"
           "       Consider shortening summary.")

# Write our information, and close.
version_file.write(out)
print "[INFO] Contents of " + version_file_path + " replaced with:"
print "\"\"\"\n" + out + "\n\"\"\""
version_file.close()
