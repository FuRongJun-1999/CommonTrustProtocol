#!/usr/bin/env bash
# 灵枢 AEIS · 蜂群首次启动（DELIVERY-ENGINEERING-20260813-FINAL）
cd "$(dirname "$0")"
python -m aeis.swarm.start_cluster
