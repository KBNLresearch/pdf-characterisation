#! /usr/bin/env python3

import os
import xml.etree.ElementTree as ET
import argparse

"""
This script takes a JHOVE output file, extracts the validation status and writes that to
stdout
"""

# Create parser
parser = argparse.ArgumentParser(
description="Create Markdown table with annotations from JHOVE output")

def parseCommandLine():
    # Add arguments
    
    parser.add_argument('fileIn',
                        action="store",
                        type=str,
                        help="input file")
    # Parse arguments
    args = parser.parse_args()

    return(args)


def parseXML(fileIn):

    tree = ET.parse(fileIn)
    root = tree.getroot()

    repInfos = root.findall(".//{http://schema.openpreservation.org/ois/xml/ns/jhove}repInfo")

    for repInfo in repInfos:

        statusElt = repInfo.find(".//{http://schema.openpreservation.org/ois/xml/ns/jhove}status")
        status = statusElt.text

    return status


def main():

    args = parseCommandLine()   
    fileIn = args.fileIn
    status = parseXML(fileIn)
    print(status)

if __name__ == "__main__":
    main()

