import sys, os

# Get the parent directory
parent_dir = os.path.dirname(os.path.realpath(__file__))

# Add the parent directory to sys.path
sys.path.append(parent_dir)

import utils

from importlib import reload
reload( utils )


# ============================== main =============================

utils.st.title( "Population around the world" )         

w_df = utils.pd.read_csv( utils.Path(f"{utils.root_path}/data/ne_110m_admin_0_countries.csv") )
w_df = w_df.rename( columns= {'LABEL_X':'Longitude', 'LABEL_Y':'Latitude' } )

utils.st.header( "Population vs GDP" )           
fig=utils.px.scatter( w_df, y='POP_EST', x='GDP_YEAR', color='SOVEREIGNT', title='GDP vs population')  #"layout.hovermode='color'"  )                    
fig.show()
utils.st.plotly_chart(fig)

try:
  fig = utils.px.scatter( w_df, x="POP_EST", y="GDP_YEAR", size="POP_EST", color="LABELRANK",
                 hover_name="SOVEREIGNT", log_x=True, size_max=60, title = 'GDP vs population')
  fig.show()
  utils.st.plotly_chart(fig)
except:
  pass
  
utils.st.write( "Filter the following dataframe to help answer your queries" )         
world_sub = utils.filter_dataframe( w_df[[ 'SOVEREIGNT','TYPE','GDP_YEAR','POP_EST','Longitude','Latitude']].copy(), 'Add filters?' )                    
g=world_sub.iloc[:,:-1]
g=utils.pd.DataFrame(g)

utils.st.write( 'Filtered subset:' )
utils.st.dataframe( g )      
csv2 = utils.convert_df( g )    
utils.st.download_button(
   "Press to download filtered subset",
   csv2,
   "subset_geo.csv",
   "text/csv",
   key='download-subset'
) 


csv = utils.convert_df( world_sub )    
utils.st.download_button(
   "Press to download CSV containing geocoordinates of select countries",
   csv,
   "world_geo.csv",
   "text/csv",
   key='download-global-geo-csv'
) 

utils.print_footer()

print('rendered More_stats.py')
