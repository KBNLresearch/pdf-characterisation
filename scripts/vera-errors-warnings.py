#! /usr/bin/env python3

import os
import xml.etree.ElementTree as ET
import argparse

"""
This script takes a VeraPDF output file, extracts any exceptions and logs and writes those to
stdout
"""

# Create parser
parser = argparse.ArgumentParser(
description="Create Markdown table with exceptions and logs from VeraPDF output")

def parseCommandLine():
    # Add arguments
    
    parser.add_argument('fileIn',
                        action="store",
                        type=str,
                        help="input file")
    parser.add_argument('separator',
                        action="store",
                        type=str,
                        default=",",
                        help="output separator")
    # Parse arguments
    args = parser.parse_args()

    return(args)


def parseXML(fileIn, sep):

    tree = ET.parse(fileIn)
    root = tree.getroot()

    jobs = root.findall(".//job")

    for job in jobs:
        
        parseErrors = False
        warnings = False
        errors = False

        try:
            taskResults = job.findall(".//taskResult")

            for taskResult in taskResults:
                type = taskResult.get("type")
                if type == "PARSE":
                    isSuccess = taskResult.get("isSuccess")
                    if isSuccess == "false":
                        #exceptionMessage = taskResult.find(".//exceptionMessage")
                        #exceptionMessageText = exceptionMessage.text
                        parseErrors = True
                        break
        except:
                pass

        try:
            logs = job.findall(".//logs/logMessage")

            for logMessage in logs:
                level = logMessage.get("level")
                if level == "WARNING":
                     warnings = True
                if level == "ERROR":
                     errors = True
        except:
                pass

        outStr = str(parseErrors) + sep + str(warnings)

    return outStr
    
def main():

    args = parseCommandLine()
    fileIn = args.fileIn
    sep = args.separator
    outStr = parseXML(fileIn, sep)
    print(outStr)

if __name__ == "__main__":
    main()

