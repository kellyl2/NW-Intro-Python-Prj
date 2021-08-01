# -*- coding: utf-8 -*-
"""
Created on Tue Jun 29 17:48:48 2021

@author: ENLCK
"""


import pandas as pd
import geopandas as gpd
import shapely.geometry
import datetime
import ast
import json
import pytz
import numpy as np
import mygeotab
from cred_read import get_credentials
from datetime import timedelta
import datetime as dt
import pandas as pd
import matplotlib.pyplot as plt
import math
from matplotlib import gridspec
import plotly.graph_objects as go
import numpy as np
import plotly.express as px
import kaleido
import os
import geopandas as gdp
from shapely.geometry import Point, Polygon, LineString, mapping
from plotly.offline import download_plotlyjs, init_notebook_mode,  plot
init_notebook_mode()



def map_box_token():
    return 'pk.eyJ1IjoiZW5sY2siLCJhIjoiY2p3MW5iZ2o1MDZrNDQzbzkxNmVxNmpwMiJ9.5eknCMxwD3PP-T9C7z-UTg'

def mapbox_style_url():
    return 'mapbox://styles/enlck/cjzcydzpl2b301cl98a0h4nrw'

def save_map(fig=None, folder='images',filename='sweeper.png'):
    cwd = os.getcwd() 
    if not os.path.exists(folder):
        os.mkdir(folder)
    img_folder=os.path.join(cwd,'images')
    img_file=img_folder+'\\'+filename 
    fig.write_image(img_file)
    print("map saved to",img_file)



def calc_zoom(min_lat,max_lat,min_lng,max_lng):
    width_y = max_lat - min_lat
    width_x = max_lng - min_lng
    zoom_y = -1.446*math.log(width_y) + 7.2753
    zoom_x = -1.415*math.log(width_x) + 8.7068
    return min(round(zoom_y,2),round(zoom_x,2))


def plot_sweeper_map(geo_df, colour_column='unit_number'):
    token =map_box_token()
    style_url=mapbox_style_url()

    px.set_mapbox_access_token(token)
    lats = []
    lons = []
    names = []
    colors = []


    geom_type = 'line'
    for feature, name in zip(geo_df.geometry, geo_df[colour_column] ):
        if isinstance(feature, shapely.geometry.linestring.LineString):
            linestrings = [feature]
        elif isinstance(feature, shapely.geometry.multilinestring.MultiLineString):
            linestrings = feature.geoms
        elif isinstance(feature, shapely.geometry.polygon.Polygon):
            polygons = [feature]
            geom_type = 'poly'
        else:
            pass
        if geom_type == 'line':
            for linestring in linestrings:
                x, y = linestring.xy
                lats = np.append(lats, y)
                lons = np.append(lons, x)
                names = np.append(names, [name]*len(y))
                colors = np.append(colors, [name]*len(y))
                lats = np.append(lats, None)
                lons = np.append(lons, None)
                names = np.append(names, None)
                colors = np.append(colors, colors[-1])
                

                
                
        else:
            for polygon in polygons:
                x, y = polygon.exterior.xy
                lats = np.append(lats, y)
                lons = np.append(lons, x)
                names = np.append(names, [names]*len(y))
                #lats = np.append(lats, None)
                #lons = np.append(lons, None)
                #names = np.append(names, None)
            
    
    min_lats = lats[0]
    max_lats = lats[0]
    min_longs = lons[0]
    max_longs = lons[0]
    
    for l in lats:
        if l is not None:
            if l > max_lats:
                max_lats = l
            if l < min_lats:
                min_lats = l
    for l in lons:
        if l is not None:
           if l > max_longs:
                max_longs = l
           if l < min_longs:
                min_longs = l 
        
    
    center_lat = (min_lats+max_lats)/2
    center_lon = (min_longs+max_longs)/2
    
    zoom_factor = calc_zoom(min_lats,max_lats,min_longs,max_longs)
    
    
    
    if geom_type != 'poly':
        fig = px.line_mapbox(lat=lats, lon=lons, hover_name=colors, color=colors, center={"lat": center_lat, "lon": center_lon},zoom = zoom_factor )
        fig.update_layout( mapbox_style=style_url)
        fig.update_layout(showlegend=True)
    
    else:
        fig = px.choropleth_mapbox(geo_df,
                   geojson=geo_df.geometry,
                   locations=geo_df.index,
                   #color = 'fields.streetuse',
                   #mapbox_style=style_url,
                   center={"lat": center_lat, "lon": center_lon},
                   zoom=zoom_factor)
        fig.update_geos(fitbounds="geojson", visible=True)


        

    

    #fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
    #fig.show()    

    return fig

   
def plot_stop_map(data,colour_column='device.id',lat='stopPoint.y',lon='stopPoint.x', zoom=11, size=8):    
    token=map_box_token()
    style_url=mapbox_style_url()
    px.set_mapbox_access_token(token)
    df = data
    fig = px.scatter_mapbox(df, lat=lat, lon=lon,     color=colour_column, 
                      color_continuous_scale=px.colors.cyclical.IceFire, size_max=15, zoom=zoom)
    fig.update_traces(marker_size=size, selector=dict(type='scattermapbox'))
    fig.update_layout(
        mapbox_style=style_url)
    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
    fig.show()
    return fig


def daily_summary_map(geo_df):
    weekday_list=geo_df['weekday'].unique()
    report_rows=len(weekday_list)
    shift_list=geo_df['shift'].unique()
    report_columns=len(shift_list)
    output={}
    for d in weekday_list:
        for s in shift_list:
            print(d,s)
            index=d+'-'+s
            print(index)
            temp=geo_df[(geo_df['weekday']==d) & (geo_df['shift']==s)]
            num_records=len(temp)
            if len==0:
                text=f"No sweeping on {d} {s} shift"
                fig=None
                output[index]={'fig':fig,'text':text}
                
            else:
                text=f"Sweeping on {d} {s} shift"
                fig=plot_sweeper_map(temp)
                output[index]={'fig':fig,'text':text}
                save_map(fig,filename=index+'.png')
                
    #print(output)

   
def generate_street_buffers(gdf,buffer_width=10):
    capped_lines = gdf.geometry.buffer(buffer_width)
    return capped_lines

        
        
    
    
    


    
                
                
            
    