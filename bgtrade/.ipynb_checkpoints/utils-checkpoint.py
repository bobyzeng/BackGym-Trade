import os
import datetime
import sqlite3 as sql

import numpy as np
import pandas as pd
import yfinance as yf


 
    
def build_table(conn, table_name, table_data):
    
    table_data.to_sql(
        name=table_name, 
        con=conn, 
        index=False, 
        if_exists='replace',
    )
    
    conn.commit()
    

    
def test_db(db_name, path):
    
    data = fetch_data(
        os.path.join(
            path, 
            db_name,
        )
    )
    
    try:
        validate_data(data)
        print('Database is valid')
        
    except Exception as e:
        print('Error in database:', e)


        
def yahoo(ticker, start, end):
    
    df = yf.Ticker(ticker)
    
    if None in (start, end, ):
        
        return (df
            .history(
                period='max',
            )
            .reset_index(
                drop=False,
            )
        )
    
    else:
        
        assert (pd.to_datetime(end)-pd.to_datetime(start)).days > 365, \
            'Must be more than 1 year of historical data'
        
        return (df
            .history(
                start=pd.to_datetime(start).strftime('%Y-%m-%d'),
                end=pd.to_datetime(end).strftime('%Y-%m-%d'),
            )
            .reset_index(
                drop=False,
            )
        )

    
    
def build_db(tickers, db_name, path='.', start=None, end=None, test=True):
    
    connection = sql.connect(
        os.path.join(
            path, 
            db_name,
        )
    )

    for ticker in tickers:
        
        df = yahoo(ticker.upper(), start, end)
                
        df.columns = df.columns.str.lower()
    
        df['date'] = pd.to_datetime(df['date'])
        df.sort_values(by='date', ascending=True, inplace=True)
        
        df['ma_30'] = df['close'].rolling(window=30, center=False).mean()
        df['ma_5'] = df['close'].rolling(window=5, center=False).mean()
        df['volatil'] = np.abs(df['ma_30']-df['close'])
        df['diff'] = df['close'].diff(periods=1)
        df['diff_ma_5'] = df['close'].diff(periods=1).rolling(window=5, center=False).mean()
        
        df.dropna(axis=0, inplace=True)
        df.drop(['open', 'high', 'low', 'stock splits', 'dividends'], axis=1, inplace=True)
        df.reset_index(drop=True, inplace=True)
                            
        print(ticker, df.shape, df.loc[0, 'date'])
            
        try:
            build_table(connection, ticker.lower(), df)
            print('Done', ticker, sep=' - ')
    
        except Exception as e:
            print('Error', ticker, e, sep=' - ')
            
        print()
            
    connection.close()
    
    if test: test_db(db_name, path)

    

def fetch_data(db_name, path='.'):
    
    data = {}
    
    conn = sql.connect(db_name)
    c = conn.cursor()
        
    ticker_query = """
        SELECT name
        FROM sqlite_master
        WHERE type='table';
    """
    
    try:
        c.execute(ticker_query)
    except Exception as e:
        conn.close()
        raise e
        
    for t in c.fetchall():
        ticker = t[0]

        tables_query = f"""
            SELECT *
            FROM {ticker};
        """
        
        try:
            data[ticker] = pd.read_sql(tables_query, con=conn, parse_dates='date')
        except Exception as e:
            conn.close()
            raise e
        
    conn.close()
    return data



def validate_data(dataframes):
    
    assert isinstance(dataframes, dict), 'Historical stock data must be dictionary instance'
    
    lens, firsts, lasts = [], [], []
    cols = ('date', 'close', 'volume', 'ma_30', 'ma_5', 'volatil', 'diff', 'diff_ma_5', )
    
    for ticker, df in dataframes.items():
        
        assert isinstance(df, pd.DataFrame), 'Historical data must be dataframe(s)'
        assert df.index.start == 0, 'Dataframe index must start at 0'
        
        df.columns = df.columns.str.lower()
        df.columns = df.columns.str.strip()
        
        assert set(df.columns) == set(cols), f'Missing {set(cols)-set(df.columns)} column(s)'
        
        df['date'] = pd.to_datetime(df['date'])
        df.sort_values(by='date', ascending=True, inplace=True)

        lens.append(len(df))
        firsts.append(df['date'].iloc[0])
        lasts.append(df['date'].iloc[-1])
        
        assert df.isna().sum().sum() == 0, 'Missing values present in historical data'
        
        df = df[[*cols]]
        
    assert len(set(lens)) == 1, 'Lengths of price histories must match'    
    assert len(set(firsts)) == 1, 'Starting dates of price histories must match'
    assert len(set(lasts)) == 1, 'Ending dates of price histories must match'    
    
    
        