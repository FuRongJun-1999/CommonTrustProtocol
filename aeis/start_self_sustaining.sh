#!/usr/bin/env bash
# 灵枢 AEIS · 单实例自持模式启动（救生艇方案）
cd "$(dirname "$0")"
python -m aeis.swarm.start_self_sustaining
