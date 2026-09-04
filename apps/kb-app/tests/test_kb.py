import io
import sqlite3
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

import kb


class SQLiteStoreTest(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.store = kb.SQLiteStore(self.root / "kb.db")

    def tearDown(self):
        self.temporary.cleanup()

    def test_save_get_list_search_and_updated(self):
        self.store.save("空正文命中", "", timestamp="2026-09-04T00:00:00+00:00")
        self.store.save("正文笔记", "前文 风格验证 后文", timestamp="2026-09-04T01:00:00+00:00")

        note = self.store.get_note("正文笔记")
        self.assertEqual(note["content"], "前文 风格验证 后文")
        self.assertEqual([item["title"] for item in self.store.list_notes()], ["正文笔记", "空正文命中"])
        self.assertEqual(self.store.search("风格")[0]["title"], "正文笔记")
        self.assertEqual(self.store.search("空正文")[0]["snippet"], "标题匹配")

        created = note["created"]
        self.store.save("正文笔记", "已修改", original_content=note["content"], timestamp="2026-09-04T02:00:00+00:00")
        updated = self.store.get_note("正文笔记")
        self.assertEqual(updated["created"], created)
        self.assertEqual(updated["updated"], "2026-09-04T02:00:00+00:00")
        self.assertEqual(updated["content"], "已修改")

    def test_conflicting_save_does_not_overwrite(self):
        self.store.save("冲突", "原文")
        with self.assertRaises(kb.ConflictError):
            self.store.save("冲突", "另一内容")
        self.assertEqual(self.store.get_note("冲突")["content"], "原文")

    def test_database_configuration(self):
        with self.store.connect() as connection:
            self.assertEqual(connection.execute("PRAGMA journal_mode").fetchone()[0], "wal")
            self.assertEqual(connection.execute("PRAGMA busy_timeout").fetchone()[0], 5000)

    def test_first_creation_migrates_markdown_without_deleting_it(self):
        migration_root = self.root / "migration"
        source = migration_root / "kb_data"
        source.mkdir(parents=True)
        markdown = source / "旧笔记.md"
        markdown.write_text("旧内容", encoding="utf-8")

        output = io.StringIO()
        with redirect_stdout(output):
            migrated = kb.SQLiteStore(migration_root / "kb.db")

        self.assertIn("已从 kb_data 导入 1 篇", output.getvalue())
        self.assertEqual(migrated.get_note("旧笔记")["content"], "旧内容")
        self.assertTrue(markdown.exists())

    def test_export_import_round_trip_and_conflict_skip(self):
        self.store.save("甲", "内容甲")
        export_dir = self.root / "export"
        self.assertEqual(self.store.export_directory(export_dir), 1)

        destination = kb.SQLiteStore(self.root / "destination.db", self.root / "no-migration")
        self.assertEqual(destination.import_directory(export_dir), (1, 0, 0))
        self.assertEqual(destination.get_note("甲")["content"], "内容甲")
        (export_dir / "甲.md").write_text("冲突内容", encoding="utf-8")
        self.assertEqual(destination.import_directory(export_dir), (0, 1, 0))
        self.assertEqual(destination.get_note("甲")["content"], "内容甲")

    def test_backup_can_be_opened_and_contains_same_data(self):
        self.store.save("备份笔记", "可靠内容")
        backup_path = self.root / "backups" / "snapshot.db"
        self.store.backup(backup_path)
        with sqlite3.connect(backup_path) as connection:
            row = connection.execute("SELECT title, content FROM notes").fetchone()
        self.assertEqual(row, ("备份笔记", "可靠内容"))


if __name__ == "__main__":
    unittest.main()
