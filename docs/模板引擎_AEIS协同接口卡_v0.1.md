# 模板引擎 · AEIS 协同接口卡 v0.1（2026-08-30）

> 目的：定义分层模板引擎「提取半边」的输入输出契约——主仓库（大脑逻辑）
> 已闭环目录/采样/验证闸/往返自洽，AEIS（身体）补图像→签名提取，
> 两端按本卡对接即可跑通 V-TBE.8 像素版与 V-TBE.12 往返闭环。

---

## 一、数据流（双向管线）

```
【生成方向·主仓库】
  TemplateCatalog.sample() → 四层组合描述 → (AEIS 渲染器消费) → 组合图像
【识别方向·AEIS→主仓库】
  组合图像 → AEIS stage4 提取 → 四层观测签名 JSON → 主仓库 catalog.verify() → 四态判定
【往返闭环 · V-TBE.12 像素版】
  sample → 渲染 → 提取 → verify → ACCEPT 率 = 模板库自洽度（像素级）
```

## 二、观测签名契约（AEIS 产出 → 主仓库消费）

```json
{
  "L1_skeleton":  {"joints": 0, "topology": "humanoid"},
  "L2_pose":      {"angles": 5, "leaning": "none"},
  "L3_appearance":{"color": 9, "texture": "flat"},
  "L4_detail":    {"pattern": 2, "ornament": "none"}
}
```

- 键名固定四层：`L1_skeleton / L2_pose / L3_appearance / L4_detail`
- 每层值为 `{字段: 值}` dict；与目录内模板 `desc` 同构（键值精确比对）
- 缺层合法：`verify` 对缺层记 **BLINDSPOT**（没看到的不假装看到）
- 字段名与种子目录一致（tools/template_catalog.py 冒烟：joints/angles/color/pattern）

## 三、主仓库侧调用（已实现，tools/template_catalog.py）

```python
from template_catalog import TemplateCatalog
cat = TemplateCatalog.load("catalog.json")        # 或现场 register
r = cat.verify(observed, threshold=0.5)
# r = {"verdict": "ACCEPT|DEFER|REJECT|BLINDSPOT",
#      "matched": n, "layers": {layer: {status, best, score}}}
```

四态口径：全层达标=ACCEPT / 过半=DEFER / 其余=REJECT / 缺层=BLINDSPOT。

## 四、AEIS 侧待实现（stage4 对接，dsh 端）

1. **提取器适配**：stage4 现有输出（四段词签名/区域 bbox/色纹理）→
   映射到上表四层字段（映射表待 dsh 端按 stage4 实际字段定）
2. **往返脚本**：`sample → 渲染器 → 提取 → verify`（落 AEIS/tools/，
   输出自洽率报告）——V-TBE.12 像素版验收
3. **种子回填**：渲染器参数空间的每层取值 → `catalog.register()`
   登记为模板（渲染器参数空间显式化为条件空间目录）

## 五、边界

- 提取器质量依赖 stage4（感知通道黑箱作工具，认知层白箱——既有路线）
- 层间耦合用模板 `conditions` 字段显式记录，不强行解耦（v0.2 边界条款）
- 任意组合可能畸形：不合格组合由 verify 闸拦截并回退已知组合，不盲选
