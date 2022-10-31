#importing all libraries
from aiohttp import ClientSession
import pandas as pd
import asyncio
import json
import csv


#user login input
login_data = {}
with open('loginData.csv', newline='') as uData:
    reader = csv.reader(uData)
    next(reader)
    for row in reader:
        login_data[row[0].strip()] = {'password' : row[1].strip(), 'pin' : row[2].strip()}


#asyncio login requests
enctokens = {}
failed_logins = {}

async def login(session, uid, pwd, pin):
    try:        
        sOne= await session.post(url='https://kite.zerodha.com/api/login',
                                 headers={'Content-Type': 'application/x-www-form-urlencoded'},
                                 data='user_id=%s&password=%s' %(uid, pwd))
        rId= (await sOne.json())['data']['request_id']
        try:
            sTwo= await session.post(url='https://kite.zerodha.com/api/twofa',
                                     headers={'Content-Type': 'application/x-www-form-urlencoded'},
                                     data='user_id=%s&request_id=%s&twofa_value=%s' %(uid, rId, pin))

            enctoken = sTwo.cookies['enctoken'].value
            margin = await session.get(url='https://kite.zerodha.com/oms/user/margins',
                                       headers={'Authorization': 'enctoken %s' %(enctoken)})
            enctokens[enctoken] = {'margin' : (await margin.json())['data']['equity']['net'], 'uId' : uid}
        except Exception as e:
            failed_logins[uid] = f'incorrect pin - {e}'
    except Exception as e:
        failed_logins[uid] = f'incorrect pwd - {e}'

async def request():
    tasks = []
    try:
        async with ClientSession() as session:
            for uid in login_data:
                task = asyncio.create_task(login(session, uid, login_data[uid]['password'], login_data[uid]['pin']))
                tasks.append(task)
            await asyncio.gather(*tasks)
    except Exception as e:
        print(f'exception {e}')

asyncio.run(request())

if len(enctokens) > 0:
    df = pd.DataFrame({'enctoken' : enctokens.keys(),
                      'margin' : [i['margin'] for i in enctokens.values()],
                      'uid' : [i['uId'] for i in enctokens.values()]})

    data1 = df
    data2 = pd.read_csv('compounding_data.csv')

    df = pd.merge(data1, data2,
                       on = 'uid',
                       how = 'inner')
    df['margin_x'] = df['margin_y']
    df = df.drop(columns='margin_y')
    df.columns = ['enctoken', 'margin', 'uid']
    df = df.sort_values(by=['uid'])
    df.to_csv('data.csv', sep=',', encoding='utf-8', index= False)

    print('successful enctoken logins saved in data.csv')
    print(df)
    print('\ntrading fund\t%s' %int(df['margin'].sum()))

if len(failed_logins)>0:
    print('\ncouldnt login for:')
    for i in failed_logins:
        print('\t%s --\t%s' %(i, failed_logins[i]))
