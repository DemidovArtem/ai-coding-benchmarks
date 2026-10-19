from pathlib import Path
import tomllib
import unittest

import yaml

ROOT = Path(__file__).resolve().parents[1]


class SerenaProfileTests(unittest.TestCase):
    def test_only_local_stdio_mcp_without_dashboard_telemetry_or_paid_token_counter(self):
        config = tomllib.loads((ROOT/'profiles/serena/config.toml').read_text())
        self.assertEqual(set(config['mcp_servers']),{'serena'})
        self.assertFalse(config.get('hooks'))
        self.assertFalse(config.get('plugins'))
        self.assertTrue(all(value is False for value in config['features'].values()))
        server = config['mcp_servers']['serena']
        self.assertTrue(server['command'].startswith('/opt/experiment-serena/python/bin/'))
        args = server['args']
        for flag in ('--enable-web-dashboard','--open-web-dashboard','--enable-gui-log-window'):
            self.assertEqual(args[args.index(flag)+1],'false')
        self.assertEqual(args[args.index('--transport')+1],'stdio')
        self.assertEqual(args[args.index('--context')+1],'codex')
        self.assertIn('--project-from-cwd',args)
        self.assertEqual(server['env']['SERENA_USAGE_REPORTING'],'false')
        self.assertEqual(server['env']['SERENA_HOME'],'/home/fakeroot/.serena-profile')
        self.assertEqual(server['env']['PATH'].split(':')[0],'/usr/local/cargo/bin')
        self.assertEqual(server['env']['RUSTUP_HOME'],'/usr/local/rustup')
        self.assertEqual(server['env']['CARGO_HOME'],'/usr/local/cargo')
        self.assertEqual(server['env']['CARGO_NET_OFFLINE'],'true')
        settings = yaml.safe_load((ROOT/'profiles/serena/server_config.yml').read_text())
        self.assertEqual(settings['projects'],[])
        self.assertEqual(settings['token_count_estimator'],'CHAR_COUNT')
        self.assertTrue(settings['record_tool_usage'])
        self.assertFalse(settings['web_dashboard'])
