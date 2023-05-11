#! /usr/bin/env python3

import os
import xml.etree.ElementTree as ET
import argparse

"""
This script takes a VeraPDF output file, extracts the Annotation subtypes and writes those to
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
       
        myAnnots = []
        
        annotations = job.findall(".//annotation")

        for annotation in annotations:
            try:
                subType = annotation.findall(".//subType")[0].text
                myAnnots.append(subType)
            except IndexError:
                pass

        myAnnots = list(set(myAnnots))

        annotStr = ""

        for myAnnot in myAnnots:
            annotStr = annotStr + myAnnot + sep
        
        # Strip trailing separator
        le = len(sep)
        annotStr = annotStr[:-le]

    return annotStr
    
def main():

    args = parseCommandLine()
    fileIn = args.fileIn
    sep = args.separator
    annotStr = parseXML(fileIn, sep)
    print(annotStr)

if __name__ == "__main__":
    main()

