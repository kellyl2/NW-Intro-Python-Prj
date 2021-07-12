# -*- coding: utf-8 -*-
"""
Created on Fri Jul  3 10:07:17 2021

@author: Lindsay Kelly
"""

import pandas as pd
import geopandas as gpd
import urllib.request, json
import numpy as np
from shapely.geometry import Point, Polygon, LineString
import datetime
import pytz
import mygeotab
import datetime as dt
from pandas.tseries.offsets import DateOffset
import os
from cred_read import get_credentials



cwd=os.getcwd()

utc=pytz.UTC
time_zone = 'America/Los_Angeles'
pst = pytz.timezone(time_zone)

datetime_format_str = lambda d: pd.to_datetime(d).__format__('%Y-%m-%d %H:%M:%S')
datetime_format_geotab = lambda d: pst.localize(dt.datetime.strptime(datetime_format_str(d),'%Y-%m-%d %H:%M:%S'))
date_time_utc = lambda d: d.astimezone(dt.timezone.utc)



class gps_data(object):
    """ Generates the configuration parameters needed for Metrics reporting
    """
    def __init__(self):
        self.user = get_credentials('geotab')['u']
        self.pwd = get_credentials('geotab')['p']
        self.api=mygeotab.API(username=self.user, password=self.pwd, database='COV_prod')
        self.credentials = self.api.authenticate()
        #print(self.credentials)

    
    def get_GPS_api(self):
        return self.api
    
    def get_GPS_data(self,type_name='Trip',query=None, resultsLimit=None):
        if resultsLimit !=None:
            results=self.api.get(type_name=type_name, search=query,resultsLimit=resultsLimit)
        
        elif query==None:
            results=self.api.get(type_name=type_name, resultsLimit=1)
        else:
            results=self.api.get(type_name=type_name, search=query)
        return results
    
    
    def getDeviceInfo(self,device_ids):
        """purpose:
        calls geotab api to get the current status of the GPS device for the list of vehicle ids provided
        inputs:
            list of vehicle identifiers
        returns:
            dataframe of key information"""
        deviceInfo = []
        print("device ids being searched",device_ids)
        for d in device_ids:

      		# Fetch and device data  
            device_status = self.api.get(type_name='DeviceStatusInfo', search={"DeviceSearch": {"id":d}})[0]
            device_info = self.api.get(type_name='Device', search={"id":d})[0]
            #print(device)
            deviceInfo.append({
      				'id': d,
      				'name': device_info['name'],
      				'isDeviceCommunicating': device_status['isDeviceCommunicating'],
                    'last_gps_record':device_status['dateTime'],
                    'active_from':device_info["activeFrom"]
                    })

        global data
        data = pd.DataFrame(deviceInfo)

        return data



class COV_open_data(object):
    
    def __init__(self, params):
        self.api_key = params['COV_open_data_api_key']
        self.bike_url = params["cov_bikelane_gis_data_url"]
        self.street_url = params["cov_street_gis_data_url"]
    
    def get_bike_lanes(self):
         
        with urllib.request.urlopen(self.bike_url) as url:
            data = json.loads(url.read().decode())
            result=pd.json_normalize(data['records'], max_level=1)                
        return result
    
    def get_street_segments(self):
        with urllib.request.urlopen(self.street_url) as url:
            data = json.loads(url.read().decode())
            result=pd.json_normalize(data['records'], max_level=1)                
        return result
        
        


#####################################################################
####################################################################
################################################################### 
    




def get_trip_summary_data(params, check_trips=False, gps_conn=None, device_list=[]):
    """generates the initial call and coordinated the data for the report"""
    #### date time setup for query to geotab api - uses UTC time
    time_period = params['time_period']
    number_of_days = datetime_format_geotab(params[time_period]['end'])-datetime_format_geotab(params[time_period]['start'])
    fromDate = datetime_format_geotab(params[time_period]['start'])
    toDate = datetime_format_geotab(params[time_period]['end'])
    ######################################
    print("generating trip summary dataset")    
    n=0
    for d in device_list:
        try: 
            getTrips = gps_conn.get_GPS_data(type_name='Trip',
                    query= {
                        'deviceSearch': { 'id': d },
                        'fromDate': fromDate,
                        'toDate': toDate
                    })
            if params['verbose']==True:
                print('\n--------------------Trip Details Raw - Geotab',d,'\n',getTrips[:1],'\n--------------------')
            if n==0: 
                result=pd.json_normalize(getTrips, max_level=1)
                #result=pd.DataFrame.from_dict(getTrips) ### creates the results dataframe
            else:
                #result=result.append(pd.DataFrame.from_dict(getTrips)) ### updates the results dataframe from subsequent loops
                result=result.append(pd.json_normalize(getTrips, max_level=1))
        except:
            if params['verbose']==True:
                print(d,"no trips during the time period")
        
    
        n+=1

    if params['verbose']==True:
        print('\n--------------------Trip Details DF Sample \n',result.tail())
        print('\n--------------------Trip Details DF Describe \n',result.describe(include='all', datetime_is_numeric=True) )
        print('\n--------------------Trip Details DF Data Types \n',result.dtypes)
    ### after hours, workDriving, speeding categories, driver are all not being utilized within the system
    result=result[['id','device.id','start','stop','averageSpeed','distance','drivingDuration','idlingDuration','maximumSpeed','nextTripStart','stopPoint.x','stopPoint.y']]
    
    ### we also need to update the timezone details from UTC to PST for any sort of reporting purposes
    result.rename(columns={'id':"trip_id"},inplace=True)
    result['nextTripStart'] = result['nextTripStart'].dt.tz_convert(time_zone)
    result['start'] = result['start'].dt.tz_convert(time_zone)
    result['stop'] = result['stop'].dt.tz_convert(time_zone)
    result['trip_day'] = pd.to_datetime(result['start']).dt.strftime('%A')
    result['trip_hr'] = pd.to_datetime(result['start']).dt.strftime('%H').astype(float)
    result['tripDuration'] = result['stop'].dt.hour+round(result['stop'].dt.minute/60,2)-result['start'].dt.hour+round(result['start'].dt.minute/60,2)
    result['drivingDuration'] = round(pd.to_timedelta(result['drivingDuration'].astype(str)).dt.total_seconds()/3600,2)

    result['averageSpeed'].round(decimals=2)
    result['distance'].round(decimals=2)
    result['shift'] = 'night'
    result['shift'] = np.where(pd.to_datetime(result['start']).dt.strftime('%H').astype(int).between(7,14), 'day', result['shift'])
    result['shift'] = np.where(pd.to_datetime(result['start']).dt.strftime('%H').astype(int).between(14,20), 'afternoon', result['shift'])
    result['shift_day'] = pd.to_datetime(result['start']).dt.strftime('%A')
    ### business rule: he shift day moves for overnight shifts is defined as the dat the shift started - for the time between 0am and 7am the shift day is the day prior
    result['shift_day'] = np.where(pd.to_datetime(result['start']).dt.strftime('%H').astype(int).between(0,7), pd.to_datetime(result['start']+DateOffset(days=-1)).dt.strftime('%A'), result['shift_day'])
    


    unit_info = params["vehicle details"]
    result['unit_number'] = result['device.id'].map(unit_info)

    if params['verbose']==True:
        
        print('\n--------------------Trip Details DF Sample \n',result.tail())
        print('\n--------------------Trip Details DF Describe \n',result.describe(include='all', datetime_is_numeric=True) )
        to_display = result[['averageSpeed','distance','tripDuration','drivingDuration','idlingDuration','maximumSpeed','trip_hr']]
        boxplot = to_display.boxplot(grid=False, rot=45, fontsize=10,return_type='axes')

    result=result[result['averageSpeed']<75]
    
    return result

    

def get_trip_pts(params,gps_conn=None, df=None):
    n=0
    print('getting gps points for each trip')
    for i, row in df.iterrows():
        if n%25==0:
            print("number of records returned",n," getting next 25 records")

        query= {
                    'deviceSearch': { 'id': row['device.id'] },
                    'fromDate':datetime_format_str(date_time_utc(row['start'])),
                    'toDate': datetime_format_str(date_time_utc(row['stop']))
                }
        getTrips = gps_conn.get_GPS_data(type_name='LogRecord',query=query         )
        #print(query)
        #print(getTrips,'\n----------------------')

        if params['verbose']==True:  print('\n--------------------Trip Details Raw - Geotab',row['device.id'] ,'\n',getTrips[:1],'\n--------------------')
        if n==0: 
            
            result=pd.json_normalize(getTrips, max_level=1)
            result['id'] = result['id'].fillna('start')
            result['dateTime']=result['dateTime'].dt.tz_convert(time_zone)
            result['trip_id']=row['trip_id']
            result['device.id']=row['device.id']
            result['trip_ordered_pts']=result.index

        else:
            temp = pd.json_normalize(getTrips, max_level=1)
            temp['id'] = temp['id'].fillna('start')
            temp['dateTime']=temp['dateTime'].dt.tz_convert(time_zone)
            temp['trip_id']=row['trip_id']
            temp['device.id']=row['device.id']
            temp['trip_ordered_pts']=temp.index
            result=result.append(temp)

        n+=1    
    if params['verbose']==True: print('\n--------------------Trip Details Table - Geotab\n',result.tail(2))

    return result ### returns the results to the main data pull file


def get_gps_exceptions(params,exception_item='',device_list=[],gps_conn=None, df=None):
    #### date time setup for query to geotab api - uses UTC time
    print("getting vehicle exception data for trips")
    
    time_period = params['time_period']
    number_of_days = datetime_format_geotab(params[time_period]['end'])-datetime_format_geotab(params[time_period]['start'])
    fromDate = datetime_format_geotab(params[time_period]['start'])
    toDate = datetime_format_geotab(params[time_period]['end'])
    result=None
    exception_id=None
    for k in params['gps_rules']:
        if params['gps_rules'][k]['rule']==exception_item:
            exception_id=params['gps_rules'][k]['id']
            print(exception_item,'\n sensor data definition',params['gps_rules'][k]['description'])
    
    if exception_id==None:
        print("cannot find the exception search paramters requested")
        raise AttributeError('pleach check the geotab rule ids for the exception event')
    ############################################################
    n=0
    for d in device_list:
        query= {
                            'deviceSearch': { 'id': d },
                            'ruleSearch':{'id':exception_id }  ,
                            'fromDate':fromDate,
                            'toDate': toDate
                    }
        getDetails = gps_conn.get_GPS_data(type_name='ExceptionEvent',query=query         )
        if params['verbose']==True:   print('\n--------------------Exception Details Raw - Geotab',d ,'\n',getDetails[:1],'\n--------------------')
        if n==0: 
            result=pd.json_normalize(getDetails, max_level=1)
            result['exception_ordered_pts']=result.index  
        else:
            temp = pd.json_normalize(getDetails, max_level=1)
            temp['exception_ordered_pts']=temp.index
            result=result.append(temp)
        n+=1
    if len(result)>0:
        result['activeFrom']=result['activeFrom'].dt.tz_convert(time_zone)
        result['activeTo']=result['activeTo'].dt.tz_convert(time_zone)
        result['exceptionDuration'] = round(pd.to_timedelta(result['duration'].astype(str)).dt.total_seconds()/3600,2)
    
    if params['verbose']==True:  print(result.head(2))
    

    return result
    



      

def generate_trip_geom(summary_df,trip_df, params):
    trips=summary_df['trip_id'].unique()
    
    geometry=[]
    n=0
    for t in trips:
        temp=trip_df[trip_df['trip_id']==t]
        coord_list=[]
        for i, row in temp.iterrows():

            coord_list.append((row['longitude'],row['latitude']))
        
        #print(n,'-----------',coord_list)
        if len(coord_list)<2:
            geom=Point(coord_list)
        else:
            geom=LineString(coord_list)
        n+=1
        if params['verbose']==True and n<5: print(geom)
        geometry.append(geom)
    summary_df['trip_geom']=geometry    
    #print(summary_df.tail())
    
    geo_df = gpd.GeoDataFrame(summary_df, geometry=summary_df['trip_geom'])
    #print(geo_df.head(1))
    return geo_df, summary_df
    


            

# def get_device_groups(device_list=[],gps_conn=None,COV_groups={}):
#     #print("assembling device groups")
#     results={}

#     for d in device_list:

#         device_groups = gps_conn.get_GPS_data(type_name='Device', query={'id':d})  
#         for g in device_groups[0]['groups']:

#             if g['id'] in results:
#                 if d not in results[g['id']]['device_list']:
#                     results[g['id']]['device_list'].append(d)
#             else:
#                 results[g['id']]={'device_list':[d]}
#     group_list=[]    

#     for g in results.keys(): ### search through device keys
#         groups = gps_conn.get_GPS_data(type_name='Group', query={'id':g})
#         group_ind=0
#         for c in COV_groups:   
#             if g in COV_groups[c]: ### find matching key in the GPS group list
#                 results[g]["group_type"]=c
#                 group_ind=1         
#         if group_ind==0:
#             results[g]["group_type"]='other'
#         try:
#             results[g]["group_name"]=groups[0]['name']
#             group_list.append(groups[0]['name'])
#         except:
#             pass

#     return results

def geotab_group_search(gps_conn,group_id):
    groups = gps_conn.get_GPS_data(type_name='Group', query={'id':group_id}) 
    return groups[0]

    

def get_COV_groups(gps_conn):
    """
    Purpose: loops through the geotab parent child group relationships to classify the vehicle group membership for reporting
    
    Parameters
    ----------
    gps_conn : (geotab api connection) returned from the api connection
    results : (dictionary) inital entry the main parent group for the city department and vehicle type group
    
    
    Returns
    -------
    results : dictionary) containing a list of groups associated with either department or vehicle classification
                this group reference can then be searched within the api to obtain the description for reporting

    """
    results={'Department':['b278D'],'Vehicle Class':['b278F']}
    items={'Department':'b278D','Vehicle Class':'b278F'}
    print("assembling COV geotab groups")
    for i in items:
        g=items[i]
        groups = geotab_group_search(gps_conn,g)  
        num_children=len(groups['children'])

        subsearch=[]
        child_list=[]
        while num_children>1:
            #print(num_children)
            for n in range(num_children):
                for c in groups['children']:
                    if c['id'] not in child_list:
                        child_list.append(c['id'])
                    
                    if c['id'] not in subsearch:
                        subsearch.append(c['id'])
                        
                    if c['id'] not in items[i]:
                        results[i].append(c['id']) 
                ### recursive search through the child list to get parent child ids for departments                          
                groups= geotab_group_search(gps_conn,child_list[0]) 
                child_list.remove(child_list[0])
                num_children=len(child_list) 
    return results
                
                
                
            

