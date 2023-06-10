#! /usr/bin/env python3

import argparse
import pandas as pd
import math
import numpy as np
from scipy import stats
from tabulate import tabulate

"""
Script creates contingency tables for comparison between JHOVE/VeraPDF output
and observed groundtruth for Lindlar-Tunnat-Wilson data set.
"""

def dfToMarkdown(dataframe, headers='keys'):
    """Convert Data Frame to Markdown table with optionally custom headers"""
    mdOut = dataframe.pipe(tabulate, headers=headers, tablefmt='pipe')
    return mdOut


def cramersV(contTable):

    """
    Calculate Cramer's V from contingency table
    Adapted from: https://towardsdatascience.com/correlation-when-pearsons-r-is-not-enough-aded72308635
    """
    #Calculate the chi-squared statistic and the p-value
    chi2, p, dof, expected = stats.chi2_contingency(contTable)

    #Calculate Cramer's V
    V = math.sqrt(chi2 / (contTable.values.sum()*min(contTable.shape[0]-1, contTable.shape[1]-1)))

    return V


def cramersVCorr(var1, var2):

    """ calculate Cramers V statistic for categorial-categorial association.
    uses correction from Bergsma and Wicher, 
    Journal of the Korean Statistical Society 42 (2013): 323-328
    Adapted from:  https://stackoverflow.com/a/39266194/1209004
    """
    confusion_matrix = pd.crosstab(var1, var2)
    chi2, p, dof, expected = stats.chi2_contingency(confusion_matrix)
    #n = confusion_matrix.sum()
    n = confusion_matrix.sum().sum()
    phi2 = chi2/n
    r,k = confusion_matrix.shape
    phi2corr = max(0, phi2 - ((k-1)*(r-1))/(n-1))    
    rcorr = r - ((r-1)**2)/(n-1)
    kcorr = k - ((k-1)**2)/(n-1)
    V = np.sqrt(phi2corr / min( (kcorr-1), (rcorr-1)))
    return V, p

def main():
    fileIn = "/home/johan/kb/pdf-risks/jhove-validation-errors/lindlar-tunnat-wilson-jhove-vera-rendering.csv"
    df = pd.read_csv(fileIn)

    # Replace JHOVE "Unknown" value with 'Not well-formed' (only 1 record)
    df['jhoveStatus'] = df['jhoveStatus'].replace(['Unknown'], 'Not well-formed')
    ## Test - does reducing no of categories the results?
    #df['jhoveStatus'] = df['jhoveStatus'].replace(['Well-Formed, but not valid'], 'Not well-formed')
    #df['jhoveStatus'] = df['jhoveStatus'].replace(['Well-Formed, but not valid'], 'Well-Formed and valid')

    # Simple contingency tables
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

    # Calculate corrected Cramer's V as a measure of association between JHOVE/VeraPDF
    # output and rendering results.
    # Note: since these are essentially ordinal data, more powerful measures such as
    # Kendall Tau and Somers' D, but these don't work if one of the variables is
    # dichotomic.
    # p-values are calculated from Chi squared test.
    # See: https://towardsdatascience.com/contingency-tables-chi-squared-and-cramers-v-ada4f93ec3fd
      
    cVJhove, pJhove = cramersVCorr(df['jhoveStatus'], df['rendersInAcrobat'])
    cVVeraErrors, pVeraErrors = cramersVCorr(df['veraParseErrors'], df['rendersInAcrobat'])
    cVVeraWarnings, pVeraWarnings = cramersVCorr(df['veraLogWarnings'], df['rendersInAcrobat'])

    print("Cramer's V (JHOVE): " + str(cVJhove) + " (p=" + str(("{:.5f}".format(round(pJhove, 5)))) + ")")
    print("Cramer's V (Vera Errors): " + str(cVVeraErrors) + " (p=" + str(("{:.5f}".format(round(pVeraErrors, 5)))) + ")")
    print("Cramer's V (Vera Warnings): " + str(cVVeraWarnings) + " (p=" + str(("{:.5f}".format(round(pVeraWarnings, 5)))) + ")")


if __name__ == "__main__":
    main()