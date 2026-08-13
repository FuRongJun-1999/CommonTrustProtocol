/**
 * 工具桥接：运行时从灵枢拉取工具清单（tools/list），把 JSON Schema
 * 转换为 dsh-tools 的 ParameterSchemaSpec，经 defineTool 注册进 ctx.tools。
 *
 * 动态拉取意味着灵枢库升级新增工具后，DSH 侧零改动即可获得新能力。
 */

import type { Context } from '@deepseek-ai/cordis'
import { defineTool, type ParameterPropertySpec, type ParameterSchemaSpec, type ValueSchemaSpec } from '@deepseek-ai/dsh-tools'
import type { LingxuBridge, McpTool } from './bridge.ts'

/** 默认暴露的核心工具集合（记忆/推理/摄取/元认知）。 */
export const CORE_TOOLS = [
  'remember',       // 写入记忆
  'recall',         // 组合联想召回
  'search',         // 内容检索
  'timeline',       // 记忆时间线
  'think',          // 推理前记忆注入
  'relate',         // 建立关系边
  'predict_routes', // 生成式预测
  'ingest_text',    // 外部知识摄取
  'ingest_url',     // URL 摄取
  'session_note',   // 会话要点外部化
  'self_check',     // 完整性自检
  'service_info',   // 服务状态
] as const

/** tools 配置：'core' | 'all' | 显式名称数组。 */
export type ToolSelection = 'core' | 'all' | string[]

/** 按配置筛选工具名。 */
export function selectTools(all: string[], selection: ToolSelection): string[] {
  if (selection === 'all') return all
  const allowed = new Set(selection === 'core' ? CORE_TOOLS : selection)
  return all.filter((name) => allowed.has(name))
}

/** 把 MCP JSON Schema 的属性表转换为 ParameterSchemaSpec。 */
export function schemaToParameters(inputSchema: Record<string, unknown> | undefined): ParameterSchemaSpec {
  if (!inputSchema || typeof inputSchema !== 'object') return {}
  const properties = inputSchema['properties'] as Record<string, unknown> | undefined
  if (!properties || typeof properties !== 'object') return {}
  const required = new Set(Array.isArray(inputSchema['required']) ? (inputSchema['required'] as string[]) : [])
  const spec: Record<string, ParameterPropertySpec> = {}
  for (const [key, raw] of Object.entries(properties)) {
    const value = toValueSpec(raw)
    if (required.has(key)) {
      spec[key] = { ...value, required: true as const }
    } else {
      spec[key] = value
    }
  }
  return spec
}

/** 递归转换单个 JSON Schema 节点为 ValueSchemaSpec。 */
function toValueSpec(raw: unknown): ValueSchemaSpec {
  if (typeof raw !== 'object' || raw === null) return { type: 'json' }
  const node = raw as Record<string, unknown>
  const annotations: { description?: string } = {}
  if (typeof node['description'] === 'string') annotations.description = node['description'] as string
  const type = node['type']
  const enumValues = Array.isArray(node['enum']) ? (node['enum'] as unknown[]) : undefined
  switch (type) {
    case 'string':
      return { type: 'string', ...annotations, ...(enumValues ? { enum: enumValues as string[] } : {}) }
    case 'number':
      return { type: 'number', ...annotations }
    case 'integer':
      return { type: 'integer', ...annotations }
    case 'boolean':
      return { type: 'boolean', ...annotations }
    case 'null':
      return { type: 'null', ...annotations }
    case 'array': {
      const spec: { type: 'array'; items?: ValueSchemaSpec } & typeof annotations = { type: 'array', ...annotations }
      if (node['items'] !== undefined) spec.items = toValueSpec(node['items'])
      return spec
    }
    case 'object': {
      const props = schemaToParameters(node)
      return { type: 'object', properties: props, additionalProperties: true, ...annotations }
    }
    default:
      return { type: 'json', ...annotations }
  }
}

/** 从灵枢 content 数组中提取文本（MCP text block 拼接）。 */
export function extractText(content: Array<{ type: string; text?: string; [key: string]: unknown }>): string {
  return content
    .map((block) => (block.type === 'text' && typeof block.text === 'string' ? block.text : ''))
    .filter(Boolean)
    .join('\n')
}

/** 注册灵枢工具到 ctx.tools；返回取消注册函数。 */
export async function registerLingxuTools(
  ctx: Context,
  bridge: LingxuBridge,
  opts: { selection: ToolSelection; toolPrefix: string },
): Promise<() => void> {
  const tools = await bridge.listTools()
  const wanted = new Set(selectTools(tools.map((t) => t.name), opts.selection))
  const disposers: Array<() => void> = []
  const registered: string[] = []
  try {
    for (const tool of tools) {
      if (!wanted.has(tool.name)) continue
      const publicName = `${opts.toolPrefix}${tool.name}`
      const definition = defineTool({
        name: publicName,
        description: tool.description || `灵枢 ${tool.name}`,
        parameters: schemaToParameters(tool.inputSchema),
        output: {
          schema: { type: 'json' } as never,
          render(_args, value) {
            return [{ type: 'text', text: extractText((value as McpCallResultLike).content ?? []) }]
          },
        },
        timeoutMs: 120_000,
        isConcurrencySafe: () => true,
        async execute(args) {
          const result = await bridge.callTool(tool.name, args as Record<string, unknown>)
          if (result.isError) {
            throw new Error(extractText(result.content) || `灵枢 ${tool.name} 执行失败`)
          }
          return { content: result.content } as never
        },
      })
      disposers.push(ctx.tools.register(definition))
      registered.push(publicName)
    }
  } catch (err) {
    for (const dispose of disposers) dispose()
    throw err
  }
  ctx.logger.info(`dsh-memory: 已注册 ${registered.length} 个灵枢工具（${registered.join(', ')}）`)
  return () => {
    for (const dispose of disposers) dispose()
  }
}

interface McpCallResultLike {
  content: Array<{ type: string; text?: string; [key: string]: unknown }>
}
