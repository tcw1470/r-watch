import sys, os

# Get the parent directory
parent_dir = os.path.dirname(os.path.realpath(__file__))

# Add the parent directory to sys.path
sys.path.append(parent_dir)

import utils

# preload
climate_dfs = utils.get_cached()

if 'climate_dfs' not in utils.st.session_state:    
  utils.st.session_state['climate_dfs'] = climate_dfs
  if utils.DEBUG:
    for k in utils.st.session_state.climate_dfs.keys():  
      utils.st.write( k )
      utils.st.write( utils.st.session_state.climate_dfs[k].keys()  )
else: 
  climate_dfs = utils.st.session_state.climate_dfs.copy()   

# ================ end of header ================



@utils.st.cache_data 
def forecast( climate_dfs ):
  Figs, Forecasts = {},{}
  for ii,tab in enumerate(tabs):
    for j,d in enumerate(dnames):
        with tab:                    
          if j==0:
            camp = utils.pale_camps[ ii ]
            utils.st.header( f'{ dnames[j]}' )
            df = climate_dfs[d][camp].iloc[ -3650:, :].copy()          
            df.rename( columns= {'date':'ds', 'raw_value':'y'}, inplace=True )

            df['ds'] = utils.pd.to_datetime( df['ds'], format= '%m/%d/%Y' )
            utils.st.dataframe( climate_dfs[d][ camp ].sample(3).iloc[:, 2: ] )

            threshold_date = utils.datetime.now() - utils.timedelta( days=365 )      
            mask = df[ 'ds' ] < threshold_date
            
            df_train = df[mask][['ds', 'y']]
            df_test = df[~ mask][['ds', 'y']]

            # Create a Prophet model instance
            model = utils.Prophet()
            model.fit(df_train)
            
            # Create a dataframe for the future period to be predicted                    
            fdf = model.make_future_dataframe(periods=12, freq='MS'); # 'W' , 'MS'
            
            # Perform prediction using the model
            Forecasts[ camp, d] = forecast = model.predict( df=fdf )                   

            fig, ax= utils.plt.subplots()
            fig.set_figheight(6)
            fig.set_figwidth(12)

            ax.fill_between(
                x=forecast['ds'],               
                y1=forecast['yhat_lower'],
                y2=forecast['yhat_upper'],
                color=utils.sns_c[2], 
                alpha=0.25,
                label=r'0.95 credible_interval'
            )
            utils.sns.lineplot(x='ds', y='y', label='y_train', data=df_train, ax=ax)
            utils.sns.lineplot(x='ds', y='y', label='y_test', data=df_test, ax=ax)
            utils.sns.lineplot(x='ds', y='yhat', label='y_hat', data=forecast, ax=ax)
            ax.axvline(threshold_date, color= utils.sns_c[3], linestyle='--', label='train test split')
            ax.legend(loc='upper left')
            ax.set(title='Dependent Variable', ylabel='');         

            Figs[camp, d] = fig 
  return Figs, Forecasts


# ================ start of main ================

camp_names = ['Al-Shati (Beach camp)', 'Bureij Camp', 'Jabalia Camp', 'Khan Yunis Camp','Maghazi Camp',  'Nuseirat Camp', 'Rafah camp' ]
camps = ['Beach','Burei', 'Jabal', 'Khan ','Magha',  'Nusei', 'Rafah'] # Deir
dnames = ['drought_stress','precipitation', 'rainfall', 'soil_moist', ] # CCSM_Ensemble_2_Temperature
data_dir = f'{utils.root_path}/data/'

names = list( climate_dfs.keys() )

utils.st.title( "Camps in Gaza Strip - Example forecast trials" )

utils.st.markdown( '''
The tabs listed below shows the names of each of these refugee camps located in Palestine.

If you wish to download the following measurements from our cache, you may do so on a different [page]
- [x] Rainfalls
- [x] Evaporative stress index (4-week)
- [x] Precipitation
- [x] Soil moist

# About the graphs below

Blue curves represent training data while organge curves represent test data for accuracy evaluation. 
When the organge curve aligns well with the green curves, which represent forecasted values, that segment suggests reliable forecasts for the corresponding season. 

''' )
 
tabs = utils.st.tabs( camp_names )
Figs, Forecasts = forecast( climate_dfs )

addresses = [
  'Beach camp, Palestine',
  'Bureij camp, Palestine',  
  'Jabalia Camp, Palestine',
  'Khan Younis Camp, Palestine',
  'Maghazi camp, Palestine',
  'Nuseirat camp,Palestine',
  'Rafah camp, Palestine'] 


for ii,tab in enumerate(tabs):
  with tab:        
    camp = utils.pale_camps[ ii ]
    geolocator = utils.geopy.geocoders.Nominatim(user_agent="3")
    location = geolocator.geocode( addresses[ii] )            
    utils.st.write( location ) 
    utils.map_loc( location.latitude, location.longitude, True ) 
    for j,d in enumerate(dnames):
      if j==0:
        utils.st.header( f'{ dnames[j] }' )         
        utils.st.dataframe( Forecasts[ camp, d] )
        utils.st.pyplot( Figs[camp, d] )

utils.print_footer()
