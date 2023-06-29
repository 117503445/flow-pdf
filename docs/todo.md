# todo

## task

- [x] page worker
- [x] worker 文件缓存支持
- [x] page worker local page result
- [x] 重构 `processor` 为 `worker`
- [x] Logger
- [x] 多栏 shot 合并
- [x] block 分自然段
- [x] Docker Web
- [x] 生成内容嵌入版本信息
- [x] Shot 延伸不足问题优化 (raft - 5, 6)
- [x] 无内容 Shot 删减
- [x] License
- [x] big-block 误识别优化
- [x] shot 上延覆盖 big-block
- [x] 基于列的 block / shot 数据结构
- [x] shot 合并优化
- [x] big-block judger: 不被 drawings 包含
- [x] Inline Shot 公式截取多余内容优化
- [x] 正文段落首行缩进
- [-] 正文段落连字符适配
- [x] 新的版本重新启动任务
- [x] 清理失败任务
- [x] 异常页面大小处理 metabolome
- [x] Cloud 函数计算
- [-] be Log Trace ID
- [-] Big Block 禁止单行多 lines
- [x] OSS 文件保留 7 天
- [x] devcontainer
- [x] 文件大小检查
- [x] shot 左右拓展
- [x] 失败图片自动重试
- [x] Shot 去除白边
- [x] font size 范围优化
- [x] 出错后前端显示
- [x] 大规模数据集
- [x] 前端上传文件后清除 input
- [ ] 基于位置进行 Block 合并
- [ ] Shot 绝对大小
- [ ] fc 挂载 OSS
- [ ] fc-be 内网 endpoint / 挂载 OSS
- [ ] fc 删除旧版本数据
- [ ] Table of Contents
- [ ] Ligature 连字识别 (Hotstuff)
- [ ] shot 可复制文字 alt-data
- [ ] 斜体识别
- [ ] list 识别支持
- [ ] figure 识别支持
- [ ] Docker CLI

## big-blocks

- [x] dag 3
- [x] metabolome 6
- [x] metabolome 7
- [ ] pbft 符号作为 block
- [ ] gossip 每行一个 block

Li et al. - 2020 - A decentralized blockchain with high throughput an
    - [ ] 3 shot 延展不足
    - [ ] big-block 判断过严格

Zhao et al. - 2021 - A learned sketch for subgraph counting

    - [ ] 3 8 big-block 判断过严格
    - [ ] shot 空白延展过度（问题不大）

Lenzen and Sheikholeslami - 2022 - A Recursive Early-Stopping Phase King Protocol

    - [] 7 big-block 漏报

Wang et al. - 2019 - A survey on consensus mechanisms and mining strate

    - [] 8, 10, 13 shot 延展不足

Abraham et al. - 2022 - Efficient and Adaptively Secure Asynchronous Binar

    - [] JSONGen 有问题

Aublin et al. - 2013 - Rbft Redundant byzantine fault tolerance

    - [] no-common-span 提取

Bankhamer et al. - 2022 - Population Protocols for Exact Plurality Consensus

    - [] 3 big-block 误报，漏报

Beaver 等。 - 2010 - Finding a needle in haystack Facebook's photo sto

    - [] 5 6 shot 空白延展过度

Chang 等。 - 2008 - Bigtable A distributed storage system for structu

    - [] min() arg is an empty sequence

Data_Replication_Using_Read-One-Write-All_Monitori

    - [] min() arg is an empty sequence

Dean and Ghemawat - 2008 - MapReduce simplified data processing on large clu

    - [] 大量 big-block 漏报

Gilad 等。 - 2017 - Algorand Scaling byzantine agreements for cryptoc

    - [] 大量 big-block 漏报

Guo 等 - 2020 - Dumbo Faster asynchronous bft protocols

    - [] Invalid bandwriter header dimensions/setup

Kapritsos et al. - 2012 - All about eve Execute-verify replication for mult

    - [] min() arg is an empty sequence

Kotla 和 Dahlin - 2004 - High throughput Byzantine fault tolerance

    - [] Invalid bandwriter header dimensions/setup

Li et al. - 2020 - A decentralized blockchain with high throughput an

    - [] 大量 big-block 漏报

Li et al. - 2020 - GHAST Breaking confirmation delay barrier in naka

    - [] Invalid bandwriter header dimensions/setup

Liu 等。 - 2018 - Scalable byzantine consensus via hardware-assisted

    - [] Invalid bandwriter header dimensions/setup

Miller 等 - 2016 - The honey badger of BFT protocols

    - [] 大量 big-block 漏报

practical byzantine fault tolerance

    - [] big-block 排列不规则

Sankar 等。 - 2017 - Survey of consensus protocols on blockchain applic

    - [] min() arg is an empty sequence

Scales 等。 - 2010 - The design of a practical system for fault-toleran

    - [] min() arg is an empty sequence

Zhu et al. - 2022 - Postharvest quality monitoring and cold chain mana

    - [] min() arg is an empty sequence
