import sys, os
import numpy as np

# Get the parent directory
parent_dir = os.path.dirname(os.path.realpath(__file__))

# Add the parent directory to sys.path
sys.path.append(parent_dir)

import utils

from importlib import reload
reload( utils )
from lightning.pytorch.tuner import Tuner
import warnings; warnings.filterwarnings("ignore")
import lightning.pytorch as pl
from lightning.pytorch.callbacks import EarlyStopping
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import torch
import streamlit as st     
from pytorch_forecasting import Baseline, DeepAR, TimeSeriesDataSet
from pytorch_forecasting.data import NaNLabelEncoder
from pytorch_forecasting.data.examples import generate_ar_data
from pytorch_forecasting.metrics import MAE, SMAPE, MultivariateNormalDistributionLoss
import pytorch_forecasting as ptf
from lightning.pytorch.tuner import Tuner
            
def set_seed(seed):
    utils.random.seed(seed)
    os.environ['PYTHONHASHSEED'] = str(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
set_seed(42) 

utils.st.title("Fit a DeepAR (Deep Auto Regressive model)")
address_str = utils.st.text_area( 'Enter name of site for forecasts: (try ""Ifo, Dadaab, Kenya"")', 
                   height=68, max_chars=None, key=None, help=None, on_change=None, args=None, 
                   disabled=False, label_visibility="visible" )

NDAYS_user = utils.st.slider( 'Number of historical records used to train forecaster (unit in day):', 
                             min_value=365, value=365, max_value=3650, step=365)

dtype = utils.st.radio( "Select the climate measure to pull from ClimateServ:",
    [0,26,29,32,664,665,666,667], horizontal=True, captions=[i for i in utils.dtype_names.values() ], index = 2 )

from nominatim import Nominatim, NominatimReverse
nom = Nominatim( ) #user_agent = 'streamlit-refugee-watch' )

st.write('''
After clicking button below, it will take some time to fetch data for the quried location.

Moments after the data is fetched, DeepAR will automatically begin fitting.'''
        )

def grab( lat, lon):
            dat,_= utils.get_climate_data( lon, lat, ndays = NDAYS_user, dtype=dtype )  
            dat['rolling_median']=dat.raw_value.rolling(2, min_periods=1).median()
            dat['rolling_mean']=dat.raw_value.rolling(2, min_periods=1).mean()
            return dat    

import requests
def get_country(lat, lon):
    url = f'https://nominatim.openstreetmap.org/reverse?lat={lat}&lon={lon}&format=json&accept-language=en&zoom=3'
    try:
        result = requests.get(url=url)
        result_json = result.json()
        return result_json['display_name']
    except Exception as e:
        # utils.st.write(e)
        return None

utils.st.write(get_country(32.782023,35.478867))


results = [] 
new_df = None
if utils.st.button('Fetch climate data collected for this location', disabled=len(address_str)<1):
    results = nom.query(address_str)                               
    if results is None:    
        utils.st.write( type(address_str))
        utils.st.write(f'Cannot find {address_str}')
    else:
        lat,lon=float(results[0]['lat']),float(results[0]['lon'])
        utils.st.write( results[0])
        utils.st.write( f'Found a place at {lat},{lon}')        
        new_df = grab(lat, lon)
    
    if new_df is not None:    
        df= new_df.copy()
        df['date']=pd.to_datetime(new_df['date'], errors='coerce')
        df=df.sort_values( ['date'])        
        df['series']= f'{utils.dtype_fileprefs[dtype]} at {address_str}'       
        df = df.astype(dict(series=str))        
        df=df[ [ 'series', 'date','raw_value','rolling_mean','rolling_median']]
        df['time_idx']= np.arange(df.shape[0])
        
        utils.st.dataframe( df )
        a=address_str.replace(',','-').replace(' ','-').replace(' ','')
        d=utils.dtype_fileprefs[dtype]
        today_s_date=utils.datetime.today().strftime('%Y-%m-%d').replace('-','')
        filename = f"{a}_index{d}_prev{NDAYS_user}days_{today_s_date}.csv"                
        id=123
        st.download_button(
             f"Download dataframe to CSV",
             utils.convert_df( df ),
             filename,
             "text/csv",
             key=f'download-{id}'
            )
                
        def run_n_plot( data, key_group, key_target ):
            
            # create dataset and dataloaders
            max_encoder_length = 60
            max_prediction_length = 20
            
            training_cutoff = data["time_idx"].max() - max_prediction_length
            
            context_length = max_encoder_length
            prediction_length = max_prediction_length
            
            training = TimeSeriesDataSet(
                data[lambda x: x.time_idx <= training_cutoff],
                time_idx="time_idx",
                target=key_target,
                group_ids=[key_group],
                static_categoricals=[  key_group ],  # as we plan to forecast correlations, it is important to use series characteristics (e.g. a series identifier)
                time_varying_unknown_reals=[ key_target ],
                max_encoder_length=context_length,
                max_prediction_length=prediction_length,
            )
            
            validation = TimeSeriesDataSet.from_dataset(training, data, min_prediction_idx=training_cutoff + 1)
            batch_size = 128
            # synchronize samples in each batch over time - only necessary for DeepVAR, not for DeepAR
            train_dataloader = training.to_dataloader(
                train=True, batch_size=batch_size, num_workers=0, batch_sampler="synchronized"
            )
            val_dataloader = validation.to_dataloader(
                train=False, batch_size=batch_size, num_workers=0, batch_sampler="synchronized"
            )
            
            pl.seed_everything(42)
            
            trainer = pl.Trainer(accelerator="cpu", gradient_clip_val=1e-1)
            net = DeepAR.from_dataset(
                training,
                learning_rate=3e-2,
                hidden_size=30,
                rnn_layers=2,
                loss=MultivariateNormalDistributionLoss(rank=30),
                optimizer="Adam",
            )                         
            # find optimal learning rate            
            res = Tuner(trainer).lr_find(
                net,
                train_dataloaders=train_dataloader,
                val_dataloaders=val_dataloader,
                min_lr=1e-5,
                max_lr=1e0,
                early_stop_threshold=100,
            )
            print(f"suggested learning rate: {res.suggestion()}")

            early_stop_callback = EarlyStopping(monitor="val_loss", min_delta=1e-4, patience=10, verbose=False, mode="min")
            trainer = pl.Trainer(
                    max_epochs=30,
                    accelerator="cpu",
                    enable_model_summary=True,
                    gradient_clip_val=0.1,
                    callbacks=[early_stop_callback],
                    limit_train_batches=50,
                    enable_checkpointing=True,
                )
            net = DeepAR.from_dataset(
                    training,
                    learning_rate=1e-2,
                    log_interval=10,
                    log_val_interval=1,
                    hidden_size=30,
                    rnn_layers=2,
                    optimizer="Adam",
                    loss=MultivariateNormalDistributionLoss(rank=30),
            )
            trainer.fit( net,
                        train_dataloaders=train_dataloader,
                        val_dataloaders=val_dataloader,
                        )

            best_model_path = trainer.checkpoint_callback.best_model_path
            best_model = DeepAR.load_from_checkpoint(best_model_path)
            # best_model = net
            predictions = best_model.predict(val_dataloader, trainer_kwargs=dict(accelerator="cpu"), return_y=True)
            perf = MAE()(predictions.output, predictions.y)
            
            return res,net,predictions,perf,best_model,validation,val_dataloader

        utils.st.write('DeepAR-fitting begins...')
        res,net,predictions,perf,best_model,validation,val_dataloader= run_n_plot( df, 'series', 'raw_value',  )            

               
        fig = res.plot(show=True, suggest=True)
        utils.st.pyplot( fig )
        net.hparams.learning_rate = res.suggestion()

        utils.st.write(net.hparams.learning_rate )
        raw_predictions = net.predict( val_dataloader, mode="raw", return_x=True, n_samples=100, trainer_kwargs=dict(accelerator="cpu") )
        series = validation.x_to_index(raw_predictions.x)["series"]
                
        for idx in range(len(series)):   
            fig = best_model.plot_prediction(raw_predictions.x, raw_predictions.output, idx=idx, add_loss_to_title=True)
            plt.suptitle(f"Series: {series.iloc[idx]}")
        
            utils.st.pyplot( fig )

        try:
            utils.st.write(type(raw_predictions.columns))
        except:
            pass
                    
         

utils.print_footer()

print('rendered Fit_DeepAR.py')
