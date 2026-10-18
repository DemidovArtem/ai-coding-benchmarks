from pathlib import Path
import subprocess
import tempfile
import unittest

from experiment.metrics import footprint, parse_numstat


class MetricsTests(unittest.TestCase):
    def test_nul_numstat_keeps_rename_tabs_and_binary(self):
        rows = parse_numstat(b"1\t2\t\0old\tname.rs\0new\nname.rs\0-\t-\timage.bin\0")
        self.assertEqual(rows[("old\tname.rs", "new\nname.rs")], (1, 2))
        self.assertEqual(rows[("image.bin", "image.bin")], (None, None))

    def test_real_git_diff_excludes_inline_tests_and_generated_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)

            def git(*args):
                return subprocess.check_output(["git", "-C", tmp, *args], stderr=subprocess.DEVNULL).decode().strip()

            def write(path, text):
                target = repo / path
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text(text)

            git("init")
            git("config", "user.name", "Test")
            git("config", "user.email", "test@example.invalid")
            source = 'pub fn value() -> i32 { 1 }\n#[cfg(test)]\nmod tests {\n    #[test]\n    fn check() { assert_eq!(super::value(), 1); }\n}\n'
            write("src/lib.rs", source)
            write("src/rename.rs", "pub fn keep() {}\n")
            write("src/old.rs", "pub fn old() {}\n")
            git("add", ".")
            git("commit", "-m", "base")
            base = git("rev-parse", "HEAD")
            write("src/lib.rs", source.replace("#[cfg(test)]", "pub fn new() {}\n#[cfg(test)]").replace("    #[test]", "    // added test comment\n    #[test]"))
            git("mv", "src/rename.rs", "src/renamed.rs")
            git("rm", "src/old.rs")
            write("src/new.rs", "pub fn added() {}\n")
            write("src/generated.rs", "pub fn generated() {}\n")
            write("tests/case.rs", "#[test]\nfn check() {}\n")
            (repo / "src/binary.rs").write_bytes(b"\0binary")
            git("add", ".")
            git("commit", "-m", "solution")
            end = git("rev-parse", "HEAD")
            metadata = {"repo_src_dirs": ["src"], "test_dirs": ["tests/**"], "generated_patterns": ["src/generated.rs"]}
            result = footprint(repo, base, end, metadata)
            self.assertEqual((result["added_prod_loc"], result["deleted_prod_loc"]), (2, 1))
            self.assertEqual((result["new_prod_files"], result["deleted_prod_files"], result["renamed_prod_files"]), (1, 1, 1))
            self.assertEqual(result["changed_prod_files"], 4)
            self.assertEqual(result["cumulative_prod_loc"], 4)
            self.assertEqual(result["binary_changes"], ["src/binary.rs"])
            direct = git("diff", "--numstat", "-M", base, end, "--", "src/lib.rs").split("\t")
            row = next(r for r in result["files"] if r["new_path"] == "src/lib.rs")
            self.assertEqual((row["raw_added"], row["raw_deleted"]), tuple(map(int, direct[:2])))
            with self.assertRaises(subprocess.CalledProcessError):
                footprint(repo, "missing-ref", end, metadata)
