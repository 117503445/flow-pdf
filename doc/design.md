# 设计

## 架构

每个 processor 对 PDF 做出解析行为。

不断传递 doc, params

可以设置 processors，对某一个 PDF 进行解析。

## 流程

1. 只分析 words 大于 500 的 Block，判断是单栏布局还是双栏布局 

2. 绘制出大块文字和位图的位置

3. 在剩余的位置，进行截图

