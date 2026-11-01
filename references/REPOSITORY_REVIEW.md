# 借鉴的 ComfyUI 教程仓库做法

核对日期：**2026-11-01**。以下 Star 数由 GitHub 仓库 API 查询，README 从各仓库的原始文件读取。这是围绕教学和展示方式选取的一组参考，不是全站排名；Star 数会继续变化，也不代表工作流适配所有当前环境。

## 参考对象与借鉴点

| 仓库 | Star 快照 | 值得借鉴的组织方式 |
| --- | ---: | --- |
| [ZHO：ComfyUI-Workflows-ZHO](https://github.com/ZHO-ZHO-ZHO/ComfyUI-Workflows-ZHO) | 7,940 | 封面、结果图和视频醒目；按任务分类；案例附近提供 JSON，部分案例列出模型和插件 |
| [Cubiq：ComfyUI_IPAdapter_plus](https://github.com/cubiq/ComfyUI_IPAdapter_plus) | 6,166 | 示例画布、examples 文件夹、视频教程相互连接；模型文件名、放置目录和排错入口明确 |
| [官方：ComfyUI_examples](https://github.com/comfyanonymous/ComfyUI_examples) | 4,662 | 原始示例图嵌入工作流元数据，下载后可拖回 ComfyUI；按任务与模型能力分类 |
| [Yolain：ComfyUI-Yolain-Workflows](https://github.com/yolain/ComfyUI-Yolain-Workflows) | 2,245 | 动图封面；基础、进阶、实用分级；用前必读与依赖表；预览图紧邻工作流下载 |
| [Cubiq：ComfyUI_Workflows](https://github.com/cubiq/ComfyUI_Workflows) | 915 | 教学画布优先可读性，按从左到右、从上到下组织；基础与实验分开；明确输入目录 |

ZHO、官方示例和 Yolain 最适合借鉴案例的浏览方式。IPAdapter Plus 本身是节点项目，这里参考它的依赖说明与教学入口。其 README 已于 **2025-04-14** 宣布转为维护模式；本仓库没有把它加入运行依赖。Yolain 的 README 明确写着暂未提供视频向工作流，这里借鉴的是文档组织方式。

之前查阅的 [Sanbu 合集](https://github.com/sanbuphy/ComfyUI-Workflow-Sanbu)（23 Star）和 [aarsla 教程](https://github.com/aarsla/comfyui-tutorials)（3 Star）可作补充阅读；它们不属于本次“高 Star 项目”的主要依据。

## 为什么这些教程更容易跟着做

读者通常要依次回答五个问题：

1. **能做出什么？** 先给实际结果图、动图或视频。
2. **我从哪个案例开始？** 按难度和任务给出有限的选择。
3. **需要准备什么？** 把输入、节点、模型、版本和目录写在运行步骤前。
4. **该下载哪个文件？** 让结果、JSON 和输入素材出现在相近位置。
5. **怎样判断成功？** 给出预期动作、输出位置和常见错误。

只增加图片数量不能回答这些问题。每张教学图都应帮助读者理解一个输入、连接、参数或结果。

## 本仓库已经采用的改进

| 借鉴做法 | 对应内容 |
| --- | --- |
| 首屏直接看到动作 | [首页](../README.md)展示实际成片的静音动图，旁边提供完整带声 MP4 |
| 先选练习，再读长文 | 首页提供 2.5 秒带声片段、现成整片导出、2 秒数学验证三个入口 |
| 图片可以恢复工作流 | [原始 PNG](../examples/vernier-caliper/review/starter-workflow.png)嵌有八节点 `workflow` 与 `prompt`；配套 JSON 保留为主入口，输入文件另行提供 |
| 输入与输出放在一起比较 | [教程对照图](../examples/vernier-caliper/review/input-output-guide.jpg)并排展示纸面、透明动画和实际合成结果 |
| 场景与工作流紧邻 | [11 场景画廊](../examples/vernier-caliper/SCENE_GALLERY.md)逐项说明解释动作，并链接对应 JSON |
| 长内容逐步展开 | 首屏保留动图，整片联系表放入折叠区；脚本批量重建留在案例文档 |
| 依赖和成功结果明确 | 首页列出三个输入、八个节点的设置、输出目录、预期动作、实测环境与排错顺序 |
| 图片来源可追踪 | 场景图直接从随包 MP4 提取；[帧号清单](../examples/vernier-caliper/review/scenes/frames.json)与[生成脚本](../examples/vernier-caliper/scripts/build_docs_media.py)可供核对 |
| 保留真实运行证据 | 实际 ComfyUI 截图、执行记录和自动检查结果继续保留，并说明尚未完成的验收项 |

## 同事新增案例时沿用这个结构

每个案例至少交付以下内容，读者就能从“看效果”走到“自己运行”：

```text
案例名称与要回答的问题
实际结果动图 + 带声完整视频
适合谁 / 预计输出时长 / 制作难点
运行依赖 + 实测版本 + 输入文件表
原始工作流 JSON + 输入下载位置
输入 → 关键节点 → 输出的对照图
逐步操作 + 预期动作 + 输出位置
常见错误 + 已检查和未检查范围
知识依据 + 素材及字体许可
```

本次使用自制图解和实际成片展示，没有复制外部仓库的截图、视频、音轨或大段文字。借鉴这些项目的教学结构，不改变本案例的实际工具分工：精确图层预先绘制，ComfyUI 合成与编码，FFmpeg 拼接；生成式模型路线仍按各自实测情况说明。
