#! /usr/bin/env python3

import argparse
import pandas as pd
from tabulate import tabulate

# Create parser
parser = argparse.ArgumentParser(
description="Create Markdown-formatted contingency tables between JHOVE validation status and VeraPDF parse errors and warnings")

def parseCommandLine():
    # Add arguments
    
    parser.add_argument('fileIn',
                        action="store",
                        type=str,
                        help="input file")

    # Parse arguments
    args = parser.parse_args()

    return(args)

def dfToMarkdown(dataframe, headers='keys'):
    """Convert Data Frame to Markdown table with optionally custom headers"""
    mdOut = dataframe.pipe(tabulate, headers=headers, tablefmt='pipe')
    return mdOut

def createTables(fileIn):
    outStr = ""
    df = pd.read_csv(fileIn)
    contTabParseErrors = pd.crosstab(index=df['statusJHOVE'], columns=df['parseErrorsVera'], margins=True)
    contTabWarnings = pd.crosstab(index=df['statusJHOVE'], columns=df['warningsVera'], margins=True)
    outStr += dfToMarkdown(contTabParseErrors, headers=['JHOVE status', 'No VeraPDF parse errors', 'VeraPDF parse errors', 'All'])
    outStr += "\n\n"
    outStr += dfToMarkdown(contTabWarnings, headers=['JHOVE status', 'No VeraPDF warnings', 'VeraPDF warnings', 'All'])
    return outStr

def main():
    args = parseCommandLine()
    fileIn = args.fileIn
    outStr = createTables(fileIn)
    print(outStr)

if __name__ == "__main__":
    main()