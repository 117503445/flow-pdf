# 设计

## 思路

通过 PyMuPDF 解析 PDF 文件结构，获取各元素（文本、图片）的相关信息。然后提取大块文字，剩下的直接截图。大块文字内部的公式直接截图。

## 流程

1. PyMuPDF 解析文件结构

2. 统计最常出现的字体，认为是正文字体；统计出现频率最高的字体大小范围，认为是正文的字体大小范围（大多数 PDF 的正文字体大小是相同的，但小部分 PDF 字体大小会有一点点浮动）。

3. 确定布局是单栏还是双栏的（甚至还有三栏的）。具体做法就是对于字比较多的大段落，统计这些大段落在 x 轴上的位置。

4. 确定哪些段落是可以提取成文字的。通过找到的好几个特征进行判断。

5. 文字段落之间的部分，进行截图。注意到论文中有些双栏布局的图片是横跨多个列的，还需要合并多个列中 y 轴位置相似的截图。

6. 按照 PDF 页 -> 列 -> 段落 / 截图 的顺序，转换为 `doc.json`，具体结构见下文。其中文字段落内也有粗体、公式等，识别出来并截图。

7. 将 `doc.json` 转换为 HTML。

## 解析模块架构

每个 processor 基本等于一个流程。

processor 的输入可以是文档级变量，也可以是页面级变量。输出可以是文档级变量，也可以是页面级变量。

执行器会根据 processor 输入变量的变量名，自动匹配先前 processor 输出变量的变量名。

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

## 运行模块架构

当前主要支持 3 种模式运行。

- dev 本地开发，命令行调用，可以根据 `config.yaml` 灵活调整需要解析的 PDF。

- be Web后端，方便用户使用 Docker Compose 把整个网站跑起来

- fc 函数计算，<https://flow-pdf.117503445.top> 使用的部署模式。用户访问 OSS 上的前端网站，上传文件到 be-fc (Golang 写的后端，通过函数计算部署)，be-fc 将文件上传到 OSS 的另一个 bucket，然后 OSS 文件更新事件触发通过函数计算部署的 flow-pdf 的 `fc.py`，完成解析后将 HTML 结果也传到 OSS 上。前端一直轮询 OSS 的任务状态文件，当解析任务完成后跳转到结果 URL 上。
