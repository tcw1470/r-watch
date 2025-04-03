import sys, os

# Get the parent directory
parent_dir = os.path.dirname(os.path.realpath(__file__))

# Add the parent directory to sys.path
sys.path.append(parent_dir)

import utils

from importlib import reload
reload( utils )

  
# ========================= main ========================= 
   
utils.st.title('Refugee camps around the world & their population densities')

utils.st.header('Populations of concern to UNHCR in refugee camps between 2006 and 2014')
url="https://docs.google.com/spreadsheets/d/1DnuzzfqSMDfdgCKh0SArO5dgoKCCELqpIQVC68iFiNs/export?format=csv"
global_df = utils.pd.read_csv(url)
utils.st.dataframe( global_df )


utils.st.markdown( '''
This dataframe was pulled from [wiki](https://en.wikipedia.org/wiki/Refugee_camp#Refugee_camps_by_country_and_population). 

The plot below reports the population (count) of different camps in different countries over time. 

The size of each dot represents population. For instance, observing the chart reveals that in Kenya, the population of Kakuma camp has surpassed that of Hagadera camp by 2014.'''
)
dff=utils.pd.wide_to_long(global_df, stubnames='20', i=["Camp",'Country'], j="Year", ).reset_index(level=[1,2])
dff.reset_index( inplace=True )

dff['20'] = utils.pd.to_numeric( dff['20'].str.replace('–','-1') )
dff[dff['20']<0] = utils.np.nan
dff['Year']=dff['Year']+2000
dff.rename( columns={ '20': 'Count'},inplace=True)
fig = utils.px.scatter(dff.dropna(), x="Year", y="Count", size='Count', color="Country", hover_data='Camp', log_y=True, title="Count over time")
fig.show()

utils.st.plotly_chart( fig )


utils.st.markdown('')
utils.st.header( 'Palestinian refugee camps' )
utils.st.markdown('''
According to [Wikipedia](https://en.wikipedia.org/wiki/Palestinian_refugee_camps#Population_statistics), camps in Palestine can be divided between five regions:

| Region | # of official refugee camps |  # of unofficial refugee camps | # of registered refugees |
| :-- | --: | --: | --: |
| Jordan | 10 | 3 | 2,034,641 |
| Gaza Strip | 8 | 0 | 1,221,110 |
| West Bank | 19|4 | 741,409 |
| Syria | 9 | 3 | 499,189 |
| Lebanon | 12 | 0 | 448,599 |

Below we present the statistics from Wiki as a sortable table.
''')


url="https://docs.google.com/spreadsheets/d/1KqgJapzfO2r6f7lenkah1Lt-21NCMZ3D9P77KCgAGk4/export?format=csv"  
density_df = utils.pd.read_csv(url)

density_df= density_df[ ['Name', 'Density (pop/km2)', 'Population', 'Area (km2)', 'Location',	'Founded','Status','Coordinates' ]]


def highlight_survived(s):
    return ['background-color: #9E9']*len(s) if s.value else ['background-color: #E99']*len(s)
def color_survived(val):
    color = '#9E9' if val else '#E99'
    return f'background-color: {color}'

utils.st.dataframe( density_df ) #.style.apply(highlight_survived, axis=1))

fd = density_df.sort_values(by='Density (pop/km2)', ascending = True)
fd=fd.dropna()

my_data = [utils.go.Bar( y =fd['Name'], x= fd['Density (pop/km2)'], orientation = 'h')]
my_layout = ({"title": "Refugee camps by density",
                       "yaxis": {"title":""},
                       "xaxis": {"title":""},
                       "showlegend": False})
fig = utils.go.Figure(data = my_data, layout = my_layout)
fig.show()
utils.st.plotly_chart( fig )

utils.st.markdown( '''
Evidently, the three refugee camps with the highest density* are:
- Jaramana, 1,633,333
- Qabar Essit, 1,185,000
- Al-Sabinah, 433,333

*Defined as population/area ($km^2$).
''')





utils.st.markdown('''
Interested visitors are encouraged to examine the density camps from other parts of the world; please
consider this [starting point](https://en.wikipedia.org/wiki/Refugee_camp#Refugee_camps_by_country_and_population).
''')

utils.print_footer()
print('rendered Density.py')
