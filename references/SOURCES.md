# 参考来源与复用范围

整理日期：2026-10-31。ComfyUI 验证范围见 [实测记录](COMFYUI_VERIFICATION.md)，题材扩展见 [适用题材](TOPIC_FIT.md)。

## 视觉参考原片

- 作者：路北路陈。
- 系列：《设计风格小课 04》，NASA 朋克主题。
- Bilibili 视频标识：`BV1Tsps6kE6z`。
- 原片入口：[Bilibili 视频](https://www.bilibili.com/video/BV1Tsps6kE6z/)。

风格总结依据所提供原片的代表性画面、联系表及分析记录。原片中的航天照片与游戏案例承担不同作用，不能将游戏画面当作历史证据。

公开仓库以原片署名和链接保留参考出处，不附带原片视频、完整音轨或提取的五张截帧。新视频使用的照片、文献、标志、音乐及其他媒体需单独取得并记录来源。

## 本项目的复现选型

风格名“复古技术档案 × 动态图解科普”、配色数值、字体组合、版式起始值与动作时长建议，属于团队总结和复现方案。它们没有从原作者工程文件读取，也不构成对原片字体、精确颜色或混音参数的确认。

此前的 NASA 风格重建使用 HTML/SVG/GSAP/HyperFrames。该工程不包含在本仓库中，其结果不能作为 ComfyUI 全流程实测依据。

## 随仓库提供的演示与截图

| 文件 | 来源与用途 | 范围 |
| --- | --- | --- |
| [diagram-example.png](../assets/reference/diagram-example.png) | 本项目自制的 Apollo 空气过滤接口功能图解 | 说明形状比较、转接与气流路径；不表示真实尺寸、实际管线或浓度 |
| [paper.png](../comfyui/input/paper.png) | 随包脚本绘制的纸面与坐标背景 | 合成验证输入 |
| [projection.webp](../comfyui/input/projection.webp) | 随包脚本按三角函数计算的透明动画图层 | 48 帧，角度从 30° 到 150° |
| [comfyui-canvas.jpg](../comfyui/verification/comfyui-canvas.jpg) | 实际 ComfyUI 画布运行截图 | 展示节点连接和结果预览，界面外观属于相应软件 |
| [contact-sheet.jpg](../comfyui/verification/contact-sheet.jpg) | 从本次输出抽取的四帧检查图 | 第 0、12、24、47 帧 |
| [composite-check.webm](../comfyui/verification/composite-check.webm) | 本次 ComfyUI 核心节点合成的输出副本 | 2 秒、24fps、无声的精确合成验证 |

`diagram-example.png` 是简化机制图解，不是原片截图、历史设备照片或已完成有声验收的成片案例。ComfyUI 演示只验证数学图层合成，不代表完整参考风格已由生成模型复现。

## 字体

| 字体文件 | 对应许可 |
| --- | --- |
| `NotoSansSC-Regular.otf`、`NotoSansSC-Bold.otf` | [NotoSansSC-OFL.txt](../assets/licenses/NotoSansSC-OFL.txt) |
| `Archivo.ttf` | [Archivo-OFL.txt](../assets/licenses/Archivo-OFL.txt) |
| `SpaceMono-Regular.ttf` | [SpaceMono-OFL.txt](../assets/licenses/SpaceMono-OFL.txt) |

随包携带完整字体文件并保留 SIL OFL 1.1 许可。版权归属见 [第三方说明](../THIRD_PARTY_NOTICES.md)。字体是本项目的排版选型，不能据此认定参考片使用相同字体。

新字幕、上下标、特殊单位与新字重仍需检查实际字形覆盖。完整字体不代表涵盖全部数学符号。

## 项目复用状态

本仓库其余内容尚未指定统一的开源许可证。字体依各自许可使用；原片与软件界面的权利归各自权利人。引用或再分发时保留实际来源与许可，不将本包描述为原片素材库或 NASA 官方资源。
