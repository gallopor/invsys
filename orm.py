import os
from sqlalchemy import create_engine, Column, ForeignKey
from sqlalchemy import String, Integer, BIGINT, Float, DATE, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base


''' 数据库连接 - sqlite '''
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_NAME = 'db.sqlite3'
DB_URI = 'sqlite:///' + os.path.join(BASE_DIR, DB_NAME)

''' 数据库连接 - MYSQL '''
# DB_NAME = 'finsys'
# # DB_SERVER = 'quantsys-mysql.cwlp0wlvgb7h.rds.cn-north-1.amazonaws.com.cn'
# DB_SERVER = 'mysql-finsys.c8jpclbaj09q.ap-southeast-1.rds.amazonaws.com'
# DB_USER = 'gallopor'
# DB_PASSWORD = 'Xy875125'
# DB_URI = 'mysql://%s:%s@%s/%s' % (DB_USER, DB_PASSWORD, DB_SERVER, DB_NAME)
# DB_STRING = 'mysql://gallopor:Xy875125@mysql-finsys.c8jpclbaj09q.ap-southeast-1.rds.amazonaws.com/finsys?charset=utf8mb4'

''' 创建数据库引擎 '''
DB_ENGINE = create_engine(DB_URI, echo=True)
# DB_ENGINE = create_engine(DB_URI, echo=True, connect_args={'charset': 'utf8mb4'})
# DB_ENGINE = create_engine(DB_STRING, echo=True)

''' 创建数据库表单的基类 '''
BASE_TABLES = declarative_base(DB_ENGINE)


class BaseInfo(BASE_TABLES):
    """ 股票基本信息 """
    __tablename__ = 'base_info'

    id = Column(Integer, primary_key=True)
    # 必须添加索引才能关联外键
    code = Column(String(16), nullable=False, index=True)   # 证券代码
    symbol = Column(String(16))                             # 证券简称
    listed_date = Column(DATE)                              # 上市日期
    update_time = Column(DateTime)                          # 更新时间


class Stock(BASE_TABLES):
    """ 股票基本信息 """
    __tablename__ = 'stock'

    id = Column(Integer, primary_key=True)
    # 必须添加索引才能关联外键
    code = Column(String(16), nullable=False, index=True)   # 证券代码
    symbol = Column(String(16))                             # 证券简称
    industry = Column(String(16))                           # 所属行业
    listed_date = Column(DATE)                              # 上市日期
    update_time = Column(DateTime)                          # 更新时间
    profit = relationship('Profit', backref='stock')
    balance = relationship('Balance', backref='stock')
    cashflow = relationship('CashFlow', backref='stock')
    matirx = relationship('FinMatrix', backref='stock')

    def __repr__(self):
        return "<Stock(code='%s', symbol='%s')>" % (self.code, self.symbol)


class Profit(BASE_TABLES):
    """ 利润表 """
    __tablename__ = 'profit'

    id = Column(Integer, primary_key=True)
    code = Column(String(16), ForeignKey('stock.code'))     # 证券代码
    report_quarter = Column(DATE, nullable=False)           # 报告期
    report_date = Column(DATE)                              # 公告日期
    revenue = Column(BIGINT)                                # 总收入
    operating_revenue = Column(BIGINT)                      # 营业收入
    operating_cost = Column(BIGINT)                         # 营业成本
    selling_expense = Column(BIGINT)                        # 销售费用
    administration_expense = Column(BIGINT)                 # 管理费用
    financing_expense = Column(BIGINT)                      # 财务费用
    operating_profit = Column(BIGINT)                       # 营业利润
    profit_before_tax = Column(BIGINT)                      # 利润总额
    net_profit = Column(BIGINT)                             # 净利润
    net_profit_ts = Column(BIGINT)                          # 归母净利润 (to shareholder)
    net_profit_ts_aii = Column(BIGINT)                      # 归母扣非净利润 (after irregular items )
    minority_interests = Column(BIGINT)                     # 少数股东损益
    update_time = Column(DateTime)                          # 更新时间

    def __repr__(self):
        return "<Profit(code='%s', report_quarter='%s')>" % (self.code, self.report_quarter)

    def fields(self):
        return ['revenue', 'operating_cost', 'selling_expense', 'administration_expense',
                'financing_expense', 'operating_profit', 'profit_before_tax', 'net_profit',
                'net_profit_ts', 'net_profit_ts_aii', 'minority_interests']


class Balance(BASE_TABLES):
    """ 资产负债表 """
    __tablename__ = 'balance'

    id = Column(Integer, primary_key=True)
    code = Column(String(16), ForeignKey('stock.code'))     # 证券代码
    report_quarter = Column(DATE, nullable=False)           # 报告期
    report_date = Column(DATE)                              # 公告日期
    total_assets = Column(BIGINT)                           # 总资产
    current_assets = Column(BIGINT)                         # 流动资产
    non_current_assets = Column(BIGINT)                     # 非流动资产
    total_liabilities = Column(BIGINT)                      # 总负债
    non_current_liabilities = Column(BIGINT)                # 非流动负债
    total_equity = Column(BIGINT)                           # 所有者权益
    equity_to_shareholders = Column(BIGINT)                 # 归属于母公司的股东权益
    update_time = Column(DateTime)                          # 更新时间

    def __repr__(self):
        return "<Balance(code='%s', report_quarter='%s')>" % (self.code, self.report_quarter)


class CashFlow(BASE_TABLES):
    """ 现金流量表 """
    __tablename__ = 'cashflow'

    id = Column(Integer, primary_key=True)
    code = Column(String(16), ForeignKey('stock.code'))     # 证券代码
    report_quarter = Column(DATE, nullable=False)           # 报告期
    report_date = Column(DATE)                              # 公告日期
    cash_from_operating = Column(BIGINT)                    # 经营活动现金流入
    cash_for_operating = Column(BIGINT)                     # 经营活动现金流出
    cash_flow_of_operating = Column(BIGINT)                 # 经营活动现金流净额
    cash_from_investing = Column(BIGINT)                    # 投资活动现金流入
    cash_for_investing = Column(BIGINT)                     # 投资活动现金流出
    cash_flow_of_investing = Column(BIGINT)                 # 投资活动现金流净额
    cash_from_financing = Column(BIGINT)                    # 筹资活动现金流入
    cash_for_financing = Column(BIGINT)                     # 筹资活动现金流出
    cash_flow_of_financing = Column(BIGINT)                 # 筹资活动现金流净额
    update_time = Column(DateTime)                          # 更新时间

    def __repr__(self):
        return "<CashFlow(code='%s', report_quarter='%s')>" % (self.code, self.report_quarter)


class FinMatrix(BASE_TABLES):
    """ 财务指标 """
    __tablename__ = 'fin_matirx'

    id = Column(Integer, primary_key=True)
    code = Column(String(16), ForeignKey('stock.code'))     # 证券代码
    report_quarter = Column(DATE)                           # 报告期
    report_date = Column(DATE)                              # 公告日期
    price = Column(Float)                                   # 最新价格
    total_shares = Column(BIGINT)                           # 总股本
    circulation_shares = Column(BIGINT)                     # 流通股本
    capitalization = Column(BIGINT)                         # 总市值
    return_on_asset = Column(Float)                         # 净资产回报率
    gross_profit_margin = Column(Float)                     # 毛利率
    net_profit_margin = Column(Float)                       # 净利率
    earnings_ps = Column(Float)                             # 每股收益 (per share)
    book_value_ps = Column(Float)                           # 每股净资产 (per share)
    dividend_ps = Column(Float)                             # 每股分红 (per share)
    update_time = Column(DateTime)                          # 更新时间

    def __repr__(self):
        return "<FinMatrix(code='%s', report_quarter='%s')>" % (self.code, self.report_quarter)


def db_init():
    BASE_TABLES.metadata.create_all(DB_ENGINE)


def db_drop():
    BASE_TABLES.metadata.drop_all(DB_ENGINE)


db_init()



