# 设计

## 架构

每个 processor 对 PDF 做出解析行为。

不断传递 doc, params

可以设置 processors，对某一个 PDF 进行解析。

## 流程

1. 先解析出大块文字和位图

2. 判断出矢量图

3. 扩张矢量图，包含周边文字
