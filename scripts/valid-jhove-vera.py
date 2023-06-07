#! /usr/bin/env python3

import os
import sys
import glob
import argparse
import subprocess as sub
import xml.etree.ElementTree as ET
import pandas as pd
from tabulate import tabulate

"""
This script runs both JHOVE and VeraPDF on all files with a .pdf extension,
and then extracts information that allows for a comparison between JHOVE
validation status and VeraPDF parse errors and logged warnings.
"""

# Create parser
parser = argparse.ArgumentParser()

def parseCommandLine():
    # Add arguments
    
    parser.add_argument('dirIn',
                        action="store",
                        type=str,
                        help="input directory")
    parser.add_argument('dirOut',
                        action="store",
                        type=str,
                        help="output directory")
    # Parse arguments
    args = parser.parse_args()

    return(args)


def errorExit(msg):
    """Print error to stderr and exit"""
    msgString = ("Error: " + msg + "\n")
    sys.stderr.write(msgString)
    sys.exit(1)


def runJhove(jhoveBin, fileIn, fileOut):

    """
    Run JHOVE on one PDF
    """
    args = [jhoveBin]
    args.append('-m')
    args.append('PDF-hul')
    args.append('-h')
    args.append('XML')
    args.append('-i')
    args.append(fileIn)
    args.append('-o')
    args.append(fileOut)

    p = sub.Popen(args, stdout=sub.PIPE, stderr=sub.PIPE, shell=False)
    output, errors = p.communicate()


def runVeraPDF(veraPDFBin, fileIn, fileOut):

    """
    Run VeraPDF on one PDF
    """
    args = [veraPDFBin]
    args.append('--off')
    args.append('--addlogs')
    args.append('--extract')
    args.append(fileIn)

    p = sub.Popen(args, stdout=sub.PIPE, stderr=sub.PIPE, shell=False)
    output, errors = p.communicate()

    with open(fileOut, 'wb') as f:
        f.write(output)


def main():

    # User input
    args = parseCommandLine()   
    dirIn = os.path.abspath(args.dirIn)
    dirOut = os.path.abspath(args.dirOut)

    # Check if input directory exists
    if not os.path.isdir(dirIn):
        errorExit("input directory does not exist")

    # Create output directory if it doesn't exist alread
    if not os.path.isdir(dirOut):
        os.makedirs(dirOut)

    # Locations of JHOVE and VeraPDF
    jhoveBin = os.path.abspath("/home/johan/jhove/jhove")
    veraPDFBin = os.path.abspath("/home/johan/verapdf/verapdf")

    # Create list of all files with .pdf extension in dirIn
    pdfsIn = glob.glob(dirIn + '/*.pdf')
    
    for pdfIn in pdfsIn:

        # Strip path to get file name
        fileName = os.path.basename(pdfIn)
        # Strip file extension to get base name
        baseName = os.path.splitext(fileName)[0]

        # Generate JHOVE and VeraPDF output file names
        outJhove = os.path.join(dirOut, baseName + "-jhove.xml")
        outVeraPDF = os.path.join(dirOut, baseName + "-vera.xml")

        # Run JHOVE and VeraPDF
        runJhove(jhoveBin, pdfIn, outJhove)
        runVeraPDF(veraPDFBin, pdfIn, outVeraPDF)



if __name__ == "__main__":
    main()