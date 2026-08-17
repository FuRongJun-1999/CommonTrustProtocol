# -*- coding: utf-8 -*-
"""灵枢 + 智慧之书 · 信息分层演示（v1.16）

给其他人看「灵枢结合智慧之书」的核心能力：
  1. 知识秒答（图谱自处理，可溯源）
  2. 情感共情（先接情绪）
  3. 诚实边界（不知道就说不知道，不瞎编）
  4. 条件空间（先答再引，白箱条件）
  5. 图谱外 LLM 兜底（分层：智慧之书没把握 → 交给 LLM）

运行：
  python demo_lingshu.py            # 全部演示
  python demo_lingshu.py 5          # 只演示第 5 节（LLM 兜底）

依赖：Python 3.10 + aeis（pip install -e aeis/）+ 智慧之书库（随包）
LLM 兜底需要 DEEPSEEK_API_KEY（没有也能跑——显示 self_fallback 降级）
"""
import sys
import os

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__))))


def _ensure_wisdom_deployed():
    """自愈部署：智慧之书（aeis/wisdom）不在 site-packages 时从仓库复制。
    pyproject 只打包 aeis 包，wisdom/ 平级目录需手动部署。"""
    try:
        import site as _site
        sp = _site.getsitepackages()[0]
    except Exception:
        return
    dst = os.path.join(sp, "wisdom")
    src = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "aeis", "wisdom")
    if os.path.exists(os.path.join(dst, "wisdom_book.py")):
        return  # 已部署
    if not os.path.isdir(src):
        return  # 仓库无 wisdom（仅 clone 了 knowledge-base）→ 用种子卡
    import shutil
    os.makedirs(dst, exist_ok=True)
    for f in os.listdir(src):
        p = os.path.join(src, f)
        if os.path.isfile(p) and f.endswith((".py", ".json", ".npz", ".html")):
            shutil.copy2(p, os.path.join(dst, f))
    print("⚠️ 智慧之书已部署到 site-packages/wisdom（首次运行自动复制）")


_ensure_wisdom_deployed()

from aeis.api import Agent

SESS = "demo"

SECTIONS = [
    ("① 知识秒答（图谱自处理 · route=self）", [
        "铁门放外面久了为什么会生锈？",
        "水在标准大气压下多少度沸腾？",
        "我肚子咕咕叫了，是饿了吗？",
        "1加1等于几？",
    ]),
    ("② 情感共情（先接情绪 · route=self）", [
        "我今天好累，什么都不想干。",
        "太开心了！项目终于跑通了！",
        "心情不好，想找人说说话。",
    ]),
    ("③ 诚实边界（不知道就说不知道 · route=self）", [
        "你知道外星人的具体长相吗？",
        "你能保证你说的都是对的吗？",
        "量子纠缠能不能用来超光速通信？",
    ]),
    ("④ 条件空间（先答再引 · 白箱）", [
        "铁球和羽毛哪个先落地？",
        "女人比男人聪明这个说法对吗？",
        "地球是宇宙中心吗？",
    ]),
    ("⑤ 图谱外 LLM 兜底（信息分层 · route=llm）", [
        "帮我规划一次北京三天旅行",
        "相对论和量子力学为什么互相争论？",
    ]),
]


def main():
    only = None
    if len(sys.argv) > 1:
        only = int(sys.argv[1])
    # 灵枢记忆库：默认 :memory:（演示用临时记忆）；可用 AEIS_DB 指定持久库。
    # 智慧之书图谱库：随包加载（aeis/wisdom/wisdom-book-cloud.db，138 卡）。
    db_path = os.environ.get("AEIS_DB", ":memory:")
    agent = Agent(identity="灵枢", db_path=db_path)
    print("=" * 66)
    print("灵枢 + 智慧之书 · 信息分层演示")
    print("结构智能(5.71MB 图谱) 优先自处理 → 不足走 LLM → 无法判断放上下文续答")
    print("=" * 66)
    for idx, (title, questions) in enumerate(SECTIONS, 1):
        if only and idx != only:
            continue
        print(f"\n■ {title}")
        for q in questions:
            try:
                r = agent.chat(q, session_id=SESS)
            except Exception as e:
                print(f"  ✗ {q[:20]}... 错误: {e}")
                continue
            route = r.get("route", "?")
            reply = (r.get("reply") or "").replace("\n", " ")[:110]
            tag = {"self": "灵枢自处理", "llm": "LLM 续答",
                   "self_fallback": "降级自处理"}.get(route, route)
            print(f"  Q: {q}")
            print(f"    [{tag}] {reply}")
            if route == "llm" and r.get("wisdom_reply"):
                print(f"    （智慧之书初答: {(r.get('wisdom_reply') or '')[:50]}…）")
    agent.close()
    print("\n" + "=" * 66)
    print("演示完。想看更多：网页端 http://127.0.0.1:18766/ui（图谱检索+七操作）")
    print("=" * 66)


if __name__ == "__main__":
    main()
