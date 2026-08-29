# KCCS LSP · VS Code 接入说明（2026-08-29）

> 条件路由图进编辑器——写代码时看见条件边界。数据源=主仓库条件路由图。

## 启动服务器

```bash
cd D:\Program Files\2_ai\CommonTrustProtocol\tools
python kccs_lsp.py --tcp 2087
```

## VS Code 接入（两种方式）

### 方式一：通用 LSP 客户端扩展（最快）

1. 安装扩展 「LSP Support」（或 any-lsp 客户端类扩展）
2. 配置连接 `tcp://127.0.0.1:2087`，语言注册 `python`

### 方式二：官方语言服务器协议注册（settings.json）

若使用支持自定义 LSP 的扩展（如「Language Server Protocol」类），
在 settings.json 指向：

```json
{
  "kccs-lsp.server": {
    "command": "python",
    "args": ["D:\\Program Files\\2_ai\\CommonTrustProtocol\\tools\\kccs_lsp.py", "--stdio"]
  }
}
```

## 能力

| 能力 | 触发 | 效果 |
|---|---|---|
| KCCS 悬停卡 | 光标停在标识符上 | 悬浮显示条件卡四要素（生效条件/子功能/执行/不适用条件） |
| 条件词实时诊断 | 打开/编辑含 `# 生效条件：` 注释的文件 | R1-R3 违规标警告（条件词边界规范 v1.0） |

## 诚实边界

- **中文条件词检索面**：英文标识符经 snake_case 变体尝试（`insertion_sort`
  → `问insertionsort`），未命中返回 None——英文条件词全覆盖属行动项 4。
  现阶段在 KCCS 注释行内使用中文条件词即可完整生效（诊断+悬停）。
- 服务器无鉴权，仅监听 127.0.0.1（本机信任域）。
