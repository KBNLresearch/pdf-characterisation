#! /usr/bin/env python3

import os
import sys
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


def cramersVThresh(var1, var2):
    """
    Prints the degrees of freedom, effect size thresholds, and Cramer's V value.
    
    Adapted from:

    https://towardsdatascience.com/contingency-tables-chi-squared-and-cramers-v-ada4f93ec3fd

    """

    cross_tabs = pd.crosstab(var1, var2)

    # effect size data frame for cramer's v function
    data = np.array([[1, .1, .3, .5],
       [2, .07, .21, .35],
       [3, .06, .17, .29],
       [4, .05,.15,.25],
       [5, .04, .13, .22]])
    
    sizes = pd.DataFrame(data, columns=['Degrees of Freedom', 'Small Effect', 'Medium Effect', 'Large Effect']) 
    
    # getting the chi sq. stat
    chi2 = stats.chi2_contingency(cross_tabs)[0]
    
    # calculating the total number of observations
    n = cross_tabs.sum().sum()
    # getting the degrees of freedom
    dof = min(cross_tabs.shape)-1
    # calculating cramer's v
    v = np.sqrt(chi2/(n*dof))
    
    """
    # printing results
    print(f'V = {v}')
    print(f'Cramer\'s V Degrees of Freedom = {dof}')
    print(f'\nEffect Size Thresholds\n{sizes}\n')
    """
    return v, dof

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
    scriptPath = os.path.split(os.path.realpath(__file__))[0]
    repoRoot = os.path.dirname(scriptPath)
    print(repoRoot)
    fileIn = os.path.join(repoRoot, "misc/lindlar-tunnat-wilson/lindlar-tunnat-wilson-jhove-vera-rendering.csv")
    df = pd.read_csv(fileIn)

    # Replace JHOVE "Unknown" value with 'Not well-formed' (only 1 record)
    df['jhoveStatus'] = df['jhoveStatus'].replace(['Unknown'], 'Not well-formed')

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
    dfTemp = df.copy()

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