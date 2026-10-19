import copy
import io
from pathlib import Path
import tarfile
import tempfile
import unittest

from experiment.skill_trial import require_ready, assert_no_profile_artifacts, freeze_config
from experiment.runner import ROOT, setup_fingerprint


class SkillTrialTests(unittest.TestCase):
    def test_every_profile_must_activate_on_the_exact_verified_common_image(self):
        runtime={'image_id':'sha256:'+'a'*64,'rust_lsp_verified':True}
        activation={name:{'image_id':runtime['image_id'],'native_hook_activation_verified':True} for name in ('ponytail','caveman')}
        activation['serena']={'image_id':runtime['image_id'],'mcp_activation_verified':True,'observed_mcp_tool_calls':1}
        self.assertEqual(require_ready(runtime,activation),runtime['image_id'])
        for case in ('runtime','missing_profile','other_image','unverified_hook','serena_unused'):
            r=copy.deepcopy(runtime);a=copy.deepcopy(activation)
            if case=='runtime':r['rust_lsp_verified']=False
            elif case=='missing_profile':del a['serena']
            elif case=='other_image':a['ponytail']['image_id']='another image'
            elif case=='unverified_hook':a['caveman']['native_hook_activation_verified']=False
            else:a['serena']['observed_mcp_tool_calls']=0
            with self.subTest(case=case),self.assertRaises(ValueError):
                require_ready(r,a)

    def test_skill_cohort_adds_one_common_image_without_changing_phase2(self):
        import json
        base=json.loads((ROOT/'experiment.yaml').read_text());before=copy.deepcopy(base)
        runtime={'image_id':'sha256:'+'a'*64,'rust_lsp_verified':True}
        activation={name:{'image_id':runtime['image_id'],'native_hook_activation_verified':True} for name in ('ponytail','caveman')}
        activation['serena']={'image_id':runtime['image_id'],'mcp_activation_verified':True,'observed_mcp_tool_calls':1}
        # The real Serena report is created only after its activation smoke finishes.
        from unittest.mock import patch
        with patch.object(Path,'read_bytes',return_value=b'pinned fixture'):
            frozen=freeze_config(base,runtime,activation)
        self.assertEqual(base,before)
        self.assertEqual(frozen['benchmark']['skill_runtime_image_id'],runtime['image_id'])
        self.assertNotEqual(setup_fingerprint(base)[0],setup_fingerprint(frozen)[0])
        self.assertEqual(frozen['variants'],['baseline','ponytail','caveman','serena'])

    def test_profile_state_is_rejected_before_unchanged_grader_runs(self):
        for path in ('crates/lib.rs','crates/.serena/memories/notes.md','.codex/config.toml'):
            with tempfile.TemporaryDirectory() as tmp:
                snapshot=Path(tmp)/'snapshot.tar'
                with tarfile.open(snapshot,'w') as archive:
                    member=tarfile.TarInfo(path);member.size=1
                    archive.addfile(member,io.BytesIO(b'x'))
                if path=='crates/lib.rs':
                    assert_no_profile_artifacts(snapshot)
                else:
                    with self.assertRaisesRegex(ValueError,'grader snapshot'):
                        assert_no_profile_artifacts(snapshot)
