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
- [x] 基于位置进行 Block 合并
- [x] fc 挂载 OSS
- [x] fc 删除旧版本数据
- [x] Markdown output
- [x] fc-be 内网 endpoint / 挂载 OSS
- [x] 行末连字符处理
- [x] 行内公式延伸
- [ ] 行内截图延伸
- [ ] 行内斜体识别
- [ ] Shot 绝对大小
- [ ] Table of Contents
- [ ] Ligature 连字识别 (Hotstuff)
- [ ] shot 可复制文字 alt-data
- [ ] list 识别支持
- [ ] figure 识别支持
- [ ] Docker CLI
- [ ] 水印
## big-blocks

- [x] dag 3
- [x] metabolome 6
- [x] metabolome 7

lines relayout

- /root/project/flow-pdf/data/out/Abraham et al. - 2022 - Efficient and Adaptively Secure Asynchronous Binar/pre-marked/4.png
- /root/project/flow-pdf/data/out/Majeed and Hong - 2019 - FLchain Federated learning via MEC-enabled blockc/marked/1.png

Block 延展

- [x] /root/project/flow-pdf/data/out/Abraham et al. - 2022 - Efficient and Adaptively Secure Asynchronous Binar/pre-marked/4.png
- /root/project/flow-pdf/data/out/Abraham et al. - 2022 - Efficient and Adaptively Secure Asynchronous Binar/marked/28.png
- /root/project/flow-pdf/data/out/Aublin et al. - 2013 - Rbft Redundant byzantine fault tolerance/marked/6.png
- /root/project/flow-pdf/data/out/Gai et al. - 2022 - Devouring the Leader Bottleneck in BFT Consensus/marked/15.png

Code big-block 漏报

- /root/project/flow-pdf/data/out/Abraham et al. - 2022 - Efficient and Adaptively Secure Asynchronous Binar/marked/14.png
- /root/project/flow-pdf/data/out/Bankhamer et al. - 2022 - Population Protocols for Exact Plurality Consensus/marked/3.png
- /root/project/flow-pdf/data/out/Bankhamer et al. - 2022 - Population Protocols for Exact Plurality Consensus/marked/5.png
- /root/project/flow-pdf/data/out/Bankhamer et al. - 2022 - Population Protocols for Exact Plurality Consensus/marked/7.png
- /root/project/flow-pdf/data/out/Majeed and Hong - 2019 - FLchain Federated learning via MEC-enabled blockc/marked/2.png
- /root/project/flow-pdf/data/out/Miller 等 - 2016 - The honey badger of BFT protocols/marked/5.png
- /root/project/flow-pdf/data/out/Miller 等 - 2016 - The honey badger of BFT protocols/marked/6.png
- /root/project/flow-pdf/data/out/Yin 等。 - 2019 - Hotstuff Bft consensus with linearity and respons/marked/4.png

- data/out/Accelerating Blockchain Search of Full Nodes Using/marked/2.png

Table big-block 漏报

- /root/project/flow-pdf/data/out/Beaver 等。 - 2010 - Finding a needle in haystack Facebook's photo sto/marked/5.png
- /root/project/flow-pdf/data/out/Pancha et al. - 2022 - PinnerFormer Sequence Modeling for User Represent/marked/6.png
- /root/project/flow-pdf/data/out/Sigelman et al. - 2010 - Dapper, a large-scale distributed systems tracing /marked/6.png
- /root/project/flow-pdf/data/out/Van Der Sar 等。 - 2019 - Yardstick A benchmark for minecraft-like services/marked/6.png
- /root/project/flow-pdf/data/out/Wang et al. - 2022 - Bft in blockchains From protocols to use cases/marked/7.png
- /root/project/flow-pdf/data/out/Wang et al. - 2022 - Bft in blockchains From protocols to use cases/marked/24.png
- /root/project/flow-pdf/data/out/Yakovenko - 2018 - Solana A new architecture for a high performance /marked/5.png

其他原因 big-block 漏报

- /root/project/flow-pdf/data/out/Buterin 等。 - 2020 - Combining GHOST and Casper/marked/24.png （公式）

- data/out/DPF-ECC_A_Framework_for_Efficient_ECC_With_Double_Precision_Floating-Point_Computing_Power/marked/4.png
- data/out/Scalable_Anomaly_Detection_Method_for_Blockchain_Transactions_using_GPU/marked/0.png
- data/out/Scalable_Anomaly_Detection_Method_for_Blockchain_Transactions_using_GPU/marked/1.png
- data/out/sDPF-RSA_Utilizing_Floating-point_Computing_Power_of_GPUs_for_Massive_Digital_Signature_Computations/marked/2.png
- data/out/sDPF-RSA_Utilizing_Floating-point_Computing_Power_of_GPUs_for_Massive_Digital_Signature_Computations/marked/7.png
- data/out/sDPF-RSA_Utilizing_Floating-point_Computing_Power_of_GPUs_for_Massive_Digital_Signature_Computations/marked/8.png
- data/out/Towards_High-performance_X25519_448_Key_Agreement_in_General_Purpose_GPUs/marked/5.png

panic

- [x] Chang 等。 - 2008 - Bigtable A distributed storage system for structu (is_common_text_too_little, 被 drawing 包围正文)
- [x] Kapritsos et al. - 2012 - All about eve Execute-verify replication for mult (is_common_text_too_little, 被 drawing 包围正文)
- [x] Scales 等。 - 2010 - The design of a practical system for fault-toleran (is_not_be_contained, 被 drawing 包围正文)

- [x] Fang et al. - 2021 - Dragoon a hybrid and efficient big trajectory man (width 判断错误)
- Wang et al. - 2017 - Development and evaluation on a wireless multi-gas (每行 1 block, width 判断错误)
- [x] Wang et al. - 2019 - A survey on consensus mechanisms and mining strate (width 判断错误)
- [x] Zhao 等 - 2021 - A learned sketch for subgraph counting (width 判断错误)
- Zhu et al. - 2022 - Postharvest quality monitoring and cold chain mana (每行 1 block, width 判断错误)

- Kotla 和 Dahlin - 2004 - High throughput Byzantine fault tolerance （PDF 格式有问题）

- CPU-GPU_Collaborative_Acceleration_of_Bulletproofs_-_A_Zero-Knowledge_Proof_Algorithm
split new block 误报 [x]

- [x] /root/project/flow-pdf/data/out/Danezis et al. - 2022 - Narwhal and Tusk a DAG-based mempool and efficien/pre-marked/0.png （0.6 -> 0.5）
- [x] /root/project/flow-pdf/data/out/DiemBFT v4 State Machine Replication in the Diem Blockchain/pre-marked/11.png
- [x] /root/project/flow-pdf/data/out/Lenzen and Loss - 2022 - Optimal Clock Synchronization with Signatures/marked/1.png
- [x] /root/project/flow-pdf/data/out/Neiheiser 等。 - 2021 - Kauri Scalable bft consensus with pipelined tree-/marked/4.png
- [x] /root/project/flow-pdf/data/out/Van Der Sar 等。 - 2019 - Yardstick A benchmark for minecraft-like services/marked/4.png

- Applied Cryptography, 2nd Edition

split new block 漏报

- /root/project/flow-pdf/data/out/Gilad 等。 - 2017 - Algorand Scaling byzantine agreements for cryptoc/marked/13.png
- Kapritsos et al. - 2012 - All about eve Execute-verify replication for mult
- /root/project/flow-pdf/data/out/Van Der Sar 等。 - 2019 - Yardstick A benchmark for minecraft-like services/marked/0.png

- data/out/A survey of breakthrough in blockchain technology_Adoptions, applications, challenges and future research/marked/1.png

多余截图 [x]

- [x] /root/project/flow-pdf/data/out/Duan et al. - 2018 - BEAT Asynchronous BFT made practical
- [x] /root/project/flow-pdf/data/out/practical byzantine fault tolerance/marked/10.png
- [x] /root/project/flow-pdf/data/out/practical byzantine fault tolerance and proactive recovery/marked/9.png
- [x] /root/project/flow-pdf/data/out/Wang et al. - 2018 - Improving quality control and transparency in hone/marked/1.png

截图遗漏

- /root/project/flow-pdf/data/out/Li 等。 - 2014 - Communication efficient distributed machine learni/marked/3.png

shot 延伸过多

- /root/project/flow-pdf/data/out/Low et al. - 2014 - Graphlab A new framework for parallel machine lea/marked/3.png
- /root/project/flow-pdf/data/out/Low et al. - 2014 - Graphlab A new framework for parallel machine lea/marked/4.png

column 漏报

- /root/project/flow-pdf/data/out/Sankar 等。 - 2017 - Survey of consensus protocols on blockchain applic/marked/0.png(文档结构有问题)

shot 延展不足 [x]

- [x] /root/project/flow-pdf/data/out/Solutions to Scalability of Blockchain_A Survey/marked/2.png
- [x] /root/project/flow-pdf/data/out/Toshniwal 等。 - 2014 - Storm@ twitter/marked/4.png
