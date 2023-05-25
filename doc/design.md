# 设计

## 架构

每个 processor 对 PDF 做出解析行为。

不断传递 doc, params

可以设置 processors，对某一个 PDF 进行解析。

## 流程

1. 丢进 layout-parser 进行分析，采信标题、列表、表格
2. 实心文字 作为正文，并进行正文内 公式、加粗的解析
3. 在核心页内，不含以上的部分，进行截图
