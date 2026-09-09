from orchestrator.config import load_config
from orchestrator.runner import run_pipeline
from cleaning.pipeline import clean_document


def test_global_orchestrator_imports_and_chain_is_available():
    assert load_config is not None
    assert run_pipeline is not None
    assert clean_document is not None


def test_repo_root_config_path_resolves_to_src_config_yaml():
    cfg = load_config("config.yaml")
    assert cfg.raw_data_path == "./data/raw"
    assert cfg.output_path == "./data/processed"
