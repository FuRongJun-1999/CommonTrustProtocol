#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
vision_categories · 图像语义识别词表（视觉面 v1）
====================================================
来源：文生图（danbooru/sd-webui tagcomplete 词库）高频物体标签——
人类图像描述中常见物体的标准集合，作为 YOLO-World 开放词汇检测的
动态类别模板（set_classes）。

结构：分组词表（英文 danbooru 标签 + 中文翻译）→ 构建检测类别列表。
- CORE_CATEGORIES：核心物体词表（检测默认类别，覆盖生物/自然/人造物/
  食物/交通/场景/奇幻等）
- category_list(lang)：生成 YOLO-World 类别列表（英文或中文标签）
- 可扩展：按需向分组追加标签（保持 danbooru 标签风格，下划线连接）
"""

# ---------------------------------------------------------------------------
# 核心物体词表（分组：英文 danbooru 标签 → 中文）
# 精选原则：可物理检测的实体（非人物属性/构图/情感词）
# ---------------------------------------------------------------------------

CORE_CATEGORIES = {
    # ---- 人物 ----
    "人物": [
        ("person", "人"), ("girl", "女孩"), ("boy", "男孩"), ("man", "男人"),
        ("woman", "女人"), ("child", "小孩"), ("baby", "婴儿"),
        ("old_man", "老人"), ("knight", "骑士"), ("samurai", "武士"),
        ("ninja", "忍者"), ("maid", "女仆"), ("nun", "修女"), ("pirate", "海盗"),
        ("wizard", "法师"), ("princess", "公主"), ("queen", "女王"), ("king", "国王"),
        ("soldier", "士兵"), ("police", "警察"), ("doctor", "医生"),
        ("nurse", "护士"), ("chef", "厨师"), ("angel", "天使"), ("demon", "恶魔"),
        ("ghost", "幽灵"), ("vampire", "吸血鬼"), ("witch", "女巫"),
        ("zombie", "僵尸"), ("skeleton", "骷髅"), ("mermaid", "美人鱼"),
        ("fairy", "妖精"), ("robot", "机器人"), ("mecha", "机甲"), ("cyborg", "赛博格"),
    ],
    # ---- 动物 ----
    "动物": [
        ("wolf", "狼"), ("dog", "狗"), ("cat", "猫"), ("fox", "狐狸"),
        ("dragon", "龙"), ("bird", "鸟"), ("eagle", "鹰"), ("owl", "猫头鹰"),
        ("horse", "马"), ("deer", "鹿"), ("bear", "熊"), ("rabbit", "兔子"),
        ("snake", "蛇"), ("butterfly", "蝴蝶"), ("tiger", "老虎"), ("lion", "狮子"),
        ("whale", "鲸"), ("dolphin", "海豚"), ("spider", "蜘蛛"), ("crow", "乌鸦"),
        ("swan", "天鹅"), ("penguin", "企鹅"), ("bat", "蝙蝠"), ("frog", "青蛙"),
        ("mouse", "老鼠"), ("sheep", "羊"), ("cow", "牛"), ("pig", "猪"),
        ("chicken", "鸡"), ("fish", "鱼"), ("shark", "鲨鱼"), ("octopus", "章鱼"),
        ("crab", "螃蟹"), ("seagull", "海鸥"), ("peacock", "孔雀"),
        ("unicorn", "独角兽"), ("phoenix", "凤凰"), ("kitsune", "狐狸精"),
    ],
    # ---- 自然/天空 ----
    "自然": [
        ("moon", "月亮"), ("sun", "太阳"), ("star", "星星"), ("sky", "天空"),
        ("cloud", "云"), ("rainbow", "彩虹"), ("lightning", "闪电"),
        ("snow", "雪"), ("rain", "雨"), ("sunset", "日落"), ("night", "夜晚"),
        ("aurora", "极光"), ("milky_way", "银河"), ("planet", "行星"),
        ("earth", "地球"), ("comet", "彗星"),
    ],
    # ---- 自然/地貌植物 ----
    "地貌植物": [
        ("mountain", "山"), ("sea", "海"), ("ocean", "海洋"), ("river", "河"),
        ("lake", "湖"), ("forest", "森林"), ("tree", "树"), ("flower", "花"),
        ("cherry_blossoms", "樱花"), ("waterfall", "瀑布"), ("beach", "海滩"),
        ("desert", "沙漠"), ("volcano", "火山"), ("island", "岛屿"),
        ("cave", "洞穴"), ("cliff", "悬崖"), ("grass", "草"), ("bamboo", "竹子"),
        ("pine_tree", "松树"), ("palm_tree", "棕榈树"), ("cactus", "仙人掌"),
        ("mushroom", "蘑菇"), ("lotus", "莲花"), ("sunflower", "向日葵"),
        ("rose", "玫瑰"), ("crystal", "水晶"), ("rock", "岩石"),
    ],
    # ---- 建筑/场景 ----
    "建筑场景": [
        ("castle", "城堡"), ("tower", "塔"), ("house", "房子"), ("bridge", "桥"),
        ("temple", "寺庙"), ("church", "教堂"), ("city", "城市"), ("street", "街道"),
        ("building", "建筑"), ("lighthouse", "灯塔"), ("fountain", "喷泉"),
        ("gate", "大门"), ("ruins", "废墟"), ("village", "村庄"), ("harbor", "港口"),
        ("train_station", "火车站"), ("library", "图书馆"), ("school", "学校"),
        ("mansion", "宅邸"), ("cabin", "木屋"), ("windmill", "风车"),
    ],
    # ---- 武器/装备 ----
    "武器装备": [
        ("sword", "剑"), ("shield", "盾"), ("gun", "枪"), ("knife", "刀"),
        ("bow_and_arrow", "弓箭"), ("spear", "长矛"), ("axe", "斧"),
        ("hammer", "锤子"), ("staff", "法杖"), ("armor", "盔甲"), ("helmet", "头盔"),
        ("crown", "皇冠"), ("whip", "鞭子"), ("cannon", "大炮"),
    ],
    # ---- 食物 ----
    "食物": [
        ("apple", "苹果"), ("bread", "面包"), ("cake", "蛋糕"), ("ice_cream", "冰淇淋"),
        ("ramen", "拉面"), ("sushi", "寿司"), ("pizza", "披萨"), ("hamburger", "汉堡"),
        ("donut", "甜甜圈"), ("coffee", "咖啡"), ("tea", "茶"), ("wine", "葡萄酒"),
        ("beer", "啤酒"), ("fruit", "水果"), ("watermelon", "西瓜"), ("orange", "橙子"),
        ("banana", "香蕉"), ("strawberry", "草莓"), ("egg", "鸡蛋"), ("cheese", "奶酪"),
    ],
    # ---- 交通工具 ----
    "交通": [
        ("car", "汽车"), ("motorcycle", "摩托车"), ("bicycle", "自行车"),
        ("train", "火车"), ("airplane", "飞机"), ("ship", "船"), ("boat", "小船"),
        ("helicopter", "直升机"), ("bus", "公交车"), ("truck", "卡车"),
        ("spaceship", "飞船"), ("airship", "飞艇"), ("sailboat", "帆船"),
    ],
    # ---- 物品 ----
    "物品": [
        ("book", "书"), ("candle", "蜡烛"), ("lantern", "灯笼"), ("umbrella", "雨伞"),
        ("clock", "时钟"), ("mirror", "镜子"), ("key", "钥匙"), ("throne", "王座"),
        ("chair", "椅子"), ("table", "桌子"), ("bed", "床"), ("desk", "书桌"),
        ("sofa", "沙发"), ("door", "门"), ("window", "窗户"), ("bookshelf", "书架"),
        ("phone", "手机"), ("computer", "电脑"), ("camera", "相机"),
        ("television", "电视"), ("headphones", "耳机"), ("piano", "钢琴"),
        ("guitar", "吉他"), ("violin", "小提琴"), ("drum", "鼓"), ("flute", "长笛"),
        ("bottle", "瓶子"), ("cup", "杯子"), ("plate", "盘子"), ("bowl", "碗"),
        ("swing", "秋千"), ("ball", "球"), ("kite", "风筝"), ("doll", "玩偶"),
        ("mask", "面具"), ("flag", "旗帜"), ("balloon", "气球"), ("gift", "礼物"),
        ("carpet", "地毯"), ("curtain", "窗帘"), ("fireplace", "壁炉"),
    ],
}

# 中文标签 → 英文标签映射（支持 see 的 classes 参数传中文）
ZH_TO_EN = {}
for _group, _items in CORE_CATEGORIES.items():
    for _en, _zh in _items:
        ZH_TO_EN[_zh] = _en

# 默认检测类别（英文，YOLO-World 文本编码）
DEFAULT_CLASSES = [en for _group, _items in CORE_CATEGORIES.items() for en, _ in _items]


def category_list(lang: str = "en") -> list:
    """生成 YOLO-World 类别列表。lang='en' 英文标签；'zh' 中文标签。"""
    if lang == "zh":
        return [zh for _g, items in CORE_CATEGORIES.items() for _e, zh in items]
    return list(DEFAULT_CLASSES)


def normalize_classes(classes) -> list:
    """规范化 see 的 classes 参数：支持中文标签/混合，返回英文列表。"""
    if not classes:
        return list(DEFAULT_CLASSES)
    if isinstance(classes, str):
        classes = [classes]
    out = []
    for c in classes:
        c = str(c).strip()
        if not c:
            continue
        en = ZH_TO_EN.get(c, c)  # 中文 → 英文；否则原样（允许任意英文标签）
        if en not in out:
            out.append(en)
    return out or list(DEFAULT_CLASSES)
