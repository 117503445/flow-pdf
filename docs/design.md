# 设计

## 架构

每个 processor 对 PDF 做出解析行为。

processor 输入可以是文档级变量，也可以是页面级变量。输出可以是文档级变量，也可以是页面级变量。

执行器会根据输入变量，自动寻找祖先 processor，并编排执行顺序。

## 流程

1. 基于 x 轴位置判断正文块，并进行正文内 公式、加粗 的解析
2. 提取位图 figure
3. 提取标题（基于 LOC）
4. 在核心区域内，不含以上的部分，进行截图

## doc.json Schema

```jsonc
{
  // meta 文档的元信息
  "meta": {
    // flow-pdf 版本
    "flow-pdf-version": "dev-63120cf16af4f3d609ff84a546eb7f30e47cb130"
  },

  // HTML 元素，依次渲染即可
  "elements": [
    {
      "type": "shot", // shot 类型的 element
      "path": "./assets/page_0_shot_16.png" // 图片路径
    },
    {
      "type": "paragraph", // text 类型的 element
      "children": [
        {
          "type": "text", // text 类型的 element
          "text": "The Number is" // 文本内容
        },
        {
          "type": "shot", // in-line shot
          "path": "./assets/page_0_shot_17.png" // 图片路径
        },
        {
          "type": "text",
          "text": "."
        },
        // ...
      ]
    }
    // ...
  ]
}
```
