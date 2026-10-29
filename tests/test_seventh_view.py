import copy
import unittest
from reports.plots.seventh_view import append_seventh
from reports.plots.extension_view import append_fourth
from tests.test_extension_view import fixtures
from reports.plots.seventh_curves import annotated_footer


def seven_rows():
    view, rows = fixtures()
    for step, task in ((5,'milestone_seed_8c6595c_1'),(6,'milestone_seed_a6e0be3_1_sub-01'),(7,'milestone_seed_292bc54_1')):
        row = copy.deepcopy(rows[-1])
        row.update(trial_id=f't{step}', ending_commit=f'c{step}', milestone_id=task, setup_fingerprint=f'extension{step}')
        row['continuous'].update(step=step, input_commit=f'c{step-1}')
        row['extension'].update(parent_trial=f't{step-1}',prefix_trials=[f't{s}' for s in range(1,step)])
        row['usage']['executor_cumulative'].update(output_tokens=100+40*(step-4),input_tokens=200+80*(step-4),cached_input_tokens=100+40*(step-4))
        row['grading_state']={'valid':True}
        rows.append(row)
    return view,rows


class SeventhViewTests(unittest.TestCase):
    def test_six_step_points_unchanged_and_seventh_not_new_prefix_repetitions(self):
        view,rows=seven_rows()
        old=append_fourth(view,rows[:-1])
        new=append_seventh(view,rows)
        self.assertEqual(new['points'][:-1],old['points'])
        self.assertEqual(new['extension_sources'][:-1],old['extension_sources'])
        self.assertEqual(new['points'][-1]['n_trajectories'],1)
        self.assertEqual(new['points'][-1]['metrics']['output_tokens']['mean'],220)

    def test_duplicate_and_changed_session_rejected(self):
        view,rows=seven_rows();duplicate=copy.deepcopy(rows[-1]);duplicate['trial_id']='duplicate'
        with self.assertRaises(ValueError):append_seventh(view,rows+[duplicate])
        rows[-1]['continuous']['executor_session_id']='other'
        with self.assertRaises(ValueError):append_seventh(view,rows)

    def test_unfinished_seventh_does_not_invent_point(self):
        view,rows=seven_rows();rows[-1]['sonar']['analysis_ok']=None
        self.assertEqual(append_seventh(view,rows)['points'],append_fourth(view,rows[:-1])['points'])


class SeventhFooterTests(unittest.TestCase):
    def test_seventh_note_requires_completed_observation_and_current_footer(self):
        text='Churn/Net values\nПравка 6: frozen'
        self.assertIn('Правка 7:',annotated_footer(text,True))
        self.assertEqual(annotated_footer(text,False),text)
        self.assertEqual(annotated_footer('Historical title',True),'Historical title')
