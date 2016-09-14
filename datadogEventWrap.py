#!/usr/local/bin/python
##
# Wrapper utility to send events to datadog when starting another process and on process completion
##

import getopt
import os
import sys
import time
import yaml
from datadog import api
from datadog import initialize
from subprocess import call

def usage(errorMessage=None):
    if not errorMessage is None:
        print errorMessage + "\n"
    print "Datadog Event Wrapper"
    print "\tLogs events using the DataDog API when the given command starts and finishes"
    print "\nUsage:"
    print "\tddEventWrap <options> <command>"
    print "\nOptions:"
    print "\t-c=/some/config.yaml, --config=/some/config.yaml - Path to the configuration file. Defaults to datadogEventWrap.yaml"
    print "\t-t=sometag:somevalue, --eventtag=sometag:somevalue - Additional tag to include for all the events triggered"
    print "\t-s=sometag:somevalue, --starttag=sometag:somevalue - Additional tag to include for the start event triggered"
    print "\t-e=sometag:somevalue, --endtag=sometag:somevalue - Additional tag to include for the end event triggered"
    print "\t-d, --debug - Enable debug mode"
    print "\t--dryrun - Enable debug mode and skip event creation"
    print "\t--ignore-event-errors - Ignore errors that happen during event creation"

def printEvent(title, text='', tags=[]):
    print "\n--- EVENT ---"
    print "Title: " + title
    print "Text: " + text
    print "Tags: "
    for tag in tags:
        print "\t" + tag
    print "\n"

configFile = "datadogEventWrap.yaml"
startTags = []
endTags = []
eventTags = []
dryrun = False
debug = False
ignoreEventErrors = False

try:
    opts, commandToRun = getopt.getopt(sys.argv[1:], "hc:t:s:e:d", ["help", "config=", "tag=", "eventtag=", "starttag=", "endtag=", "dryrun", "debug", "ignore-event-errors"])
except getopt.GetoptError:
    usage()
    sys.exit(2)
for opt, arg in opts:
    if opt in ("-h", "--help"):
        usage()
        sys.exit()
    elif opt in ("-c", "--config"):
        configFile = arg
    elif opt in ("-t", "--tag", "--eventtag"):
        eventTags.append(arg);
    elif opt in ("-s", "--starttag"):
        startTags.append(arg);
    elif opt in ("-e", "--endtag"):
        endTags.append(arg);
    elif opt in ("--dryrun"):
        dryrun = True
        debug = True
    elif opt in ("-d", "--debug"):
        debug = True
    elif opt == "--ignore-event-errors":
        ignoreEventErrors = True

if not commandToRun:
    usage(errorMessage="A command is required to run")
    sys.exit(2)

datadog_api_key = None
datadog_app_key = None

# First check if the config file exists...
if os.path.isfile(configFile):
    with open(configFile, 'r') as stream:
        try:
            configuration = yaml.load(stream)
            if debug:
                print "--- CONFIG FILE ---"
                print configuration
                print "\n"
            if "datadog_api_key" in configuration:
                datadog_api_key = configuration["datadog_api_key"]
            if "datadog_app_key" in configuration:
                datadog_app_key = configuration["datadog_app_key"]
            if "start_tags" in configuration:
                startTags+= configuration["start_tags"]
            if "end_tags" in configuration:
                endTags+= configuration["end_tags"]
            if "event_tags" in configuration:
                eventTags+= configuration["event_tags"]
            if "ignore_event_errors" in configuration:
                ignoreEventErrors = configuration["ignore_event_errors"]
        except yaml.YAMLError as exc:
            print "There was an error processing your configuration file:"
            print exc

# Initialize the Datadog connection if we're not doing a dry run
if not dryrun:
    # Setup options based on environment variables
    try:
        options = {
            'api_key': datadog_api_key if datadog_api_key else os.environ['datadog_api_key'],
            'app_key': datadog_app_key if datadog_app_key else os.environ['datadog_app_key']
        }
        if debug:
            print options
    except KeyError:
        usage(errorMessage="The environment variables 'datadog_api_key' and 'datadog_app_key' must be set unless using --dry-run")
        sys.exit(2)

    # Make sure the values are sane
    if not options['api_key']:
        usage(errorMessage="The environment variable 'datadog_api_key' must be set unless using --dry-run");
        sys.exit(2)
    if not options['app_key']:
        usage(errorMessage="The environment variable 'datadog_app_key' must be set unless using --dry-run");
        sys.exit(2)
    initialize(**options)

# Send (and/or debug) the start event
startEventTitle = "Starting `" + " ".join(commandToRun) + "`"
startEventText = startEventTitle
startEventTags = startTags+eventTags
if dryrun or debug:
    printEvent(title=startEventTitle, text=startEventText, tags=startEventTags)
if not dryrun:
    try:
        api.Event.create(title=startEventTitle, text=startEventText, tags=startEventTags)
    except ValueError, e:
        if not ignoreEventErrors:
            print "Could not create start event: " + str(e)
            sys.exit(2)

# Log starting time
startTime = round(time.time(), 1)

if debug:
    print "Executing: " + " ".join(commandToRun)

# Run the command that was passed in
call(commandToRun, shell=True)

# Log ending time
endTime = round(time.time(), 1)

# Send (and/or debug) the end event
endEventTitle = "Finished `" + " ".join(commandToRun) + "`"
endEventText = "Completed in " + str(endTime - startTime) + " seconds."
endEventTags = endTags+eventTags
if dryrun or debug:
    printEvent(title=endEventTitle, text=endEventText, tags=endEventTags)
if not dryrun:
    try:
        api.Event.create(title=endEventTitle, text=endEventText, tags=endEventTags)
    except ValueError, e:
        if not ignoreEventErrors:
            print "Could not create end event: " + str(e)
            sys.exit(2)
