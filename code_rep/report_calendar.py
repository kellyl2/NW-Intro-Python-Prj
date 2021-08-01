# -*- coding: utf-8 -*-
"""
Created on Tue Feb  2 13:32:55 2021

@author: ENLCK
UPDATED to consolidate a number of the calander items
"""

import datetime as dt
from pandas.tseries.offsets import DateOffset
from datetime import datetime
from calendar import monthrange

def last_day_of_month(date_value):
    return format_date(date_value.replace(day = monthrange(date_value.year, date_value.month)[1]))

def format_date(date_string,custom='N',custom_entry={'custom_day':'01'}):
    """ returns the date formatted as expected from all datasets YYYY-MM-DD"""
    custom_day='%d'
    custom_month='%m'
    custom_year='%Y'
   
    if custom=='N':
        return str(dt.datetime.__format__(date_string,"%Y-%m-%d"))
    else:
       for r in custom_entry:
           if 'custom_day' in r:
               custom_day=str(custom_entry['custom_day'])
           if 'custom_month' in r:
               custom_month=str(custom_entry['custom_month'])
           if 'custom_year' in r:
               custom_year=str(custom_entry['custom_year'])
       return str(dt.datetime.__format__(date_string, custom_year+"-"+custom_month+"-"+custom_day))
        

def get_week_dt(date_string,time_period):
    """returns a list of tuples:
        search date[0], search week num[1], start of week date[2], end of week[3]"""
    dt1=dt.datetime.strptime(date_string,"%Y-%m-%d")
    week_num=int(dt1.strftime("%U"))    

    year=int(dt1.year)
    week=str(year)+"-W"+str(week_num)

    start_of_week_dt=dt.datetime.strptime(week + '-1', '%G-W%V-%u')
    end_of_week_dt=dt.datetime.strptime(week + '-1', '%G-W%V-%u')+DateOffset(days=6)
    start_of_week=format_date(start_of_week_dt)
    end_of_week=format_date(end_of_week_dt)
    return [(dt1),(week_num),(start_of_week),(end_of_week)]
    
    
    
def get_last_week_dt(wk_num,time_period):
    dt1=dt.datetime.today().date()
    c_year=int(dt1.year)
    lw_week=str(c_year)+"-W"+str(wk_num)
    start_of_week_dt=dt.datetime.strptime(lw_week + '-1', '%G-W%V-%u')+DateOffset(days=-1)    
    return format_date(start_of_week_dt)


#########################################
##KEY DATES
########################################
class report_dates(object):
    """ Generates the key dates for the reports and query pulls from the various data sources 
    rep_frequency takes the following values: 'WEEKLY', 'MONTHLY', 'YEARLY'
    custom_dt takes the following values: "Y" or "N"
    timing takes the following values: "LAST" or "THIS"
    """
    
    def __init__(self, rep_frequency='MONTHLY', custom_dt='N',timing='LAST'):
        """all dates are generated against the date in which the function is called"""
        self.rpt_frequency=rep_frequency
        self.now = dt.datetime.today().date()
        self.custom_dt=custom_dt
        self.timing=timing

        self.year_month=dt.datetime.__format__(self.now + DateOffset(months=-1),'%b-%Y')
        
    
    def get_monthly_details(self):
        date_dict={}
        self.current_month=int(dt.date.today().month)
        self.last_month=int(dt.datetime.__format__(self.now + DateOffset(months=-1),"%m"))

        if self.custom_dt=='N':
            if self.timing=='LAST':
                self.report_month_num=self.last_month
                self.report_cy_search_start=format_date(self.now + DateOffset(months=-1),custom='Y',custom_entry={'custom_day':'01'})
                self.report_cy_search_end=last_day_of_month(self.now + DateOffset(months=-1))
            else:
                self.report_month_num=self.current_month
                self.report_cy_search_start=format_date(self.now,custom='Y',custom_entry={'custom_day':'01'})
                self.report_cy_search_end=last_day_of_month(self.now)

                
        if self.report_month_num == 12:
            self.yr_start=format_date(self.now + DateOffset(years=-1),custom='Y',custom_entry={'custom_month':'01','custom_day':'01'})
            self.yr_end=format_date(self.now + DateOffset(years=-1),custom='Y',custom_entry={'custom_month':'12','custom_day':'31'})
            self.cy_year=int(dt.date.today().year)-1
            
        else:
            self.yr_start=format_date(self.now + DateOffset(years=0),custom='Y',custom_entry={'custom_month':'01','custom_day':'01'})
            self.yr_end=format_date(self.now + DateOffset(years=0),custom='Y',custom_entry={'custom_month':'12','custom_day':'31'})
            self.cy_year=int(dt.date.today().year)
            
        
        self.report_date_string= self.rpt_frequency+" REPORT ("+self.report_cy_search_start+" - "+self.report_cy_search_end+")"
    
        ### build date dictionary
        date_dict['current_month']=self.current_month
        date_dict['last_month']=self.last_month
        date_dict['time_period']=self.rpt_frequency
        date_dict['report_month_num']=self.report_month_num
        date_dict['report_cy_search_start']=self.report_cy_search_start
        date_dict['report_cy_search_end']=self.report_cy_search_end
        date_dict['report_cy_yr_start']=self.yr_start
        date_dict['report_cy_yr_end']=self.yr_end
        date_dict['report_cy_year']=self.cy_year
        date_dict['report_date_string']=self.report_date_string
        date_dict['report_file_name']=self.rpt_frequency+"_"+str(self.cy_year)+"-"+str(self.report_month_num)

        return date_dict
    

    def get_weekly_details(self):
        date_dict={}
        self.current_week_num=int(self.now.strftime("%U"))
        self.last_week_num=int(self.current_week_num)-1
        
        
        if self.custom_dt=='N':
            if self.timing=="LAST":
                dt_lw=get_last_week_dt(self.last_week_num,'cy')
                d1=get_week_dt(dt_lw,'cy')
                self.cy_year=int(d1[2][:4])
                self.report_week_num=int(self.last_week_num)
            else:
                d1=get_week_dt(self.d_today,'cy')
                self.report_week_num=int(self.current_week_num)
                self.cy_year=int(dt.date.today().year)
            
            self.report_cy_search_start=d1[2]
            self.report_cy_search_end=d1[3]
            self.report_current_start_week=d1[1]
            self.report_date_string= self.rpt_frequency+" REPORT ("+self.report_cy_search_start+" - "+self.report_cy_search_end+")"

            self.yr_start=format_date(self.now + DateOffset(years=0),custom='Y',custom_entry={'custom_month':'01','custom_day':'01'})
            self.yr_end=format_date(self.now + DateOffset(years=0),custom='Y',custom_entry={'custom_month':'12','custom_day':'31'})
            self.ly_yr_start=format_date(self.now + DateOffset(years=-1),custom='Y',custom_entry={'custom_month':'01','custom_day':'01'})
            self.ly_yr_end=format_date(self.now + DateOffset(years=-1),custom='Y',custom_entry={'custom_month':'12','custom_day':'31'})
            self.cy_year=int(dt.date.today().year)
            self.ly_year=int(dt.date.today().year)-1
            self.metro_flows_start=format_date(self.now + DateOffset(years=-4),custom='Y',custom_entry={'custom_month':'01','custom_day':'01'})
        
        
        
        ### build date dictionary
        date_dict['current_week']=self.current_week_num
        date_dict['last_week']=self.last_week_num
        date_dict['time_period']=self.rpt_frequency
        date_dict['report_week_num']=self.report_week_num
        date_dict['report_cy_search_start']=self.report_cy_search_start
        date_dict['report_cy_search_end']=self.report_cy_search_end
        date_dict['report_cy_yr_start']=self.yr_start
        date_dict['report_cy_yr_end']=self.yr_end
        date_dict['report_cy_year']=self.cy_year
        date_dict['report_date_string']=self.report_date_string
        date_dict['report_file_name']=self.rpt_frequency+"_"+str(self.cy_year)+"-"+str(self.report_week_num)

        
        return date_dict  
        

    def get_daily_details(self):
        date_dict={} 
        
      ### build date dictionary
        date_dict['time_period']=self.rpt_frequency
            
        date_dict['report_cy_search_start']= format_date(self.now + DateOffset(days=-1),custom='N') 
        date_dict['report_cy_search_end']= format_date(self.now ,custom='N')   
        date_dict['report_ly_search_start']=format_date(self.now + DateOffset(years=-1)+DateOffset(days=-1))
        date_dict['report_ly_search_end']=format_date(self.now + DateOffset(years=-1) ,custom='N')
        date_dict['report_cy_year']=int(dt.date.today().year)
        date_dict['report_ly_year']=int(dt.date.today().year)-1
        date_dict['report_year_month']=self.year_month
        
        #date_dict['report_date_string']=self.rpt_frequency+" REPORT ("+report_dict['report_cy_yr_start']+" - "+report_dict['report_cy_search_end']+") and ("+report_dict['report_ly_yr_start']+" - "+report_dict['report_ly_yr_end']+")"
    
        return date_dict 
    
    
class custom_dates(report_dates):
    """Builds custom date selector for items"""
    def __init__(self, rpt_frequency, custom_dt,c_start_dt,c_end_dt,timing):
        #report_dates.__init__(self, rep_frequency, custom_dt,timing)
        self.rpt_frequency=rpt_frequency
        self.now = dt.datetime.today().date()
        self.end_year=dt.datetime.strptime(c_end_dt,"%Y-%m-%d").year
        self.custom_dt=custom_dt
        self.custom_start=c_start_dt
        self.custom_end=c_end_dt
        self.rpt_start=dt.datetime.strptime(c_start_dt,"%Y-%m-%d")
        self.year_month=dt.datetime.__format__(self.rpt_start,'%b-%Y')
        
    def get_custom_dates(self):
        self.cy_year=dt.datetime.strptime(self.custom_start,"%Y-%m-%d").year
        self.ly_year=int(self.cy_year)-1
        self.ly_year_end=str(self.ly_year)+'-12-31'
        #[(dt1),(week_num),(start_of_week),(end_of_week)]
        self.date_dict={}
        self.date_dict['time_period']=self.rpt_frequency
        self.date_dict['report_week_num']=1
        self.date_dict['report_month_num']=1
        self.date_dict['report_cy_search_start']=self.custom_start
        self.date_dict['report_cy_search_end']= self.custom_end
        self.date_dict['report_ly_search_start']=dt.datetime.strptime(self.custom_start,"%Y-%m-%d")+DateOffset(years=-1)
        self.date_dict['report_ly_search_end']=dt.datetime.strptime( self.custom_end,"%Y-%m-%d")+DateOffset(years=-1)
        self.date_dict['report_metro_flows_search_start']=self.custom_start
        self.date_dict['report_year_month']=self.year_month
        
        self.date_dict['report_cy_yr_start']=self.custom_start
        self.date_dict['report_cy_yr_end']= self.custom_end
        self.date_dict['report_ly_yr_start']=dt.datetime.strptime(self.custom_start,"%Y-%m-%d")+DateOffset(years=-1)
        self.date_dict['report_ly_yr_end']=dt.datetime.strptime( self.custom_end,"%Y-%m-%d")+DateOffset(years=-1)
        self.date_dict['report_cy_year']=self.cy_year
        self.date_dict['report_ly_year']=self.ly_year
        self.date_dict['report_date_string']=self.rpt_frequency+" REPORT ("+self.custom_start+" - "+ self.custom_end+")"
        self.date_dict['report_file_name']=self.rpt_frequency+"_"+str(self.cy_year)+"- CUSTOM"
        
        return self.date_dict 
