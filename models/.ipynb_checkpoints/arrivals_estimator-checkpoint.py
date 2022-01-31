import pandas as pd
import numpy as np
import scipy
import plotly.express as px
from scipy.stats import expon
from scipy.stats import poisson



class ArrivalEstimator:
    def __init__(self,df):
        """
        Parameters:
        df: datafile
      
        """
        df.reset_index(drop= True, inplace = True)
        df = df[df.stage == "arrival"]
        self.df = df
                
    def fit(self):
        """        
        Parameters: df
        Return:
            - array with lambda parameter of the non homogeneous poisson process
            - plot with the NH poisson process
            - plot of individual poisson and exponential distribution for each hour.            
        """
        df = self.df
        df['date'] = pd.to_datetime(df.date)
        df['day'] = df.date.dt.day_name()
        df['hour'] = df.date.dt.hour
        self.nhpp_day_hour_lambda = df[['day','hour','activity']].groupby(['day','hour']).agg(['count'])
        self.nhpp_hour_lambda = self.nhpp_day_hour_lambda.groupby("hour").mean()
        self.nhpp_hour_lambda_dict = dict(zip(range(0,24),[i[0]  for i in self.nhpp_hour_lambda.values]))
        self.search_list = [{'label': f'{i+1} h', 'value': j} for i,j in self.nhpp_hour_lambda_dict.items() ]
    
    
    def nh_poisson(self):
        try:
            df = self.df
            df  =self.nhpp_day_hour_lambda.reset_index()
            df.rename(columns={'day': 'day', 'hour': 'hour','activity  count':'count'}, inplace=True)
            df.reset_index(drop = True, inplace = True)
            df.columns = [ 'day','hour','count']
            fig = px.line(df, x = 'hour', y = 'count', color = 'day',
                         labels={'x':'Day hours', 'y':'Arrival rate'},
                          title=f"Estimated hourly arrival rate 𝜆̂(t) per day")
            return fig
        except:
            pass
        
    def plot_poisson(self, params):
        try:
            lmbda = params
            X = [0, 1, 2, 3, 4, 5,6,7,8,9,10]
            poisson_pd = poisson.pmf(X, lmbda)
            fig = px.line( x=X, y=poisson_pd,
                          labels={'x':'Number of patients arrivals', 'y':'Density'},
                          markers=True,
                          title=f"Poisson distribution, lambda = {params}",
                         )

            fig.update_layout(
                xaxis = dict(
                    tickmode = 'linear',
                )
            )
            return fig
        except:
            pass
        
        
    def plot_exponential(self,params):
        try:
            X = [0, 1, 2, 3, 4, 5,6,7,8,9,10]
            lmbda = params
            exp_x = np.arange(0, 4, 0.1)   
            exp_pd = expon.pdf(exp_x, 0, 1/lmbda) 
            fig = px.line( x=exp_x, y=exp_pd,
                          labels={'x':'Inter arrivals time', 'y':'Density'},

                          title=f"Exponential distribution, lambda = {params},",
                         )

            fig.update_layout(
                xaxis = dict(
                    tickmode = 'linear',
                )
            )
            return fig     
        except:
            pass