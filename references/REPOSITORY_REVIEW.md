# 借鉴的 ComfyUI 教程仓库做法

整理日期：2026-11-01。

这份仓库不是照搬其他项目的文字或素材，而是参考它们如何让新手从“看到案例”走到“成功运行”。

## 参考对象

### 官方 `ComfyUI_examples`

官方示例把结果图当作入口：图片中保存工作流元数据，用户可以把图片拖回 ComfyUI 恢复节点结构。它的 README 也是一个按能力分类的视觉索引。这个思路适合“看见结果，再打开工作流”，而不是先阅读长篇节点说明。

参考：[ComfyUI_examples](https://github.com/comfyanonymous/ComfyUI_examples)

### Cubiq `ComfyUI_Workflows`

Cubiq 的仓库强调工作流的可读性、从左到右的执行方向、基础与实验分类，并要求把输入文件放进 ComfyUI 的 `input` 目录后再拖 JSON 运行。多数工作流尽量不依赖自定义节点，以降低新手的安装成本。

参考：[ComfyUI_Workflows](https://github.com/cubiq/ComfyUI_Workflows)

### Sanbu `ComfyUI-Workflow-Sanbu`

这个中文工作流合集把 ComfyUI 下载、Manager、中文界面和“拖工作流图片到画布”放在 README 前面，再用分级目录组织基础、放大、分割、局部修复等任务。它适合借鉴“先给快速开始，再给目录”，但其中部分工作流依赖额外节点或模型，不能把安装清单省略。

参考：[ComfyUI-Workflow-Sanbu](https://github.com/sanbuphy/ComfyUI-Workflow-Sanbu)

### aarsla `comfyui-tutorials`

aarsla 的项目更接近课程：每课有配套工作流、节点说明、示例结果和网站化的逐步说明；它还强调工作流在放入仓库前经过测试。这个思路适合工程类科普，因为同事需要知道“每个节点为什么在这里”，不只是拿到一个能跑的 JSON。

参考：[comfyui-tutorials](https://github.com/aarsla/comfyui-tutorials)、[在线教程](https://aarsla.github.io/comfyui-tutorials/)

## 我们在本仓库采用的改进

| 借鉴做法 | 本仓库对应内容 |
| --- | --- |
| 结果先行、图片作为入口 | 首页先展示游标卡尺完整预览；案例目录加入 11 张关键场景图 |
| 输入、工作流、结果成套交付 | `examples/vernier-caliper/input/`、`workflows/`、`review/`、`vernier-caliper.mp4` |
| 基础路线与进阶路线分开 | 首页先教一个 2.5 秒八节点片段，再说明 26 段整片重建 |
| 每个案例写清依赖 | README 明确核心节点、帧数、音频、FFmpeg、系统限制和实测版本 |
| 工作流按解释任务命名 | `01-question`、`03-nine`、`05-one`、`09-result` 等名称直接对应旁白与画面动作 |
| 可验证，而不只展示截图 | `verification.json`、`REPLAY.md`、执行记录和实际 ComfyUI 截图一起保存 |
| 允许新手先不安装模型 | 卡尺案例使用确定性图层，先验证 ComfyUI 合成；生成模型放到后续素材阶段 |

## 还没有照搬的部分

- 没有把第三方模型、LoRA、ControlNet 或自定义节点打包进仓库。
- 没有把一部卡尺视频包装成“输入任意主题就自动生成”的通用节点。
- 没有把外部教程的截图、原片素材或音轨复制进来。
- 没有把当前版本的动态 GitHub Star 数量写死在文档里；读者应以仓库页面当前显示为准。

原因是 ComfyUI、模型和自定义节点更新很快。对新手最有用的文档不是声称所有电脑都能复现，而是把输入、依赖、版本、成功结果和未验证范围写清楚。
