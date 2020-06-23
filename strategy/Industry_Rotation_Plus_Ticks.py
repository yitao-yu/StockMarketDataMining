'''
author: yitao-yu@github

License:
Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without rest riction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
'''


# 导入函数库
from jqdata import *
import talib as ta
import pandas as pandas

# 初始化函数，设定基准等等
def initialize(context):
    # 设定沪深300作为基准
    set_benchmark('000300.XSHG')
    #医药、消费、金融、信息、电信
    g.stockindex = ["000913.XSHG","000912.XSHG","000914.XSHG","000915.XSHG","000916.XSHG"]
    g.dic = {}
    # 开启动态复权模式(真实价格)
    set_option('use_real_price', True)
    # 输出内容到日志 log.info()
    log.info('初始函数开始运行且全局只运行一次')
    # 过滤掉order系列API产生的比error级别低的log
    # log.set_level('order', 'error')
    for key in g.stockindex:
        g.dic[key] = {
            "sar_m":[],
            "close":0.0,
            "close_m":[],
            "bs":0,
            "stocks":[],
            "count":0
        }
    ### 股票相关设定 ###
    # 股票类每笔交易时的手续费是：买入时佣金万分之三，卖出时佣金万分之三加千分之一印花税, 每笔交易佣金最低扣5块钱
    set_order_cost(OrderCost(close_tax=0.001, open_commission=0.0003, close_commission=0.0003, min_commission=5), type='stock')

    ## 运行函数（reference_security为运行时间的参考标的；传入的标的只做种类区分，因此传入'000300.XSHG'或'510300.XSHG'是一样的）
      # 开盘前运行
    run_monthly(before_market_open,monthday = 1,force= True, time='8:30', reference_security='000300.XSHG')
    
    run_monthly(choose_index,monthday = 1,force = True, time='8:31', reference_security='000300.XSHG')
      # 开盘时运行
    run_monthly(trade,monthday = 1,force = True,time = '9:30',reference_security='000300.XSHG')
      # 收盘后运行
    run_monthly(after_market_close,monthday = 28, time='after_close', reference_security='000300.XSHG')

## 开盘前运行函数
def before_market_open(context):
    # 输出运行时间
    log.info('函数运行时间(before_market_open)：'+str(context.current_dt.time()))
    for key in g.stockindex:
        close_m = attribute_history(key, 5, '1m', ['close']).dropna()['close']
        close = attribute_history(key, 5, '1d', ['close']).dropna()['close'][-1]
        month = attribute_history(key, 60, '1m', ['high','low']).dropna()
        g.dic[key].update({
            "sar_m":ta.SAR(month["high"],month["low"],0.02,0.2),
            "close":close,
            "close_m":close_m,
            "bs":0
        })
    
## 开盘时运行函数
def choose_index(context):
    log.info('函数运行时间(market_open):'+str(context.current_dt.time()))
    for index in g.stockindex:
        
        if len(g.dic[index]["stocks"]) > 0:
            g.dic[index]["count"] += 1
        
        mc = g.dic[index]["sar_m"][-1] - g.dic[index]["close_m"][-1]
        mp = g.dic[index]["sar_m"][-2] - g.dic[index]["close_m"][-2]
        close = g.dic[index]["close_m"]
        gain = close[-1] - close[-2]
        if mc > 0 and g.dic[index]["count"]<= 4 and (mp < 0 or (close[-1] - close[-2] > 0 and close[-2] - close[-3] > -0.5*(close[-1] - close[-2]))):
            g.dic[index]["bs"] = 1
        elif(mc < 0 and mp > 0) or (g.dic[index]["count"] > 4) or (close[-1] - close[-2] < 0 and close[-2] - close[-3]<0):
            g.dic[index]["bs"] = -1
            g.dic[index]["count"] = 0
    
def trade(context):
    index_list = []
    for index in g.stockindex:
        if g.dic[index]["bs"] > 0:
            index_list.append(index)
        elif g.dic[index]["bs"] < 0:
            for security in g.dic[index]["stocks"]:
                order_target_value(security, 0)
            g.dic[index]["stocks"] = []
    buy(context,index_list)
    
def buy(context,index_list):
    cash = context.portfolio.available_cash
    position = cash/context.portfolio.total_value
    if position < 0.2:#仓位过高则不买入#
        return
    buy = []
    for index in index_list:
        for security in get_index_stocks(index, date=None):
            high = max(attribute_history(security, 60, '1d', ['high','low']).dropna()['high'])
            low = min(attribute_history(security, 60, '1d', ['high','low']).dropna()['low'])
            today=context.current_dt.strftime("%Y-%m-%d")
            ticks = get_ticks(security, end_dt = today,start_dt=None, count=60, fields=['time', 'current',"a1_v","b1_p"], skip=True, df=True).dropna()
            count = []
            if len(ticks) < 10:
                print("No Data!!")
                continue
            if high - low > 5:
                count = [1 for k in range(0,12)]
            else:
                count = [1 for k in range(0,6)]
                
            for j,r in ticks.iterrows():
                price = r['current']
                cindex = int((r['current'] - low)/(high-low)*len(count))
                if cindex >= len(count):
                    cindex = len(count) -1
                count[cindex] += r["a1_v"]-r["b1_p"]
            lower = low + (high-low)*count.index(min(count))
            upper = low + (high-low)*count.index(max(count))
            close = attribute_history(security,2,'1d',['close']).dropna()["close"][-1]
            if (upper-close)/(upper-lower) >= 0.8:
                buy.append((security, (upper-close)/(upper-lower),index))
    end = int(position * 4) + 1
    winners = sorted(buy,key = lambda x:x[1])[0:end]
    
    for sec in winners:
        order_value(sec[0],cash*0.8/end)
        if sec[0] in g.dic[sec[2]]["stocks"]:
            continue
        g.dic[sec[2]]["stocks"].append(sec[0]) 
    
## 收盘后运行函数
def after_market_close(context):
    log.info(str('函数运行时间(after_market_close):'+str(context.current_dt.time())))
    #得到当天所有成交记录
    trades = get_trades()
    for _trade in trades.values():
        log.info('成交记录：'+str(_trade))
    log.info('一月结束')
    log.info('##############################################################')
