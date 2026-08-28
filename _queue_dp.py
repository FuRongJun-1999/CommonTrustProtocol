# -*- coding: utf-8 -*-
"""_queue_design_patterns.py · 通道 B 第六批：设计模式域（一次性）"""
import json
import io
import os
import time

p = os.path.join("tools", "channel_b_queue.json")
d = json.load(io.open(p, encoding="utf-8"))

CODE_SINGLETON = '''def singleton(cls):
    # 生效条件：cls 为可实例化的类
    # 子功能：① 首次调用创建实例并缓存 ② 后续调用返回缓存实例
    # 执行：装饰器闭包缓存
    # 不适用条件：需要多实例或带参重建的场景不适用
    instances = {}
    def get_instance(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]
    return get_instance'''

CODE_OBSERVER = '''def observer_notify(observers, event):
    # 生效条件：observers 为可调用对象列表；event 为事件数据
    # 子功能：① 遍历通知所有观察者 ② 收集各观察者返回值
    # 执行：循环迭代调用
    # 不适用条件：观察者抛异常时中断通知（不做异常隔离）；不用内建通知机制
    results = []
    for obs in observers:
        results.append(obs(event))
    return results'''

new = [
    {"task": "单例模式",
     "spec": "singleton(cls) 装饰器：首次调用创建实例并缓存，后续调用返回同一实例",
     "cases": [
         [[[1, 2]], [1, 2]],
     ],
     "generated_by": "glm-5.3-flash-zcode",
     "ts": time.strftime("%Y-%m-%d %H:%M"),
     "code": CODE_SINGLETON, "status": "pending"},
    {"task": "观察者通知",
     "spec": "observer_notify(observers, event) 遍历通知所有观察者并收集返回值",
     "cases": [
        [[["log", "alert"]], {"e": 1}], ["log-alert"],
     ],
     "generated_by": "glm-5.3-flash-zcode",
     "ts": time.strftime("%Y-%m-%d %H:%M"),
     "code": CODE_OBSERVER, "status": "pending"},
]

d.setdefault("pending", []).extend(new)
json.dump(d, io.open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("queued 2; pending =", len(d["pending"]))
