import os
import json
import datetime
from orm import Stock, Profit, Balance, CashFlow, FinMatrix, BaseInfo
from orm_ope import get_session, session_scope
from contextlib import contextmanager
import time


log = open('log.csv', 'w+')


@contextmanager
def timing(title, name):
    start = time.time()
    try:
        yield
    finally:
        end = time.time()
        print('%s,%s,%s' % (title, name, end - start), file=log)


BASE_DIR = 'D:/gallopor/invsys'
# BASE_DIR = os.path.dirname(os.path.abspath(__file__))
db_session = get_session()

# code = '000001.SZ'
start_year = 2001
quarter = ['03-31', '06-30', '09-30', '12-31']

for stock in db_session.query(BaseInfo):
    code = stock.code

    ''' 加载数据源 '''
    report_file = os.path.join(BASE_DIR, 'data/lxr/finrep/code/%s.json' % code[:6])
    if not os.path.exists(report_file):
        continue
    with open(report_file, mode='r', encoding='utf-8') as fp:
        finrep = json.load(fp)

    for y in range(start_year, 2018):
        for q in quarter:
            report_quarter = '%s-%s' % (str(y), q)
            # 数据源中是否存在该财报信息
            if report_quarter not in finrep:
                continue
            else:
                with timing(code, report_quarter):

                    ''' 导入数据到Profit表 '''
                    profit = db_session.query(Profit).filter(
                        Profit.code == code, Profit.report_quarter == report_quarter
                    ).first()
                    if profit is None:
                        profit = Profit(
                            code=code,
                            report_quarter=datetime.datetime.strptime(report_quarter, '%Y-%m-%d'),
                            revenue=finrep[report_quarter]['revenue']['t'],
                            operating_cost=finrep[report_quarter]['operating_cost']['t'],
                            selling_expense=finrep[report_quarter]['selling_expense']['t'],
                            administration_expense=finrep[report_quarter]['administration_expense']['t'],
                            financing_expense=finrep[report_quarter]['financing_expense']['t'],
                            operating_profit=finrep[report_quarter]['operating_profit']['t'],
                            profit_before_tax=finrep[report_quarter]['profit_before_tax']['t'],
                            net_profit=finrep[report_quarter]['net_profit']['t'],
                            net_profit_ts=finrep[report_quarter]['net_profit_to_shareholders']['t'],
                            net_profit_ts_aii=finrep[report_quarter]['net_profit_to_shareholders_aii']['t'],
                            minority_interests=finrep[report_quarter]['minority_interests']['t']
                        )
                        db_session.add(profit)
                    else:
                        print('Profit %s of %s exists' % (report_quarter, code))

                    ''' 导入数据到Balance表 '''
                    balance = db_session.query(Balance).filter(
                        Balance.code == code, Balance.report_quarter == report_quarter
                    ).first()
                    if balance is None:
                        balance = Balance(
                            code=code,
                            report_quarter=datetime.datetime.strptime(report_quarter, '%Y-%m-%d'),
                            total_assets=finrep[report_quarter]['total_assets']['t'],
                            current_assets=finrep[report_quarter]['current_assets']['t'],
                            non_current_assets=finrep[report_quarter]['non_current_assets']['t'],
                            total_liabilities=finrep[report_quarter]['total_liabilities']['t'],
                            non_current_liabilities=finrep[report_quarter]['non_current_liabilities']['t'],
                            total_equity=finrep[report_quarter]['total_equity']['t'],
                            equity_to_shareholders=finrep[report_quarter]['equity_to_shareholders']['t'],
                        )
                        db_session.add(balance)
                    else:
                        print('Balance %s of %s exists' % (report_quarter, code))

                    ''' 导入数据到CashFlow表 '''
                    cashflow = db_session.query(CashFlow).filter(
                        CashFlow.code == code, CashFlow.report_quarter == report_quarter
                    ).first()
                    if cashflow is None:
                        cashflow = CashFlow(
                            code=code,
                            report_quarter=datetime.datetime.strptime(report_quarter, '%Y-%m-%d'),
                            cash_from_operating=finrep[report_quarter]['cash_from_operating_activities']['t'],
                            cash_for_operating=finrep[report_quarter]['cash_paid_for_operating_activities']['t'],
                            cash_flow_of_operating=finrep[report_quarter]['cash_flow_from_operating_activities']['t'],
                            cash_from_investing=finrep[report_quarter]['cash_from_investing_activities']['t'],
                            cash_for_investing=finrep[report_quarter]['cash_paid_for_investing_activities']['t'],
                            cash_flow_of_investing=finrep[report_quarter]['cash_flow_from_investing_activities']['t'],
                            cash_from_financing=finrep[report_quarter]['cash_from_financing_activities']['t'],
                            cash_for_financing=finrep[report_quarter]['cash_paid_for_financing_activities']['t'],
                            cash_flow_of_financing=finrep[report_quarter]['cash_flow_from_financing_activities']['t'],
                        )
                        db_session.add(cashflow)
                    else:
                        print('CashFlow %s of %s exists' % (report_quarter, code))

                    ''' 导入数据到FinMatrix表 '''
                    fin_matirx = db_session.query(FinMatrix).filter(
                        FinMatrix.code == code, FinMatrix.report_quarter == report_quarter
                    ).first()
                    if fin_matirx is None:
                        fin_matirx = FinMatrix(
                            code=code,
                            report_quarter=datetime.datetime.strptime(report_quarter, '%Y-%m-%d'),
                            return_on_asset=finrep[report_quarter]['return_on_asset']['t'],
                            net_profit_margin=finrep[report_quarter]['net_profit_margin']['t'],
                        )
                        db_session.add(fin_matirx)
                    else:
                        print('FinMatrix %s of %s exists' % (report_quarter, code))
    # 每个股票保存一次数据库
    with timing('commit', code):
        db_session.commit()
    print('Report of %s has been imported' % code)

# 断开数据库连接
db_session.close()
log.close()
