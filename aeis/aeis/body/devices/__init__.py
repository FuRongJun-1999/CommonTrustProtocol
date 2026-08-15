# -*- coding: utf-8 -*-
"""body.devices · 身体设备层（screen/files/process/audio/control/browser/realtime）。

空 __init__ 使 devices 成为子包（setuptools 才打包）——否则干净安装缺 aeis.body.devices，
导入 aeis.body 时 from .devices.screen 报 ModuleNotFoundError。
"""
