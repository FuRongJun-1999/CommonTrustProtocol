# Ollama 上下文扩容（DSH 400 溢出修复）

> 触发：DSH 切到本地 Ollama 后报 `400 request (15287 tokens) exceeds the available context size (8192 tokens)`。
> 根因：模型 Modelfile `PARAMETER num_ctx 8192`（模型级默认）——Ollama OpenAI 兼容层
> 不读请求里的 contextWindow（OpenAI 协议无此字段），DSH 的大请求（系统提示+历史+工具 schema）溢出。

## 修复链（排查过程）

| 步骤 | 尝试 | 结果 |
|---|---|---|
| 1 | OLLAMA_CONTEXT_LENGTH=32768 环境变量 | ❌ 模型 Modelfile 已「指定」num_ctx 8192，env 默认值不覆盖 |
| 2 | 原生 API options.num_ctx=32768 | ✅ per-request 有效（但 DSH OpenAI 适配器不传） |
| 3 | **Modelfile 创建 32k 模型** | ✅ 最终方案 |

## 方案：创建 ornith-1.5-9b-32k（num_ctx 32768）

```bash
# 导出原模型 Modelfile → 改 num_ctx 8192→32768 → 创建新模型
ollama show ornith-1.5-9b --modelfile > ornith.modelfile
# 改 PARAMETER num_ctx 32768
ollama create ornith-1.5-9b-32k -f ornith-32k.modelfile
```

settings.yaml 更新：
```yaml
agent-default-model:
  provider: ollama
  model: ornith-1.5-9b-32k
llm-pi-ai:
  providers:
    ollama:
      baseURL: http://localhost:11434/v1
      models:
        - id: ornith-1.5-9b-32k
          name: Ornith-1.5-9B-32k
          contextWindow: 32768
          maxTokens: 4096
```

## 验证

| 场景 | 结果 |
|---|---|
| 大请求（>15k tokens，对应 DSH 15287 溢出场景） | ✅ 成功 |
| DSH 完整场景（长系统提示+多轮历史+工具 schema+工具结果回传） | ✅ 成功（正确发起工具调用） |

## 注意事项

- 32k 上下文显存占用更高（9B 模型 32k ctx）；显存不足时降低 num_ctx（如 16384）
- 原模型 ornith-1.5-9b（8k）保留未动；如切回用 8k 模型会再次溢出（DSH 请求大）
- 若需调整：`ollama show ornith-1.5-9b-32k --modelfile` 查看参数
