# GPU 环境确认与 CSPMN 升级路径（2026-08-20 实测）

> 荣指出：有 GPU 4090（任务管理器可查）。本文档实测确认硬件与软件，
> 校准 CSPMN 落地（GPU 版可行，非远期）。

---

## 0. 实测环境（2026-08-20 19:36）

| 项 | 实测值 | 结论 |
|---|---|---|
| GPU 硬件 | **NVIDIA GeForce RTX 4090**（24GB 显存）| ✓ 已确认 |
| GPU 状态 | 0% 利用率、44°C、99MiB/24564MiB 空闲 | 完全空闲可用 |
| 驱动 | NVIDIA 591.44（支持 CUDA 13.1）| ✓ 现代驱动 |
| 系统 CUDA | v11.8 工具链（nvcc V11.8.89）+ 驱动级 CUDA 13.1 | ✓ 双版本 |
| Python | 3.10.10 | ✓ |
| **当前 torch** | **2.13.0+cpu（无 CUDA 支持）** | ✗ **瓶颈在这里** |

**结论：硬件完全就绪（4090 空闲 24GB），唯一缺口是 torch 是 CPU 版——
装 CUDA 版 torch 即可让 CSPMN 真正跑在 GPU 上。**

---

## 1. 为什么 torch.cuda.is_available() 返回 False

- torch 2.13.0 是 `+cpu` 后缀版本（pip 默认源装的是 CPU 版）
- GPU 硬件/驱动/CUDA 都在，只是 torch 没带 CUDA 运行时
- 解决：从 PyTorch 官方源装 `torch+cu12x`（CUDA 12.x wheel，兼容驱动 591.44）

### 升级命令（需确认网络/磁盘，~2.5GB 下载）

```
pip install torch --index-url https://download.pytorch.org/whl/cu121
# 或 cu124（驱动 591.44 支持 CUDA 13.1，向下兼容 cu12x）
```

注意：这会**替换**现有 torch 2.13.0+cpu（依赖 torch 的包需回归测试：
bge-small-zh 编码、neural_retrieve、灵枢 API）。

---

## 2. CSPMN 在 4090 上的可行性（重新校准）

| CSPMN 项 | 4090 能力 | 结论 |
|---|---|---|
| sgemv/sgemm 矩阵乘 | 4090 ≈ 82 TFLOPS FP16 / 4090 内存 24GB | ✓ 原生 |
| 10^8 × 512 稠密（204.8GB）| 超 24GB | 仍需稀疏/分块（远期）|
| **当前 3030×512（6.2MB）** | 显存零头 | ✓ **毫秒级** |
| 扩展到 10^6×512（2GB）| 24GB 装得下 | ✓ 中间态可行 |
| torch.topk | GPU 原生 | ✓ |

**4090 让 CSPMN 从「CPU 可行」升级为「GPU 高效」**：现有 3030 向量
矩阵乘从 ~5ms（CPU）→ 预计 <1ms（GPU），且支持 10^5-10^6 规模子实例。

---

## 3. 落地路径（GPU 版，更新）

```
Step 0（今天）：装 CUDA 版 torch（cu121/cu124）+ 回归测试 bge/检索
Step 1（本周）：条件空间分块矩阵——classify_condition_space + domain_filter，
                GPU 矩阵乘（3030 真实向量），T2 定向 vs 全库（准确率+耗时）
Step 2（下周）：条件空间入口向量 + 门控（排除条件）——真增量，GPU topk
Step 3（持续）：盲区注入闭环（Hebbian）+ 冷热缓存（高频→GPU 常驻）
Step 4（远期）：10^8 规模——稀疏/倒排/多卡（架构已预留 Backend 抽象）
```

---

## 4. 待确认

1. **装 CUDA torch 的磁盘/网络**：wheel ~2.5GB，需要磁盘空间 + 网络（当前
   GitHub 网络不稳，PyTorch 官方源可能也受影响）
2. **是否替换现有 torch**：会动 bge 依赖——需先备份 + 回归
3. **装哪个 CUDA 版本**：cu121（驱动 591.44 向下兼容）或 cu124

> 纪律：先确认磁盘/网络，再动 torch。装完先跑 bge 编码回归（
> neural_retrieve 冷启动），确认无破坏再进 Step 1。
