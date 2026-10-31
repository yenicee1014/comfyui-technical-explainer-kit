# ComfyUI 节点提示词

这里的短描述用于图像或视频工作流的文本条件节点。`PROMPT.md` 是给编导 / 语言模型的制作任务指令，两者不要混用。

以下提供英文通用写法，方便团队从已有工作流试起；实际模型可使用中文或调整表达。它们是美术与动作提示，不保证公式、机械结构或视频时序准确。

## 1. 图像正向：固定风格 + 本镜头内容

固定风格：

```text
retro technical archive, engineering handbook editorial collage,
aged off-white paper, charcoal ink, subtle engineering grid,
restrained red accents, precise composition, clear hierarchy,
tactile paper edges, soft contact shadows, restrained material wear,
clearly readable objects and visual relationships,
reserved blank space for later labels and diagrams
```

镜头内容接在其后：

```text
Subject: [one main object or one comparison].
View: [front / top / cutaway / orthographic].
Material and environment: [specific materials and scene].
Layout: [subject location and blank annotation area].
Lighting: [one consistent direction].
Exclude rendered lettering, numbers, formulas and logos.
```

这套文本不默认包含 `NASA`、`space` 或 `astronaut`；避免把所有题材引向航天。

## 2. 可选负向

仅在当前模型和工作流支持且实际启用负向条件时使用：

```text
illegible text, fake formulas, random numbers, random logos,
neon holograms, excessive glow, heavy particles, noisy paper texture,
cluttered layout, warped geometry, duplicated parts, floating labels
```

某些模型或低引导配置对负向条件的处理不同，不能把同一组负向词当成所有模型通用参数。关键内容仍靠精确图层保证。

## 3. 工程例：传动装置外观素材

追加到固定风格之后：

```text
a single compact mechanical transmission housing, functional industrial
design, as an engineering
handbook object plate, pale painted metal with clear panel seams,
front three-quarter view, isolated on an aged paper sheet,
dark worktable visible around the paper, small purposeful red accent,
one stable soft light from the upper left,
empty annotation area on the right, no text, no numbers, no logo
```

这条用于建立外观与材料。要讲齿轮啮合、传动比和转向时，关键齿轮与运动用核实图或精确动画单独制作，不依赖生成外观充当机构证明。

## 4. 数学例：导数图解的背景板

```text
retro technical notebook page, flat off-white paper on a charcoal desk,
subtle paper fiber, very faint engineering grid,
clean large empty central region for an exact function plot,
small blank header region and a clear subtitle margin,
restrained red editorial accent near the edge,
even soft light, no formulas, no axes, no curves, no text, no numbers
```

在后续精确图层上画函数、割线与切线。用同一数据源计算点和线，再按台词推进；不要让图像模型自行生成坐标、函数和公式。

## 5. 图生视频：物件展示镜头

```text
The object remains rigid and keeps the same shape and part layout.
One slow controlled camera move reveals its surface and construction.
The paper, tape and contact shadows remain stable.
Keep the reserved annotation region clear.
No new objects, no new text, no shape morphing.
```

用于允许少量镜头运动的展示段。生成结果仍需检查。精确测量镜头可固定相机，用合成层控制局部变化。

## 6. 图生视频：纸面镜头

```text
Locked overhead camera.
The paper sheet remains flat and completely stationary.
Maintain the original lighting and composition.
No drifting grid, no changing edges, no generated lettering.
```

若目标只是静止纸面，直接保持静帧通常更合适，不必强行消耗生成式视频步骤。这段提示词只在团队已有镜头确需图生视频时使用。

## 7. 精确动作任务：不要粘进生成节点

这些内容交给绘图、排版和合成环节：

```text
工程：保持齿轮中心和齿数不变，按正确传动关系计算旋转；
     标注与对应零件共用变换，箭头在台词锚点出现。

数学：按指定函数计算曲线与采样点；割线通过两个实际点；
     参数变化时重新计算位置，坐标尺度在比较过程中保持一致。

排版：公式、单位、标签与字幕使用真实字体或公式排版；
     每条文字记录起止时间和锚定对象。
```

数学严谨性和机构正确性不能通过增加“accurate”“precise”等提示词就视为完成。

## 8. 每镜头记录卡

| 字段 | 填写 |
| --- | --- |
| 镜头 ID / 台词锚点 | [填写] |
| 本镜头路线 | [文生图 / 图生视频 / 精确合成 / 组合] |
| 使用模型与节点版本 | [填写] |
| 固定风格文本 | [使用哪一版] |
| 本镜头内容或动作描述 | [填写] |
| 输入参考与结构条件 | [填写] |
| 不可变化项 | [几何、身份、方向、连接、文字等] |
| 另做的精确图层 | [填写] |
| 生成尺寸 / 源帧率 / 目标帧率 | [分别填写] |
| 输出与检查结果 | [填写] |
