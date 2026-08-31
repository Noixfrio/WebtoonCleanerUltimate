import numpy as np
import pytest

from core.advanced_inpaint import LaMaInpainter
from core.exceptions import InpaintServiceError


def test_lama_reports_insufficient_disk_space(monkeypatch, tmp_path):
    engine = LaMaInpainter()
    engine._session = None
    engine.base_dir = str(tmp_path)
    engine.model_path = str(tmp_path / "lama.onnx")

    monkeypatch.setattr(
        "core.advanced_inpaint.get_free_space",
        lambda path: 100 * 1024 * 1024,
    )

    with pytest.raises(InpaintServiceError, match="Espaço insuficiente"):
        engine.process(np.zeros((8, 8, 3), dtype=np.uint8), np.zeros((8, 8), dtype=np.uint8))


def test_lama_downloads_into_chosen_cache(monkeypatch, tmp_path):
    engine = LaMaInpainter()
    engine._session = None
    engine.base_dir = str(tmp_path)
    engine.model_path = str(tmp_path / "lama.onnx")
    captured = {}

    monkeypatch.setattr("core.advanced_inpaint.get_free_space", lambda path: 2 * 1024 ** 3)
    monkeypatch.setattr(
        "core.advanced_inpaint.apply_huggingface_cache",
        lambda models_dir=None: tmp_path / "huggingface",
    )

    def fake_download(**kwargs):
        captured.update(kwargs)
        dest = tmp_path / "downloaded.onnx"
        dest.write_bytes(b"onnx")
        return str(dest)

    monkeypatch.setattr("core.advanced_inpaint.hf_hub_download", fake_download)
    monkeypatch.setattr(
        "core.advanced_inpaint.ort.InferenceSession",
        lambda *args, **kwargs: object(),
    )

    engine.process(np.zeros((8, 8, 3), dtype=np.uint8), np.zeros((8, 8), dtype=np.uint8))

    assert captured["cache_dir"] == str(tmp_path / "huggingface")
    assert (tmp_path / "lama.onnx").exists()
