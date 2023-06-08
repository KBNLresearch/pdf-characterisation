#! /usr/bin/env python3

import argparse
import pandas as pd
from tabulate import tabulate

"""
Script creates contingency tables for comparison between JHOVE/VeraPDF output
and observed groundtruth for Lindlar-Tunnat-Wilson data set.
"""

def dfToMarkdown(dataframe, headers='keys'):
    """Convert Data Frame to Markdown table with optionally custom headers"""
    mdOut = dataframe.pipe(tabulate, headers=headers, tablefmt='pipe')
    return mdOut

def main():
    fileIn = "/home/johan/kb/pdf-risks/jhove-validation-errors/lindlar-tunnat-wilson-jhove-vera-rendering.csv"
    df = pd.read_csv(fileIn)
    contTabJHOVE = pd.crosstab(index=df['jhoveStatus'], columns=df['rendersInAcrobat'], margins=True)
    contTabVeraParseErrors = pd.crosstab(index=df['veraParseErrors'], columns=df['rendersInAcrobat'], margins=True)
    contTabVeraWarnings = pd.crosstab(index=df['veraLogWarnings'], columns=df['rendersInAcrobat'], margins=True)

    contTabJHOVEMd = dfToMarkdown(contTabJHOVE, headers=['JHOVE status', "Doesn't render", 'Renders', 'Renders with issues', 'All'])
    contTabVeraParseErrorsMd = dfToMarkdown(contTabVeraParseErrors, headers=['Results in VeraPDF parse errors', "Doesn't render", 'Renders', 'Renders with issues', 'All'])
    contTabVeraWarningsMd = dfToMarkdown(contTabVeraWarnings, headers=['Results in VeraPDF warnings', "Doesn't render", 'Renders', 'Renders with issues', 'All'])

    with open("jhove-rendering.md", 'w') as f:
        f.write(contTabJHOVEMd)
    with open("vera-parserr-rendering.md", 'w') as f:
        f.write(contTabVeraParseErrorsMd)
    with open("vera-warn-rendering.md", 'w') as f:
        f.write(contTabVeraWarningsMd)

if __name__ == "__main__":
    main()