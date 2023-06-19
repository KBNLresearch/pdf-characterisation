#! /usr/bin/env python3

"""
Script creates contingency tables for comparison between JHOVE/VeraPDF output
and observed groundtruth for Lindlar-Tunnat-Wilson data set.
"""

import os
import sys
import argparse
import pandas as pd
import math
import numpy as np
from scipy import stats
from tabulate import tabulate


def dfToMarkdown(dataframe, headers='keys'):
    """Convert Data Frame to Markdown table with optionally custom headers"""
    mdOut = dataframe.pipe(tabulate, headers=headers, tablefmt='pipe')
    return mdOut


def cramersVCorr(var1, var2):

    """ calculate Cramers V statistic for categorial-categorial association.
    uses correction from Bergsma and Wicher, 
    Journal of the Korean Statistical Society 42 (2013): 323-328
    Adapted from:  https://stackoverflow.com/a/39266194/1209004
    """
    confusion_matrix = pd.crosstab(var1, var2)
    chi2, p, dof, expected = stats.chi2_contingency(confusion_matrix)
    n = confusion_matrix.sum().sum()
    phi2 = chi2/n
    r,k = confusion_matrix.shape
    phi2corr = max(0, phi2 - ((k-1)*(r-1))/(n-1))    
    rcorr = r - ((r-1)**2)/(n-1)
    kcorr = k - ((k-1)**2)/(n-1)
    V = np.sqrt(phi2corr / min( (kcorr-1), (rcorr-1)))
    return V, p


def main():
    """ Main function"""

    scriptPath = os.path.split(os.path.realpath(__file__))[0]
    repoRoot = os.path.dirname(scriptPath)
    print(repoRoot)
    fileIn = os.path.join(repoRoot, "misc/lindlar-tunnat-wilson/lindlar-tunnat-wilson-jhove-vera-rendering.csv")
    #fileIn = os.path.join(repoRoot, "misc/lindlar-tunnat-wilson/jhove-vera-rendering-test.csv")

    df = pd.read_csv(fileIn)

    # Replace JHOVE "Unknown" value with 'Not well-formed' (only 1 record)
    df['jhoveStatus'] = df['jhoveStatus'].replace(['Unknown'], 'Not well-formed')

    # Simple contingency tables
    
    contTabJHOVE = pd.crosstab(index=df['rendersInAcrobat'], columns=df['jhoveStatus'], margins=True)
    contTabVeraParseErrors = pd.crosstab(index=df['rendersInAcrobat'], columns=df['veraParseErrors'], margins=True)
    contTabVeraWarnings = pd.crosstab(index=df['rendersInAcrobat'], columns=df['veraLogWarnings'], margins=True)

    # Change order of JHOVE/VeraPDF and rendering metrics so we go from "worst" to "best"
    jhove_index = ['Not well-formed', 'Well-Formed, but not valid', 'Well-Formed and valid', 'All']
    vera_index = [True, False, 'All']
    render_index = ['No', 'YesWithIssues', 'Yes', 'All']

    contTabJHOVE = contTabJHOVE.reindex(render_index)
    contTabJHOVE = contTabJHOVE.reindex(columns=jhove_index)

    contTabVeraParseErrors = contTabVeraParseErrors.reindex(render_index)
    contTabVeraParseErrors = contTabVeraParseErrors.reindex(columns=vera_index)

    contTabVeraWarnings = contTabVeraWarnings.reindex(render_index)
    contTabVeraWarnings = contTabVeraWarnings.reindex(columns=vera_index)

    contTabJHOVEMd = dfToMarkdown(contTabJHOVE)
    contTabVeraParseErrorsMd = dfToMarkdown(contTabVeraParseErrors)
    contTabVeraWarningsMd = dfToMarkdown(contTabVeraWarnings)
    
    with open("jhove-rendering.md", 'w') as f:
        f.write(contTabJHOVEMd)
    with open("vera-parserr-rendering.md", 'w') as f:
        f.write(contTabVeraParseErrorsMd)
    with open("vera-warn-rendering.md", 'w') as f:
        f.write(contTabVeraWarningsMd)

    # Calculate corrected Cramer's V as a measure of association between JHOVE validation
    # status and VeraPDF parsec errors and warnings/.
    # Note: since these are essentially ordinal data, more powerful measures such as
    # Kendall Tau and Somers' D, but these don't work if one of the variables is
    # dichotomic.
    # p-values are calculated from Chi squared test.
    # See: https://towardsdatascience.com/contingency-tables-chi-squared-and-cramers-v-ada4f93ec3fd
 
    cVJhoveVeraErr, pJhoveVeraErr = cramersVCorr(df['jhoveStatus'], df['veraParseErrors'])
    cVJhoveVeraWarn, pJhoveVeraWarn = cramersVCorr(df['jhoveStatus'], df['veraLogWarnings'])
  
    print()
    print("Cramer's V - JHOVE validation status vs VeraPDF parse errors and warnings")
    print("-------------------------------------------")
    print("Cramer's V (JHOVE - Vera Errors): " + str(cVJhoveVeraErr) + " (p=" + str(("{:.5f}".format(round(pJhoveVeraErr, 5)))) + ")")
    print("Cramer's V (JHOVE - Vera Warnings): " + str(cVJhoveVeraWarn) + " (p=" + str(("{:.5f}".format(round(pJhoveVeraWarn, 5)))) + ")")

    # Save original dataframe state
    dfTemp = df.copy()

    print()
    print("As original, but lumping JHOVE's 'Well-Formed, but not valid' and 'Not well-formed' values")
    print("-------------------------------------------")
    df['jhoveStatus'] = df['jhoveStatus'].replace(['Well-Formed, but not valid'], 'Not well-formed')

    cVJhoveVeraErr, pJhoveVeraErr = cramersVCorr(df['jhoveStatus'], df['veraParseErrors'])
    cVJhoveVeraWarn, pJhoveVeraWarn = cramersVCorr(df['jhoveStatus'], df['veraLogWarnings'])

    print("Cramer's V (JHOVE - Vera Errors): " + str(cVJhoveVeraErr) + " (p=" + str(("{:.5f}".format(round(pJhoveVeraErr, 5)))) + ")")
    print("Cramer's V (JHOVE - Vera Warnings): " + str(cVJhoveVeraWarn) + " (p=" + str(("{:.5f}".format(round(pJhoveVeraWarn, 5)))) + ")")

    # Revert dataframe to original state
    df = dfTemp.copy()

    print()
    print("As original, but lumping JHOVE's 'Well-Formed, but not valid' and 'Well-Formed and valid'")
    print("-------------------------------------------")
    df['jhoveStatus'] = df['jhoveStatus'].replace(['Well-Formed, but not valid'], 'Well-Formed and valid')

    cVJhoveVeraErr, pJhoveVeraErr = cramersVCorr(df['jhoveStatus'], df['veraParseErrors'])
    cVJhoveVeraWarn, pJhoveVeraWarn = cramersVCorr(df['jhoveStatus'], df['veraLogWarnings'])

    print("Cramer's V (JHOVE - Vera Errors): " + str(cVJhoveVeraErr) + " (p=" + str(("{:.5f}".format(round(pJhoveVeraErr, 5)))) + ")")
    print("Cramer's V (JHOVE - Vera Warnings): " + str(cVJhoveVeraWarn) + " (p=" + str(("{:.5f}".format(round(pJhoveVeraWarn, 5)))) + ")")

    # Revert dataframe to original state
    df = dfTemp.copy()

    # Calculate corrected Cramer's V as a measure of association between JHOVE/VeraPDF
    # output and rendering results.

    cVJhove, pJhove = cramersVCorr(df['jhoveStatus'], df['rendersInAcrobat'])
    cVVeraErrors, pVeraErrors = cramersVCorr(df['veraParseErrors'], df['rendersInAcrobat'])
    cVVeraWarnings, pVeraWarnings = cramersVCorr(df['veraLogWarnings'], df['rendersInAcrobat'])

    print()
    print("Cramer's V - JHOVE validation status and VeraPDF parse errors and warnings vs rendering")
    print("-------------------------------------------")

    print("Cramer's V (JHOVE): " + str(cVJhove) + " (p=" + str(("{:.5f}".format(round(pJhove, 5)))) + ")")
    print("Cramer's V (Vera Errors): " + str(cVVeraErrors) + " (p=" + str(("{:.5f}".format(round(pVeraErrors, 5)))) + ")")
    print("Cramer's V (Vera Warnings): " + str(cVVeraWarnings) + " (p=" + str(("{:.5f}".format(round(pVeraWarnings, 5)))) + ")")

    ## Additional tests to see if reducing no. of JHOVE categories influences the results

    # Save original dataframe state
    #dfTemp = df.copy()

    print()
    print("As original, but lumping JHOVE's 'Well-Formed, but not valid' and 'Not well-formed' values")
    print("-------------------------------------------")
    df['jhoveStatus'] = df['jhoveStatus'].replace(['Well-Formed, but not valid'], 'Not well-formed')

    cVJhove, pJhove = cramersVCorr(df['jhoveStatus'], df['rendersInAcrobat'])
    cVVeraErrors, pVeraErrors = cramersVCorr(df['veraParseErrors'], df['rendersInAcrobat'])
    cVVeraWarnings, pVeraWarnings = cramersVCorr(df['veraLogWarnings'], df['rendersInAcrobat'])

    print("Cramer's V (JHOVE): " + str(cVJhove) + " (p=" + str(("{:.5f}".format(round(pJhove, 5)))) + ")")
    print("Cramer's V (Vera Errors): " + str(cVVeraErrors) + " (p=" + str(("{:.5f}".format(round(pVeraErrors, 5)))) + ")")
    print("Cramer's V (Vera Warnings): " + str(cVVeraWarnings) + " (p=" + str(("{:.5f}".format(round(pVeraWarnings, 5)))) + ")")

    # Revert dataframe to original state
    df = dfTemp.copy()

    print()
    print("As original, but lumping JHOVE's 'Well-Formed, but not valid' and 'Well-Formed and valid'")
    print("-------------------------------------------")
    df['jhoveStatus'] = df['jhoveStatus'].replace(['Well-Formed, but not valid'], 'Well-Formed and valid')

    cVJhove, pJhove = cramersVCorr(df['jhoveStatus'], df['rendersInAcrobat'])
    cVVeraErrors, pVeraErrors = cramersVCorr(df['veraParseErrors'], df['rendersInAcrobat'])
    cVVeraWarnings, pVeraWarnings = cramersVCorr(df['veraLogWarnings'], df['rendersInAcrobat'])

    print("Cramer's V (JHOVE): " + str(cVJhove) + " (p=" + str(("{:.5f}".format(round(pJhove, 5)))) + ")")
    print("Cramer's V (Vera Errors): " + str(cVVeraErrors) + " (p=" + str(("{:.5f}".format(round(pVeraErrors, 5)))) + ")")
    print("Cramer's V (Vera Warnings): " + str(cVVeraWarnings) + " (p=" + str(("{:.5f}".format(round(pVeraWarnings, 5)))) + ")")

    # Revert dataframe to original state
    df = dfTemp.copy()

    ## Additional tests to see if reducing no. of rendering categories influences the results

    print()
    print("As original, but lumping 'Yes' and 'YesWithIssues' rendering values")
    print("-------------------------------------------")

    df['rendersInAcrobat'] = df['rendersInAcrobat'].replace(['YesWithIssues'], 'Yes')

    cVJhove, pJhove = cramersVCorr(df['jhoveStatus'], df['rendersInAcrobat'])
    cVVeraErrors, pVeraErrors = cramersVCorr(df['veraParseErrors'], df['rendersInAcrobat'])
    cVVeraWarnings, pVeraWarnings = cramersVCorr(df['veraLogWarnings'], df['rendersInAcrobat'])

    print("Cramer's V (JHOVE): " + str(cVJhove) + " (p=" + str(("{:.5f}".format(round(pJhove, 5)))) + ")")
    print("Cramer's V (Vera Errors): " + str(cVVeraErrors) + " (p=" + str(("{:.5f}".format(round(pVeraErrors, 5)))) + ")")
    print("Cramer's V (Vera Warnings): " + str(cVVeraWarnings) + " (p=" + str(("{:.5f}".format(round(pVeraWarnings, 5)))) + ")")

    # Revert dataframe to original state
    df = dfTemp.copy()

    print()
    print("As original, but lumping 'No' and 'YesWithIssues' rendering values")
    print("-------------------------------------------")

    df['rendersInAcrobat'] = df['rendersInAcrobat'].replace(['YesWithIssues'], 'No')

    cVJhove, pJhove = cramersVCorr(df['jhoveStatus'], df['rendersInAcrobat'])
    cVVeraErrors, pVeraErrors = cramersVCorr(df['veraParseErrors'], df['rendersInAcrobat'])
    cVVeraWarnings, pVeraWarnings = cramersVCorr(df['veraLogWarnings'], df['rendersInAcrobat'])

    print("Cramer's V (JHOVE): " + str(cVJhove) + " (p=" + str(("{:.5f}".format(round(pJhove, 5)))) + ")")
    print("Cramer's V (Vera Errors): " + str(cVVeraErrors) + " (p=" + str(("{:.5f}".format(round(pVeraErrors, 5)))) + ")")
    print("Cramer's V (Vera Warnings): " + str(cVVeraWarnings) + " (p=" + str(("{:.5f}".format(round(pVeraWarnings, 5)))) + ")")

if __name__ == "__main__":
    main()