import json
import datetime
from contextlib import contextmanager
from sqlalchemy.orm import sessionmaker, scoped_session

from orm import DB_ENGINE, db_init
from orm import Stock, Balance, Profit, CashFlow, FinMatrix
from util import uniform_code, utc2date, timing

# DB_SESSION = scoped_session(sessionmaker(bind=DB_ENGINE))
DB_SESSION = scoped_session(sessionmaker(bind=DB_ENGINE, expire_on_commit=False))


class DBAgent(object):

    db_session = DB_SESSION()

    def __init__(self):
        db_init()

    @contextmanager
    def session_scope(self):
        session = DB_SESSION()
        try:
            yield session
            session.commit()
        except:
            session.rollback()
            raise
        finally:
            session.close()

    def stock_import(self, df, ft='json'):
        """
        从文件中导入数据到数据库
        :param ft: 数据文件类型，支持json或csv
        :param df: 数据文件路径
        :return:
        """
        if ft == 'json':
            with open(df, mode='r', encoding='utf-8') as fp:
                stock_info = json.load(fp)['data']
        elif ft == 'csv':
            with open(df, mode='r', encoding='utf-8') as fp:
                stock_info = json.load(fp)['data']
        else:
            print('No support file type.')

        for si in stock_info:
            code = uniform_code(si['stockCode'])
            symbol = si['cnName']
            # 读取listed_date信息，未上市则为None
            if 'ipoDate' in si:
                listed_date = utc2date(si['ipoDate'])
            else:
                listed_date = None
            # 如已退市，则跳出循环，读取下一条信息
            if 'delistingDate' in si:
                continue

            # 读取数据库已存信息，与更新信息比较
            now = datetime.datetime.now()
            bi = self.db_session.query(Stock).filter_by(code=code).first()
            if bi is not None:
                if bi.symbol != symbol:
                    bi.symbol = symbol
                    bi.update_time = now
                if bi.listed_date != listed_date:
                    if bi.listed_date is None:
                        bi.update_time = now
                    else:
                        # 与原信息不符，则提示，但不修改
                        print('listed_date %s of %s maybe wrong' % (listed_date, code))
            else:
                bi = Stock(code=code, symbol=symbol, listed_date=listed_date, update_time=now)
                self.db_session.add(bi)
                print('Add stock: %s %s' % (code, symbol))

        # 保存数据到数据库
        self.db_session.commit()

    def stock_export(self, df, ft='json'):
        """
        从数据库中导出数据到文件
        :param ft: 数据文件类型，支持json或csv
        :param df: 数据文件路径
        :return:
        """
        if ft == 'json':
            with open(df, mode='r', encoding='utf-8') as fp:
                stock_info = json.load(fp)['data']
        elif ft == 'csv':
            with open(df, mode='r', encoding='utf-8') as fp:
                stock_info = json.load(fp)['data']
        else:
            print('No support file type.')

    def profit_update(self, finrep, code, report_quarter, commit=False):
        """ 导入数据到Profit表 """

        profit = self.db_session.query(Profit).filter(
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
            self.db_session.add(profit)
            if commit:
                self.db_session.commit()
        else:
            print('Profit %s of %s exists' % (report_quarter, code))

    def balance_update(self, finrep, code, report_quarter, commit=False):
        """
        导入数据到 Balance 表
        :param finrep: 数据文件类型，支持json或csv
        :param code: 数据文件路径
        :param report_quarter: 数据文件路径
        :param commit: 数据文件路径
        :return:
        """
        balance = self.db_session.query(Balance).filter(
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
            self.db_session.add(balance)
            if commit:
                self.db_session.commit()
        else:
            print('Balance %s of %s exists' % (report_quarter, code))

    def cashflow_update(self, finrep, code, report_quarter, commit=False):
        ''' 导入数据到CashFlow表 '''
        cashflow = self.db_session.query(CashFlow).filter(
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
            self.db_session.add(cashflow)
            if commit:
                self.db_session.commit()
        else:
            print('CashFlow %s of %s exists' % (report_quarter, code))

    def matrics_update(self, finrep, code, report_quarter, commit=False):
        ''' 导入数据到FinMatrix表 '''
        fin_matirx = self.db_session.query(FinMatrix).filter(
            FinMatrix.code == code, FinMatrix.report_quarter == report_quarter
        ).first()
        if fin_matirx is None:
            fin_matirx = FinMatrix(
                code=code,
                report_quarter=datetime.datetime.strptime(report_quarter, '%Y-%m-%d'),
                return_on_asset=finrep[report_quarter]['return_on_asset']['t'],
                net_profit_margin=finrep[report_quarter]['net_profit_margin']['t'],
            )
            self.db_session.add(fin_matirx)
            if commit:
                self.db_session.commit()
        else:
            print('FinMatrix %s of %s exists' % (report_quarter, code))

    def db_commit(self):
        self.db_session.commit()


if __name__ == '__main__':
    dba = DBAgent()
