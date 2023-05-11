#! /usr/bin/env python3

import os
import xml.etree.ElementTree as ET
import argparse

"""
This script takes a JHOVE output file, extracts the Annotation
subtypes, and then writes those to stdout
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

    repInfos = root.findall(".//{http://schema.openpreservation.org/ois/xml/ns/jhove}repInfo")

    for repInfo in repInfos:
    
        myAnnots = []

        properties = repInfo.findall(".//{http://schema.openpreservation.org/ois/xml/ns/jhove}property")

        for property in properties:
            name = property.find("{http://schema.openpreservation.org/ois/xml/ns/jhove}name")
            if name.text == "Annotation":
                annotProps = property
                for property in annotProps:
                    name = property.findall(".//{http://schema.openpreservation.org/ois/xml/ns/jhove}name")
                    try:
                        if name[0].text == "Subtype":
                            subtypeProps = property
                            subType = subtypeProps.findall(".//{http://schema.openpreservation.org/ois/xml/ns/jhove}value")[0].text
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

