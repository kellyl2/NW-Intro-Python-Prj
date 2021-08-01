# -*- coding: utf-8 -*-
"""
Created on Fri Jul  2 10:19:30 2021

@author: ENLCK
PURPOSE: checks the python environment for the required modules for the data processing and that the user have valid credentials to access the Geotab API

"""

import importlib
import geotab_testing as gps

def check_modules():
    ### check for required modules for data processing
    
    module_list=["json","pytz","pandas","numpy","datetime","os","sys","geopandas","shapely","ast","matplotlib","plotly","kaleido","mygeotab"]
    not_installed = []
    
    for _ in module_list:
    
        spam_spec = importlib.util.find_spec(_)
        if spam_spec is  None:
            not_installed.append(_)
            print(f"please install module {_}")
    if len(not_installed)==0: 
        print("all required modules present")
        return True
    else:
        return False
    
    
def check_geotab():
    try:
        gps_data=gps.gps_data() ### generates the geotab connection string for all geotab queries
        if gps_data.get_GPS_api() is not None:
            print("valid geotab connection")
            return True
        else:
            return False
    except:
        print("invalid authentication credentials")
        return False


    