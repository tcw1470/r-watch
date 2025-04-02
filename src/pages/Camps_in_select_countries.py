
import sys, os

# Get the parent directory
parent_dir = os.path.dirname(os.path.realpath(__file__))

# Add the parent directory to sys.path
sys.path.append(parent_dir)

import utils

from importlib import reload
reload( utils )

# ========================= 



# admin
import numpy as np
rng = np.random.default_rng( 12345 )

import sys, os, copy, json
from pathlib import Path
from glob import glob
from datetime import datetime, timedelta
from time import sleep
import requests 

import pandas as pd
from pandas.api.types import (
    is_categorical_dtype,
    is_datetime64_any_dtype,
    is_numeric_dtype,
    is_object_dtype,
)
 
# plotting
import plotly.express as px
#import matplotlib.pyplot as plt

# mapping
import geopandas # geodatasets
from branca.element import Figure
import folium, geopy; from folium import plugins; import geopandas as gpd

# streamlit 
import streamlit.components.v1 as components
import streamlit as st
from streamlit_folium import st_folium, folium_static
import utils

DEBUG = 0
NDAYS = 30 #365*2
 
prefices = sorted( ['tur_pntcntr_camps', 
                    'Sudan_UNHCR_Refugee_11Jan21', 
                    'Eth_refugee_camps_unhcr_2019', 
                    'uga_rr_refugee_camps_polygons'] )
countries = sorted(['Turkey', 'Sudan', 'Ethiopia', 'Uganda' ])

def load_maps():          
   hmaps, gdfs, figs = {},{},{}
   # read in boundaries of each country
   df = pd.read_csv( Path( f"{utils.root_path}/data/ne_110m_admin_0_countries.csv") )
   w_gdf = geopandas.read_file( Path( f"{utils.root_path}/data/ne_110m_admin_0_countries.shp") )
   utils.st.dataframe( df ) 
   keys = df.keys() 
   w_df = df.rename( columns= {'LABEL_X':'Longitude', 'LABEL_Y':'Latitude' } )
   
   for i,f in enumerate( countries ): # lat,long of refugee camps
        k = f[:3].upper()
        print( k ) 
        gdfs[ k ]= gpd.read_file( data_dir + prefices[i] + '.shp' )
        
        try:
            print( k, gdfs[k].geometry[0] )
            gdfs[k].rename(columns ={'Latitude': 'latitude', 'Longitude':'longitude'},  inplace=True )
        except:
            pass 
            
        try:
            if k=='UGA': # uganda  
                gdfs[k][ 'longitude' ] = gdfs[k][['geometry']].centroid.x.values
                gdfs[k][ 'latitude'] = gdfs[k][['geometry']].centroid.y.values
        except Exception as e:
            st.text( f'Uganda parse centroids: {e}')
        if DEBUG:
            st.text( k ) 

        fig, hm0, site_name, heat_data, Addr = utils.get_heatmap( gdfs[k], show_addr=False ) # plot all ref camp sites as heat map
        figs[k] = fig

        #hm = utils.add_overlap( w_gdf, hm0, countries[i] ) # show country's boundary        
        plugins.HeatMap(heat_data).add_to(hm0)
        try:
            sw = gdfs[k][['latitude','longitude']].min().values.tolist() 
            ne = gdfs[k][['latitude','longitude']].max().values.tolist()
            hm.fit_bounds([sw, ne]) 
        except Exception as e:
            st.text( f'Map bounds: {e}' )

        if len(Addr) > 0:
            try:
                gdfs[k]['Addr'] = np.array(Addr)
            except Exception as e:
                st.text( f'Add addresses to gdfs: {e}'  )
        hmaps[k] = hm        
   return w_df, w_gdf, keys, figs, hmaps, gdfs, prefices, countries
   




# ================== paths ==================

data_dir = f'{utils.root_path}/data/'

utils.st.header( 'Refugee camps in select countries' )
utils.st.write( '''
Below we plot the spatial distributions of refugee camps in select developing countries.

''' )

world_df, world_gdf, keys, figs, hmaps, gdfs, prefices, countries = load_maps()
  
# ================== setup the layout ==================

for ii in range( len(countries) ):        
    hmap_keys = np.array(list( hmaps.keys() ))
    k=hmap_keys[ii]          
    utils.st.header( countries[ii] )          
    utils.st_folium( hmaps[k] )

         
