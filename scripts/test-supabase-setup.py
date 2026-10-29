"""Offline safeguards only: no SQL engine, database connection or real HTTP."""
import contextlib
import importlib.util
import io
import json
import os
from pathlib import Path
import unittest
from unittest.mock import patch
import urllib.error

spec = importlib.util.spec_from_file_location('setup_runner', Path(__file__).with_name('supabase-setup.py'))
runner = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runner)
REF = 'abcdefghijklmnopqrst'
TOKEN = 'sbp_LOCAL_TEST_VALUE_NEVER_PRINT'


class SetupSafeguards(unittest.TestCase):
    def setUp(self):
        self.no_network = patch('urllib.request.OpenerDirector.open', side_effect=AssertionError('Real HTTP forbidden in offline tests'))
        self.no_network.start()

    def tearDown(self):
        self.no_network.stop()

    def call(self, args):
        output = io.StringIO()
        with contextlib.redirect_stdout(output), contextlib.redirect_stderr(output):
            code = runner.main(args)
        self.assertNotIn(TOKEN, output.getvalue())
        self.assertNotIn('postgres://', output.getvalue())
        return code, output.getvalue()

    def test_default_inspects_only_and_preserves_catalog(self):
        code, output = self.call([])
        self.assertEqual(code, 0)
        data = json.loads(output)
        self.assertEqual((data['models'], data['brands'], data['priced'], data['price_on_request']), (200, 10, 27, 173))
        self.assertFalse(data['sql_executed'])
        self.assertFalse(data['database_changed'])

    def test_invalid_arguments_do_not_echo_sensitive_values(self):
        output = io.StringIO()
        with contextlib.redirect_stderr(output), self.assertRaises(SystemExit):
            runner.main(['--unknown-option', 'SENSITIVE_VALUE_MUST_NOT_APPEAR'])
        self.assertNotIn('SENSITIVE_VALUE_MUST_NOT_APPEAR', output.getvalue())

    def test_atomic_payload_has_one_outer_transaction(self):
        text, boundaries, _ = runner.inspect_files()
        atomic = runner.atomic_sql(text, boundaries)
        transaction_lines = [line for line in atomic.splitlines() if line in ['begin;', 'commit;']]
        self.assertEqual(transaction_lines, ['begin;', 'commit;'])
        self.assertIn('Existing Fretline objects require separate review', atomic)
        self.assertLess(atomic.index('Fretline import verification failed'), atomic.rindex('commit;'))

    def test_changed_source_fails_before_network(self):
        with patch.object(runner, 'SOURCE_SHA256', 'unreviewed'):
            code, output = self.call(['--check-connection'])
        self.assertEqual(code, 2)
        self.assertIn('changed since review', output)

    def test_missing_settings_do_not_connect(self):
        with patch.dict(os.environ, {}, clear=True):
            code, output = self.call(['--check-connection'])
        self.assertEqual(code, 2)
        self.assertIn('No request or SQL was sent', output)

    def test_invalid_reference_does_not_echo_connection_input(self):
        with patch.dict(os.environ, {runner.REF_ENV: 'postgres://DO_NOT_DISCLOSE', runner.TOKEN_ENV: TOKEN}):
            code, output = self.call(['--check-connection'])
        self.assertEqual(code, 2)
        self.assertNotIn('DO_NOT_DISCLOSE', output)

    def test_frontend_secret_and_service_keys_are_not_management_tokens(self):
        for token in ['sb_secret_LOCAL_TEST', 'sb_publishable_LOCAL_TEST', 'eyJLOCAL_TEST']:
            with patch.dict(os.environ, {runner.REF_ENV: REF, runner.TOKEN_ENV: token}):
                self.assertEqual(self.call(['--check-connection'])[0], 2)

    def test_apply_requires_exact_approval_before_network(self):
        with patch.dict(os.environ, {runner.REF_ENV: REF, runner.TOKEN_ENV: TOKEN}):
            for args in [['--apply'], ['--apply', '--approve-project', REF, '--approve-sha256', 'wrong']]:
                code, output = self.call(args)
                self.assertEqual(code, 2)
                self.assertIn('No request or SQL sent', output)

    def test_connection_check_is_metadata_only(self):
        api = runner.ManagementAPI(REF, TOKEN)
        calls = []
        def fake(suffix='', query=None):
            calls.append((suffix, query))
            return {'ref': REF, 'name': 'Fretline', 'database': {'password': 'DO_NOT_DISCLOSE'}} if not suffix else [{'name': 'db', 'status': 'ACTIVE_HEALTHY'}]
        api.request = fake
        result = api.check_connection()
        self.assertEqual(calls, [('', None), ('/health?services=db', None)])
        self.assertFalse(result['sql_executed'])
        self.assertNotIn('DO_NOT_DISCLOSE', json.dumps(result))

    def test_wrong_project_and_unhealthy_database_are_blocked(self):
        api = runner.ManagementAPI(REF, TOKEN)
        api.request = lambda *args: {'ref': REF, 'name': 'Other Project'}
        with self.assertRaises(runner.SafeError): api.check_connection()
        api.request = lambda suffix='': {'ref': REF, 'name': 'Fretline'} if not suffix else [{'name': 'db', 'status': 'UNHEALTHY'}]
        with self.assertRaises(runner.SafeError): api.check_connection()

    def test_existing_schema_blocks_setup_submission(self):
        class FakeAPI:
            def __init__(self): self.calls = []
            def request(self, endpoint, payload):
                self.calls.append(payload)
                return [{'existing_app_tables': 1, 'existing_app_bucket': False}]
        api = FakeAPI()
        with self.assertRaises(runner.SafeError): runner.apply(api, 'DO NOT EXECUTE')
        self.assertEqual(len(api.calls), 1)
        self.assertIs(api.calls[0]['read_only'], True)

    def test_http_failure_is_sanitized_and_never_retried(self):
        api = runner.ManagementAPI(REF, TOKEN)
        error = urllib.error.HTTPError('https://api.supabase.com', 403, TOKEN, {}, io.BytesIO(b'DO_NOT_DISCLOSE'))
        with patch.object(api.opener, 'open', side_effect=error) as request:
            with self.assertRaises(runner.SafeError) as caught: api.request()
        self.assertEqual(request.call_count, 1)
        self.assertNotIn(TOKEN, str(caught.exception))
        self.assertNotIn('DO_NOT_DISCLOSE', str(caught.exception))

    def test_redirect_and_unknown_endpoints_are_refused(self):
        with self.assertRaises(runner.SafeError): runner.NoRedirect().redirect_request(None, None, 302, '', {}, 'http://other-host.invalid')
        with self.assertRaises(runner.SafeError): runner.ManagementAPI(REF, TOKEN).request('/other')


if __name__ == '__main__':
    unittest.main(verbosity=2)
