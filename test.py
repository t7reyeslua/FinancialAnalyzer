#!/usr/bin/python

import pandas as pd
from pandas.tseries.offsets import *

import sys

#Path where the analyze.py is saved.
mypath = '/home/t7/Dropbox/dev/FinancialAnalyzer'
sys.path.append(mypath)

import analyze as fin

from pylab import rcParams
import matplotlib.pyplot as plt

rcParams['figure.figsize'] = (14, 6)
plt.style.use('ggplot')

pth = '/home/t7/Dropbox/Documents/Finanzas/TXT150511224047.TAB'
pth_csv = '/home/t7/Dropbox/Documents/Finanzas/bs_temp.csv'

#Import========================================================================

#Import file as it is downloaded
yy = fin.import_tab(pth)
#Try to automatically categorize as many transactions as possible
yy = fin.categorize_transactions(yy)
#Save categorized file to csv
fin.save_to_file(pth_csv, yy)

"""MANUALLY ADJUST INCORRECT/MISSING VALUES IN CSV FILE

-Inspect all transactions for more confidence, but mainly the ones categorized
as 'TBD'.

"""

#Reimport fully categorized file
y = fin.import_csv(pth_csv)


#Info=========================================================================
cs = fin.get_categories_and_subcategories(y)
c  = fin.get_categories(y)
s  = fin.get_subcategories(y)

tw  = fin.totals_week_by_week(y)
ty  = fin.totals_year_by_year(y)
tm  = fin.totals_month_by_month(y)
td  = fin.totals_by_day_of_week(y)
tcs = fin.totals_by_subcategory(y)
tc  = fin.totals_by_category(y)

ytc  = fin.totals_categories_yearly(y)
ytcs = fin.totals_subcategories_yearly(y)
mtc  = fin.totals_categories_monthly(y)
mtcs = fin.totals_subcategories_monthly(y)

yac   = fin.average_categories_per_year(y)
yacs  = fin.average_subcategories_per_year(y)
mac   = fin.average_categories_per_month(y)
macs  = fin.average_subcategories_per_month(y)
wac   = fin.average_categories_per_week(y)
wacs  = fin.average_subcategories_per_week(y)

#Print results
fin.print_dict(ytc)
fin.print_dict(ytcs)
fin.print_dict(mtc)
fin.print_dict(mtcs)

#Plots=========================================================================

#Total expenses by day of week
td['Out'].plot(kind='bar')
#Total expenses by month
tm.plot(kind='bar')
#Total expenses by year
ty.plot(kind = 'bar')

#Total expenses by category
tc['Total'].plot(kind='pie')
#Total expenses by subcategory
tcs['Total'].plot(kind='pie')

#Total expenses by subcategory in a month
mtcs['201503']['Total'].plot(kind='pie')

#Total expenses of specific category by day of week
fin.totals_by_day_of_week(fin.filter_by_category(y, 'Comidas'))['Out'].plot(kind='bar')
#Total expenses of specific subcategory by day of week
fin.totals_by_day_of_week(fin.filter_by_subcategory(y, 'Cenas'))['Out'].plot(kind='bar')
#Total expenses of transactions with a keyword in the description by day of week
fin.totals_by_day_of_week(fin.filter_by_description(y, 'umbo'))['Out'].plot(kind='bar')

#Expenses of a category within a timeframe
yd = fin.filter_by_date(y,'20150101','20150501')
ydd = fin.filter_by_category_subcategory(yd,'Viveres','Super')
wacs_sp  = fin.totals_subcategories_weekly(ydd)
#In one line
wacs_sp  = fin.totals_subcategories_weekly(fin.filter_by_category_subcategory(fin.filter_by_date(y,'20150101','20150501'),'Viveres','Super'))

#Plot weekly expenses of 2015
tw['2015-01-01':'2016-01-01']['Out'].plot(kind='bar')

#Plot weekly expenses of Super in 2015
ydd = fin.filter_by_category_subcategory(y,'Viveres','Super')
tw_sp  = fin.totals_week_by_week(ydd)
tw_sp['2015-01-01':'2016-01-01']['Out'].plot(kind='bar')
#In one line
fin.totals_week_by_week(fin.filter_by_category_subcategory(y,'Viveres','Super'))['Out'].plot(kind='bar')

fin.totals_week_by_week(fin.filter_by_category(y,'Comidas'))['Out'].plot(kind='bar')


#Compare Super and Eating out weekly
yy = fin.totals_week_by_week(fin.filter_by_category_subcategory(y,'Viveres','Super'))
xx = fin.totals_week_by_week(fin.filter_by_category(y,'Comidas'))
xy = pd.concat([xx['Out'], yy['Out']], axis=1).fillna(0)
xy.columns = ['x','y']
xy.plot(kind='bar', stacked=True)

#OR like this better
xy = fin.compare_expenses_weekly(y, ['Comidas','Viveres/Super'])
xy['2015-01-01':'2016-01-01'].plot(kind='bar', stacked=False)

#Compare type of Comidas
fin.compare_expenses_weekly(y, ['Comidas/Comidas', 'Comidas/Cenas','Comidas/Bar', 'Comidas/Snack'])['2015-01-01':'2016-01-01'].plot(kind='bar', stacked=True)
