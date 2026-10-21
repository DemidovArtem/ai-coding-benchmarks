import unittest

from experiment.serena_continuous import verify_memory_boundary, verify_usage
from tests.test_serena_required import mcp


def call(tool, result='{}', **arguments):
    event=mcp(tool,result)
    event['item']['arguments']=arguments
    return event


class ContinuousSerenaTests(unittest.TestCase):
    def test_independent_trials_start_cold_and_previous_memory_survives_exactly(self):
        empty={'count':0,'files':{},'bytes':0}
        warm={'count':1,'files':{'orientation.md':{'sha256':'abc','bytes':3}},'bytes':3}
        verify_memory_boundary(empty,None)
        verify_memory_boundary(warm,warm)
        for before,previous in ((warm,None),(empty,warm),({**warm,'bytes':4},warm)):
            with self.assertRaises(ValueError):verify_memory_boundary(before,previous)

    def test_only_verified_dispatch_read_is_exempt_from_cold_start_order(self):
        read={'type':'item.completed','item':{'id':'dispatch','type':'command_execution'}}
        events=[read,call('initial_instructions'),call('onboarding'),
                call('get_symbols_overview','{"Function":["f"]}'),call('write_memory')]
        self.assertEqual(verify_usage(events,'dispatch',{'count':0})['memory_mode'],'cold')
        events.insert(2,{'type':'item.completed','item':{'id':'other','type':'command_execution'}})
        with self.assertRaises(ValueError):verify_usage(events,'dispatch',{'count':0})

    def test_warm_turn_reads_real_retained_memory_and_does_not_onboard_again(self):
        before={'count':1,'files':{'orientation.md':{'sha256':'abc','bytes':3}},'bytes':3}
        good=[call('initial_instructions'),call('read_memory',memory_name='orientation'),
              call('find_symbol','[{"name":"f"}]'),call('write_memory')]
        result=verify_usage(good,'dispatch',before)
        self.assertTrue(result['retained_memory_read_verified'])
        invalid=[good[:1]+good[2:],good[:1]+[call('read_memory',memory_name='other')]+good[2:],
                 good[:2]+[call('onboarding')]+good[2:],good[:2]+[call('find_symbol','[]')]+good[3:],
                 good[:3]+[{'type':'item.completed','item':{'type':'file_change'}}]+good[3:]]
        for events in invalid:
            with self.subTest(events=events),self.assertRaises(ValueError):verify_usage(events,'dispatch',before)
