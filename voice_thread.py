#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
voice_thread · 语音对话后台线程（不阻塞主进程）
==================================================
线程职责（只管采集与输出，理解交给主进程）：
1. 持续监听麦克风（VAD 断句，N.E.K.O 同款交互——说一句停顿=一次提交）
2. 每次短句（sherpa is_endpoint 断句产出）→ 追加到队列 voice_queue.jsonl
3. 退出词检测（结束/退出/再见/stop）→ 写 exit 标记 → 停止

主进程（ZCode 会话）消费队列：新条目 → LLM 回复 → say 输出。
"""

import json
import os
import sys
import time

QUEUE_NAME = "voice_queue.jsonl"


def main():
    workspace = os.environ.get("AEIS_WORKSPACE", "")
    model_dir = os.environ.get("AEIS_ASR_MODEL_DIR", "")
    if not workspace or not model_dir:
        print("需要 AEIS_WORKSPACE 与 AEIS_ASR_MODEL_DIR", flush=True)
        return 1
    queue_path = os.path.join(workspace, QUEUE_NAME)
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    # 轻量路径：只装配音频设备（避免 Agent 构造加载 YOLO-World/torch 冷启动）
    from aeis.body import build_default_registry
    from aeis.body.devices.audio import AudioDevice

    audio = AudioDevice(workspace)
    exit_words = ["结束", "退出", "再见", "stop", "exit", "关闭"]

    def write_entry(entry: dict):
        with open(queue_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")

    write_entry({"type": "system", "ts": time.time(), "text": "语音线程启动"})
    print("语音线程启动：持续监听，说一句停顿=一次提交；说 结束/退出 关闭", flush=True)
    audio.invoke("say", {"text": "我在听，请直接说话。"})

    round_no = 0
    while True:
        round_no += 1
        # 持续监听 + VAD 断句（说一句停顿 = 一次提交，N.E.K.O 交互模式）
        r = audio.invoke("listen_stream", {"max_seconds": 8,
                                           "max_sentences": 3,
                                           "source": "mic"})
        data = r.data or {}
        sentences = data.get("sentences", []) or []
        if not sentences:
            if round_no % 10 == 0:
                write_entry({"type": "heartbeat", "ts": time.time(),
                             "text": "（监听中）"})
            continue
        for text in sentences:
            text = str(text).strip()
            if not text:
                continue
            print(f"[{round_no}] 识别: {text}", flush=True)
            # 退出词
            if any(kw in text for kw in exit_words):
                write_entry({"type": "exit", "ts": time.time(), "text": text})
                audio.invoke("say", {"text": "好的，语音对话结束。"})
                print("收到退出词，线程停止", flush=True)
                return 0
            write_entry({"type": "user", "ts": time.time(), "text": text})


if __name__ == "__main__":
    sys.exit(main())
