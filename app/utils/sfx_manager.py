"""
Soul Stage Sound Effects (SFX) Manager
Provides procedural and asset-backed audio feedback for dice rolls,
success/failure stingers, encounters, items, and rest interludes.
"""

import os
import random
import logging
import threading
import numpy as np
from typing import Optional

try:
    import sounddevice as sd
except ImportError:
    sd = None

logger = logging.getLogger("SoulStage.SFX")

class SFXManager:
    _instance: Optional["SFXManager"] = None
    _lock = threading.Lock()

    def __init__(self):
        self._sound_cache: dict[str, np.ndarray] = {}
        self._sample_rate = 44100
        self.enabled = True
        self.volume = 0.7  # 0.0 to 1.0

        try:
            from app.configuration import configuration
            self._cfg = configuration.ConfigurationSettings()
        except Exception:
            self._cfg = None

    @classmethod
    def get_instance(cls) -> "SFXManager":
        with cls._lock:
            if cls._instance is None:
                cls._instance = cls()
            return cls._instance

    def _get_device_index(self) -> Optional[int]:
        if self._cfg:
            try:
                idx = self._cfg.get_main_setting("output_device_real_index")
                if idx is not None:
                    return int(idx)
            except Exception:
                pass
        return None

    # -------------------------------------------------------------------------
    # Procedural Audio Synthesizers
    # -------------------------------------------------------------------------

    def _synth_dice_roll(self) -> np.ndarray:
        sr = self._sample_rate
        duration = 0.52
        total_samples = int(sr * duration)
        sound = np.zeros(total_samples, dtype=np.float32)

        # 7 tumble clicks at jittered intervals
        impact_times = [0.02, 0.09, 0.17, 0.26, 0.34, 0.42, 0.47]
        for t_imp in impact_times:
            jitter = random.uniform(-0.015, 0.015)
            idx = max(0, min(total_samples - 100, int((t_imp + jitter) * sr)))
            imp_len = int(random.uniform(0.025, 0.045) * sr)
            if idx + imp_len > total_samples:
                imp_len = total_samples - idx
            if imp_len <= 0:
                continue

            t = np.linspace(0, imp_len / sr, imp_len, False, dtype=np.float32)
            # Wood impact: filtered noise burst + resonant wooden click tone
            noise = (np.random.rand(imp_len).astype(np.float32) * 2.0 - 1.0) * np.exp(-t * 110.0)
            freq = random.uniform(340.0, 480.0)
            tone = np.sin(2.0 * np.pi * freq * t) * np.exp(-t * 85.0) * 0.45
            sound[idx:idx+imp_len] += (noise + tone)

        peak = np.max(np.abs(sound))
        if peak > 0:
            sound = (sound / peak) * 0.85
        return sound

    def _synth_dice_land(self) -> np.ndarray:
        sr = self._sample_rate
        dur = 0.15
        samples = int(sr * dur)
        t = np.linspace(0, dur, samples, False, dtype=np.float32)
        noise = (np.random.rand(samples).astype(np.float32) * 2.0 - 1.0) * np.exp(-t * 120.0)
        tone = np.sin(2.0 * np.pi * 380.0 * t) * np.exp(-t * 90.0) * 0.5
        out = noise + tone
        peak = np.max(np.abs(out))
        return (out / peak * 0.8) if peak > 0 else out

    def _synth_chime(self, frequencies: list[float], duration: float, decay_rate: float = 6.0) -> np.ndarray:
        sr = self._sample_rate
        total_samples = int(sr * duration)
        sound = np.zeros(total_samples, dtype=np.float32)
        note_spacing = int(total_samples * 0.18)

        for i, freq in enumerate(frequencies):
            start = i * note_spacing
            if start >= total_samples:
                break
            rem = total_samples - start
            t = np.linspace(0, rem / sr, rem, False, dtype=np.float32)
            env = np.exp(-t * decay_rate)
            # Bell overtone formula: fundamental + octave shimmer + fifth
            tone = (
                np.sin(2.0 * np.pi * freq * t) * 0.6 +
                np.sin(2.0 * np.pi * (freq * 2.0) * t) * 0.25 +
                np.sin(2.0 * np.pi * (freq * 2.76) * t) * 0.15
            ) * env
            sound[start:start+rem] += tone

        peak = np.max(np.abs(sound))
        return (sound / peak * 0.75) if peak > 0 else sound

    def _synth_success(self) -> np.ndarray:
        # C5 (523Hz), E5 (659Hz), G5 (784Hz)
        return self._synth_chime([523.25, 659.25, 783.99], duration=0.65, decay_rate=6.0)

    def _synth_critical_success(self) -> np.ndarray:
        # C5 (523Hz), G5 (784Hz), C6 (1046Hz), E6 (1318Hz) radiant fanfare
        return self._synth_chime([523.25, 783.99, 1046.50, 1318.51], duration=0.95, decay_rate=4.5)

    def _synth_failure(self) -> np.ndarray:
        # Muted descending 2-tone: Eb4 (311Hz) -> C4 (261Hz)
        sr = self._sample_rate
        dur = 0.50
        samples = int(sr * dur)
        sound = np.zeros(samples, dtype=np.float32)
        half = samples // 2

        t1 = np.linspace(0, half / sr, half, False, dtype=np.float32)
        sound[:half] += np.sin(2.0 * np.pi * 311.13 * t1) * np.exp(-t1 * 7.0)

        t2 = np.linspace(0, (samples - half) / sr, samples - half, False, dtype=np.float32)
        sound[half:] += np.sin(2.0 * np.pi * 261.63 * t2) * np.exp(-t2 * 6.0)

        peak = np.max(np.abs(sound))
        return (sound / peak * 0.7) if peak > 0 else sound

    def _synth_critical_failure(self) -> np.ndarray:
        # Dissonant tritone drop: C3 (130.8Hz) + F#3 (185Hz) with sub-bass impact
        sr = self._sample_rate
        dur = 0.75
        samples = int(sr * dur)
        t = np.linspace(0, dur, samples, False, dtype=np.float32)
        sub = np.sin(2.0 * np.pi * 65.4 * t) * np.exp(-t * 4.0) * 0.7
        tritone = (
            np.sin(2.0 * np.pi * 130.81 * t) * 0.5 +
            np.sin(2.0 * np.pi * 184.99 * t) * 0.5
        ) * np.exp(-t * 5.0)
        noise = (np.random.rand(samples).astype(np.float32) * 2.0 - 1.0) * np.exp(-t * 25.0) * 0.3
        sound = sub + tritone + noise
        peak = np.max(np.abs(sound))
        return (sound / peak * 0.8) if peak > 0 else sound

    def _synth_encounter(self) -> np.ndarray:
        # Dramatic martial drum thud + brass sting (D3 146Hz, A3 220Hz)
        sr = self._sample_rate
        dur = 0.65
        samples = int(sr * dur)
        t = np.linspace(0, dur, samples, False, dtype=np.float32)
        drum = np.sin(2.0 * np.pi * (80.0 - 40.0 * (t / dur)) * t) * np.exp(-t * 8.0) * 0.8
        brass = (
            np.sin(2.0 * np.pi * 146.83 * t) * 0.4 +
            np.sin(2.0 * np.pi * 220.00 * t) * 0.3
        ) * np.exp(-t * 5.5)
        sound = drum + brass
        peak = np.max(np.abs(sound))
        return (sound / peak * 0.8) if peak > 0 else sound

    def _synth_discovery(self) -> np.ndarray:
        # Ethereal harp chime: G4 (392Hz), B4 (493Hz), D5 (587Hz), G5 (784Hz)
        return self._synth_chime([392.00, 493.88, 587.33, 783.99], duration=0.80, decay_rate=5.0)

    def _synth_twist(self) -> np.ndarray:
        # Sharp stinger chord with quick crescendo & decay
        sr = self._sample_rate
        dur = 0.60
        samples = int(sr * dur)
        t = np.linspace(0, dur, samples, False, dtype=np.float32)
        envelope = (1.0 - np.exp(-t * 40.0)) * np.exp(-t * 5.0)
        sound = (
            np.sin(2.0 * np.pi * 370.0 * t) * 0.5 +
            np.sin(2.0 * np.pi * 440.0 * t) * 0.4 +
            np.sin(2.0 * np.pi * 554.37 * t) * 0.3
        ) * envelope
        peak = np.max(np.abs(sound))
        return (sound / peak * 0.75) if peak > 0 else sound

    def _synth_item_use(self) -> np.ndarray:
        # Crisp potion / cork pop + sparkle
        sr = self._sample_rate
        dur = 0.40
        samples = int(sr * dur)
        t = np.linspace(0, dur, samples, False, dtype=np.float32)
        pop = np.sin(2.0 * np.pi * (600.0 - 300.0 * t) * t) * np.exp(-t * 45.0)
        sparkle = np.sin(2.0 * np.pi * 1567.98 * t) * np.exp(-t * 12.0) * 0.4
        sound = pop + sparkle
        peak = np.max(np.abs(sound))
        return (sound / peak * 0.7) if peak > 0 else sound

    def _synth_rest(self) -> np.ndarray:
        # Warm campfire chord: F3 (174Hz), C4 (261Hz), A4 (440Hz) with gentle crackle
        sr = self._sample_rate
        dur = 1.10
        samples = int(sr * dur)
        t = np.linspace(0, dur, samples, False, dtype=np.float32)
        chord = (
            np.sin(2.0 * np.pi * 174.61 * t) * 0.4 +
            np.sin(2.0 * np.pi * 261.63 * t) * 0.35 +
            np.sin(2.0 * np.pi * 440.00 * t) * 0.25
        ) * np.exp(-t * 2.8)
        # Random crackle bursts
        crackle = np.zeros(samples, dtype=np.float32)
        for _ in range(8):
            c_pos = random.randint(0, samples - 200)
            crackle[c_pos:c_pos+100] += (np.random.rand(100).astype(np.float32) * 2 - 1) * 0.15
        sound = chord + crackle
        peak = np.max(np.abs(sound))
        return (sound / peak * 0.75) if peak > 0 else sound

    # -------------------------------------------------------------------------
    # Audio Retrieval & Playback
    # -------------------------------------------------------------------------

    def _get_audio_data(self, name: str) -> Optional[np.ndarray]:
        if name in self._sound_cache:
            return self._sound_cache[name]

        # Check for asset on disk first
        for base in ("app/gui/sounds", "app/cache/sounds"):
            candidate = os.path.join(base, f"{name}.wav")
            if os.path.exists(candidate):
                try:
                    import soundfile as sf
                    data, sr = sf.read(candidate, dtype="float32")
                    if data.ndim > 1:
                        data = data[:, 0]
                    self._sound_cache[name] = data
                    return data
                except Exception as e:
                    logger.debug(f"[SFX] Failed reading file {candidate}: {e}")

        # Procedural fallback
        synth_map = {
            "dice_roll": self._synth_dice_roll,
            "dice_land": self._synth_dice_land,
            "success": self._synth_success,
            "critical_success": self._synth_critical_success,
            "failure": self._synth_failure,
            "critical_failure": self._synth_critical_failure,
            "encounter": self._synth_encounter,
            "discovery": self._synth_discovery,
            "twist": self._synth_twist,
            "item_use": self._synth_item_use,
            "rest": self._synth_rest,
        }

        fn = synth_map.get(name)
        if fn:
            try:
                data = fn()
                self._sound_cache[name] = data
                return data
            except Exception as e:
                logger.warning(f"[SFX] Synthesizer failed for {name}: {e}")

        return None

    def play_sound(self, name: str, volume_mult: float = 1.0) -> None:
        if not self.enabled or sd is None:
            return

        def _worker():
            try:
                audio = self._get_audio_data(name)
                if audio is None:
                    return

                dev = self._get_device_index()
                vol = max(0.0, min(1.0, self.volume * volume_mult))
                scaled_audio = audio * vol

                sd.play(scaled_audio, samplerate=self._sample_rate, device=dev)
            except Exception as e:
                logger.debug(f"[SFX] Playback error ({name}): {e}")

        t = threading.Thread(target=_worker, daemon=True)
        t.start()

    # -------------------------------------------------------------------------
    # Convenience RPG Triggers
    # -------------------------------------------------------------------------

    def play_dice_roll(self):
        self.play_sound("dice_roll")

    def play_dice_land(self):
        self.play_sound("dice_land")

    def play_success(self):
        self.play_sound("success")

    def play_critical_success(self):
        self.play_sound("critical_success")

    def play_failure(self):
        self.play_sound("failure")

    def play_critical_failure(self):
        self.play_sound("critical_failure")

    def play_dice_result(self, total: int, dc: Optional[int] = None, natural: Optional[int] = None, success: Optional[bool] = None):
        if natural == 20:
            self.play_critical_success()
        elif natural == 1:
            self.play_critical_failure()
        elif success is True:
            self.play_success()
        elif success is False:
            self.play_failure()
        elif dc is not None:
            if total >= dc:
                self.play_success()
            else:
                self.play_failure()
        else:
            self.play_dice_land()

    def play_stinger(self, event_type: str):
        evt = str(event_type).lower().strip()
        if evt in ("encounter", "battle", "combat"):
            self.play_sound("encounter")
        elif evt in ("discovery", "clue", "lore", "arc"):
            self.play_sound("discovery")
        elif evt in ("twist", "trap", "danger", "clock"):
            self.play_sound("twist")
        elif evt in ("rest", "camp", "campfire"):
            self.play_sound("rest")
        else:
            self.play_sound("discovery", volume_mult=0.6)

    def play_item_use(self):
        self.play_sound("item_use")

    def play_rest(self):
        self.play_sound("rest")
