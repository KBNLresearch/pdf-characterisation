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
validation status and VeraPDF parse errors and logged warnings. Results are
summarised in CSV file that can be further analyzed with script
jhove-verapdf-validation-analyze.py.

Python requirements:

- Pandas (https://pypi.org/project/pandas/)

Other requirements:

- JHOVE (tested with v. 1.28.0)
- veraPDF (tested with v. 1.22.3)
"""

# Locations of JHOVE and VeraPDF
jhoveBin = os.path.abspath("/home/johan/jhove/jhove")
veraPDFBin = os.path.abspath("/home/johan/verapdf/verapdf")

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
                        help="output directory"),
    parser.add_argument('--existingoutput', '-e',
                        action="store_true",
                        dest="existingOutputFlag",
                        default=False,
                        help="don't run JHOVE and VeraPDF, but use existing output")

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

    # Write output (stdout) to file
    with open(fileOut, 'wb') as f:
        f.write(output)


def getJhoveResults(fileIn):

    """
    Return validation status from JHOVE output
    """

    tree = ET.parse(fileIn)
    root = tree.getroot()

    repInfo = root.find(".//{http://schema.openpreservation.org/ois/xml/ns/jhove}repInfo")

    statusElt = repInfo.find(".//{http://schema.openpreservation.org/ois/xml/ns/jhove}status")
    status = statusElt.text

    return status


def getVeraPDFResults(fileIn):

    """
    Return two Boolean flags that indicate if VeraPDF output contains any parse errors
    or logged warnings 
    """

    tree = ET.parse(fileIn)
    root = tree.getroot()

    job = root.find(".//job")
        
    parseErrors = False
    logErrors = False # Don't think these are even a thing in VeraPDF?
    logWarnings = False

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
        logMessages = job.findall(".//logs/logMessage")

        for logMessage in logMessages:
            level = logMessage.get("level")
            if level == "WARNING":
                    logWarnings = True
            if level == "ERROR":
                    logErrors = True
    except:
            pass

    return parseErrors, logWarnings


def main():
    """Main processing loop"""

    # User input
    args = parseCommandLine()   
    dirIn = os.path.abspath(args.dirIn)
    dirOut = os.path.abspath(args.dirOut)
    existingOutputFlag = args.existingOutputFlag

    # Check if input directory exists
    if not os.path.isdir(dirIn):
        errorExit("input directory does not exist")

    # Create output directory if it doesn't exist already
    if not os.path.isdir(dirOut):
        os.makedirs(dirOut)

    # Create dictionary that will contain extracted data
    dataDict = {
                "fileName": [],
                "jhoveStatus": [],
                "veraParseErrors": [],
                "veraLogWarnings": []
    }

    # Create list of all files with .pdf extension in dirIn
    pdfsIn = glob.glob(dirIn + '/*.pdf')

    # Process all files, and add results to dictionary
    for pdfIn in pdfsIn:

        # Strip path to get file name
        fileName = os.path.basename(pdfIn)
        # Strip file extension to get base name
        baseName = os.path.splitext(fileName)[0]

        # Generate JHOVE and VeraPDF output file names
        outJhove = os.path.join(dirOut, baseName + "-jhove.xml")
        outVeraPDF = os.path.join(dirOut, baseName + "-vera.xml")

        if not existingOutputFlag:
            # Run JHOVE and VeraPDF
            runJhove(jhoveBin, pdfIn, outJhove)
            runVeraPDF(veraPDFBin, pdfIn, outVeraPDF)

        # Get JHOVE validation status from output file
        try:
            jhoveStatus = getJhoveResults(outJhove)
        except FileNotFoundError:
             errorExit("JHOVE output files not found, try running without --existingoutput option")

        # Get Boolean flags that indicate parse errors or log warnings
        # in VeraPDF output file
        try:
            veraParseErrors, veraLogWarnings = getVeraPDFResults(outVeraPDF)
        except FileNotFoundError:
             errorExit("VeraPDF output files not found, try running without --existingoutput option")
    
        # Updata data dictionary
        dataDict["fileName"].append(fileName)
        dataDict["jhoveStatus"].append(jhoveStatus)
        dataDict["veraParseErrors"].append(veraParseErrors)
        dataDict["veraLogWarnings"].append(veraLogWarnings)

    # Convert dictionary to dataframe
    df = pd.DataFrame(dataDict)

     # Write all data to a CSV file
    csvOut = os.path.join(dirOut, "data.csv")
    df.to_csv(csvOut, encoding='utf-8', index=False)


if __name__ == "__main__":
    main()