#!/usr/bin/python

import pandas as pd
from pandas import DataFrame, DateOffset

from pandas.tseries.offsets import *
#from pylab import rcParams
#import matplotlib.pyplot as plt
import pprint

import sys
#Path where the categorize.py is saved.
mypath = '/home/t7/Dropbox/dev/FinancialAnalyzer'
sys.path.append(mypath)
import categorize as categorize


def import_csv(pth):
    y = DataFrame.from_csv(pth, sep='\t', index_col=0)
    y = y.fillna('')
    return y


def import_tab(pth):
    c = ['accountNumber','mutationcode','startsaldo','endsaldo','transactiondate','amount','description']
    y= DataFrame.from_csv(pth, header=None, sep='\t', index_col=2)
    y.columns = c
    y['dayofweek'] = y.index.dayofweek
    y = y.fillna('-')
    return y


def save_to_file(fnpath, y):
    y.to_csv(fnpath+'bs_cats.csv', sep='\t')
  
def categorize_transactions(y):  
    cats = []
    subcats = []
    
    for index, row in y.iterrows():
        cc = 'TBD'
        ss = 'TBD'
        description = row['description']
        for cat_subcat in sorted(categorize.keywords):            
            s = cat_subcat.split('/')
            category    = s[0]
            subcategory = s[1]
            cat_keywords = categorize.keywords[cat_subcat]
            for kw in cat_keywords:
                if kw in description:
                    cc = category
                    ss = subcategory
                    break
        cats.append(cc)
        subcats.append(ss)
        
    y['category'] = cats
    y['subcategory'] = subcats
    return y


def totals_week_by_week(y):    
    #Start from Monday of first week
    start = y.index[0]
    start = start - DateOffset(days = start.dayofweek)
    #End on Sunday of last week
    endt   = y.index[-1]
    endt   = endt + DateOffset(days = (6 - endt.dayofweek))
    
    incomes = []
    outcomes = []
    totals = []
    index = []
    #pctgs = []
    while start < endt:
        end = start + DateOffset(days = 6)
        income  = y['amount'][y['amount']>0][start:end].sum()
        outcome = y['amount'][y['amount']<0][start:end].sum()
        total   = y['amount'][start:end].sum()
        incomes.append(income)
        outcomes.append(abs(outcome))
        totals.append(total)
        index.append(start)        
        #pctgs.append("{0:.2f}%".format(abs(100*outcome/income)))
        #print start, income, outcome, total
        start   = start + Week()
    r = {'In': incomes, 'Out': outcomes, 'Total': totals}#, 'Total pct': pctgs}
    t = DataFrame(r, index = index)
    return t
    
def totals_month_by_month(y):
    start = y.index[0] - MonthBegin()
    endt   = y.index[-1] + MonthEnd()
    incomes = []
    outcomes = []
    totals = []
    index = []
    pctgs = []
    while start < endt:
        end = start + MonthEnd()
        income  = y['amount'][y['amount']>0][start:end].sum()
        outcome = y['amount'][y['amount']<0][start:end].sum()
        total   = y['amount'][start:end].sum()
        incomes.append(income)
        outcomes.append(abs(outcome))
        totals.append(total)
        index.append(start)        
        pctgs.append("{0:.2f}%".format(abs(100*outcome/income)))
        #print start, income, outcome, total
        start   = start + DateOffset(months=1)
    r = {'In': incomes, 'Out': outcomes, 'Total': totals, 'Total pct': pctgs}
    t = DataFrame(r, index = index)
    return t

def totals_year_by_year(y):
    start = y.index[0] - YearBegin()
    endt   = y.index[-1] + YearEnd()
    incomes = []
    outcomes = []
    totals = []
    index = []
    pctgs = []
    while start < endt:
        end = start + YearEnd()
        income  = y['amount'][y['amount']>0][start:end].sum()
        outcome = y['amount'][y['amount']<0][start:end].sum()
        total   = y['amount'][start:end].sum()
        incomes.append(income)
        outcomes.append(abs(outcome))
        totals.append(total)
        index.append(start)
        pctgs.append("{0:.2f}%".format(abs(100*outcome/income)))
        #print start, income, outcome, total
        start   = start + DateOffset(years=1)
    r = {'In': incomes, 'Out': outcomes, 'Total': totals, 'Total pct': pctgs}
    t = DataFrame(r, index = index)
    return t

def totals_by_day_of_week(y):
    incomes = []
    outcomes = []
    totals = []
    index = []
    for i in range(0,7):
        income  = y['amount'][(y['amount'] > 0) & (y['dayofweek'] == i)].sum()
        outcome = y['amount'][(y['amount'] < 0) & (y['dayofweek'] == i)].sum()
        total   = y['amount'][y['dayofweek'] == i].sum()
        incomes.append(income)
        outcomes.append(abs(outcome))
        totals.append(total)
        index.append(i)        
        #print i, income, outcome, total
    r = {'In': incomes, 'Out': outcomes, 'Total': totals}
    t = DataFrame(r, index = index)
    return t

def totals_by_subcategory(y):
    cs = get_categories_and_subcategories(y)
    totals = []
    index = []
    pctgs = []
    pctgs_in = []
    income_all = 0
    for cat_subcat in sorted(cs):
        s = cat_subcat.split('/')
        category    = s[0]
        subcategory = s[1]
        t = filter_by_category_subcategory(y, category, subcategory)
        total = t['amount'].sum()        
        if total < 0:
            totals.append(abs(total))
            index.append(cat_subcat)
        else:
            income_all += total
    total_all = sum(totals)
    for t in totals:
        pctgs.append("{0:.2f}%".format(abs(100*t/total_all)))
        pctgs_in.append("{0:.2f}%".format(abs(100*t/income_all)))
    r = {'Total': totals, '% Expenses': pctgs, '% Income': pctgs_in}
    t = DataFrame(r, index = index)
    return t

def totals_by_category(y):
    c = get_categories(y)
    totals = []
    index = []
    pctgs = []
    pctgs_in = []
    income_all = 0
    for cat in sorted(c):
        t = filter_by_category(y, cat)
        total = t['amount'].sum()
        if total < 0:
            totals.append(abs(total))
            index.append(cat)
        else:
            income_all += total
    total_all = sum(totals)
    for t in totals:
        pctgs.append("{0:.2f}%".format(abs(100*t/total_all)))
        pctgs_in.append("{0:.2f}%".format(abs(100*t/income_all)))
    r = {'Total': totals, '% Expenses': pctgs, '% Income': pctgs_in}
    t = DataFrame(r, index = index)
    return t

def totals_categories_weekly(y):
    #Start from Monday of first week
    start = y.index[0]
    start = start - DateOffset(days = start.dayofweek)
    #End on Sunday of last week
    endt   = y.index[-1]
    endt   = endt + DateOffset(days = (6 - endt.dayofweek))

    rc  = {}
    while start < endt:
        end = start + DateOffset(days = 6)
        ym = y[start:end]
        tc = totals_by_category(ym)   
        tc = tc.drop('% Income', 1)

        rc[start.strftime('%Y%m%d')]  = tc
        start   = start + Week()
    return rc

def totals_subcategories_weekly(y):
    #Start from Monday of first week
    start = y.index[0]
    start = start - DateOffset(days = start.dayofweek)
    #End on Sunday of last week
    endt   = y.index[-1]
    endt   = endt + DateOffset(days = (6 - endt.dayofweek))

    rc  = {}
    while start < endt:
        end = start + DateOffset(days = 6)
        ym = y[start:end]
        tc = totals_by_subcategory(ym)   
        tc = tc.drop('% Income', 1)
      
        rc[start.strftime('%Y%m%d')]  = tc
        start   = start + Week()
    return rc
    
def totals_categories_monthly(y):
    start = y.index[0] - MonthBegin()
    endt   = y.index[-1] + MonthEnd()
    rc  = {}
    while start < endt:
        end = start + MonthEnd()
        ym = y[start:end]
        tc  = totals_by_category(ym)        
        rc[start.strftime('%Y%m')]  = tc
        start   = start + DateOffset(months=1)
    return rc
    
def totals_subcategories_monthly(y):
    start = y.index[0] - MonthBegin()
    endt   = y.index[-1] + MonthEnd()
    rcs = {}
    while start < endt:
        end = start + MonthEnd()
        ym = y[start:end]
        tcs = totals_by_subcategory(ym)        
        rcs[start.strftime('%Y%m')] = tcs
        start   = start + DateOffset(months=1)
    return rcs

def totals_categories_yearly(y):
    start = y.index[0] - YearBegin()
    endt   = y.index[-1] + YearEnd()
    rc  = {}
    while start < endt:
        end = start + YearEnd()
        ym = y[start:end]
        tc  = totals_by_category(ym)        
        rc[start.strftime('%Y')]  = tc
        start   = start + DateOffset(years=1)
    return rc
    
def totals_subcategories_yearly(y):
    start = y.index[0] - YearBegin()
    endt   = y.index[-1] + YearEnd()
    rcs = {}
    while start < endt:
        end = start + YearEnd()
        ym = y[start:end]
        tcs = totals_by_subcategory(ym)
        rcs[start.strftime('%Y')] = tcs
        start   = start + DateOffset(years=1)
    return rcs

def average_categories_per_year(y):
    rc = totals_categories_yearly(y)
    c = get_categories(y)
    avgs_tot = []
    avgs_exs = []
    index = []
    
    for cat in c:
        sum_totals    = 0
        n_total       = 0
        n_no_exists   = 0
        for year in rc.keys():
            try:
                s = rc[year]['Total'][cat]
            except Exception:
                s = 0
                n_no_exists += 1
            sum_totals += s    
            n_total += 1
        n_exists = n_total-n_no_exists        
        avg_total  = sum_totals/n_total
        if n_exists > 0:
            avg_exists = sum_totals/n_exists
            index.append(cat)
            avgs_tot.append(avg_total)
            avgs_exs.append(avg_exists)
        
    r = {'Avg. Total': avgs_tot, 'Avg. when used': avgs_exs}
    t = DataFrame(r, index = index)
    return t


def average_subcategories_per_year(y):
    rc = totals_subcategories_yearly(y)
    c = get_categories_and_subcategories(y)
    avgs_tot = []
    avgs_exs = []
    index = []
    
    for cat in c:
        sum_totals    = 0
        n_total       = 0
        n_no_exists   = 0
        for year in rc.keys():
            try:
                s = rc[year]['Total'][cat]
            except Exception:
                s = 0
                n_no_exists += 1
            sum_totals += s    
            n_total += 1
        n_exists = n_total-n_no_exists        
        avg_total  = sum_totals/n_total
        if n_exists > 0:
            avg_exists = sum_totals/n_exists
            index.append(cat)
            avgs_tot.append(avg_total)
            avgs_exs.append(avg_exists)
        
    r = {'Avg. Total': avgs_tot, 'Avg. when used': avgs_exs}
    t = DataFrame(r, index = index)
    return t   

def average_categories_per_month(y):
    rc = totals_categories_monthly(y)
    c = get_categories(y)
    avgs_tot = []
    avgs_exs = []
    index = []
    
    for cat in c:
        sum_totals    = 0
        n_total       = 0
        n_no_exists   = 0
        for month in rc.keys():
            try:
                s = rc[month]['Total'][cat]
            except Exception:
                s = 0
                n_no_exists += 1
            sum_totals += s    
            n_total += 1
        n_exists = n_total-n_no_exists        
        avg_total  = sum_totals/n_total
        if n_exists > 0:
            avg_exists = sum_totals/n_exists
            index.append(cat)
            avgs_tot.append(avg_total)
            avgs_exs.append(avg_exists)
        
    r = {'Avg. Total': avgs_tot, 'Avg. when used': avgs_exs}
    t = DataFrame(r, index = index)
    return t
    
def average_subcategories_per_month(y):
    rc = totals_subcategories_monthly(y)
    c = get_categories_and_subcategories(y)
    avgs_tot = []
    avgs_exs = []
    index = []
    
    for cat in c:
        sum_totals    = 0
        n_total       = 0
        n_no_exists   = 0
        for month in rc.keys():
            try:
                s = rc[month]['Total'][cat]
            except Exception:
                s = 0
                n_no_exists += 1
            sum_totals += s    
            n_total += 1
        n_exists = n_total-n_no_exists        
        avg_total  = sum_totals/n_total
        if n_exists > 0:
            avg_exists = sum_totals/n_exists
            index.append(cat)
            avgs_tot.append(avg_total)
            avgs_exs.append(avg_exists)
        
    r = {'Avg. Total': avgs_tot, 'Avg. when used': avgs_exs}
    t = DataFrame(r, index = index)
    return t   


def average_categories_per_week(y):
    rc = totals_categories_weekly(y)
    c = get_categories(y)
    avgs_tot = []
    avgs_exs = []
    index = []
    
    for cat in c:
        sum_totals    = 0
        n_total       = 0
        n_no_exists   = 0
        for week in rc.keys():
            try:
                s = rc[week]['Total'][cat]
            except Exception:
                s = 0
                n_no_exists += 1
            sum_totals += s    
            n_total += 1
        n_exists = n_total-n_no_exists        
        avg_total  = sum_totals/n_total
        if n_exists > 0:
            avg_exists = sum_totals/n_exists
            index.append(cat)
            avgs_tot.append(avg_total)
            avgs_exs.append(avg_exists)
        
    r = {'Avg. Total': avgs_tot, 'Avg. when used': avgs_exs}
    t = DataFrame(r, index = index)
    return t    
    
def average_subcategories_per_week(y):
    rc = totals_subcategories_weekly(y)
    c = get_categories_and_subcategories(y)
    avgs_tot = []
    avgs_exs = []
    index = []
    
    for cat in c:
        sum_totals    = 0
        n_total       = 0
        n_no_exists   = 0
        for week in rc.keys():
            try:
                s = rc[week]['Total'][cat]
            except Exception:
                s = 0
                n_no_exists += 1
            sum_totals += s    
            n_total += 1
        n_exists = n_total-n_no_exists        
        avg_total  = sum_totals/n_total
        if n_exists > 0:
            avg_exists = sum_totals/n_exists
            index.append(cat)
            avgs_tot.append(avg_total)
            avgs_exs.append(avg_exists)
        
    r = {'Avg. Total': avgs_tot, 'Avg. when used': avgs_exs}
    t = DataFrame(r, index = index)
    return t  
    

#TODO  weekly average per month, monthly average per year
def compare_expenses_weekly(y, l):
    totals_weekly = {}
    for category in l:
        if '/' in category:
            subcat = category.split('/')[1]
            cat = category.split('/')[0]
            yy = totals_week_by_week(filter_by_category_subcategory(y, cat, subcat))   
        else:
            yy = totals_week_by_week(filter_by_category(y, category))
        totals_weekly[category] = yy
    
    
    xxy = totals_weekly[sorted(totals_weekly.keys())[0]]['Out']
    xy  = DataFrame(xxy)
    for i in range(1,len(totals_weekly)):
        yy = totals_weekly[sorted(totals_weekly.keys())[i]]['Out']
        xy = pd.concat([xy, yy], axis=1).fillna(0)    
    xy.columns = [sorted(totals_weekly.keys()) ]    
            
#    yy = totals_week_by_week(fin.filter_by_category_subcategory(y,'Viveres','Super'))
#    xx = totals_week_by_week(fin.filter_by_category(y,'Comidas'))
#    xy = pd.concat([xx['Out'], yy['Out']], axis=1).fillna(0)
#    xy.columns = ['x','y']
    return xy

    
def get_categories_and_subcategories(y):
	groups = []
	for i,transaction in enumerate(y.index):
	    cat = y['category'].values[i]
	    subcat = y['subcategory'].values[i]
	    groups.append(cat + '/' + subcat)
	    
	categories_subcategories = list(set(groups))
	return sorted(categories_subcategories)

def get_subcategories(y):
	subcategories = list(set(y['subcategory']))
	return sorted(subcategories)
 
def get_categories(y):
	categories = list(set(y['category']))
	return sorted(categories)

def filter_by_date(y, sd, ed):
    start = pd.to_datetime(sd)
    end   = pd.to_datetime(ed)
    t = y[start:end]
    return t
    
def filter_by_description(y, regex):
    t = y[y['description'].str.contains(regex)]
    return t

def filter_by_category(y, category):
    t = y[y['category'] == category]
    return t
    
def filter_by_subcategory(y, subcategory):
    t = y[y['subcategory'] == subcategory]
    return t
    
def filter_by_category_subcategory(y, category, subcategory):
    t = y[(y['category'] == category) & (y['subcategory'] == subcategory)]
    return t
    
def print_dict(d):
    for t in sorted(d):
        print '\n'
        print t, '========================================'
        if len(d[t]) > 0:
            pprint.pprint(d[t])    