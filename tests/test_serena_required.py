import unittest

from experiment.serena_required import verify_required_usage


def mcp(tool,result='{}',status='completed'):
    return {'type':'item.completed','item':{'type':'mcp_tool_call','server':'serena','tool':tool,'status':status,'error':None,'result':{'content':[{'type':'text','text':result}]}}}


class RequiredSerenaTests(unittest.TestCase):
    def test_real_cold_semantic_usage_must_precede_shell_and_source_changes(self):
        good=[mcp('initial_instructions'),mcp('onboarding'),mcp('get_symbols_overview','{"Function":["example"]}'),mcp('write_memory'),{'type':'item.completed','item':{'type':'file_change'}}]
        self.assertTrue(verify_required_usage(good)['required_usage_verified'])
        cases=[[],good[1:],good[:1]+good[2:],good[:2]+[mcp('get_symbols_overview','{}')]+good[3:],good[:2]+[mcp('get_symbols_overview','{"Function":["example"]}','failed')]+good[3:],good[:2]+[{'type':'item.completed','item':{'type':'command_execution'}}]+good[2:],good[-1:]+good[:-1],good[:2]+[mcp('replace_symbol_body')]+good[2:],good[:2]+[mcp('get_symbols_overview','{"Function":[]}')]+good[3:]]
        for events in cases:
            with self.subTest(events=events),self.assertRaises(ValueError):verify_required_usage(events)
