#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
body.devices.audio · 语音设备（BODY-REV1 批次 2）
====================================================
动作：
- record: 麦克风录音（sounddevice 可选依赖 → wav 文件，工作区 audio/ 下）
- transcribe: 语音识别 ASR（音频文件 → 文本；OpenAI 兼容 Whisper API）
- speak: 语音合成 TTS（文本 → 音频文件；edge-tts 免 key / OpenAI TTS）

Provider 抽象（参考 N.E.K.O tts_client/asr_client 注册表模式，简化）：
- ASR: openai_whisper（OPENAI_API_KEY + OPENAI_BASE_URL 可配，兼容本地 whisper server）
- TTS: edge（edge-tts 免 key）| openai（OPENAI_API_KEY）

依赖策略（D-005 延续）：第三方库全部惰性导入，缺失时优雅降级
（check() 返回 unavailable + 原因；invoke 返回容器化失败）。
输出为 DeviceResult：转写文本/音频路径是数据（provenance=device:audio）。
"""

import os
import time
from typing import Dict, Optional

from ..base import BodyDevice, DeviceResult

_AUDIO_DIR = "audio"


class AudioDevice(BodyDevice):
    """语音设备（感知+行动模态：麦克风/ASR/TTS）。"""

    name = "audio"
    modality = "audio"
    description = "语音（麦克风录音/ASR 识别/TTS 合成；依赖可选降级）"

    def __init__(self, workspace: str = ""):
        super().__init__(workspace)
        # 惰性探测（不阻断装配）
        self._sounddevice = None
        self._edge_tts = None
        self._openai = None
        self._probe()

    # ---- 后端探测 ----

    def _probe(self) -> None:
        try:
            import sounddevice  # type: ignore

            self._sounddevice = sounddevice
        except Exception:
            pass
        try:
            import edge_tts  # type: ignore

            self._edge_tts = edge_tts
        except Exception:
            pass
        try:
            import openai  # type: ignore

            self._openai = openai
        except Exception:
            pass

    # ---- 配置 ----

    def _env(self, key: str, default: str = "") -> str:
        return os.environ.get(key, default)

    def _asr_available(self) -> bool:
        """ASR 可用：openai 客户端 + API key（或 base_url 指向本地服务）。"""
        if self._openai is None:
            return False
        if self._env("OPENAI_API_KEY"):
            return True
        # 允许纯本地端点（如 whisper-server）
        return bool(self._env("OPENAI_BASE_URL"))

    def _tts_available(self) -> bool:
        return self._edge_tts is not None or bool(self._env("OPENAI_API_KEY"))

    # ---- 接口 ----

    def check(self) -> Dict:
        parts = []
        if self._sounddevice is not None:
            parts.append("录音(sounddevice)")
        else:
            parts.append("录音(缺 sounddevice)")
        if self._asr_available():
            parts.append("ASR(openai)")
        else:
            parts.append("ASR(缺 key/客户端)")
        if self._edge_tts is not None:
            parts.append("TTS(edge-tts)")
        elif self._env("OPENAI_API_KEY"):
            parts.append("TTS(openai)")
        else:
            parts.append("TTS(缺 edge-tts)")
        available = self._sounddevice is not None or self._asr_available() or self._tts_available()
        return {"available": available, "detail": " | ".join(parts)}

    def capabilities(self) -> Dict:
        caps = super().capabilities()
        caps["actions"] = ["record", "transcribe", "speak"]
        caps["providers"] = {
            "asr": "openai_whisper" if self._asr_available() else "none",
            "tts": ("edge" if self._edge_tts is not None
                    else "openai" if self._env("OPENAI_API_KEY") else "none"),
        }
        return caps

    def invoke(self, action: str, params: Optional[Dict] = None) -> DeviceResult:
        p = params or {}
        try:
            if action == "record":
                return self._record(p)
            if action == "transcribe":
                return self._transcribe(p)
            if action == "speak":
                return self._speak(p)
            if action == "say":
                return self._say(p)
            if action == "listen":
                return self._listen(p)
            if action == "listen_stream":
                return self._listen_stream(p)
            if action == "ptt":
                return self._ptt(p)
        except Exception as exc:
            return self._fail(f"{action} 异常: {exc}")
        return self._fail(f"未知动作 {action}（可用: record/transcribe/speak/say/listen/listen_stream/ptt）")

    # ---- 动作 ----

    def _record(self, p: Dict) -> DeviceResult:
        """麦克风录音 → wav 文件（工作区 audio/ 下）。"""
        if self._sounddevice is None:
            return self._fail("录音不可用：pip install sounddevice")
        seconds = max(0.5, min(float(p.get("seconds", 5.0)), 60.0))
        samplerate = int(p.get("samplerate", 16000))
        audio_dir = os.path.join(self.workspace, _AUDIO_DIR) if self.workspace else _AUDIO_DIR
        os.makedirs(audio_dir, exist_ok=True)
        path = os.path.join(audio_dir, f"rec_{int(time.time() * 1000)}.wav")
        try:
            sd = self._sounddevice
            data = sd.rec(int(seconds * samplerate), samplerate=samplerate, channels=1, dtype="int16")
            sd.wait()
            self._write_wav(path, data, samplerate)
        except Exception as exc:
            return self._fail(f"录音失败: {exc}")
        meta = {"path": os.path.abspath(path), "seconds": seconds,
                "samplerate": samplerate, "bytes": os.path.getsize(path)}
        return self._r(meta, "record",
                       text_summary=f"录音完成: {meta['path']}（{seconds}s）")

    def _transcribe(self, p: Dict) -> DeviceResult:
        """ASR：音频文件（工作区内）→ 文本。
        引擎优先级：sherpa-onnx 本地（AEIS_ASR_MODEL_DIR）→ OpenAI 兼容。"""
        path = p.get("path", "")
        if not path:
            return self._fail("缺少 path（音频文件，须在工作区内）")
        if self.workspace:
            target = os.path.abspath(os.path.join(self.workspace, path))
            ws = os.path.abspath(self.workspace)
            if not (target == ws or target.startswith(ws + os.sep)):
                return self._fail(f"路径越出工作区: {path}")
            full = target
        else:
            full = os.path.abspath(path)
        if not os.path.isfile(full):
            return self._fail(f"文件不存在: {path}")

        # 1. sherpa-onnx 本地（零 API，TMSpeech 同源）
        local_text = self._asr_transcribe(full)
        if local_text:
            return self._r({"text": local_text, "source_file": path, "engine": "sherpa-onnx"},
                           "transcribe",
                           text_summary=f"识别完成（{len(local_text)} 字符，本地 sherpa-onnx）")
        # 2. OpenAI 兼容
        if self._openai is not None and self._env("OPENAI_API_KEY"):
            try:
                client = self._openai.OpenAI(
                    api_key=self._env("OPENAI_API_KEY"),
                    base_url=self._env("OPENAI_BASE_URL") or None)
                with open(full, "rb") as f:
                    resp = client.audio.transcriptions.create(
                        model=p.get("model", "whisper-1"), file=f)
                text = str(getattr(resp, "text", "") or "")
                if text:
                    return self._r({"text": text, "source_file": path,
                                    "engine": "openai"},
                                   "transcribe",
                                   text_summary=f"识别完成（{len(text)} 字符，openai）")
            except Exception:
                pass
        # 3. 降级提示
        hint = ("本地 sherpa-onnx 未配置（AEIS_ASR_MODEL_DIR），或 openai 未配置"
                if not local_text else "")
        return self._fail(hint or "ASR 不可用：配置 AEIS_ASR_MODEL_DIR（本地）或 OPENAI_API_KEY")

    def _speak(self, p: Dict) -> DeviceResult:
        """TTS：文本 → 音频文件（edge-tts 免 key，或 OpenAI TTS）。"""
        text = str(p.get("text", "")).strip()
        if not text:
            return self._fail("缺少 text")
        if len(text) > 2000:
            return self._fail(f"文本过长（{len(text)} 字符，上限 2000）")
        audio_dir = os.path.join(self.workspace, _AUDIO_DIR) if self.workspace else _AUDIO_DIR
        os.makedirs(audio_dir, exist_ok=True)
        stamp = int(time.time() * 1000)

        if self._edge_tts is not None:
            path = os.path.join(audio_dir, f"tts_{stamp}.mp3")
            voice = p.get("voice", "zh-CN-XiaoxiaoNeural")
            try:
                import asyncio

                async def _synth():
                    communicate = self._edge_tts.Communicate(text, voice)
                    await communicate.save(path)

                asyncio.run(_synth())
            except Exception as exc:
                return self._fail(f"edge-tts 合成失败: {exc}")
            provider = "edge"
        elif self._env("OPENAI_API_KEY"):
            path = os.path.join(audio_dir, f"tts_{stamp}.mp3")
            voice = p.get("voice", "alloy")
            client = self._openai.OpenAI(api_key=self._env("OPENAI_API_KEY"))
            resp = client.audio.speech.create(model=p.get("model", "tts-1"),
                                              voice=voice, input=text)
            resp.stream_to_file(path)
            provider = "openai"
        else:
            return self._fail("TTS 不可用：pip install edge-tts（免 key）或配置 OPENAI_API_KEY")

        meta = {"path": os.path.abspath(path), "provider": provider,
                "chars": len(text), "bytes": os.path.getsize(path)}
        return self._r(meta, "speak",
                       text_summary=f"语音合成完成: {meta['path']}（{provider}）")

    # ---- 工具 ----

    def _say(self, p: Dict) -> DeviceResult:
        """语音输出。引擎优先级：
        nahida（GPT-SoVITS 纳西妲音色·常驻服务热加载）→ cosyvoice（zero-shot 克隆）
        → System.Speech（零依赖兜底）。
        engine 参数可显式指定：nahida / cosyvoice / system / edge。"""
        import subprocess

        text = str(p.get("text", "")).strip()
        if not text:
            return self._fail("缺少 text")
        if len(text) > 500:
            return self._fail(f"文本过长（{len(text)} 字符，上限 500）")
        engine = str(p.get("engine", "nahida"))
        # 纳西妲引擎（本地 GPU·常驻服务·热加载）
        if engine in ("nahida", "auto"):
            try:
                out = self._say_nahida(text)
                if out:
                    try:
                        import winsound
                        winsound.PlaySound(out, winsound.SND_FILENAME)
                    except Exception:
                        pass
                    return self._r({"chars": len(text), "engine": "nahida",
                                    "path": out}, "say",
                                   text_summary=f"纳西妲语音输出 {len(text)} 字符")
            except Exception as exc:
                if engine == "nahida":
                    return self._fail(f"纳西妲输出失败: {exc}")
                # auto → 降级 CosyVoice
        # CosyVoice 引擎（本地 GPU·zero-shot 音色克隆）
        if engine in ("cosyvoice", "auto"):
            try:
                sys_path = os.path.dirname(os.path.dirname(os.path.dirname(
                    os.path.dirname(os.path.abspath(__file__)))))  # AEIS 根
                import importlib.util
                spec = importlib.util.spec_from_file_location(
                    "cosyvoice_tts", os.path.join(sys_path, "cosyvoice_tts.py"))
                if spec and spec.loader:
                    mod = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(mod)
                    out = os.path.join(self.workspace or ".", "audio",
                                       f"say_{int(time.time()*1000)}.wav")
                    os.makedirs(os.path.dirname(out), exist_ok=True)
                    mod.synthesize(text, out_wav=out, timeout=120)
                    if os.path.getsize(out) > 1000:
                        # 播放
                        ref_wav = getattr(mod, "DEFAULT_REF", "")
                        try:
                            import winsound
                            winsound.PlaySound(out, winsound.SND_FILENAME)
                        except Exception:
                            pass
                        return self._r({"chars": len(text), "engine": "cosyvoice",
                                        "path": os.path.abspath(out)}, "say",
                                       text_summary=f"CosyVoice 语音输出 {len(text)} 字符")
            except Exception as exc:
                if engine == "cosyvoice":
                    return self._fail(f"CosyVoice 输出失败: {exc}")
                # auto → 降级 System.Speech
        voice = str(p.get("voice", ""))
        rate = str(p.get("rate", "0"))  # -10~10
        try:
            cmd = ("Add-Type -AssemblyName System.Speech; "
                   f"$s = New-Object System.Speech.Synthesis.SpeechSynthesizer; "
                   f"$s.Rate = {rate}; ")
            if voice:
                cmd += f"$s.SelectVoice('{voice}'); "
            cmd += f"$s.Speak('{text.replace(chr(39), chr(39)+chr(39))}')"
            proc = subprocess.run(["powershell", "-NoProfile", "-Command", cmd],
                                  capture_output=True, timeout=30)
            if proc.returncode != 0:
                return self._fail(f"语音输出失败: {proc.stderr.decode('utf-8', 'replace')[:120]}")
        except Exception as exc:
            return self._fail(f"语音输出异常: {exc}")
        return self._r({"chars": len(text), "engine": "system.speech"}, "say",
                       text_summary=f"已语音输出 {len(text)} 字符")

    # ---- 纳西妲常驻服务（GPT-SoVITS） ----

    _nahida_proc = None  # 类级单例：常驻进程跨调用保持热加载

    def _say_nahida(self, text: str) -> str:
        """纳西妲合成：常驻 GPT-SoVITS 服务（JSON-lines over stdio）。
        首次启动加载模型（~110s，之后保持热加载），每次请求 ~1s 合成。"""
        import json
        import queue as _q
        import random
        import subprocess
        import threading

        proc = self._nahida_proc
        if proc is None or proc.poll() is not None:
            sys_path = os.path.dirname(os.path.dirname(os.path.dirname(
                os.path.dirname(os.path.abspath(__file__)))))  # AEIS 根
            srv = os.path.join(sys_path, "nahida_server.py")
            py = r"D:\Program Files\ai_voice\GPT-SoVITS-v3lora-20250228\runtime\python.exe"
            # 单例化：启动前清理所有旧 nahida_server 实例（防孤儿累积——
            # harness 崩溃后旧实例成为孤儿进程，曾导致多实例 + CPU 忙等）
            try:
                import subprocess as _sp
                _sp.run(
                    ["powershell", "-NoProfile", "-Command",
                     "Get-CimInstance Win32_Process -Filter \"Name='python.exe'\" "
                     "| Where-Object { $_.CommandLine -like '*nahida_server*' "
                     "} | ForEach-Object { Stop-Process -Id $_.ProcessId -Force }"],
                    capture_output=True, timeout=15)
                time.sleep(1)
            except Exception:
                pass
            proc = subprocess.Popen(
                [py, srv], stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                stderr=subprocess.DEVNULL,
                creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
            # 等 READY（模型加载 ~110s）
            line = proc.stdout.readline().decode("utf-8", "replace").strip()
            if "READY" not in line:
                proc.kill()
                raise RuntimeError(f"纳西妲服务启动失败: {line[:100]}")
            self._nahida_proc = proc
        rid = f"{int(time.time() * 1000)}{random.randint(100, 999)}"
        proc.stdin.write((json.dumps({"id": rid, "text": text}) + "\n").encode("utf-8"))
        proc.stdin.flush()
        q = _q.Queue()

        def _reader():
            try:
                q.put(proc.stdout.readline().decode("utf-8", "replace").strip())
            except Exception:
                q.put(None)

        th = threading.Thread(target=_reader, daemon=True)
        th.start()
        th.join(timeout=120)
        if th.is_alive():
            proc.kill()
            self._nahida_proc = None
            raise RuntimeError("纳西妲服务响应超时")
        data = json.loads(q.get() or "{}")
        if not data.get("ok"):
            raise RuntimeError(data.get("error", "未知错误"))
        return data["wav"]

    def _listen(self, p: Dict) -> DeviceResult:
        """语音输入：麦克风录音 → wav（sounddevice）→ ASR 转写（可用引擎）。

        ASR 引擎优先级：sherpa-onnx 本地（若已装模型）→ OpenAI 兼容
        （OPENAI_API_KEY）→ 无引擎时降级返回录音文件路径。
        """
        if self._sounddevice is None:
            return self._fail("录音不可用：pip install sounddevice")
        seconds = max(1.0, min(float(p.get("seconds", 5.0)), 30.0))
        samplerate = int(p.get("samplerate", 16000))
        audio_dir = os.path.join(self.workspace, _AUDIO_DIR) if self.workspace else _AUDIO_DIR
        os.makedirs(audio_dir, exist_ok=True)
        path = os.path.join(audio_dir, f"in_{int(time.time() * 1000)}.wav")
        try:
            sd = self._sounddevice
            data = sd.rec(int(seconds * samplerate), samplerate=samplerate,
                          channels=1, dtype="int16")
            sd.wait()
            self._write_wav(path, data, samplerate)
        except Exception as exc:
            return self._fail(f"录音失败: {exc}")

        # ASR 转写
        text = self._asr_transcribe(path)
        data = {"path": os.path.abspath(path), "seconds": seconds,
                "bytes": os.path.getsize(path)}
        if text:
            data["text"] = text
            data["asr"] = True
            summary = f"识别: {text[:60]}"
        else:
            data["asr"] = False
            summary = f"已录音（{seconds}s），无 ASR 引擎（可配 OPENAI_API_KEY 或本地 sherpa-onnx）"
        return self._r(data, "listen", text_summary=summary)

    def _listen_stream(self, p: Dict) -> DeviceResult:
        """实时监听麦克风 + 流式识别 + 断句输出（TMSpeech 同款方案）。

        sounddevice 实时捕获 → sherpa-onnx OnlineRecognizer 流式解码 →
        is_endpoint 断句检测 → 完整句子列表。
        params: max_seconds（监听上限，默认 30）、max_sentences（句子数上限，默认 10）。
        """
        if self._sounddevice is None:
            return self._fail("实时监听不可用：pip install sounddevice")
        model_dir = os.environ.get("AEIS_ASR_MODEL_DIR", "")
        if not model_dir or not os.path.isdir(model_dir):
            return self._fail("本地 ASR 未配置：设置 AEIS_ASR_MODEL_DIR（sherpa-onnx 模型目录）")
        try:
            import sherpa_onnx  # type: ignore
            import numpy as np  # type: ignore
            import queue as _queue
        except Exception as exc:
            return self._fail(f"依赖缺失: {exc}")

        max_seconds = max(1.0, min(float(p.get("max_seconds", 30.0)), 120.0))
        max_sentences = max(1, min(int(p.get("max_sentences", 10)), 50))
        samplerate = 16000
        # 音源：mic（麦克风·人说话）/ loopback（WASAPI 录内音·系统声音，
        # TMSpeech 同款——无需物理收音，直接捕获系统输出）
        source = str(p.get("source", "mic"))

        recognizer = sherpa_onnx.OnlineRecognizer.from_transducer(
            encoder=os.path.join(model_dir, "encoder-epoch-99-avg-1.int8.onnx"),
            decoder=os.path.join(model_dir, "decoder-epoch-99-avg-1.int8.onnx"),
            joiner=os.path.join(model_dir, "joiner-epoch-99-avg-1.int8.onnx"),
            tokens=os.path.join(model_dir, "tokens.txt"),
            num_threads=2)
        stream = recognizer.create_stream()
        audio_q = _queue.Queue()

        def _callback(indata, frames, time_info, status):
            audio_q.put(indata.copy())

        try:
            if source == "loopback":
                # WASAPI loopback：输出设备作输入（录内音，TMSpeech 同款）
                dev = None
                try:
                    sd = self._sounddevice
                    wasapi = None
                    for i, ha in enumerate(sd.query_hostapis()):
                        if "WASAPI" in str(ha.get("name", "")).upper():
                            wasapi = i
                            break
                    if wasapi is not None:
                        for i, d in enumerate(sd.query_devices(hostapi=wasapi)):
                            if d.get("max_output_channels", 0) > 0:
                                dev = i
                                break
                except Exception:
                    pass
                if dev is None:
                    return self._fail("未找到 WASAPI 输出设备（录内音不可用）")
                settings = (self._sounddevice.WasapiSettings(loopback=True)
                            if hasattr(self._sounddevice, "WasapiSettings") else None)
                with self._sounddevice.InputStream(
                        device=dev, samplerate=samplerate, channels=1,
                        dtype="int16", callback=_callback,
                        extra_settings=settings):
                    sentences = self._listen_loop(recognizer, stream, audio_q,
                                                  max_seconds, max_sentences, samplerate)
            else:
                with self._sounddevice.InputStream(
                        samplerate=samplerate, channels=1, dtype="int16",
                        callback=_callback):
                    sentences = self._listen_loop(recognizer, stream, audio_q,
                                                  max_seconds, max_sentences, samplerate)
        except Exception as exc:
            return self._fail(f"监听异常: {exc}")

        joined = " ".join(sentences)
        data = {"sentences": sentences, "count": len(sentences),
                "text": joined, "source": source}
        summary = (f"监听完成：{len(sentences)} 句（{len(joined)} 字符）"
                   if sentences else "监听完成：未检测到语音")
        return self._r(data, "listen_stream", text_summary=summary)

    def _ptt(self, p: Dict) -> DeviceResult:
        """Push-to-Talk：按住说话，松开 = 一句话提交（猫娘计划交互模式）。

        流程：等待用户按住触发键 → 开始录音（麦克风）→ 松开 → 停止 →
        sherpa-onnx 识别 → 返回一句话文字（一次输入提交）。
        params: key（触发键，默认 space）、max_seconds（最长按住，默认 30）。
        """
        if self._sounddevice is None:
            return self._fail("PTT 不可用：pip install sounddevice")
        model_dir = os.environ.get("AEIS_ASR_MODEL_DIR", "")
        if not model_dir or not os.path.isdir(model_dir):
            return self._fail("本地 ASR 未配置：设置 AEIS_ASR_MODEL_DIR")
        try:
            import keyboard  # type: ignore
            import sherpa_onnx  # type: ignore
            import numpy as np  # type: ignore
        except Exception as exc:
            return self._fail(f"依赖缺失: {exc}")

        key = str(p.get("key", "space"))
        max_seconds = max(1.0, min(float(p.get("max_seconds", 30.0)), 120.0))
        samplerate = 16000
        state = {"recording": False, "done": False, "frames": []}

        def _on_press(e):
            if e.name == key and not state["recording"]:
                state["recording"] = True
                state["frames"] = []

        def _on_release(e):
            if e.name == key and state["recording"]:
                state["recording"] = False
                state["done"] = True

        keyboard.hook(_on_press)
        keyboard.hook(_on_release)
        try:
            # 等待用户按住
            import time as _time
            waited = 0.0
            while not state["recording"] and waited < 60:
                _time.sleep(0.05)
                waited += 0.05
            if not state["recording"]:
                return self._r({"text": "", "count": 0, "timed_out": True},
                               "ptt", text_summary="等待按键超时（未按下）")
            # 按住期间录音
            frames = []
            with self._sounddevice.InputStream(
                    samplerate=samplerate, channels=1, dtype="int16",
                    callback=lambda indata, f, t, s: frames.append(indata.copy())):
                started = _time.time()
                while not state["done"] and (_time.time() - started < max_seconds):
                    _time.sleep(0.05)
            # 松开 → 识别提交
            if frames:
                samples = np.concatenate(frames).flatten()
            else:
                samples = np.zeros(samplerate, dtype=np.int16)
            recognizer = sherpa_onnx.OnlineRecognizer.from_transducer(
                encoder=os.path.join(model_dir, "encoder-epoch-99-avg-1.int8.onnx"),
                decoder=os.path.join(model_dir, "decoder-epoch-99-avg-1.int8.onnx"),
                joiner=os.path.join(model_dir, "joiner-epoch-99-avg-1.int8.onnx"),
                tokens=os.path.join(model_dir, "tokens.txt"),
                num_threads=2)
            stream = recognizer.create_stream()
            stream.accept_waveform(samplerate, samples)
            stream.input_finished()
            while recognizer.is_ready(stream):
                recognizer.decode_stream(stream)
            text = recognizer.get_result(stream).strip()
            return self._r({"text": text, "count": 1 if text else 0,
                            "seconds": round(_time.time() - started, 1)},
                           "ptt",
                           text_summary=(f"PTT 提交: {text[:60]}"
                                         if text else "PTT 未检测到语音"))
        finally:
            keyboard.unhook_all()

    def _listen_loop(self, recognizer, stream, audio_q, max_seconds,
                     max_sentences, samplerate):
        """流式解码 + 断句主循环（is_endpoint 检测）。"""
        import time as _time
        sentences = []
        started = _time.time()
        while (_time.time() - started < max_seconds
               and len(sentences) < max_sentences):
            try:
                block = audio_q.get(timeout=0.5)
            except Exception:
                continue
            samples = block.flatten()
            stream.accept_waveform(samplerate, samples)
            while recognizer.is_ready(stream):
                recognizer.decode_stream(stream)
            # 断句检测（端点/静音）
            if recognizer.is_endpoint(stream):
                text = recognizer.get_result(stream).strip()
                if text:
                    sentences.append(text)
                stream = recognizer.create_stream()
        # 收尾残句
        tail = recognizer.get_result(stream).strip()
        if tail and (not sentences or sentences[-1] != tail):
            sentences.append(tail)
        return sentences

    def _asr_transcribe(self, wav_path: str) -> str:
        """ASR 转写：sherpa-onnx 本地优先 → OpenAI 兼容。"""
        # 1. sherpa-onnx 本地（零 API）
        try:
            import sherpa_onnx  # type: ignore
        except Exception:
            sherpa_onnx = None
        if sherpa_onnx is not None:
            try:
                # 需要已配置模型路径（环境变量 AEIS_ASR_MODEL_DIR）
                model_dir = os.environ.get("AEIS_ASR_MODEL_DIR", "")
                if model_dir and os.path.isdir(model_dir):
                    import wave as _wave
                    import numpy as np  # type: ignore

                    with _wave.open(wav_path, "rb") as w:
                        rate = w.getframerate()
                        samples = np.frombuffer(w.readframes(w.getnframes()),
                                                dtype=np.int16)
                    recognizer = sherpa_onnx.OnlineRecognizer.from_transducer(
                        encoder=os.path.join(model_dir, "encoder-epoch-99-avg-1.int8.onnx"),
                        decoder=os.path.join(model_dir, "decoder-epoch-99-avg-1.int8.onnx"),
                        joiner=os.path.join(model_dir, "joiner-epoch-99-avg-1.int8.onnx"),
                        tokens=os.path.join(model_dir, "tokens.txt"),
                        num_threads=2)
                    stream = recognizer.create_stream()
                    stream.accept_waveform(rate, samples)
                    stream.input_finished()
                    while recognizer.is_ready(stream):
                        recognizer.decode_stream(stream)
                    return recognizer.get_result(stream).strip()
            except Exception:
                pass
        # 2. OpenAI 兼容
        if self._openai is not None and self._env("OPENAI_API_KEY"):
            try:
                client = self._openai.OpenAI(api_key=self._env("OPENAI_API_KEY"))
                with open(wav_path, "rb") as f:
                    resp = client.audio.transcriptions.create(
                        model="whisper-1", file=f)
                return str(getattr(resp, "text", "") or "").strip()
            except Exception:
                pass
        return ""

    @staticmethod
    def _write_wav(path: str, data, samplerate: int) -> None:
        """纯标准库写 WAV（PCM16 单声道）。"""
        import struct
        import wave

        with wave.open(path, "wb") as w:
            w.setnchannels(1)
            w.setsampwidth(2)
            w.setframerate(samplerate)
            w.writeframes(data.tobytes())
