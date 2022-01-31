import pandas as pd
import numpy as np
from datetime import datetime
from fitter import Fitter, get_common_distributions, get_distributions, HistFit
import plotly.graph_objects as go
import plotly.figure_factory as ff
from scipy import stats
import random
from config import activity_pairs,distributions_list



random.seed(10)


class DensityEstimator:
    def __init__(self,df):
        self.df = df
        self.update_activity_values()
        self.dist_string = None
        self.dist_params = None
               
    def update_activity_values(self):
        datos1 = self.df
        try:
            datos1['activity'] = datos1.activity.replace('biochimeBAStartDateTime','biochimieBAStartDateTime')            
        except:
            pass
        try:            
            datos1['activity'] = datos1.activity.replace('biochimeTakeBADateTime','biochimieTakeBADateTime')            
        except:
            pass
        try:
            datos1['activity'] = datos1.activity.replace('biochimeBAStartDateTime','biochimieBAStartDateTime')            
        except:
            pass
        try:
            datos1['activity2'] = datos1.activity.shift(-1)
            datos1['date2'] = datos1.date.shift(-1)
            datos1=datos1.reset_index(drop=True)
            datos1['duracion'] = (datos1.date2.iloc[:-1].apply(lambda x: datetime.strptime(x, '%Y-%m-%d %H:%M:%S')) - 
                                  datos1.date.iloc[:-1].apply(lambda x: datetime.strptime(x, '%Y-%m-%d %H:%M:%S'))).astype(
                'timedelta64[m]')
            datos1 = datos1[datos1.duracion>=0]
        except Exception as e:
            print(e)        
        self.df =datos1 
    
    def activity_data(self,activity):
        print(f"Ploting data for the pair: {activity}-{activity_pairs[activity]}")
        datos1 = self.df    
        df = datos1[(datos1.activity == activity) & (datos1.activity2 == activity_pairs[activity])]
        
        dur_df = df.duracion[(np.abs(stats.zscore(df.duracion))< 3)]
        return dur_df
    
    def fitter(self,dur_df):        
        f = Fitter(dur_df, distributions= distributions_list )
        f.fit()
        self.best_fit = f.get_best(method = 'sumsquare_error')
        try:
            params = self.best_fit
            dist = list(params.keys())[0]
            self.dist_string = f'Distribution: {list(params.keys())[0]}'
            self.dist_params = pd.DataFrame(params[dist].items(), columns = ['params','values']).round(2)
        except:
            pass
    
    def plot(self,activity):
        try:
            df = self.activity_data(activity)
            self.fitter(df)
            best = self.best_fit
            x = np.linspace(df.min(), df.max(), 1000)
            y = eval('stats.'+list(best.keys())[0]+'.pdf(x,**best[list(best.keys())[0]])')
            hist_data = [df]
            group_labels = ['Kernel density'] # name of the dataset
            fig = ff.create_distplot(hist_data, group_labels, bin_size=10)
            fig.add_trace(
                go.Scatter(
                    x=x,
                    y=y,
                    name ="Fitted distribution"
                ),
            )
            fig.update_layout(title=f'Density distribution for betweem: {activity}-{activity_pairs[activity]}') 
            fig.update_xaxes(title='Duration in minutes')
            fig.update_yaxes(title='Density')
            return fig
        except:
            pass
        