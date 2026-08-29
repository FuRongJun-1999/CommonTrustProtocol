# -*- coding: utf-8 -*-
"""image_units.py · 图像域条件单元库（生图提示词 = 条件化信息 · 2026-08-29 吸纳）

来源：gpt-image2-ref（awesome-gpt-image-2，541 逆向案例 + 13 模板类别 + 25 风格标签）
洞察：生图提示词就是条件化信息——「Prompt as Code」的 JSON 模板 = 条件空间 + 参数槽，
与我们 KCCS 条件化同构（殊途同归）。

每个单元 = 一个生图模板类别（KCCS 五要素）：
  trigger_words（检索面）/ 生效条件（when）/ 子功能（模板要素）/ 执行（填充）/
  不适用条件（负路由）
用途：作为 3D 语义时空图的可索引知识——后续主动内部条件化明确（强化图像骨架生成）。
"""
import os, json

IMAGE_UNITS = {
    "图像-UI界面": {
        "task": "UI与界面",
        "pattern": (
            "# 生效条件：用户要[产品类型]的[平台]界面图（iOS/Android/Web）\n"
            "# 子功能：① 核心功能列表 ② 视觉风格/主色/强调色 ③ 布局结构 ④ 输出规格\n"
            "# 执行：JSON 模板{type,platform,product,layout,style{theme,primary_color,typography},content,constraints}\n"
            "# 不适用条件：非界面类（纯插画/摄影）；要求手绘稿；多视图混合风格"),
        "cases": [('UI 界面', {'type': 'UI Screenshot', 'platform': 'iOS',
                               'product': 'Fitness App', 'style': {'theme': 'Dark', 'primary_color': 'Neon Green'}})],
        "params": [],
        "calibration": "对照：gpt-image2-ref UI与界面模板（常规模板+JSON 进阶模板）",
    },
    "图像-图表信息": {
        "task": "图表与信息可视化",
        "pattern": (
            "# 生效条件：用户要数据可视化/图表（柱状/折线/饼图/仪表盘）\n"
            "# 子功能：① 图表类型 ② 数据系列 ③ 配色方案 ④ 标注与图例\n"
            "# 执行：JSON 模板{type,data[],chart_type,color_scheme,labels,constraints}\n"
            "# 不适用条件：非数值内容；需要真实数据统计（应拒绝伪造数据）"),
        "cases": [('仪表盘', {'type': 'Dashboard', 'chart_type': 'line+bar'})],
        "params": [],
        "calibration": "对照：gpt-image2-ref 图表模板（Dashboard/Chart 风格标签）",
    },
    "图像-海报排版": {
        "task": "海报与排版",
        "pattern": (
            "# 生效条件：用户要海报/宣传页/版式设计（Typography/版式）\n"
            "# 子功能：① 主视觉 ② 标题层级 ③ 配色 ④ 排版网格\n"
            "# 执行：JSON 模板{type,headline,subtitle,visual,layout,constraints}\n"
            "# 不适用条件：纯文字文档（无视觉）；要求可印刷文件（应转设计工具）"),
        "cases": [('海报', {'type': 'Poster', 'headline': '促销活动'})],
        "params": [],
        "calibration": "对照：gpt-image2-ref 海报与排版模板（Typography/Publishing 标签）",
    },
    "图像-商品电商": {
        "task": "商品与电商",
        "pattern": (
            "# 生效条件：用户要商品图/电商主图/产品展示（Products & E-commerce）\n"
            "# 子功能：① 商品主体 ② 背景/场景 ③ 光照 ④ 卖点标注\n"
            "# 执行：JSON 模板{type,product,background,lighting,angles,constraints}\n"
            "# 不适用条件：要求真实商品照片（应摄影而非生成）；品牌方严格规范"),
        "cases": [('商品图', {'type': 'Product', 'product': '运动鞋', 'background': '纯白'})],
        "params": [],
        "calibration": "对照：gpt-image2-ref 商品与电商模板（Packaging/Logo 标签）",
    },
    "图像-品牌标志": {
        "task": "品牌与标志",
        "pattern": (
            "# 生效条件：用户要 Logo/品牌标识/身份系统（Identity/Logo）\n"
            "# 子功能：① 品牌名 ② 图形符号 ③ 配色 ④ 应用场景\n"
            "# 执行：JSON 模板{type,brand,symbol,color_palette,applications,constraints}\n"
            "# 不适用条件：商标法律审查（应提示专业服务）；风格与品牌调性冲突"),
        "cases": [('Logo', {'type': 'Logo', 'brand': '新品牌', 'symbol': '几何鸟'})],
        "params": [],
        "calibration": "对照：gpt-image2-ref 品牌与标志模板（Identity/Logo 标签）",
    },
    "图像-建筑空间": {
        "task": "建筑与空间",
        "pattern": (
            "# 生效条件：用户要建筑外观/室内/空间效果图（Architecture & Spaces）\n"
            "# 子功能：① 建筑类型 ② 风格（现代/古典/极简） ③ 视角 ④ 环境\n"
            "# 执行：JSON 模板{type,building_style,view,environment,constraints}\n"
            "# 不适用条件：真实建筑项目设计（应转 BIM/设计软件）；结构安全声明"),
        "cases": [('室内', {'type': 'Interior', 'style': '极简', 'view': '透视'})],
        "params": [],
        "calibration": "对照：gpt-image2-ref 建筑与空间模板（Architecture/Interior 标签）",
    },
    "图像-摄影写实": {
        "task": "摄影与写实",
        "pattern": (
            "# 生效条件：用户要写实照片风格（Photography & Realism，Lens/镜头）\n"
            "# 子功能：① 主体 ② 镜头语言（焦段/光圈/景深） ③ 光照 ④ 后期风格\n"
            "# 执行：JSON 模板{type,subject,lens,lighting,film_style,constraints}\n"
            "# 不适用条件：真实人物肖像（应授权）；新闻纪实（应真实拍摄）；深度伪造"),
        "cases": [('写实', {'type': 'Photography', 'lens': '85mm f/1.4', 'lighting': '黄昏'})],
        "params": [],
        "calibration": "对照：gpt-image2-ref 摄影与写实模板（Lens 标签）",
    },
    "图像-插画艺术": {
        "task": "插画与艺术",
        "pattern": (
            "# 生效条件：用户要插画/艺术风格图（Illustration & Art，Art/创意）\n"
            "# 子功能：① 艺术风格（水彩/油画/扁平/3D） ② 主题 ③ 色调 ④ 媒介\n"
            "# 执行：JSON 模板{type,art_style,subject,color_tone,medium,constraints}\n"
            "# 不适用条件：风格混搭冲突（明确一种主导风格）；抄袭特定艺术家"),
        "cases": [('插画', {'type': 'Illustration', 'art_style': '水彩', 'subject': '森林'})],
        "params": [],
        "calibration": "对照：gpt-image2-ref 插画与艺术模板（Art/Illustration 标签）",
    },
    "图像-人物角色": {
        "task": "人物与角色",
        "pattern": (
            "# 生效条件：用户要人物/角色形象（Characters & People，Pose/动作）\n"
            "# 子功能：① 角色特征 ② 服装/造型 ③ 姿势/表情 ④ 背景\n"
            "# 执行：JSON 模板{type,character,appearance,pose,background,constraints}\n"
            "# 不适用条件：真实人物肖像权；色情/暴力内容（硬拦截）；深度伪造"),
        "cases": [('角色', {'type': 'Character', 'pose': '站姿', 'appearance': '古装'})],
        "params": [],
        "calibration": "对照：gpt-image2-ref 人物与角色模板（Pose/Characters 标签）",
    },
    "图像-场景叙事": {
        "task": "场景与叙事",
        "pattern": (
            "# 生效条件：用户要场景/故事板/电影感画面（Scenes & Storytelling，分镜/长卷）\n"
            "# 子功能：① 场景描述 ② 时间/光线 ③ 氛围 ④ 叙事元素\n"
            "# 执行：JSON 模板{type,scene,time_of_day,atmosphere,narrative,constraints}\n"
            "# 不适用条件：分镜需多帧序列（应脚本化生成）；真实事件还原需来源"),
        "cases": [('分镜', {'type': 'Storyboard', 'scene': '雨夜城市', 'atmosphere': '悬疑'})],
        "params": [],
        "calibration": "对照：gpt-image2-ref 场景与叙事模板（Storyboard/Scene 标签）",
    },
    "图像-历史古风": {
        "task": "历史与古风题材",
        "pattern": (
            "# 生效条件：用户要历史题材/古风/古典风格（History & Classical，Classical/古典）\n"
            "# 子功能：① 时代背景 ② 服饰/器物 ③ 画风（水墨/工笔/油画） ④ 构图\n"
            "# 执行：JSON 模板{type,era,style,costume,constraints}\n"
            "# 不适用条件：历史事实严格考据（应文献核实）；民族图腾滥用（文化敏感）"),
        "cases": [('古风', {'type': 'Classical', 'era': '唐代', 'style': '水墨'})],
        "params": [],
        "calibration": "对照：gpt-image2-ref 历史与古风模板（Classical 标签）",
    },
    "图像-文档出版": {
        "task": "文档与出版物",
        "pattern": (
            "# 生效条件：用户要文档/出版物/教育材料图（Documents & Publishing，Education/文档）\n"
            "# 子功能：① 文档类型（封面/学习卡/报告） ② 内容结构 ③ 视觉层级 ④ 可读性\n"
            "# 执行：JSON 模板{type,document,layout,content,constraints}\n"
            "# 不适用条件：正式公文（应办公软件）；内容准确性需校对"),
        "cases": [('学习卡', {'type': 'Education', 'layout': '卡片', 'content': '词汇拆解'})],
        "params": [],
        "calibration": "对照：gpt-image2-ref 文档与出版物模板（Education/Document 标签）",
    },
    "图像-其他场景": {
        "task": "其他应用场景",
        "pattern": (
            "# 生效条件：未匹配上述类别的图像生成需求（Other Use Cases，Special/特殊输出）\n"
            "# 子功能：① 意图澄清 ② 尝试匹配最接近类别 ③ 自定义模板 ④ 诚实边界\n"
            "# 执行：先条件路由匹配 13 类；不匹配则 DEFER（澄清需求）或 BLINDSPOT\n"
            "# 不适用条件：无法归属类别且意图不明（应 DEFER 而非猜）"),
        "cases": [],
        "params": [],
        "calibration": "对照：gpt-image2-ref 其他应用场景（诚实边界：不强行归属）",
    },
}

# 25 风格标签 → 触发词（对齐 style-library tagLabels）
STYLE_TRIGGERS = {
    "Art": ["艺术", "插画风格"], "Campaign": ["商业", "Campaign", "广告"],
    "Chart": ["图表", "数据图"], "Classical": ["古典", "古风"],
    "Creative": ["创意", "概念"], "Dashboard": ["仪表盘", "面板"],
    "Document": ["文档", "报告"], "Education": ["教育", "学习卡"],
    "Identity": ["身份系统", "VI"], "Interior": ["室内", "空间"],
    "Layout": ["版式", "排版", "海报"], "Lens": ["镜头", "焦段", "摄影"],
    "Logo": ["Logo", "标志"], "Map": ["地图", "导览"],
    "Packaging": ["包装", "产品包装", "商品", "主图", "电商"], "Pose": ["动作", "姿势", "人物", "角色"],
    "Publishing": ["出版", "书封"], "R&D": ["研发", "概念图"],
    "Scene": ["场景", "氛围"], "Screenshot": ["截图", "界面截图", "界面", "UI"],
    "Scroll": ["长卷", "长图"], "Special": ["特殊输出", "实验"],
    "Storyboard": ["分镜", "故事板"], "Style": ["风格", "样式"],
    "Typography": ["字体", "字型", "标题"],
}


def route_image_unit(question):
    """任务识别（问题 → 图像单元）：task/uid + 风格触发词，最长关键词优先。"""
    best, best_len = None, 0
    for uid, u in IMAGE_UNITS.items():
        for kw in (u["task"], uid):
            if kw in question and len(kw) > best_len:
                best, best_len = uid, len(kw)
    for tags in STYLE_TRIGGERS.values():
        for t in tags:
            if t in question and len(t) > best_len:
                # 风格命中 → 映射到主类别（简化：用该风格最常见的单元）
                mapped = _style_to_unit(t)
                if mapped is None:
                    continue  # 无映射的风格不占位，避免顶高 best_len 挡住后续命中
                best, best_len = mapped, len(t)
    return best


def _style_to_unit(style_trigger):
    """风格触发词 → 图像单元（简化映射：风格主要属于哪类）"""
    mapping = {
        "UI": "图像-UI界面", "界面": "图像-UI界面", "截图": "图像-UI界面",
        "图表": "图像-图表信息", "数据": "图像-图表信息", "仪表盘": "图像-图表信息",
        "海报": "图像-海报排版", "排版": "图像-海报排版", "字体": "图像-海报排版",
        "商品": "图像-商品电商", "包装": "图像-商品电商", "电商": "图像-商品电商",
        "Logo": "图像-品牌标志", "标志": "图像-品牌标志", "品牌": "图像-品牌标志",
        "VI": "图像-品牌标志", "Identity": "图像-品牌标志",
        "建筑": "图像-建筑空间", "室内": "图像-建筑空间", "空间": "图像-建筑空间",
        "摄影": "图像-摄影写实", "镜头": "图像-摄影写实", "写实": "图像-摄影写实",
        "插画": "图像-插画艺术", "艺术": "图像-插画艺术", "水彩": "图像-插画艺术",
        "人物": "图像-人物角色", "角色": "图像-人物角色", "姿势": "图像-人物角色",
        "场景": "图像-场景叙事", "分镜": "图像-场景叙事", "故事板": "图像-场景叙事",
        "古风": "图像-历史古风", "古典": "图像-历史古风", "历史": "图像-历史古风",
        "教育": "图像-文档出版", "文档": "图像-文档出版", "学习卡": "图像-文档出版",
    }
    for k, v in mapping.items():
        if k in style_trigger:
            return v
    return None


if __name__ == "__main__":
    print("=== 图像域条件单元库（生图提示词 = 条件化信息）===")
    for uid, u in IMAGE_UNITS.items():
        print(f"[{uid}] 任务={u['task']} 样例数={len(u['cases'])}")
    print(f"\n单元数: {len(IMAGE_UNITS)} · 风格标签触发词: {len(STYLE_TRIGGERS)}")
    for q in ["生成一张 iOS 健身 App 界面图", "画一幅水墨古风山水", "数据可视化仪表盘", "写实 85mm 人像摄影"]:
        print(f"  「{q}」→ {route_image_unit(q)}")
