import numpy as np
import pandas as pd
import random
import matplotlib.pyplot as plt

def get_entropy(data, id, t, N):
    data = data.sort_values([id, t])
    tbl = data.groupby(id)[t].agg(F='size',max_t='max')
    tbl['R'] = N - tbl['max_t'] + 1

    data['prev_t'] = data.groupby(id)[t].shift(1)

    # without last
    data['x'] = np.where(
        data['prev_t'].isna(), 
        data[t], # prev_t is nan: First
        data[t] - data['prev_t'] # prev_t is not nan: not First
        )
    # last
    last_period = pd.DataFrame({
        id: tbl.index,
        'x': (N + 1 - tbl['max_t'])
    })
    data = pd.concat([data[[id,'t', 'x']], last_period], ignore_index=True)

    data['x'] = data['x'] / (N + 1)
    data['xlogx'] = data['x'] * np.log(data['x'])

    entropy = data.groupby(id)['xlogx'].sum()
    tbl['H'] = 1 + (entropy / np.log(tbl['F'] + 1))
    return tbl[['R','F','H']]

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
    if type(N)!=int or type(M)!=int:
        raise ValueError('N and M must be an integer value.')
    for x in [id, t]:
        if x in varnames:
            raise ValueError(f'{x} cannot be named same as following variable names (internally used): f{varnames}')
    if (alpha > 1)or(alpha < 0):
        raise ValueError('alpha must be in [0, 1] value.')

def check_data(data, id, t, N):
    N1 = len(data)
    N2 = len(data.drop_duplicates([id, t]))
    if N1 != N2:
        raise ValueError('There is a duplication. Combination of id & t must be unique.')
    if data[t].min() < 1:
        raise ValueError('t cannot be less than 1')
    if data[t].max() > N:
        raise ValueError('t must be less than N')

def plot_occurrence(data, user_id='user_id', t='t', N=30):
    user_order = data[user_id].unique()[::-1]
    user_mapping = {user: idx for idx, user in enumerate(user_order)}

    y = data[user_id].map(user_mapping)

    plt.figure(figsize=(8, 3))
    plt.scatter(data[t], y, marker='o')

    plt.yticks(range(len(user_order)), user_order)
    plt.xticks(range(1, N+1))
    plt.xlabel(t)
    plt.ylabel(user_id)
    plt.title('Event Occurrences')
    plt.grid(axis='y', linestyle='-', alpha=0.5)
    plt.show()

def get_RFC(data, id, t, N, M=3000, alpha=0.05, plot=False):
    check_args(id=id, t=t, N=N, M=M, alpha=alpha)
    check_data(data=data, id=id, t=t, N=N)
    if plot:
        plot_occurrence(data=data, user_id=id, t=t, N=N)
    RFC = get_entropy(data=data, id=id, t=t, N=N).reset_index(drop=False)
    thr = calc_threshold(N = N, M = M, alpha = alpha)
    RFC = pd.merge(RFC, thr, on = 'F', how='inner')
    RFC['C'] = (RFC['H'] > RFC['H0']).astype(int)
    return RFC

def create_one_user_sample(name, ts=[1,2,5]):
    user_sample = pd.DataFrame({'user_id': [name]*len(ts), 't': ts})
    return user_sample

def load_sample_data():
    d = []
    d.append(create_one_user_sample('Ava', ts=[1,2,4,5,7,8,10,11,13,14,16,18,20,21,23,25,26,28]))
    d.append(create_one_user_sample('Chris', ts=[i*3+1 for i in range(10)]))
    d.append(create_one_user_sample('Jack', ts=[i+1 for i in range(9)]+[28]))
    d.append(create_one_user_sample('Jane', ts=[1, 2, 5, 7]))
    d.append(create_one_user_sample('Smith', ts=[1, 10, 19, 28]))
    d = pd.concat(d, axis = 0).reset_index(drop=True)
    return d
