# -*- coding: utf-8 -*-
"""白箱验证/可移植性单元回归测试（v1.22 · 外部测试报告 P2-7 补缺）。

覆盖：
  1. roleplay_chat 的 _WISDOM_OK 白箱加载（可移植性：非硬编码路径）
  2. neural_retrieve MODEL_PATH 环境变量优先（AEIS_BGE_PATH）
  3. portable_env 路径引导（site-packages 自动探测）
  4. ConditionSpace.from_json 缺 time_window 键的健壮性

运行：python -m pytest aeis/tests/test_whitebox_verify.py 或直接执行。
"""
import os
import sys
import unittest

sys.stdout.reconfigure(encoding="utf-8")
_pkg = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # aeis/
if _pkg not in sys.path:
    sys.path.insert(0, _pkg)


class TestRoleplayWhiteboxOK(unittest.TestCase):
    """roleplay_chat 白箱加载可移植性。"""

    def test_wisdom_ok(self):
        """_WISDOM_OK 应为 True（白箱机制启用），且不依赖作者本机路径。"""
        try:
            from aeis.roleplay_chat import _WISDOM_OK
        except Exception as e:
            self.fail(f"roleplay_chat 导入失败: {e}")
        self.assertTrue(_WISDOM_OK)


class TestNeuralModelPath(unittest.TestCase):
    """神经检索模型路径可移植性。"""

    def test_env_override_code_path(self):
        """AEIS_BGE_PATH 环境变量应优先（验证探测函数而非单例）。"""
        # 单例模式下 reload 不重置 __new__ 缓存，这里直接测探测逻辑：
        # 设 env 后 _probe_bge_path() 应返回 env 值（若函数可调用）。
        os.environ["AEIS_BGE_PATH"] = r"D:\__fake_bge_test__"
        try:
            wdir = os.path.join(_pkg, "wisdom")
            if wdir not in sys.path:
                sys.path.insert(0, wdir)
            import neural_retrieve as nr
            if hasattr(nr, "_probe_bge_path"):
                self.assertEqual(nr._probe_bge_path(),
                                 r"D:\__fake_bge_test__")
            else:
                # 旧版无探测函数：跳过（v1.22 起应有）
                self.skipTest("neural_retrieve 无 _probe_bge_path")
        finally:
            os.environ.pop("AEIS_BGE_PATH", None)

    def test_index_paths_exist(self):
        """索引路径基于 HERE，非硬编码绝对路径。"""
        sys.path.insert(0, os.path.join(_pkg, "wisdom"))
        import neural_retrieve as nr
        self.assertIn("neural_index.npz", nr.INDEX_NPZ)
        self.assertTrue(nr.INDEX_NPZ.endswith("neural_index.npz"))


class TestPortableEnv(unittest.TestCase):
    """portable_env 路径引导。"""

    def test_setup_path_no_crash(self):
        """setup_path 在任何机器都不应崩溃（找不到路径也 OK）。"""
        try:
            sys.path.insert(0, os.path.join(os.path.dirname(_pkg),
                                            "knowledge-base", "tools"))
            from portable_env import setup_path, resolve_db
            setup_path()
            # AEIS_DB 未设置时默认 :memory:
            os.environ.pop("AEIS_DB", None)
            self.assertEqual(resolve_db(), ":memory:")
            os.environ["AEIS_DB"] = r"D:\tmp\custom.db"
            self.assertEqual(resolve_db(), r"D:\tmp\custom.db")
            os.environ.pop("AEIS_DB", None)
        except ImportError:
            self.skipTest("portable_env 不在本仓库（knowledge-base/tools）")


class TestConditionSpaceRobust(unittest.TestCase):
    """ConditionSpace.from_json 缺键健壮性。"""

    def test_missing_time_window(self):
        """缺 time_window 键不应崩溃（补默认值）。"""
        from aeis.core import ConditionSpace
        cs = ConditionSpace.from_json(
            '{"observation_position": "外部"}')
        self.assertEqual(cs.observation_position, "外部")
        self.assertIsNotNone(cs.time_window)

    def test_full_json(self):
        """完整 JSON 正常解析。"""
        from aeis.core import ConditionSpace
        cs = ConditionSpace.from_json(
            '{"observation_position": "P", "observation_tool": "T",'
            ' "time_window": [1.0, 2.0], "existence_constraint": "E"}')
        self.assertEqual(cs.time_window, (1.0, 2.0))


if __name__ == "__main__":
    unittest.main(verbosity=2)
