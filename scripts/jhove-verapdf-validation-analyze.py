#! /usr/bin/env python3

"""
Script creates contingency tables for comparison between JHOVE/VeraPDF output
and observed groundtruth for Lindlar-Tunnat-Wilson data set.

Python requirements:

- Pandas (https://pypi.org/project/pandas/)
- Tabulate https://pypi.org/project/tabulate/)

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
    return V, p, dof


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

    ## ***********************************************************************
    ## Simple contingency tables
    ## ***********************************************************************

    # JHOVE vs VeraPDF metrics
    contTabJHOVEVeraErrors = pd.crosstab(index=df['jhoveStatus'], columns=df['veraParseErrors'], margins=True)
    contTabJHOVEVeraWarnings = pd.crosstab(index=df['jhoveStatus'], columns=df['veraLogWarnings'], margins=True)

    # JHOVE/ VeraPDF metrics vs rendering
    contTabJHOVE = pd.crosstab(index=df['rendersInAcrobat'], columns=df['jhoveStatus'], margins=True)
    contTabVeraParseErrors = pd.crosstab(index=df['rendersInAcrobat'], columns=df['veraParseErrors'], margins=True)
    contTabVeraWarnings = pd.crosstab(index=df['rendersInAcrobat'], columns=df['veraLogWarnings'], margins=True)

    # Change order of JHOVE/VeraPDF and rendering metrics so we go from "worst" to "best"
    jhove_index = ['Not well-formed', 'Well-Formed, but not valid', 'Well-Formed and valid', 'All']
    vera_index = [True, False, 'All']
    render_index = ['No', 'YesWithIssues', 'Yes', 'All']

    contTabJHOVEVeraErrors = contTabJHOVEVeraErrors.reindex(jhove_index)
    contTabJHOVEVeraErrors = contTabJHOVEVeraErrors.reindex(columns=vera_index)

    contTabJHOVEVeraWarnings = contTabJHOVEVeraWarnings.reindex(jhove_index)
    contTabJHOVEVeraWarnings = contTabJHOVEVeraWarnings.reindex(columns=vera_index)

    contTabJHOVE = contTabJHOVE.reindex(render_index)
    contTabJHOVE = contTabJHOVE.reindex(columns=jhove_index)

    contTabVeraParseErrors = contTabVeraParseErrors.reindex(render_index)
    contTabVeraParseErrors = contTabVeraParseErrors.reindex(columns=vera_index)

    contTabVeraWarnings = contTabVeraWarnings.reindex(render_index)
    contTabVeraWarnings = contTabVeraWarnings.reindex(columns=vera_index)

    contTabJHOVEVeraErrorsMd = dfToMarkdown(contTabJHOVEVeraErrors)
    contTabJHOVEVeraWarningsMd = dfToMarkdown(contTabJHOVEVeraWarnings)
    contTabVeraWarningsMd = dfToMarkdown(contTabVeraWarnings)
    contTabJHOVEMd = dfToMarkdown(contTabJHOVE)
    contTabVeraParseErrorsMd = dfToMarkdown(contTabVeraParseErrors)
    contTabVeraWarningsMd = dfToMarkdown(contTabVeraWarnings)

    with open("jhove-vera-parserr.md", 'w', encoding='utf-8') as f:
        f.write(contTabJHOVEVeraErrorsMd)
    with open("jhove-vera-warn.md", 'w', encoding='utf-8') as f:
        f.write(contTabJHOVEVeraWarningsMd)
    with open("jhove-rendering.md", 'w', encoding='utf-8') as f:
        f.write(contTabJHOVEMd)
    with open("vera-parserr-rendering.md", 'w', encoding='utf-8') as f:
        f.write(contTabVeraParseErrorsMd)
    with open("vera-warn-rendering.md", 'w', encoding='utf-8') as f:
        f.write(contTabVeraWarningsMd)

    # Express associations between JHOVE / VeraPDF metrics and with rendering outcomes using 
    # corrected Cramer's V statistic.
    # Note: since these are essentially ordinal data, more powerful measures such as
    # Kendall Tau and Somers' D, but these don't work if one of the variables is
    # dichotomic.
    # p-values are calculated from Chi squared test.
    # See: https://towardsdatascience.com/contingency-tables-chi-squared-and-cramers-v-ada4f93ec3fd

    # Create dataframe for Cramer's V reporting
    dfV = pd.DataFrame({'desc': [], 'V': [], 'p': [], 'dof': []})

    ## ***********************************************************************
    ## JHOVE vs VeraPDF metrics
    ## ***********************************************************************

    desc = "JHOVE status vs VeraPDF parse errors"
    V, p, dof = cramersVCorr(df['jhoveStatus'], df['veraParseErrors'])
    row = pd.Series([desc, V, p, dof], index=['desc', 'V', 'p', 'dof'])
    dfV = dfV.append(row, ignore_index=True)

    desc = "JHOVE status vs VeraPDF warnings"
    V, p, dof = cramersVCorr(df['jhoveStatus'], df['veraLogWarnings'])
    row = pd.Series([desc, V, p, dof], index=['desc', 'V', 'p', 'dof'])
    dfV = dfV.append(row, ignore_index=True)

    # Save original dataframe state
    dfTemp = df.copy()

    ## ***********************************************************************
    ## Test effect of lumping JHOVE status classes
    ## ***********************************************************************

    # Lump JHOVE's 'Well-Formed, but not valid' and 'Not well-formed' classes"
    df['jhoveStatus'] = df['jhoveStatus'].replace(['Well-Formed, but not valid'], 'Not well-formed')

    desc = "JHOVE status vs VeraPDF parse errors (lumping JHOVE's 'Well-Formed, but not valid' and 'Not well-formed' classes)"
    V, p, dof = cramersVCorr(df['jhoveStatus'], df['veraParseErrors'])
    row = pd.Series([desc, V, p, dof], index=['desc', 'V', 'p', 'dof'])
    dfV = dfV.append(row, ignore_index=True)

    desc = "JHOVE status vs VeraPDF warnings (lumping JHOVE's 'Well-Formed, but not valid' and 'Not well-formed' classes)"
    V, p, dof = cramersVCorr(df['jhoveStatus'], df['veraLogWarnings'])
    row = pd.Series([desc, V, p, dof], index=['desc', 'V', 'p', 'dof'])
    dfV = dfV.append(row, ignore_index=True)

    # Revert dataframe to original state
    df = dfTemp.copy()

    # Lump JHOVE's 'Well-Formed, but not valid' and 'Well-Formed and valid'
    df['jhoveStatus'] = df['jhoveStatus'].replace(['Well-Formed, but not valid'], 'Well-Formed and valid')

    desc = "JHOVE status vs VeraPDF parse errors (lumping JHOVE's 'Well-Formed, but not valid' and 'Well-Formed and valid' classes)"
    V, p, dof = cramersVCorr(df['jhoveStatus'], df['veraParseErrors'])
    row = pd.Series([desc, V, p, dof], index=['desc', 'V', 'p', 'dof'])
    dfV = dfV.append(row, ignore_index=True)

    desc = "JHOVE status vs VeraPDF warnings (lumping JHOVE's 'Well-Formed, but not valid' and 'Well-Formed and valid' classes)"
    V, p, dof = cramersVCorr(df['jhoveStatus'], df['veraLogWarnings'])
    row = pd.Series([desc, V, p, dof], index=['desc', 'V', 'p', 'dof'])
    dfV = dfV.append(row, ignore_index=True)

    # Revert dataframe to original state
    df = dfTemp.copy()

    ## ***********************************************************************
    ## JHOVE/VeraPDF metrics vs rendering results
    ## ***********************************************************************

    desc = 'JHOVE status vs rendering'
    V, p, dof = cramersVCorr(df['jhoveStatus'], df['rendersInAcrobat'])
    row = pd.Series([desc, V, p, dof], index=['desc', 'V', 'p', 'dof'])
    dfV = dfV.append(row, ignore_index=True)

    desc = 'VeraPDF parse errors vs rendering'
    V, p, dof = cramersVCorr(df['veraParseErrors'], df['rendersInAcrobat'])
    row = pd.Series([desc, V, p, dof], index=['desc', 'V', 'p', 'dof'])
    dfV = dfV.append(row, ignore_index=True)

    desc = 'VeraPDF parse warnings vs rendering'
    V, p, dof = cramersVCorr(df['veraLogWarnings'], df['rendersInAcrobat'])
    row = pd.Series([desc, V, p, dof], index=['desc', 'V', 'p', 'dof'])
    dfV = dfV.append(row, ignore_index=True)

    ## ***********************************************************************
    ## Test effect of lumping JHOVE status classes
    ## ***********************************************************************

    # Lump JHOVE's 'Well-Formed, but not valid' and 'Not well-formed' classes
    df['jhoveStatus'] = df['jhoveStatus'].replace(['Well-Formed, but not valid'], 'Not well-formed')

    desc = "JHOVE status vs rendering (lumping JHOVE's 'Well-Formed, but not valid' and 'Not well-formed' classes)"
    V, p, dof = cramersVCorr(df['jhoveStatus'], df['rendersInAcrobat'])
    row = pd.Series([desc, V, p, dof], index=['desc', 'V', 'p', 'dof'])
    dfV = dfV.append(row, ignore_index=True)

    # Revert dataframe to original state
    df = dfTemp.copy()

    # Lump JHOVE's 'Well-Formed, but not valid' and 'Well-Formed and valid' classes
    df['jhoveStatus'] = df['jhoveStatus'].replace(['Well-Formed, but not valid'], 'Well-Formed and valid')

    desc = "JHOVE status vs rendering (lumping JHOVE's 'Well-Formed, but not valid' and 'Well-Formed and valid' classes)"
    V, p, dof = cramersVCorr(df['jhoveStatus'], df['rendersInAcrobat'])
    row = pd.Series([desc, V, p, dof], index=['desc', 'V', 'p', 'dof'])
    dfV = dfV.append(row, ignore_index=True)

    # Revert dataframe to original state
    df = dfTemp.copy()

    ## ***********************************************************************
    ## Test effect of lumping rendering classes
    ## ***********************************************************************

    # Lump 'Yes' and 'YesWithIssues' rendering classes
    df['rendersInAcrobat'] = df['rendersInAcrobat'].replace(['YesWithIssues'], 'Yes')

    desc = "JHOVE status vs rendering (lumping 'Yes' and 'YesWithIssues' rendering classes)"
    V, p, dof = cramersVCorr(df['jhoveStatus'], df['rendersInAcrobat'])
    row = pd.Series([desc, V, p, dof], index=['desc', 'V', 'p', 'dof'])
    dfV = dfV.append(row, ignore_index=True)

    desc = "VeraPDF parse errors vs rendering (lumping 'Yes' and 'YesWithIssues' rendering classes)"
    V, p, dof = cramersVCorr(df['veraParseErrors'], df['rendersInAcrobat'])
    row = pd.Series([desc, V, p, dof], index=['desc', 'V', 'p', 'dof'])
    dfV = dfV.append(row, ignore_index=True)

    desc = "VeraPDF parse warnings vs rendering (lumping 'Yes' and 'YesWithIssues' rendering classes)"
    V, p, dof = cramersVCorr(df['veraLogWarnings'], df['rendersInAcrobat'])
    row = pd.Series([desc, V, p, dof], index=['desc', 'V', 'p', 'dof'])
    dfV = dfV.append(row, ignore_index=True)

    # Revert dataframe to original state
    df = dfTemp.copy()

    # Lump 'No' and 'YesWithIssues' rendering classes
    df['rendersInAcrobat'] = df['rendersInAcrobat'].replace(['YesWithIssues'], 'No')

    desc = "JHOVE status vs rendering (lumping 'No' and 'YesWithIssues' rendering classes)"
    V, p, dof = cramersVCorr(df['jhoveStatus'], df['rendersInAcrobat'])
    row = pd.Series([desc, V, p, dof], index=['desc', 'V', 'p', 'dof'])
    dfV = dfV.append(row, ignore_index=True)

    desc = "VeraPDF parse errors vs rendering (lumping 'No' and 'YesWithIssues' rendering classes)"
    V, p, dof = cramersVCorr(df['veraParseErrors'], df['rendersInAcrobat'])
    row = pd.Series([desc, V, p, dof], index=['desc', 'V', 'p', 'dof'])
    dfV = dfV.append(row, ignore_index=True)

    desc = "VeraPDF parse warnings vs rendering (lumping 'No' and 'YesWithIssues' rendering classes)"
    V, p, dof = cramersVCorr(df['veraLogWarnings'], df['rendersInAcrobat'])
    row = pd.Series([desc, V, p, dof], index=['desc', 'V', 'p', 'dof'])
    dfV = dfV.append(row, ignore_index=True)

    dfVmd = dfToMarkdown(dfV)
    with open("statistics.md", 'w', encoding='utf-8') as f:
        f.write(dfVmd)


if __name__ == "__main__":
    main()