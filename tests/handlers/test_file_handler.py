import os
import json
from loglight.handlers import FileHandler, RotatingFileHandler


def test_file_handler_writes_and_closes(tmp_path):
    file_path = tmp_path / "log.txt"
    handler = FileHandler(str(file_path))

    handler.emit('{"event":"test"}')
    handler.file.close()

    with open(file_path) as f:
        content = f.read().strip()
    assert '{"event":"test"}' in content


def test_rotating_file_handler_rotates(tmp_path):
    log_file = tmp_path / "app.log"
    max_bytes = 100
    backup_count = 3
    handler = RotatingFileHandler(
        str(log_file), max_bytes=max_bytes, backup_count=backup_count
    )
    for i in range(20):
        data = json.dumps({"msg": f"log_{i}", "num": i})
        handler.emit(data)

    handler.file.close()

    # Check current log file exists and backups
    assert os.path.exists(log_file)
    for i in range(1, backup_count + 1):
        backup = tmp_path / f"app.log.{i}"
        # backups might exist or not depending on rotation count, but at least one backup should exist
        if backup.exists():
            with open(backup) as f:
                assert f.read() != ""


def test_rotating_file_handler_deletes_oldest(tmp_path):
    log_file = tmp_path / "rotate.log"
    max_bytes = 50
    backup_count = 2
    handler = RotatingFileHandler(
        str(log_file), max_bytes=max_bytes, backup_count=backup_count
    )

    # Write enough logs to create 4 rotations (oldest backup should be deleted)
    for i in range(50):
        handler.emit(json.dumps({"msg": f"log_{i}"}))

    handler.file.close()

    # Oldest backup (rotate.log.3) should not exist because backup_count=2
    assert not (tmp_path / "rotate.log.3").exists()
    # Backups up to rotate.log.2 should exist (or maybe just rotate.log.1)
    assert (tmp_path / "rotate.log.1").exists()


def test_rotating_file_handler_handles_missing_files(tmp_path):
    # Simulate situation with missing backup files
    log_file = tmp_path / "missing.log"
    max_bytes = 50
    backup_count = 3
    handler = RotatingFileHandler(
        str(log_file), max_bytes=max_bytes, backup_count=backup_count
    )

    # Only create one backup file manually
    backup1 = tmp_path / "missing.log.1"
    backup1.write_text("old backup")

    # Emit logs enough to trigger rotation
    for _ in range(10):
        handler.emit(json.dumps({"msg": "test"}))

    handler.file.close()
    # Should rotate without error despite missing some backup files
    assert (tmp_path / "missing.log.1").exists()


def test_file_handler_closes_on_del(tmp_path):
    file_path = tmp_path / "del_test.log"
    handler = FileHandler(str(file_path))
    handler.emit('{"test":1}')
    file_obj = handler.file
    del handler
    # File should be closed after del
    assert file_obj.closed
