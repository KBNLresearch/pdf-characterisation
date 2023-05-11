#! /usr/bin/env python3

import os
import xml.etree.ElementTree as ET
import argparse

"""
This script takes a VeraPDF output file, extracts the Action types and writes those to
stdout
"""

# Create parser
parser = argparse.ArgumentParser(
description="Create Markdown table with actions and annotations from VeraPDF output")

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
      
        myActions = []
        actions = job.findall(".//action")

        for action in actions:
            type = action.get("type")
            myActions.append(type)
        
        myActions = list(set(myActions))

        actionStr = ""

        for myAction in myActions:
            actionStr = actionStr + myAction + sep
        
        # Strip trailing separator
        le = len(sep)
        actionStr = actionStr[:-le]

    return actionStr
    
def main():

    args = parseCommandLine()
    fileIn = args.fileIn
    sep = args.separator
    actionStr = parseXML(fileIn, sep)
    print(actionStr)

if __name__ == "__main__":
    main()

