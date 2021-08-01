# -*- coding: utf-8 -*-
"""
Created on Tue May 18 10:25:11 2021

@author: enlck
"""

import datetime as dt
import json
import sys
import report_calendar as rpt_dt
#########################################
##CONFIG
########################################


class config(object):
    """ Generates the configuration parameters needed for Metrics reporting
    """
    def __init__(self, rep_frequency='MONTHLY', YTD='N',  output_file=True, custom_items={},output_file_name='config.json'):
        self.file={}
        self.rpt_frequency=rep_frequency
        self.now = dt.datetime.today().date()
        self.YTD=YTD
        self.output_file=output_file
        if len(custom_items)>0:
            self.custom=True
            self.customizations=custom_items
            self.set_custom()
        
        if self.output_file==True:
            self.file_name=output_file_name
                  
        
    
    def get_date_dict(self):
        DATE_RANGE=rpt_dt.report_dates(self.rpt_frequency,custom_dt='N',timing='LAST')
        if self.rpt_frequency.upper()=='MONTHLY':
            self.date_dict = DATE_RANGE.get_monthly_details()    
        elif self.rpt_frequency.upper()=='WEEKLY':
            self.date_dict = DATE_RANGE.get_weekly_details()
        elif self.rpt_frequency.upper()=='ANNUAL':
            self.date_dict = DATE_RANGE.get_YTD_details() 
        elif self.rpt_frequency.upper()=='DAILY':
            self.date_dict = DATE_RANGE.get_daily_details()

        
        self.set_dates()
        
        if self.YTD=='Y':
            self.YTD_date_dict = DATE_RANGE.get_YTD_details()
            self.set_YTD()
        
        
    def set_dates(self):
        if self.rpt_frequency.upper()!='ANNUAL': 
            self.file[self.rpt_frequency]={
                  "start":self.date_dict['report_cy_search_start'],
                  "end":self.date_dict['report_cy_search_end'],
                   "year": self.date_dict['report_cy_year']    
                     
                  }
            
        else:
            self.file[self.rpt_frequency]={
                  "start":self.date_dict['report_cy_search_start'],
                  "end":self.date_dict['report_cy_search_end'],
                  "year": self.date_dict['report_cy_year']                  
                  }
            
        self.file['time_period']=self.date_dict['time_period']
        
    
    def set_YTD(self):
        self.file['YTD']={
        "YTD_cy_start":self.YTD_date_dict['report_cy_search_start'],
        "YTD_cy_end":self.YTD_date_dict['report_cy_search_end'],
        "YTD_ly_start":self.YTD_date_dict['report_ly_search_start'],
        "YTD_ly_end":self.YTD_date_dict['report_ly_search_end'],
        "cy_year":self.YTD_date_dict['report_cy_year'],
        "ly_year":self.YTD_date_dict['report_ly_year']           
            }
        
        
    def set_sender(self):
        self.file['sender']={
            "name": "Lindsay Kelly",
            "position": "Business Analyst",
            "email": "lindsay.kelly@vancouver.ca",
            "phone": "604-871-6958"
                       
            }
    
    def set_custom(self):
        print("function called")
        for i in self.customizations:
            self.file[i]=self.customizations[i]
        
    
    def build_config(self):
        self.get_date_dict()

        
        if self.output_file==True:
            self.get_file()
            return self.file_name
        else:
            return self.file
        
        
    def get_file(self):
        print("saved file",self.file_name)
        with open(self.file_name,'w') as json_file:
            json.dump(self.file,json_file,indent=4,sort_keys=True)
        
        
    
    
    
    
    
    