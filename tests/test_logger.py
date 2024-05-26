import os


def test_file_logging(temp_logger):
    """
    GIVEN a temporary logger
    WHEN  logs are made
    THEN  a file file exists containing those messages
    """
    log = temp_logger.get(__name__)

    # log at different log levels
    log.debug("Debug message")
    log.info("Info message")
    log.warning("Warning message")
    log.error("Error message")
    log.critical("Critical message")

    # check log file exists and contains the logged messages
    assert os.path.exists(temp_logger.log_file)
    with open(temp_logger.log_file, "r") as log_file:
        log_content = log_file.read()
        assert "Debug message" in log_content
        assert "Info message" in log_content
        assert "Warning message" in log_content
        assert "Error message" in log_content
        assert "Critical message" in log_content
