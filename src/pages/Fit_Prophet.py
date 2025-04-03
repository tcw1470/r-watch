import sys, os

# Get the parent directory
parent_dir = os.path.dirname(os.path.realpath(__file__))

# Add the parent directory to sys.path
sys.path.append(parent_dir)

import utils

from importlib import reload
reload( utils )

from prophet import Prophet
from prophet.diagnostics import cross_validation, performance_metrics

utils.st.title("Fit a statistical model")

addresses =[    
    'Balukhali refugee camp, Bangladesh', 
    'Kutupalong refugee camp, Cox Bazar, Bangladesh',
    'Leda makeshift settlement, Bangladesh', # 'Rohingya refugee camp,  Bangladesh',    
    'Bidibidi Refugee Settlement, Uganda', 
    'Adjumani refugee camp, Uganda', 
    'Ifo, Dadaab, Kenya',        
    'Kalobeyei, refugee camp, Kenya' 
    ]
addresses =[  
    'Za’atari, Syria',
    'Kakuma refugee camp, Kenya',
    'Dadaab refugee camp, Kenya',    
    'Kutupalong refugee camp, Cox Bazar, Bangladesh',
    'Um Rakuba refugee camp, Sudan'    
]

addresses = ['Kutupalong refugee camp, Cox Bazar, Bangladesh' ]
addresses = ['Ifo, Dadaab, Kenya']

addresses0 = [
  'Beach camp, Palestine',
  'Bureij camp, Palestine',
  'Deir El-Balah Camp, Palestine',
  'Jabalia Camp, Palestine',
  'Khan Younis Camp, Palestine',
  'Maghazi camp, Palestine',
  'Nuseirat camp,Palestine',
  'Rafah camp, Palestine'] 

def grab( NDAYS = 60, dtypes=[0] ):
  X,debug_str = {},{}
  M,siteids,Lx,Ly,Addr=[],[],[],[],[]
  
  for dtype in dtypes:
    try:
      X[ dtype ]
    except:
      X[ dtype ] = {}
  
    for i,ad in enumerate(addresses):
      geolocator = utils.geopy.geocoders.Nominatim(user_agent="3")
      location = geolocator.geocode( ad )          
      lx,ly=location.longitude, location.latitude
      Addr.append( location.address )
      Lx.append(lx)
      Ly.append(ly)
      k = ad[:8]    
      siteids.append(k)
      try:        
        dat, debug_str[dtype,k] = utils.get_climate_data( lx, ly, ndays = NDAYS, dtype=dtype )  
        if utils.DEBUG:
            utils.st.text( 'Shape of T.S.' )
            utils.st.text( dat.shape )
        X[ dtype ][k] = dat          
        res = utils.np.nanmedian( dat[ 'raw_value'] )
        M.append( res )                  
      except Exception as e:
        print( f'Get climate: {e}')  
        M.append( utils.np.nan )
          
  return X, debug_str, utils.pd.DataFrame( 
    {'SiteID':siteids, utils.dtype_fileprefs[dtype]:M, 'longitude':Lx, 'latitude':Ly, 'Addr':Addr}),  Lx, Ly



# =============================== hyperparameters ===============================
def build_model():
    """ https://juanitorduz.github.io/fb_prophet/ """
    
    model = Prophet(
        yearly_seasonality=True,
        weekly_seasonality=False,
        daily_seasonality=False, 
        interval_width=0.95, 
        mcmc_samples = 500
    )

    model.add_seasonality(
        name='monthly', 
        period=30.5, 
        fourier_order=5
    )    
    return model


# =============================== ===============================    

def get_forecasts( climate_dfs, do_cv=False ):
    Forecasts,Forecasts_7, Figs={},{},{}
    
    for d in climate_dfs.keys():
        for a in climate_dfs[d].keys():                
        
            # Train the model with the prepared data
            df = climate_dfs[d][a][['date', 'raw_value'] ]
            df.rename( columns= {'date':'ds', 'raw_value':'y'}, inplace=True )
    
            # Create a Prophet model instance
            model = build_model()
            model.fit(df)
            
            if do_cv:
                utils.st.write('Cross validation begins')
                df_cv = cross_validation(
                    model = model, 
                    initial='730 days', 
                    period ='35 days', 
                    horizon='56 days')
                               
                df_cv.assign(
                    abs_error = lambda x: (x['y'] - x['yhat']).abs()) \
                    .assign(horizon = lambda x: x['ds'] - x['cutoff']) \
                    .assign(horizon = lambda x: x['horizon']) \
                    .groupby('horizon', as_index=False) \
                    .agg({'abs_error': utils.np.mean}) \
                    .rename(columns={'abs_error': 'mae'})
                
                fig = utils.plot_cross_validation_metric(df_cv=df_cv, metric='mae', rolling_window=0.1)
                utils.st.pyplot( fig ) 
               
            
            # Create a dataframe for the future period to be predicted
            future_df = model.make_future_dataframe(periods=6, freq='MS')
            future_df_next7days = model.make_future_dataframe(periods=30, freq='D')
    
            # Perform prediction using the model
            Forecasts[d,a] = forecast = model.predict(future_df)
            Forecasts_7[d,a] = forecast = model.predict(future_df_next7days)
            Figs[d,a] = model.plot(forecast)

            utils.st.write( 'Daily forecasts beyond historical data' )
            utils.st.dataframe( Forecasts_7[d,a][['ds', 'yhat', 'yhat_lower', 'yhat_upper']].tail(30) )

            utils.st.write( 'Monthly forecasts for the next 6 months' )
            utils.st.dataframe( Forecasts[d,a][['ds', 'yhat', 'yhat_lower', 'yhat_upper']].tail(6) )
            
    return Forecasts, Forecasts_7, Figs






# ========================= main ========================= 

utils.st.title('Download, train, and forecast...')
utils.st.write('''
While loading, this page may be running for about a minute as it may be requesting data from ClimateServ. After data has been pulled from ClimateServ, visitor may click on the button to "Train and forecast".

Note that data is pulled according to the input settings (defaulting to rainfall data from a refugee camp in Kenya), changing the input parameters would involve a new request being sent to ClimateServ.

Note: developers may adjust code so that more historical records are pulled off ClimateServ but
a big data pull would cost longer execution time for model-fitting, in which case, please refrain from refreshing the page.
''')

print( '>', addresses[0] )
addresses = [utils.st.text_area( 'Enter name of queried site for forecasts:', value=addresses[0],
                   height=68, max_chars=None, key=None, help=None, on_change=None, args=None, 
                   disabled=False, label_visibility="visible" )]

NDAYS_user = utils.st.slider( 'Number of historical records used to train forecaster (unit in day):', 
                             min_value=1460, value=2900, max_value=3650, step=365)

dtype = utils.st.radio( "Select the climate measure to pull from ClimateServ:",
    [0,26,29,32,664,665,666,667], horizontal=True, captions=[i for i in utils.dtype_names.values() ], index = 2 )









utils.st.header( '' )
new_df, debug_str, queried_df, Lx, Ly = grab( NDAYS = NDAYS_user, dtypes = [dtype]  ) # get time series for all locations

utils.st.header( 'Geo-coordinates of queried site' )
#utils.st.write( '(Longitude, Latitude) of queried sites given name of the site:' )
utils.st.dataframe( queried_df )

#utils.st.write( 'Most recent records pulled for the queried sites' )
#utils.st.dataframe( new_df[dtype][k].tail(3) ) 


if len(Lx) == 1:
    utils.map_loc( Ly[0], Lx[0], True ) 


utils.st.header( 'Time-series pulled from server')
for ii,d in enumerate( new_df.keys() ):
    for a in new_df[d].keys():                
        try:
            na = utils.dtype_names[d]
            fig = utils.px.bar( new_df[d][a], 'date','raw_value', title = f'{na} at {a}' )
            fig.show()
            utils.st.plotly_chart( fig )
        except Exception as e:
            utils.st.text( e)

        today_s_date=utils.datetime.today().strftime('%Y-%m-%d').replace('-','')
        filename = f"{a}_index{d}_prev{NDAYS_user}days_{today_s_date}.csv".replace(',','-').replace(' ','')
        
        utils.st.download_button(
             f"Download {d} measured at {a} to CSV",
             utils.convert_df( new_df[d][a] ),
             filename,
             "text/csv",
             key=f'download-{d}_{a}'
            )



with utils.st.expander('Debugging info'):
    for d in new_df.keys():
        for a in new_df[d].keys():                
            utils.st.text( f'Address-key:\n{ debug_str[d,a] }' )


utils.st.write( 'Below are links used to pull data from ClimateServ.' )


utils.st.divider()
utils.st.header( 'Train and forecast' )
do_cv = utils.st.radio(
    "Run cross-validation for more reliable forecasts?",
    [0, 1], index=0, horizontal=True, 
    captions = ["Skip CV", "Do not skip CV"])
utils.st.write('Warning: Cross validation will take a longer execution time.')

if utils.st.button('Train and forecast now!'):
    Forecasts, Forecasts_7, Figs = get_forecasts( new_df, do_cv )


    utils.st.write( 'Result for forcast' )
    for d in new_df.keys():
        for a in new_df[d].keys():                            
            try:
                utils.st.header("Forecasts for the year ahead")
                utils.st.plotly_chart(Figs[d,a], use_container_width=True)     
                utils.st.text( 'Forecasting completed' )
                #utils.st.dataframe( Forecasts_7[d,a], )     
            except:
                pass
                

utils.print_footer()

print('rendered Fit_Prophet.py')
