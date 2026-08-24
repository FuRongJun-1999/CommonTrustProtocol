# DSH 本地 Ollama 提供方（双 provider 并存）

> 目的：DSH 同时提供**云端 DeepSeek**（默认）与**本地 Ollama**（后备）两个模型提供方，
> 模型选择器直接可选——DeepSeek API 断开时切到 Ollama 模型即可，不影响云端配置。
> 教训（2026-08-22）：不要改 llm-deepseek 段的 baseURL 做「二选一切换」——
> 那会让 deepseek-official 路由整体打到 Ollama、云端失效；正确做法是**新增 provider**。

## 一、配置（C:\Users\FuRongJun\.dsh\settings.yaml）

```yaml
# ① 云端 DeepSeek（默认路由，保持官方）
agent-default-model:
  provider: deepseek-official
  model: deepseek-v4-flash
  reasoningEffort: high

llm-deepseek:
  apiKeyEnv: DEEPSEEK_API_KEY
  baseURL: https://api.deepseek.com   # 不带 /v1（源码 fetch `${baseURL}/chat/completions`）
  thinking: enabled

# ② 本地 Ollama（新增 provider，与云端并存）
llm-pi-ai:
  providers:
    ollama:
      displayName: Ollama 本地 (Ornith-1.5-9B)
      apiKeyEnv: OLLAMA_API_KEY
      api: openai-completions          # OpenAI 兼容适配器
      baseURL: http://localhost:11434/v1
      models:
        - id: ornith-1.5-9b
          name: Ornith-1.5-9B
          contextWindow: 32768
          maxTokens: 4096
```

## 二、凭据（C:\Users\FuRongJun\.dsh\.credentials.yaml，双键并存）

```yaml
DEEPSEEK_API_KEY: sk-...   # 云端
OLLAMA_API_KEY: sk-...     # Ollama 本地不校验 key，任意非空即可
```

## 三、使用

- **默认**：模型选择器选 `deepseek-v4-flash`（云端）
- **后备**：DeepSeek API 断开时，模型选择器选 `Ornith-1.5-9B`（本地 Ollama）
- 配置**热加载**（settings/credentials 文件被 watch，适配器每次请求重解析）——刷新页面/新会话即生效，无需重启

## 四、已验证

| 检查项 | 结果 |
|---|---|
| DeepSeek key 有效性（官方 /models） | ✅ deepseek-v4-flash / v4-pro |
| Ollama 服务 + ornith-1.5-9b | ✅ 运行中 |
| 两个 settings 段过 schema 校验 | ✅（schemastery Config() 解析） |
| dsh web（127.0.0.1:3080） | ✅ HTTP 200，日志无 settings 错误 |
| Ollama OpenAI 端点承载 DSH 请求 | ✅ 基础对话 / 工具调用(tools) / 系统提示 |

## 五、坏文件备份（本次修复前）

- `settings.yaml.broken.bak` / `.credentials.yaml.broken.bak`（误改导致云端失效的版本）
