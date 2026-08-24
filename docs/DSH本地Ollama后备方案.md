# DSH 本地 Ollama 后备方案（DeepSeek API 断开时）

> 目的：DSH（DeepSeek Harness）对话依赖 DeepSeek API——API 断开（如被限制访问）
> 时 DSH 无法响应。本方案将本地 Ollama（OpenAI 兼容端点）作为后备提供方，
> 一键切换，API 断开后仍可对话。

## 一、原理

DSH 的 LLM 路由 `deepseek-official`（@deepseek-ai/dsh-llm-deepseek 适配器）
支持 **baseURL 可配置**（env `DEEPSEEK_BASE_URL` 优先，settings `llm-deepseek:` 段次之）。
Ollama 提供 OpenAI 兼容端点（`http://localhost:11434/v1/chat/completions`），
已验证支持 DSH 所需能力：基础对话、**工具调用（tools）**、系统提示。

所以：DeepSeek 断开时，把 `deepseek-official` 路由的 baseURL 指向本地 Ollama +
模型名改为 ollama 模型（ornith-1.5-9b）即可。

## 二、切换脚本（C:\Users\FuRongJun\.dsh\dsh_ollama_switch.py）

```powershell
# 切到本地 Ollama（DeepSeek 断开时）
python C:\Users\FuRongJun\.dsh\dsh_ollama_switch.py on

# 切回云端 DeepSeek（API 恢复后）
python C:\Users\FuRongJun\.dsh\dsh_ollama_switch.py off

# 查看当前状态
python C:\Users\FuRongJun\.dsh\dsh_ollama_switch.py status
```

**on 时执行**：settings.yaml 备份(.bak) + model 改 ornith-1.5-9b +
reasoningEffort 改 off（本地模型不支持 thinking 模式，README：high/max 会导致插件加载失败）+
设用户级 env `DEEPSEEK_BASE_URL=http://localhost:11434/v1`、`DEEPSEEK_API_KEY=ollama-local`。
**off 时执行**：还原 settings（model=deepseek-v4-flash, effort=high）+ 清除 env。
**生效**：重启 dsh（新会话）后生效；当前运行中的 dsh 进程不受影响。

## 三、已验证（test_ollama_openai.py）

| DSH 所需能力 | Ollama 兼容端点 |
|---|---|
| 基础 chat.completions | ✓ |
| 工具调用（tools，agent 依赖） | ✓（tool_calls 正常返回） |
| 系统提示 + 多轮 | ✓ |

## 四、注意事项

- **thinking/reasoning**：本地 ornith-1.5-9b 无思维链——切换时 reasoningEffort 必须 off（脚本已处理）
- **工具调用质量**：本地 9B 模型的工具调用可靠性低于云端 v4——后备可用，复杂任务建议恢复云端
- **性能**：本地推理（5.6GB 模型）速度慢于云端，适合应急
- 切换只影响**新启动**的 dsh 会话；备份在 settings.yaml.bak（off 时按备份还原亦可）

## 五、备份链

- 灵枢本体：无 API 自维持三层（白箱 538+ 簇 / 本地 Ollama 角色扮演 / 云端 DeepSeek）——见 `docs/无API自维持_P0存在保护.md`
- DSH：本方案（deepseek-official 路由指向 Ollama）
