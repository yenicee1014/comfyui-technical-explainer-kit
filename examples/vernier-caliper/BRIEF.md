# 游标卡尺：多一排刻度，为什么就能读得更细？

- 用户要求：制作选题 5，并直接操作本机 ComfyUI。
- 画幅：1280×720，24fps，中文配音与字幕。
- 风格：复古技术档案 × 动态图解；深色桌面、纸张、工程网格、金属工具示意与少量红色。
- 范围：十分度直接游标，主尺每格 1mm，游标十格对应 9mm，分度值 0.1mm。
- 读数例：无零位误差的理想示意，主尺 12mm，第三条游标线对齐，得到 12.3mm。
- 必须准确：两排刻度间距、零线位置、对齐索引、单位及读数计算。
- 制作分工：Python/Pillow 计算并绘制精确动画输入；ComfyUI 核心节点完成蒙版合成、配音装载与 MP4 输出；FFmpeg 拼接分段，最终再由 ComfyUI 保存完整影片。
- 音频：本机 Tingting 合成声，按短语独立录制、裁去首尾静音，测量音长后建立时间轴；不伪称词级对齐。
- 模型：本次使用确定性图层，不加载扩散或图生视频模型；不修改全局 ComfyUI 配置。
- 验证：先检查对齐动作样段，再制作全片；记录刻度计算、字形、布局、实际节点执行和输出解码结果。

## 依据

1. Mitutoyo, Quick Guide to Measurement，游标 9mm/10 格与 0.1mm 分度示例：
   https://www.mitutoyo.com/wp-content/uploads/2022/08/14003_Quick-Guide-2022.pdf
2. Mitutoyo, Caliper Educational Kit：
   https://www.mitutoyo.com/webfoo/wp-content/uploads/E12009_20519-Caliper-Educational-Kit.pdf

工具外形采用原创结构示意，不将绘制图冒充产品照片或历史档案。参考片仅用于视觉语法，不复制音轨、台词或画面。
