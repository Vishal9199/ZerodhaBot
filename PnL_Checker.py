#importing libraries
from aiohttp import ClientSession
import pandas as pd
import asyncio
import json
import csv


#enctoken input
enctokens = []
with open('data.csv', newline='') as uData:
        reader = csv.reader(uData)
        enctokens.clear()
        next(reader)
        for row in reader:
                enctokens.append(row[0])

original_id = ['ZTR317', 'RJ1253']
original_id.sort()

#asyncio orders requests
user = {}
asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

async def positions(session, enctoken):
   try:
        name = await session.get(url='https://kite.zerodha.com/oms/user/profile/full',
                                 headers={'Authorization': 'enctoken %s' %(enctoken)})
        margin = await session.get(url='https://kite.zerodha.com/oms/user/margins',
                                   headers={'Authorization': 'enctoken %s' %(enctoken)})
        details = await session.get(url='https://kite.zerodha.com/oms/portfolio/positions',
                                    headers={'Authorization': 'enctoken %s' %(enctoken)})

        net_margin = int((await margin.json())['data']['equity']['net'])
        opening_balance = int((await margin.json())['data']['equity']['available']['opening_balance'])
        pnl = 0
        for i in (await details.json())['data']['net']:
                if 'NIFTY' in i['tradingsymbol']:
                        pnl += i['pnl']
        if opening_balance > 0:
                user[(await name.json())['data']['user_id']] = {'pnl' : round(pnl, 2), 'roi' : round((pnl/opening_balance)*100, 2), 'open_bal' : opening_balance, 'available_bal' : net_margin}
        else:
                user[(await name.json())['data']['user_id']] = {'pnl' : round(pnl, 2), 'roi' : round((pnl/net_margin)*100, 2), 'open_bal' : opening_balance, 'available_bal' : net_margin}

   except Exception as e:
           pass

async def request():
        try:
                tasks = []
                async with ClientSession() as session:
                    for token in enctokens:
                        task = asyncio.create_task(positions(session, token))
                        tasks.append(task)
                    await asyncio.gather(*tasks)
        except Exception as e:
                logger.error(e)

asyncio.run(request())
logged_out_users = [i for i in original_id if i not in user.keys()]

df = pd.DataFrame({'UID' : user.keys(),
                   'pnl' : [i['pnl'] for i in user.values()],
                   'roi' : [i['roi'] for i in user.values()],
                   'open_bal' : [i['open_bal'] for i in user.values()],
                   'available_bal' : [i['available_bal'] for i in user.values()]})

df = df.sort_values(by=['UID'])
print(df.to_string(index=False))
print()

tot_pnl = 0
ope_bal = 0
tot_bal = 0
for i in user.values():
        tot_pnl += i['pnl']
        tot_bal += i['available_bal']
        ope_bal += i['open_bal']

print(f'total pnl - {tot_pnl}')
print(f'total bal - {tot_bal}')
print(f'total roi - {(tot_pnl/ope_bal)*100}')

print('logged out users:')
print(logged_out_users)
input()
