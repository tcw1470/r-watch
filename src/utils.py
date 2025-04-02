
# admin
import numpy as np
rng = np.random.default_rng( 12345 )

import sys, os, copy, json
from pathlib import Path
from glob import glob
from datetime import datetime, timedelta
from time import sleep
import requests 
import random 

import seaborn as sns
sns.set_style('darkgrid', {'axes.facecolor': '.9'})
sns.set_palette(palette='deep')
sns_c = sns.color_palette(palette='deep')

import pandas as pd
from pandas.api.types import (
    is_categorical_dtype,
    is_datetime64_any_dtype,
    is_numeric_dtype,
    is_object_dtype,
)

# plotting
import plotly.express as px
import plotly.graph_objs as go

import matplotlib.pyplot as plt

# mapping
import geopandas
from branca.element import Figure
import folium, geopy; from folium import plugins; import geopandas as gpd

# streamlit 
import streamlit.components.v1 as components
import streamlit as st
from streamlit_folium import st_folium, folium_static

# statistical modelling for simple forecasting
from prophet import Prophet
from prophet.diagnostics import cross_validation, performance_metrics
from prophet.plot import plot_cross_validation_metric

# Get the parent directory
parent_dir = os.path.dirname(os.path.realpath(__file__))

gparent_dir = os.path.dirname( parent_dir )
sys.path.append(gparent_dir)
sys.path.append(parent_dir)


repo_name = 'refugee-watch'

# Current . 
# parent: /workspaces/refugee-watch/rcamps 
# Granny: /workspaces/refugee-watch

print( 'utils.py\n Current',os.curdir, 'parent:', parent_dir, 'Granny:', gparent_dir)

v_colors = [
        '#fde725',
        '#c2df23',
        '#86d549',
        '#52c569',
        '#2ab07f',
        '#1e9b8a',
        '#25858e',
        '#2d708e',
        '#38588c',
        '#433e85',
        '#482173',
        '#440154']

date_today = datetime.now() 

DEBUG=0

path_data = Path( f'/mount/src/{repo_name}/data/' )
path_root = Path( f'/mount/src/{repo_name}/rcamps/' )
path_pages= Path( f'/mount/src/{repo_name}/rcamps/pages/' )

# w_gdf = geopandas.read_file( Path( gparent_dir, 'data/ne_110m_admin_0_countries.shp') )


pale_camps = ['Beach','Burei', 'Jabal', 'Khan ','Magha',  'Nusei', 'Rafah'] # Deir
pale_dnames = ['drought_stress','precipitation', 'rainfall', 'soil_moist', ] # CCSM_Ensemble_2_Temperature


dtype_names = {}
dtype_names[0]='Rainfall'
dtype_names[26]='IMERG'
dtype_names[29]='Evaporative stress index'
dtype_names[32]='Forecasted mean precip'
dtype_names[664]='Soil moisture 0-10cm'
dtype_names[665]='Soil moisture 10-40cm'
dtype_names[666]='Soil moisture 40-100cm'
dtype_names[667]='Soil moisture 100-200cm' 

dtype_fileprefs = {}
dtype_fileprefs[0]='Rainfall'
dtype_fileprefs[26]='IMERG'
dtype_fileprefs[29]='Stress_index'
dtype_fileprefs[32]='Forecasted_mean_precip'
dtype_fileprefs[664]='Soil_moisture_0-10cm'
dtype_fileprefs[665]='Soil_moisture_10-40cm'
dtype_fileprefs[666]='Soil_moisture_40-100cm'
dtype_fileprefs[667]='Soil_moisture_100-200cm' 



def read_markdown_file( f ):
    return Path( f ).read_text()
