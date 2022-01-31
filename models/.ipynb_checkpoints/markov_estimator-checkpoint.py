import pandas as pd
import numpy as np
import networkx as nx
from scipy import stats
import plotly.graph_objects as go
import re


class MarkovChainEstimator:
    def __init__(self,df):
        self.df = self._read_and_process_data(df)    
        
    def _read_and_process_data(self,df):
        datos1 = df
        datos1['tipo'] = datos1.activity.apply(lambda x: re.sub( r"([A-Z])", r" \1", x).split()[0])
        datos1['filtro'] = datos1.activity.apply(lambda x: re.sub( r"([A-Z])", r" \1", x).split()[1] if len(re.sub( r"([A-Z])", r" \1", x).split())>1 else "otro" )
        datos1 = datos1[-datos1.filtro.isin(["Take","B","End"])]
        datos1 = datos1[-datos1.stage.isin(["arrival"])]
        datos1.loc[-(datos1['stage']=='blood_analysis'),'tipo']=datos1[-(datos1['stage']=='blood_analysis')]['stage']
        datos1 = datos1.drop(['stage','activity','filtro'],axis=1)
        datos1 = datos1.sort_values(["PatientNumber","date"])
        datos1['tipo'].replace({'biochime':'biochimie'}, inplace=True)
        datos1['tipo2'] = datos1.tipo.shift(-1)
        datos1['PatientNumber2'] = datos1.PatientNumber.shift(-1)
        datos1.loc[datos1.PatientNumber != datos1.PatientNumber2,'tipo2']="Exit"
        return datos1
    
    def transition_matrix_df(self):
        datos1 = self.df.copy()
        datos1 = datos1.drop(['PatientNumber2','date','PatientNumber'],axis=1)
        datos1 = datos1.groupby(['tipo','tipo2']).size().reset_index(name='n')
        datos1['t'] = datos1['n'].groupby(datos1['tipo']).transform('sum')
        datos1['p'] = datos1['n']/datos1['t']
        datos1 = datos1.drop(['n','t'],axis=1)
        new_row = {'tipo':'Exit', 'tipo2':'Exit', 'p':1.0}    
        datos1 = datos1.append(new_row, ignore_index=True)
        trans_matrix = datos1.pivot(index='tipo', columns='tipo2', values='p')
        trans_matrix['triage']=0.0
        trans_matrix = trans_matrix.replace(np.nan,0)
        self.trans_matrix = trans_matrix
        return trans_matrix
    
    def transition_matrix_array(self):
        datos1 = self.df.copy()
        datos1 = datos1.drop(['PatientNumber2','date','PatientNumber'],axis=1)
        datos1 = datos1.groupby(['tipo','tipo2']).size().reset_index(name='n')
        datos1['t'] = datos1['n'].groupby(datos1['tipo']).transform('sum')
        datos1['p'] = datos1['n']/datos1['t']
        datos1 = datos1.drop(['n','t'],axis=1)
        new_row = {'tipo':'Exit', 'tipo2':'Exit', 'p':1.0}    
        datos1 = datos1.append(new_row, ignore_index=True)
        trans_matrix = datos1.pivot(index='tipo', columns='tipo2', values='p')
        trans_matrix['triage']=0.0
        trans_matrix = trans_matrix.replace(np.nan,0)
        trans_matrix_num = trans_matrix.to_numpy()
        return trans_matrix_num


    def check_transition_matrix(self):
        return (self.trans_matrix_num.sum(axis=1)==1).all()

    def _get_states(self,trans_matrix_df):
        states = list(trans_matrix_df.columns)
        return states


    def get_markov_edges(self,trans_matrix_df):
        edges = {}
        for col in trans_matrix_df.columns:
            for idx in trans_matrix_df.index:
                if trans_matrix_df.loc[idx,col]!=0:
                    edges[(idx,col)] = trans_matrix_df.loc[idx,col].round(3)
        return edges

    def create_networkx_object(self,trans_matrix_df):        
        edges_wts = self.get_markov_edges(trans_matrix_df)
        estados = self._get_states(trans_matrix_df)
        G = nx.Graph()
        G.add_nodes_from(estados)
        for k, v in edges_wts.items():
            tmp_origin, tmp_destination = k[0], k[1]
            G.add_edge(tmp_origin, tmp_destination,  label=v)   
        pos = nx.shell_layout(G)
        for n, p in pos.items():
            G.nodes[n]['pos'] = p
            self.G = G
        return G


    def markov_chain(self):            
        transition_matrix_df = self.trans_matrix
        transition_matrix = np.atleast_2d(transition_matrix_df.to_numpy())
        self.states = self._get_states(transition_matrix_df)
        self.index_dict = {self.states[index]: index for index in 
                           range(len(self.states))}
        self.state_dict = {index: self.states[index] for index in
                           range(len(self.states))}
        self.markov_chain = self.create_networkx_object(transition_matrix_df)
        
    # Methods to for ploting the Markov Chain
    
    def get_edge_trace(self,G):
        edge_x = []
        edge_y = []

        #etext = [f'weight{w}' for w in list(nx.get_edge_attributes(G, 'diameter').values())]#THIS list is empty for your data
        xtext=[]
        ytext=[]
        text=[]
        for edge in G.edges(data=True):
            x0, y0 = G.nodes[edge[0]]['pos']
            x1, y1 = G.nodes[edge[1]]['pos']
            xtext.append((x0+x1)/2)
            ytext.append((y0+y1)/2)
            text.append(edge[2].get('label'))
            edge_x.append(x0)
            edge_x.append(x1)
            edge_x.append(None)
            edge_y.append(y0)
            edge_y.append(y1)
            edge_y.append(None)

        edge_trace = go.Scatter(
            x=edge_x, y=edge_y,
            line=dict(width=0.5, color='#888'),
            mode='lines'
        )
        eweights_trace = go.Scatter(x=xtext,y= ytext, mode='text',
                                    marker_size=0.4,
                                    text=text,
                                    textposition='top center',
                                    textfont=dict(
                                        family="sans serif",
                                        size=10,
                                        color="midnightblue"
                                    )
                                   )
        self.edge_trace = edge_trace
        self.eweights_trace = eweights_trace
        return edge_trace, eweights_trace


    def get_node_trace(self,G):
        node_x = []
        node_y = []
        node_text = []
        for node in G.nodes():
            x, y = G.nodes[node]['pos']
            node_x.append(x)
            node_y.append(y)
            node_text.append(node)

        node_trace = go.Scatter(
            x=node_x, y=node_y,
            mode='markers+text',
            marker_size=80,
            text=node_text,
            #hoverinfo='text', #THIS LINE HAS NO SENSE BECAUSE text WAS NOT DEFINED
            marker_color='lightskyblue',
            marker_symbol='diamond-wide',
            textfont=dict(
                family="sans serif",
                size=13,
                color="black"
                )
            )

        return node_trace

    def plot_markov_chain(self,G):
        try:
            edge_trace, eweights_trace = self.get_edge_trace(G)
            node_trace = self.get_node_trace(G)
            fig = go.Figure(data=[edge_trace, node_trace,eweights_trace ],
                            layout=go.Layout(
                                title='<br>Markov Chain',
                                titlefont_size=16,
                                showlegend=False,
                                hovermode='closest',
                                margin=dict(b=20, l=5, r=5, t=40),
                                xaxis_visible=False,
                                yaxis_visible=False,
                                template="plotly_white")
                            )
            return fig
        except:
            pass
        
    
    # Methods to for testing Markov Chain Properties
    # Markov Property
    
    def contingency_table(self): #data from read_and_process_data
        datos2 = self.df.copy()
        datos2['tipo3'] = datos2.tipo2.shift(-1)
        datos2['PatientNumber3'] = datos2.PatientNumber2.shift(-1)
        datos2.loc[datos2.PatientNumber != datos2.PatientNumber3,'tipo3']="Exit"
        datos2 = datos2.drop(['PatientNumber2','date','PatientNumber','PatientNumber3'],axis=1)
        df1 = datos2.groupby(['tipo','tipo2']).size().reset_index(name='TSO')
        estados=self._get_states(self.transition_matrix_df())
        df2 = pd.DataFrame({"tipo3":estados})
        df3= datos2.groupby(['tipo','tipo2','tipo3']).size().reset_index(name='SSO')
        df2['key'] = 1
        df1['key'] = 1
        contingency_table = pd.merge(df1, df2, on ='key').drop("key", 1)
        contingency_table = pd.merge(contingency_table, df3, on =['tipo','tipo2','tipo3'])
        contingency_table["NSO"]=contingency_table["TSO"]-contingency_table["SSO"]
        return contingency_table

    def test_markov_prop_p_value(self,contingency_table):
        try:
            N_i_j=contingency_table[['SSO','NSO']].to_numpy()
            N_punto_j = contingency_table[['SSO','NSO']].sum().to_numpy()
            N_i_punto = contingency_table[['TSO']].T.to_numpy()
            n= N_punto_j.sum()
            h=contingency_table.shape[0]
            Q_Est=0
            for i in range(h):
                for j in range(2):
                    Q_Est=Q_Est+((N_i_j[i,j]-((N_i_punto[0,i])*(N_punto_j[j]/n)))**2)/((N_i_punto[0,i])*(N_punto_j[j]/n))
            p=1-stats.chi2.cdf(Q_Est, (h-1)**2)
            print('Q statistic is: ',Q_Est,'p-value is: ',p)
        except:
            pass
        return p.round(3)

    def test_markov_prop(self): #data from read_and_process_data
        data = self.df
        cont_table=self.contingency_table()
        test=cont_table.groupby(['tipo2','tipo3']).apply(lambda x: self.test_markov_prop_p_value(x)).reset_index(name='p_value')
        return test
    
    # Markov Chain Order 
    
    def test_order_markov_chain(self):
        datos2 = self.df.copy()
        datos2['tipo3'] = datos2.tipo2.shift(-1)
        datos2['PatientNumber3'] = datos2.PatientNumber2.shift(-1)
        datos2.loc[datos2.PatientNumber != datos2.PatientNumber3,'tipo3']="Exit"
        datos2 = datos2.drop(['PatientNumber2','date','PatientNumber','PatientNumber3'],axis=1)
        datos2 = datos2.groupby(['tipo','tipo2','tipo3']).size().reset_index(name="number")
        datos2 = pd.pivot_table(datos2,index=['tipo','tipo2'], columns='tipo3', values='number').replace(np.nan,0)
        datos2['n_i_j_punto'] = datos2.sum(axis=1)
        p_est_j_m = datos2.groupby(['tipo2']).sum().iloc[:,:-1].div(self.df.groupby(['tipo2']).sum().sum(axis=1), axis=0)
        p_est_i_j_m = datos2.iloc[:,:-1].div(datos2.n_i_j_punto, axis=0)
        estados=self._get_states(self.transition_matrix_df())
        Qj=[]
        Q_j=0
        for j in estados[:-1]:
            for i in estados[1:]:
                for m in estados[:-1]:
                    try:
                        if np.isnan((datos2.loc[(i,j),m]*(p_est_i_j_m.loc[(i,j),m]-p_est_j_m.loc[j,m])**2)/(p_est_j_m.loc[j,m])):
                            pass
                        else:
                            Q_j=Q_j+ (datos2.loc[(i,j),m]*(p_est_i_j_m.loc[(i,j),m]-p_est_j_m.loc[j,m])**2)/(p_est_j_m.loc[j,m])
                        continue
                    except:
                        pass
            Qj.append(Q_j)
        Q=sum(Qj)
        k=len(estados)
        p_value = 1-stats.chi2.cdf(Q, k*(k-1)**2)
        print('Q statistic is: ',Q,'p-value is: ',p_value)
        return Q, p_value