# 服务器信息监控

## 需求
数据生成部分（上游）：
1. 服务器监控系统大数据实现  
2. 服务器使用信息
下游应用：
- 日报表、周报表、月报表 *聚合任务：对数据进行多维度的统计分析*
- 即时服务器推荐 *响应任务：实时推荐*

## 目前计划：

1. 基本信息数据采集 吴书函
   + 修改为异步消息队列传递日志
     + 添加GPU监控
   + 需要采集的数据：
      + the demo data is as follows:
      全部是实时数据！
      ```
      now is:  update {
         "online0": false, √
         "protocol_version": 1.0, 
         "uptime": 7793761, 
         "memory_total": 115389480, 
         "memory_used": 12404684, 
         "hdd_total": 7930348, 
         "hdd_used": 7217486, 
         "cpu": 31.9, 
         "network_in": 1472131498480, 
         "network_out": 6131962388933, 
         "gpu_status": [["0", "TITAN Xp", 7271, 12196], ["1", "TITAN Xp", 8541, 12196], ["2", "TITAN Xp", 10, 12196], ["3", "TITAN Xp", 10, 12196]]}
      ```
      静态数据：
      - 概况 general：服务器数量 server_num，用户数量 user_num
      - 卡 gpu：显卡id gpu_id，型号 gpu_type，显存上限 gpu_memory_limit
      - 服务器 server：内存上限 memory_limit，硬盘总量hdd_total ，ip地址 address，别名 name，cuda版本 cuda_version，存放位置 location，gpu卡数量 gpu_num

      实时数据：
      - 服务器：
        在线状态 online，CPU利用率 cpu，网络上传/下载速率【折线图】 network_up  network_down，硬盘使用率【折线序列】 hdd_rate、使用量 hdd_used【饼图】，内存使用率 memory_total【饼图】、使用量 memory_used【折线】、推荐指数[按照使用率分三个等级] like_index【首页展示】
      - 显卡：可用显存[单独展示占用情况] gpu_memory【折线图】
      - 推荐服务器id：返回显卡可用top3  like_server【首页】

      汇总数据：
      - 磁盘空间平均占用量  日、周（小时）、月（天）平均  
        hdd_used_avg
      - 网络上传下载流量 总量 
        network_up_total
        network_down_total
      - 内存使用情况 总量，已使用 
        memory_avg
      - 最忙服务器和最闲服务器（根据CPU利用率）
        busy_server, idle_server
      - 最繁忙时段（CPU利用率）
        busy_time
      - 空闲时间占比（显存剩余超过8G）
        idle_rate

      

   1. CPU使用 使用率  (实时数值)
   2. GPU使用 + 显卡状态  
      有哪些卡在线，每块卡的型号，显存总量，显存余量 (实时数值)
   3. 磁盘空间 (实时数值)
   4. 网络上传下载流量 (实时数值)
   5. 内存使用情况 总量，已使用 (实时数值)

2. Docker compose构建大数据平台:  docker + Kafka 小集群的消息队列系统 环境搭建HBase、Hive  周泽宇

3. 聚合消息内容 存到HBase  Hive 聚合 spark计算
   1. CPU使用 
     + 使用率 (实时数值)
     + 平均数、中位数、最大值、最小值 
     + 最繁忙时段 
   2. GPU使用 + 显卡状态  
   有哪些卡在线，每块卡的型号，显存总量，显存余量 (实时数值)
   每台服务器  
   平均空闲时间占比 比如我们有4张卡，每张卡如果显存占用少于10%，就认为空闲 (近实时数值)
   分为一台服务器所有卡平均信息，单张卡使用信息  
   3. 磁盘空间 平均占用量  (近实时数值，小时粒度)
   4. 网络上传下载流量 总量 日、周、月平均  (近实时数值)
   5. 内存使用情况 总量，已使用 日、周、月平均 (近实时数值)
   6. 最忙服务器和最闲服务器（reduce计算结果）
4. 周报月报内容：
    聚合到的内容
    各项指标的时间走势图（用不同粒度聚合信息，例如天级别报表用分钟级聚合信息）
    数据归档，小时、天、周、月、年层级
    定时执行报告生成（日、周、月）


6. 消费者 Server 
   定期消费消息队列数据
   为了实时信息展示：
    维护一个内存中的服务器状态表
   
   docker打包
   后端接口 项目 Flask：
   + 状态查询接口
   + 查询报告接口

7. 显示web 
   制作网页：
   + 基本信息统计页：定时刷新机制 √
   + 占用空间走势图 √
   + 报表页：日报、周报、月报 HTML模板 
