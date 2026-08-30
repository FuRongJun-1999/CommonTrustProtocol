# 待办 · wisdom-book-cloud.db 库同步防回退

> 来源：zcode 提示（2026-08-30）
> 状态：待办（挂账·停机窗口处理）

## 事项
主仓库源库 aeis/wisdom/wisdom-book-cloud.db 的同款补丁需留停机窗口，
避免下次库同步时回退 site-packages 的补丁。

## 核对（dsh 端）
- 主仓库源库 vs site-packages：schema 一致、行数全同（nodes 3133/edges 2948）
- integrity_check = ok
- 补丁已同时在两库在位，当前无需覆盖

## 风险（待防）
- 下次库同步（主仓库→site）若用旧版源库覆盖，会回退 site 的补丁
- 处理：停机窗口核对源库 mtime（16:19 旧），内容已同步则保留，落后则覆盖；
  建立同步前 diff（schema+行数）机制防盲目回退

## 行动
- [ ] 停机窗口：核对主仓库源库 vs site 内容，一致则保留，差异则覆盖
- [ ] 库同步机制：同步前 diff，避免盲目覆盖回退
