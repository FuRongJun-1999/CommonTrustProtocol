@echo off
rem 灵枢自维持启动脚本：拉起守护进程（guardian 负责 harness 心跳监控与自动重启）
rem 用法：双击运行，或由 Windows 计划任务在登录时调用
cd /d "D:\Program Files\2_ai\AEIS"
start "" /min "C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\python.exe" -m harness.guardian
echo 灵枢守护进程已启动（日志: data\guardian.log）
