import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
_spec = importlib.util.spec_from_file_location('skill_dispatch', ROOT/'profiles/hooks/dispatch.py')
dispatch = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(dispatch)


class SkillHookTests(unittest.TestCase):
    def test_upstream_ponytail_closure_matches_reviewed_hashes(self):
        profile = ROOT/'profiles/ponytail'
        manifest = json.loads((profile/'manifest.json').read_text())
        for path, expected in manifest['files_sha256'].items():
            self.assertEqual(dispatch.digest(profile/'assets'/path),expected,path)
        config = json.loads((profile/'native_hooks.json').read_text())
        self.assertEqual(set(config['hooks']),{'SessionStart','SubagentStart','UserPromptSubmit'})
        for groups in config['hooks'].values():
            for group in groups:
                for handler in group['hooks']:
                    self.assertTrue(handler['command'].startswith('python3 /opt/experiment-hooks/dispatch.py '))
                    self.assertIn(handler['command'].split()[-1],manifest['entrypoints'])

    def test_caveman_uses_pinned_upstream_communication_hook_and_complete_rules(self):
        profile = ROOT/'profiles/caveman'
        manifest = json.loads((profile/'manifest.json').read_text())
        self.assertEqual(manifest['commit'],'d262ab3882952a59312ff3537cd86d894523c5ab')
        for path, expected in manifest['files_sha256'].items():
            self.assertEqual(dispatch.digest(profile/'assets'/path),expected,path)
        hooks = json.loads((profile/'native_hooks.json').read_text())
        self.assertEqual(set(hooks['hooks']),{'SessionStart'})
        skill = (profile/'assets/skills/caveman/SKILL.md').read_text()
        self.assertIn('Clarity beats compression.',skill)
        self.assertIn('Anything persisted outside chat:',skill)

    def test_unreviewed_entrypoint_runtime_source_and_path_escape_fail_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)/'package';root.mkdir()
            node = Path(tmp)/'node';node.write_bytes(b'pinned runtime')
            source = root/'entry.js';source.write_bytes(b'reviewed source')
            manifest = {'node':{'sha256':dispatch.digest(node)},'entrypoints':['entry.js'],
                'files_sha256':{'entry.js':dispatch.digest(source)}}
            dispatch.verify_assets(root,node,manifest,'entry.js')
            with self.assertRaisesRegex(ValueError,'entrypoint'):
                dispatch.verify_assets(root,node,manifest,'unknown.js')
            source.write_bytes(b'changed source')
            with self.assertRaisesRegex(ValueError,'dependency'):
                dispatch.verify_assets(root,node,manifest,'entry.js')
            source.write_bytes(b'reviewed source');node.write_bytes(b'changed runtime')
            with self.assertRaisesRegex(ValueError,'runtime'):
                dispatch.verify_assets(root,node,manifest,'entry.js')
            manifest['node']['sha256']=dispatch.digest(node)
            manifest['files_sha256']={'../node':dispatch.digest(node)}
            with self.assertRaisesRegex(ValueError,'escapes'):
                dispatch.verify_assets(root,node,manifest,'entry.js')
