import sys, os
import plotly.graph_objects as go  

# Get the parent directory
parent_dir = os.path.dirname(os.path.realpath(__file__))

# Add the parent directory to sys.path
sys.path.append(parent_dir)

import utils
from importlib import reload
reload( utils )

# ------------------------------------------------------
@utils.st.cache_data
def get_hunger_excel():
  df  = utils.pd.read_csv( utils.Path( f'{utils.root_path}/data/', 'ghi2023b_cleaned.csv' ) )
  df2 = utils.pd.read_csv( utils.Path( f'{utils.root_path}/data/', 'ghi2023c_cleaned.csv' ) )
  return df, df2

def add_hovers( w_c, m, highlight_col ):
  '''
  Special thanks to Merlin @
  https://stackoverflow.com/questions/67117326/hovering-data-for-choropleth-maps-in-folium
  '''    
  style_func = lambda x: {'fillColor': '#ffffff', 
                              'color':'#000000', 
                              'fillOpacity': 0.1, 
                              'weight': 0.1}
  highlight_func = lambda x: {'fillColor': '#000000', 
                                  'color':'#000000', 
                                  'fillOpacity': 0.50, 
                                  'weight': 0.1}
  NIL = utils.folium.features.GeoJson(    
      data = w_c,
      name = 'Global hunger index',                
      style_function = style_func, 
      control = False,
      highlight_function = highlight_func, 
      tooltip = utils.folium.features.GeoJsonTooltip(
          fields = ['name', highlight_col ],  # use fields from the json file
          aliases= ['country','hunger index'],
          style  = ("background-color: white; color: #333333; font-family: arial; font-size: 12px; padding: 10px;") 
      )
  )
  m.add_child(NIL)
  m.keep_in_front(NIL)
  utils.folium.LayerControl().add_to(m)
  return m

def get_choropleth( maps, measures_df, col, tar_col,  w_c, country_shapes ):
  w_c[ tar_col ]= 0. 
  for i,c in enumerate(w_c.name):    
    d= measures_df[ measures_df['country'] == c][  col ]        
    d= d.replace('<','').replace('—','NaN')         
    if len(d) >0:
        w_c.loc[ i, tar_col ] = d.values[0]       
      
  w_c[ tar_col ] = utils.pd.to_numeric( w_c[ tar_col ], errors='coerce' )         
  m = utils.folium.Map( location=[0,0], zoom_start=3)       
  utils.folium.Choropleth(
        geo_data=country_shapes,
        data= w_c,
        name= tar_col ,        
        columns=['name', tar_col ],
        key_on='feature.properties.name',
        fill_color='PuRd',
        nan_fill_color='white'
      ).add_to(m)
  m = add_hovers( w_c, m, highlight_col= tar_col )  
  maps[ tar_col ]= m
  return maps, w_c


def hunger_maps( ghi2023b_df, ghi2023c_df ):
  url = 'https://raw.githubusercontent.com/python-visualization/folium/master/examples/data'
  country_shapes = f'{url}/world-countries.json'
  w_c = utils.geopandas.read_file( country_shapes ) # 177x3  
        
  maps = {}  
  tar_col =  'Global hunger index (2023)'
  maps, w_c = get_choropleth( maps, ghi2023c_df, '2023 (2018-2022)', tar_col, w_c, country_shapes )
  
  tar_col = 'Change in global hunger index since 2015'
  maps, w_c = get_choropleth( maps, ghi2023c_df, 'abs_change_since_2015', tar_col, w_c, country_shapes )
  
  
  ind_english =['Severity of malnourished children under five (per 2022 stats)']
  ind_english+=['Severity of children wasting under five (per 2022 stats)']
  ind_english+=['Severity of children stunting under five (per 2022 stats)']
  ind_english+=['Mortality rate of children under five (per 2021 stats)']
  
  for j,col in enumerate([ 'malnourished_2022',  'under5wasting_2022', 'under5stunting_2022', 'under5mortality_2021' ]):
    maps, w_c = get_choropleth( maps, ghi2023b_df, col, ind_english[j], w_c, country_shapes )    
  return maps, w_c
                         
try:
  df, df2 = get_hunger_excel()
except Exception as e:
  utils.st.write(e)

# ===========
utils.st.title( 'Mapping hunger around the globe' )



utils.st.markdown(
'''
Below, we try to plot various choropleths, including:
- Global hunger index
- **Severity of malnourished**: Children under five (years old)  
- **Severity of children wasting**: Children under five 
- **Severity of children stunting**: Children under five 
- Mortality rates in children under five
- ...
'''
)

try:
  maps, w_c = hunger_maps( df, df2 ) 
  K = list( maps.keys() )

  
  for k in maps.keys():
    utils.st.header( k )
    utils.folium_static( maps[k] )  
except Exception as e:
  utils.st.write( e )

utils.st.write( 'See the indicators by numbers...' )
fields = ['country', 'malnourished_2002','malnourished_2009','malnourished_2015','malnourished_2022',
          'under5wasting_2002', 'under5wasting_2010', 'under5wasting_2017', 'under5wasting_2022',
          'under5stunting_2002', 'under5stunting_2010'	,'under5stunting_2017', 'under5stunting_2022',
          'under5mortality_2000','under5mortality_2008','under5mortality_2015','under5mortality_2021']

utils.st.dataframe( df[ fields ] )

utils.st.write( 'See the Hunger Index by numbers...' )
utils.st.dataframe( df2 )

utils.st.markdown( '''
Above data from sheets 2 and 3 in 
<a href="https://view.officeapps.live.com/op/view.aspx?src=https%3A%2F%2Fwww.globalhungerindex.org%2Fxlsx%2F2023.xlsx&wdOrigin=BROWSELINK">
Excel file</a>
''', unsafe_allow_html=True
)

utils.st.header( 'References' )
utils.st.markdown('''
    Related materials:
    https://refugees.streamlit.app/ |
    http://www.mcrg.ac.in/cata.htm |
    https://resourcewatch.org/data/explore
    '''
)

utils.print_footer()

print('rendered Hunger_indices.py')
