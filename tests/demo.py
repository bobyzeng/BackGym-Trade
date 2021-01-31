import os
import sys
import datetime
import warnings

import numpy as np
from IPython import get_ipython

sys.path.append(
    os.path.abspath('..'),
)

import bg_trade.envs as envs
from bg_trade.utils import fetch_data, build_db

warnings.simplefilter('ignore')

get_ipython().run_line_magic('matplotlib', 'inline')



db_name = 'HistoricalPriceData.db'
tickers = ['MSFT', 'AAPL', 'TSLA']
start = '01-01-2020'
end = datetime.datetime.now()



build_db(tickers, db_name, start=start, end=end)

data = fetch_data('HistoricalPriceData.db')
env = envs.TradingEnvNorm(data)

positions = env.positions
rewards = []



if True:
    
    done = False
    obs = env.reset()

    while not done:
        
        actions = env.format_action(
            positions,
            env.action_space.sample(),
        )

        obs, reward, done, info = env.step(actions)

        rewards.append(reward)
        
env.render()        
print(np.mean(rewards))


      