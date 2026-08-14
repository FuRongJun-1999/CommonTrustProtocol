# -*- coding: utf-8 -*-
"""harness.scheduler.cron · schedule 解析（零依赖）
================================================
支持三种 schedule：
- {"type": "interval", "minutes": 30}      # 每 N 分钟（心跳）
- {"type": "daily", "hour": 1, "minute": 0} # 每日固定时刻（睡眠巩固）
- {"type": "cron", "expr": "*/30 * * * *"}  # cron 5 字段（兼容 ZCode cron_expr）

next_run(now, schedule, last_run) → 下一次到期时间戳。
"""
import time
from datetime import datetime, timedelta


def next_run(now: float, schedule: dict, last_run: float = None) -> float:
    """计算下一次运行时间。"""
    stype = schedule.get("type", "interval")
    if stype == "interval":
        minutes = max(0.1, float(schedule.get("minutes", 30)))
        # 锚点：last_run 之后间隔；无 last_run 则从 now 起算
        base = last_run if last_run else now
        return base + minutes * 60
    if stype == "daily":
        hour = int(schedule.get("hour", 0))
        minute = int(schedule.get("minute", 0))
        nxt = datetime.fromtimestamp(now).replace(hour=hour, minute=minute,
                                                  second=0, microsecond=0)
        if nxt.timestamp() <= now:
            nxt += timedelta(days=1)
        return nxt.timestamp()
    if stype == "cron":
        return _next_cron(now, schedule.get("expr", "* * * * *"))
    # 默认：间隔
    return now + 1800


def _next_cron(now: float, expr: str) -> float:
    """cron 5 字段（分 时 日 月 周），支持 */N 与 *。"""
    parts = expr.split()
    if len(parts) != 5:
        return now + 1800
    minute_f, hour_f, dom_f, mon_f, dow_f = parts

    def parse_field(field, lo, hi):
        if field == "*":
            return set(range(lo, hi + 1))
        vals = set()
        for item in field.split(","):
            if "/" in item:
                base, step = item.split("/")
                step = int(step)
                if base == "*":
                    vals.update(range(lo, hi + 1, step))
            elif "-" in item:
                a, b = item.split("-")
                vals.update(range(int(a), int(b) + 1))
            else:
                vals.add(int(item))
        return vals

    m_set = parse_field(minute_f, 0, 59)
    h_set = parse_field(hour_f, 0, 23)
    dom_set = parse_field(dom_f, 1, 31)
    mon_set = parse_field(mon_f, 1, 12)
    dow_set = parse_field(dow_f, 0, 6)

    cur = datetime.fromtimestamp(now) + timedelta(minutes=1)
    for _ in range(60 * 24 * 366):  # 最多搜一年
        if cur.month in mon_set and cur.day in dom_set \
                and cur.weekday() in dow_set \
                and cur.hour in h_set and cur.minute in m_set:
            return cur.timestamp()
        cur += timedelta(minutes=1)
    return now + 1800
