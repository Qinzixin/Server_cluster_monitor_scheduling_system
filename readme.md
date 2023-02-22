# Sever Cluster Monitor and Scheduling system(SCMS) / 实验室服务器状态监控系统

 ## OBJECTIVES / 实验目标

With the vigorous development of deep learning in many areas, many research or industry groups have purchased a large number of GPU servers; In addition, the group may also have many servers with different settings and usages.These servers are relatively independent. When the number of servers is increasing, it becomes difficult to obtain the real-time operation status of these servers and to make decisions on scheduling allocation, server selection, etc.

As time goes by, this will inevitably lead to the ***LONG-TAIL*** problem of "everyone grabs a server" and the waste problem of "unpopular servers have resources but no one uses them", caused by limited server resources or information imbalance. How to collect data indicators that reflect the running status of the server, process its large-scale service status data in real time, and form information that supports user decision-making has become an important issue.

Facing such problems, this project aims to solve the following tasks:

(1) Collect the operation indicators of the specified server regularly, and provide a page to display the operation indicators of each monitored server in real time;

(2) Design the data warehouse system architecture, data table structure, etc., and generate usage reports by day, month, year and other cycles to assist in making decisions related to scheduling and distribution;

(3) According to the real-time usage of each server and previous reports, real-time server usage recommendations are given.

While completing the task, master the design and implementation capability of data model of data warehouse/big data platform, and the architecture design capability of data-driven real-time/near-real-time intelligent decision support system.

随着深度学习的蓬勃发展以及在其许多问题上优良的表现，越来越多的研究者和团队投入到了其研究中，或是将其应用于生产中。为支持深度模型的训练与运行，许多研究单位都采购了大量的GPU服务器；此外，单位可能还拥有许多搭载服务、用途多样的服务器。

这些服务器相对独立，当服务器的数量越来越多，掌握这些服务器的实时运行状况，并作出调度分配、服务器选择等决策将变得越发困难，不可避免地会造成服务器资源有限或信息不均衡引发的“大家都抢一台服务器”的调度问题和“冷门服务器有资源没人用”的浪费问题。如何采集反映服务器的运行状况的数据指标，对其大规模的服务状态数据进行实时处理，并形成支持用户决策的信息，成为了一个重要的问题。

针对此类问题，本项目意在解决如下任务：
（1）定时收集指定服务器的各项运行指标，提供页面实时显示每一台被监控服务器的各项运行指标；
（2）设计数据仓库系统架构、各数据表结构等，按日、月、年等周期生成使用报表，以辅助做出调度、分配相关的决策；
（3）根据实时的各服务器的使用情况与往期报表，给出实时的服务器使用推荐。
在完成任务的同时，掌握数据仓库/大数据平台数据模型设计与实施能力，以及数据驱动的实时/近实时智能决策支持系统架构设计能力。

## Environment / 实验环境

(1)	Docker, Docker compose；
(2)	Python 3.7；
(3)	MySQL, Redis, Kafka, Hbase, Hadoop, etc；

## Demo / 运行效果

![image](https://user-images.githubusercontent.com/5326903/220550783-1a1a0066-cf48-46e7-b518-cef7428d3232.png)
![image](https://user-images.githubusercontent.com/5326903/220550854-956f693e-b87c-427d-9145-da20cf5d02ec.png)



