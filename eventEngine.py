#-*- coding:utf-8 -*-
# 系统模块
import Queue
import sys, traceback
import threading

# 自己开发的模块
from eventType import *

class RepeatTimer():

    def __init__(self,t,hFunction):
        self.t=t
        self.hFunction = hFunction
        self.thread = threading.Timer(self.t,self.handle_function)

    def handle_function(self):
        self.hFunction()
        self.thread = threading.Timer(self.t,self.handle_function)
        self.thread.start()

    def start(self):
        self.thread.start()

    def cancel(self):
        self.thread.cancel()

class RepeatTimer2(threading.Thread):
    def __init__(self, interval, callable, *args, **kwargs):
        threading.Thread.__init__(self)
        self.interval = interval
        self.callable = callable
        self.args = args
        self.kwargs = kwargs
        self.event = threading.Event()
        self.event.set()

    def run(self):
        while self.event.is_set():
            t = threading.Timer(self.interval, self.callable,
                                self.args, self.kwargs)
            t.start()
            t.join()

    def cancel(self):
        self.event.clear()

########################################################################
class EventEngine:
    def __init__(self, timerFreq = 1.0):
        """初始化事件引擎"""
        # 事件队列
        self.queue = Queue.Queue()
        
        # 事件引擎开关
        self.is_active = False
        
        # 事件处理线程
        self.thread = threading.Thread(target = self.run)
        
        # 计时器，用于触发计时器事件
        self.timer = RepeatTimer2(timerFreq, self.onTimer)
        
        # 这里的__handlers是一个字典，用来保存对应的事件调用关系
        # 其中每个键对应的值是一个列表，列表中保存了对该事件进行监听的函数功能
        self.handlers = {}
        
    #----------------------------------------------------------------------
    def run(self):
        """引擎运行"""
        while self.is_active == True:
            try:
                event = self.queue.get(block = True, timeout = 1)  # 获取事件的阻塞时间设为1秒
                self.process(event)
            except Queue.Empty:
                pass
            except:
                e = sys.exc_info()[0]
                print 'error msg:', str(e)
                traceback.print_exc()
            finally:
                pass
            
    #----------------------------------------------------------------------
    def process(self, event):
        """处理事件"""
        # 检查是否存在对该事件进行监听的处理函数
        if event.type in self.handlers:
            # 若存在，则按顺序将事件传递给处理函数执行
            [handler(event) for handler in self.handlers[event.type]] 
               
    #----------------------------------------------------------------------
    def onTimer(self):
        """向事件队列中存入计时器事件"""
        # 创建计时器事件
        if self.is_active:
            event = Event(type=EVENT_TIMER)
            # 向队列中存入计时器事件
            self.put(event)

    #----------------------------------------------------------------------
    def start(self):
        """引擎启动"""
        # 将引擎设为启动
        self.is_active = True
        
        # 启动事件处理线程
        self.thread.start()
        
        # 启动计时器，计时器事件间隔默认设定为1秒
        self.timer.start()
    
    #----------------------------------------------------------------------
    def stop(self):
        """停止引擎"""
        # 将引擎设为停止
        self.is_active = False

        # 停止计时器
        self.timer.cancel()
        self.timer = None
        
        # 等待事件处理线程退出
        self.thread.join()
        self.thread = None
            
    #----------------------------------------------------------------------
    def register(self, etype, handler):
        """注册事件处理函数监听"""
        # 尝试获取该事件类型对应的处理函数列表，若无则创建
        try:
            handlerList = self.handlers[etype]
        except KeyError:
            handlerList = []
            self.handlers[etype] = handlerList
        
        # 若要注册的处理器不在该事件的处理器列表中，则注册该事件
        if handler not in handlerList:
            handlerList.append(handler)
            
    #----------------------------------------------------------------------
    def unregister(self, etype, handler):
        """注销事件处理函数监听"""
        # 尝试获取该事件类型对应的处理函数列表，若无则忽略该次注销请求
        try:
            handlerList = self.handlers[etype]
            
            # 如果该函数存在于列表中，则移除
            if handler in handlerList:
                handlerList.remove(handler)

            # 如果函数列表为空，则从引擎中移除该事件类型
            if not handlerList:
                del self.handlers[etype]
        except KeyError:
            pass     
        
    #----------------------------------------------------------------------
    def put(self, event):
        """向事件队列中存入事件"""
        self.queue.put(event)

class PriEventEngine(EventEngine):
    def __init__(self, timerFreq = 1.0):
        super(PriEventEngine, self).__init__(timerFreq)
        self.queue = Queue.PriorityQueue()

    def put(self, event):
        """向事件队列中存入事件"""
        event_obj = (event.priority, event)
        self.queue.put(event_obj)

    def process(self, event_obj):
        """处理事件"""
        # 检查是否存在对该事件进行监听的处理函数
        event = event_obj[1]
        if event.type in self.handlers:
            # 若存在，则按顺序将事件传递给处理函数执行
            [handler(event) for handler in self.handlers[event.type]] 

########################################################################
class Event(object):
    """事件对象"""
    #----------------------------------------------------------------------
    def __init__(self, type=None, priority = 100):
        """Constructor"""
        self.type = type      # 事件类型
        self.priority = priority
        self.dict = {}         # 字典用于保存具体的事件数据

#----------------------------------------------------------------------
def test():
    """测试函数"""
    import sys, time
    from datetime import datetime
    def simpletest(event):
        print u'处理每秒触发的计时器事件：%s' % str(datetime.now())
    
    ee = EventEngine(0.5)
    ee.register(EVENT_TIMER, simpletest)
    ee.start()
    for i in range(1000):
        time.sleep(1.0)
        print "loop %s" % i
        if i>5:
            ee.stop()
            break
    
# 直接运行脚本可以进行测试
if __name__ == '__main__':
    test()
