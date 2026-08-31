import os
from config import user_config
from core.model_manager import ModelManager


def test_set_models_dir_persists_and_redirects_hf_cache(tmp_path, monkeypatch):
    config_file = tmp_path / "config" / "config.json"
    monkeypatch.setattr(user_config, "get_config_path", lambda: config_file)
    monkeypatch.setattr(user_config, "get_app_dir", lambda: tmp_path)

    chosen = tmp_path / "D_DRIVE" / "ToonixAI"
    resolved = user_config.set_models_dir(chosen)

    assert resolved == chosen.resolve()
    assert user_config.get_models_dir() == resolved
    assert user_config.get_hf_cache_dir() == resolved / "huggingface"
    assert os.environ["HF_HOME"] == str(resolved / "huggingface")


def test_model_manager_downloads_to_custom_disk(tmp_path, monkeypatch):
    captured = {}
    dest_root = tmp_path / "E_DRIVE" / "ToonixAI"
    dest_root.mkdir(parents=True)

    monkeypatch.setattr("core.model_manager.get_free_space", lambda path: 2 * 1024 ** 3)
    monkeypatch.setattr("core.model_manager.apply_huggingface_cache", lambda models_dir=None: dest_root / "huggingface")
    monkeypatch.setattr("core.model_manager.get_hf_cache_dir", lambda models_dir=None: dest_root / "huggingface")

    def fake_download(**kwargs):
        captured.update(kwargs)
        downloaded = dest_root / "lama.onnx"
        downloaded.write_bytes(b"onnx")
        return str(downloaded)

    monkeypatch.setattr("core.model_manager.hf_hub_download", fake_download)

    manager = ModelManager(base_dir=dest_root)
    assert manager.get_missing_models()
    assert manager.download_model("lama.onnx") is True
    assert captured["cache_dir"] == str(dest_root / "huggingface")
    assert captured["local_dir"] == str(dest_root)
    assert (dest_root / "models" / "lama_512.onnx").exists()


def test_model_manager_refuses_full_disk(tmp_path, monkeypatch):
    monkeypatch.setattr("core.model_manager.get_free_space", lambda path: 10 * 1024 * 1024)
    manager = ModelManager(base_dir=tmp_path)
    assert manager.download_model("lama.onnx") is False
