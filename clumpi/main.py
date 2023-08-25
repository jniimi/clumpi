import numpy as np
import pandas as pd
import random

def get_entropy(data, id, t, N):
    data = data.sort_values([id, t])
    data['cnt'] = 1
    tbl = data.groupby(id)[['cnt']].sum().rename(columns={'cnt':'F'})
    data['cnt'] = data.groupby(id)['cnt'].cumsum()

    tbl['R'] = N - data.groupby(id)[[t]].max() + 1

    last = data.groupby(id).last().reset_index(drop=False)
    last['cnt'] = N + 1
    data = pd.concat([data, last], axis = 0).sort_values([id, 'cnt']).reset_index(drop=True)
    
    data['prev_t'] = data[t].shift(1)
    data['x'] = np.nan

    data.loc[ data['cnt']==1,   'x' ] = data[t] # First
    data.loc[ data['cnt']==N+1, 'x' ] = N + 1 - data[t] # Remaining period
    data.loc[ data['x'].isna(), 'x' ] = data[t] - data['prev_t'] # Otherwise
    data['x'] = data['x'] / ( N + 1 )
    data['xlogx'] = data['x'] * np.log(data['x'])

    tbl['xlogx'] = data.groupby(id)['xlogx'].sum()
    tbl['log(n+1)']  = np.log(tbl['F'] + 1)
    tbl['H'] = 1 + (tbl['xlogx'] / tbl['log(n+1)'])

    return tbl[['R', 'F', 'H']]

def one_trial_in_M(N, n):
    tt = np.sort(np.random.choice((np.arange(N)+1), size=n, replace=False))

    if n == 1:
        x = np.array([tt[0], N+1-tt[-1]])
    else: # n > 1
        x = np.array([tt[0]] + np.diff(tt).tolist() + [N+1-tt[-1]])
    x = x/(N+1)
    h = 1 + sum( np.log(x) * x ) / np.log( n + 1 )
    return h

def calc_thr_for_n(N, M, n, alpha):
    H = []
    for m in range(M):
        h = one_trial_in_M(N = N, n = n)
        H.append(h)
    h_for_n = np.quantile(H, q = 1-alpha)
    return h_for_n

def calc_threshold(N = 30, M = 3000, alpha = 0.05):
    H = []
    for n in range(N):
        n = n + 1 # from 1 to N
        h_for_n = calc_thr_for_n(N = N, M = 3000, n = n, alpha = 0.05)
        H.append(h_for_n)
    thr = pd.DataFrame({
        'F' : [i+1 for i in range(N)],
        'H0': H
    })
    return thr

def check_args(id, t, N, M, alpha):
    varnames = ['R','F','C','H','H0','cnt']
    if id==t:
        raise ValueError('id and t must be different.')
    if type(N) != int:
        raise ValueError('N must be an integer value.')
    for x in [id, t]:
        if x in varnames:
            raise ValueError(x, 'cannot be names as follows,', str(varnames))
    if (alpha > 1)or(alpha < 0):
        raise ValueError('alpha needs to be between 0 - 1.')

def check_data(data, id, t, N):
    N1 = len(data)
    N2 = len(data.drop_duplicates([id, t]))
    if N1 != N2:
        raise ValueError('There is a duplication. Combination of id & t must be unique.')
    max_t = data[t].max()
    if max_t > N:
        raise ValueError('t must be less than N')

def get_RFC(data, id, t, N, M=3000, alpha=0.05):
    check_args(id=id, t=t, N=N, M=M, alpha=alpha)
    check_data(data=data, id=id, t=t, N=N)
    RFC = get_entropy(data=data, id=id, t=t, N=N).reset_index(drop=False)
    thr = calc_threshold(N = N, M = M, alpha = alpha)
    RFC = pd.merge(RFC, thr, on = 'F', how='inner')
    RFC['C'] = (RFC['H'] > RFC['H0']).astype(int)
    return RFC

def load_sample_data():
    d1 = pd.DataFrame({
        'user_id': ['Ava']*18,
        't':[1,2,4,5,7,8,10,11,13,14,16,18,20,21,23,25,26,28]
    })
    d2 = pd.DataFrame({
        'user_id': ['Chris']*10,
        't':[i*3+1 for i in range(10)]
    })
    d3 = pd.DataFrame({
        'user_id': ['Jack']*10,
        't':[i+1 for i in range(9)]+[28]
    })
    d4 = pd.DataFrame({
        'user_id': ['Jane']*4,
        't':[1, 2, 5, 7]
    })
    d = pd.concat([d1, d2, d3, d4], axis = 0)
    return d
