#### 多任务布局参考链接

* [csdn](https://blog.csdn.net/weixin_39318540/article/details/80473021)
* [其他](https://niubidian.top/blog/show/40/)
* [celery introduction](https://www.fullstackpython.com/celery.html)
* [celery分布式](https://blog.csdn.net/Jmilk/article/details/78945622)
* [celery源码分析1](https://zhangchenchen.github.io/2018/07/03/deep-in-celery/)
* [celery源码分析2](https://liqiang.io/post/celery-source-analysis-worker-start-flow)
* [python异步](https://www.cnblogs.com/earendil/p/7411115.html)
* [epool原理](https://blog.csdn.net/qq_35433716/article/details/85345907)
* [epool原理](https://blog.csdn.net/mango_song/article/details/42643971)
#### celery 原理和架构
Celery是一个自带电池的基于Python开发的分布式异步消息任务队列，它非常易于使用。通过它可以轻松的实现任务的异步处理， 如果你的业务场景中需要用到异步任务，就可以考虑使用Celery
Celery主要适用于俩大场景：异步和定时。  

#### celery 源码阅读
celery在Windows下无法调试，可以安装wsl远程调试。

#### celery 启动过程
先启动流水线，然后分发产品(任务)到流水线上。
![avatar](https://s2.ax1x.com/2019/07/31/eYlyDI.png)