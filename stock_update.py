"""
通过理性人网站更新股票(A股)基本信息
"""
import os
import json
import datetime
import requests
from orm import Stock
from dba import DBAgent
from util import uniform_code, utc2date
from settings import BASE_DIR

''' 从理性人网站下载更新信息 '''
request_url = 'https://open.lixinger.com/api/a/stock'
headers = {'Content-type': 'application/json'}
request_body = {
    'token': '31415f3e-0d6c-444f-9c5a-2eb63de60fda',
}
repdir = os.path.join(BASE_DIR, 'data', 'lxr')
response = requests.post(request_url, headers=headers, data=json.dumps(request_body), verify=False)

if response.status_code == 200:
    stock_info = json.loads(response.content)['data']
    print('Total count of Stocks: %s' % len(stock_info))

    ''' 将更新信息写入文件 '''
    fn = 'stkidx_%s.json' % str(datetime.date.today())
    stock_file = os.path.join(repdir, fn)
    with open(stock_file, mode='w+', encoding='utf8') as fp:
        json.dump(response.json(), fp, ensure_ascii=False, indent=True)

    ''' DEBUG: 加载股票信息文件 '''
    # with open(stock_file, mode='r', encoding='utf8') as fp:
    #     stock_info = json.load(fp)['data']

    ''' 将更新信息写入数据库 '''
    dba = DBAgent()
    dba.stock_import(stock_info)

    # 断开数据库连接
    dba.db_session.close()
else:
    print('Failed to get stock info from lixinger.')

