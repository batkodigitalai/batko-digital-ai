from pathlib import Path

from loguru import logger

from src.core.config.models import LoggingConfig
from src.core.logging import get_logger, setup_logging


def test_setup_logging_creates_log_file(tmp_path: Path) -> None:
    config = LoggingConfig(logs_dir=Path("logs"), file_name="test.log", rotation="10 KB")
    log_file = setup_logging(config, project_root=tmp_path)

    logger.info("test message")
    logger.complete()

    assert log_file == tmp_path / "logs" / "test.log"
    assert log_file.exists()


def test_get_logger_binds_module_name(tmp_path: Path) -> None:
    config = LoggingConfig(logs_dir=Path("logs"), file_name="bound.log", rotation="10 KB")
    setup_logging(config, project_root=tmp_path)
    module_logger = get_logger("tests.core.test_logging")

    module_logger.info("bound message")
    logger.complete()

    assert (tmp_path / "logs" / "bound.log").exists()

