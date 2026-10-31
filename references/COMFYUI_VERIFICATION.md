# ComfyUI 实测记录

测试日期：2026-10-31。

## 测试结论

随包工作流已实际运行：**预先计算的精确动画图层，可通过本次 ComfyUI 核心节点与底图合成并导出视频。** 本页原有章节记录 2 秒无声数学验证；新增带声完整案例见下方。

原无声验证的 API 队列执行成功；画布 JSON 也在实际前端载入并点击 Run，使用已有结果缓存。该项验证未运行文生图或图生视频模型，也不涉及整片旁白与字幕。

## 新增：游标卡尺带声案例

[案例文件与操作教程](../examples/vernier-caliper/README.md)提供 52.083333 秒、1280×720、24fps、1250 帧的中文配音预览。制作使用相同的核心节点环境，新增 `LoadAudio`、`CreateVideo`、`SaveVideo`，分 26 个短批次执行。可见前端也实际载入八节点工作流并点击 Run，完成未命中缓存的样段合成。

精确图解与文字由 Pillow 绘制，配音由 macOS Tingting 生成；FFmpeg 按帧拼接分段并使用统一录音，再由 ComfyUI `LoadVideo → SaveVideo` 保存整片。未加载生成模型。

实际输出已完整解码，检查音轨存在、两段滑动中的 226 帧零线标记、196 项文字画幅边界、刻度计算、字形覆盖，并提取关键词附近连续帧。完整正常速度人工有声语义验收未记为通过；配音为合成试听声，无配乐。

- [完整预览](../examples/vernier-caliper/vernier-caliper.mp4)
- [八节点实际截图](../examples/vernier-caliper/review/comfyui-compositing.jpg)
- [整片导出实际截图](../examples/vernier-caliper/review/comfyui-full-film.jpg)
- [原前端执行记录](../examples/vernier-caliper/review/ui-execution.json)
- [最终输出执行记录](../examples/vernier-caliper/review/final-execution.json)
- [检查报告](../examples/vernier-caliper/review/verification.json)

以下保留原 2 秒无声验证记录；其未覆盖的范围不代表新增案例也没有做过。

## 环境

| 项目 | 本次配置 |
| --- | --- |
| ComfyUI | 0.34.0 |
| 前端 | 1.49.6 |
| Python | 3.13.12 |
| PyTorch | 2.12.1，CPU |
| PyAV | 18.1.0 |
| Pillow | 12.3.0 |
| 扩展 | 禁用自定义节点与 API 节点，仅使用核心节点 |

运行使用隔离的输入、输出、用户配置与临时目录。上述版本是此次验证记录，不代表其他版本已通过测试。

## 输入与节点

| 文件 | 说明 |
| --- | --- |
| [画布 JSON](../comfyui/precision-composite.json) | 用于 ComfyUI 前端导入 |
| [API JSON](../comfyui/precision-composite-api.json) | 同一计算图的 API 执行版 |
| [paper.png](../comfyui/input/paper.png) | 静态纸面、文字与坐标背景 |
| [projection.webp](../comfyui/input/projection.webp) | 透明数学动画，48 帧 |
| [输入生成脚本](../comfyui/make_demo_inputs.py) | 计算几何位置并使用随包字体绘制 |

动画演示单位圆上的点与其垂直坐标投影：角度从 30° 变化到 150°，位置由三角函数计算，图层包含点、半径、虚线与标签。没有用扩散模型生成公式或几何关系。

```text
LoadImage(paper.png) → RepeatImageBatch(48) ───────→ destination
LoadImage(projection.webp) → IMAGE ──────────────→ source
                          → MASK → InvertMask ──→ mask
                         ImageCompositeMasked → SaveWEBM
```

`LoadImage` 的 MASK 对透明区域取较高值；本次使用 `InvertMask` 转成合成需要的不透明度。背景复制 48 次以匹配前景帧数。

运行前读取 `/object_info` 确认节点存在，并检查当时的 ComfyUI 源码：

| 源码路径，相对 ComfyUI 安装目录 | 核对内容 |
| --- | --- |
| `nodes.py` | `LoadImage` 动画读取与透明度约定 |
| `comfy_extras/nodes_mask.py` | 蒙版反转与图层合成 |
| `comfy_extras/nodes_images.py` | 背景批次复制 |
| `comfy_extras/nodes_video.py` | 本次使用的 `SaveWEBM` |

## 运行与输出检查

- API 提交返回 `node_errors: {}`，历史状态为 `success`、`completed: true`。
- 画布 JSON 在前端 1.49.6 成功载入，点击 Run 后成功取得结果；此操作命中缓存，不算第二次独立渲染。
- 输出副本：[composite-check.webm](../comfyui/verification/composite-check.webm)。
- 输出探测：VP9、640×360、24fps、2.000 秒，无音轨。
- 完整解码为 48 帧；两个红色位置标记共 96 个预期位置均通过检查。
- 抽看第 0、12、24、47 帧，确认纸面、文字、投影与标注可见。
- 演示所用中文字已检查随包中文 Regular / Bold 字形覆盖，无缺字。

![实际载入的 ComfyUI 画布与运行预览](../comfyui/verification/comfyui-canvas.jpg)

![第 0、12、24、47 帧检查图](../comfyui/verification/contact-sheet.jpg)

## 日志中的已知提示

测试日志并非全程无错误提示：

- 数据库初始化出现 `source code string cannot contain null bytes`。本次未修复该独立问题，服务器及本次队列仍成功运行。
- 读取动画 WebP 出现 `pyav decode error`，随后回退到图像序列读取。最终导出的 48 帧已完整检查。

以上记录保留已知限制，不将本次运行描述为日志零报错。

## 未验证范围

- 任意文生图或图生视频模型的推理、权重、显存及结构稳定性。
- Wan2.2 等模型在本风格下的画面质量与动作准确性。
- 其他电脑、ComfyUI 版本、自定义节点和模型组合。
- 任意新主题的全流程；新增卡尺已覆盖其特定录音、字幕、拼接和带声导出，但没有配乐与复杂混音。
- 完整影片按正常速度进行的人工有声语义验收。

演示没有配音或字幕时间轴，也没有完整知识叙事；静态帧图和位置检查不能代替有声样片验收。正式工程需先按自己的资料、模型、录音和图层验证代表性样段。

## 技术参考入口

- [ComfyUI 工作流基础](https://docs.comfy.org/basic-concepts/workflow)
- [Wan2.2 官方视频工作流示例](https://docs.comfy.org/tutorials/video/wan/wan2_2)

官方示例用于了解节点、模型与输入路线。文档提供某种能力，不等于本仓库或团队现有环境已经实测该路线。此前由 HTML/SVG/GSAP/HyperFrames 制作的 NASA 风格重建同样不属于本次 ComfyUI 验证。
