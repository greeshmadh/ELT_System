import logging
import os

def test_logger_writes_to_file(tmp_path):
    # Create a temporary log file
    test_log_path = tmp_path / "test_elt.log"

    # Create a separate logger just for testing
    test_logger = logging.getLogger("test_logger")
    test_logger.setLevel(logging.INFO)

    # Ensure no duplicate handlers
    test_logger.handlers.clear()

    # Add file handler to our test logger
    file_handler = logging.FileHandler(test_log_path, mode='w')
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    file_handler.setFormatter(formatter)
    test_logger.addHandler(file_handler)

    # Write a log message
    test_logger.info("Test log entry")

    # Flush and close handler
    file_handler.flush()
    file_handler.close()

    # Read and assert content
    with open(test_log_path, "r") as f:
        content = f.read()
        assert "Test log entry" in content
        assert "INFO" in content
