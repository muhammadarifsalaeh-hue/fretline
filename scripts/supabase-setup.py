#!/usr/bin/env python3
"""Review/prepare Fretline SQL. Default is offline; never apply without approval.

Only --check-connection performs GET metadata/health requests. It sends no SQL.
--apply is a separate, explicitly gated action for AFTER the owner's approval.
No database password, connection string, API token or raw HTTP error is printed.
"""
import argparse
from collections import Counter
import hashlib
import json
import os
from pathlib import Path
import re
import sys
import urllib.error
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
SOURCE_SHA256 = 'b824dfb085f5371d013b8168bf5b5fbd6e9b70e1672c65415980de8ba7bdda96'
REF_ENV = 'FRETLINE_SUPABASE_PROJECT_REF'
TOKEN_ENV = 'FRETLINE_SUPABASE_ACCESS_TOKEN'
TABLES = ['brands', 'admin_users', 'guitars', 'guitar_specifications',
          'guitar_prices', 'guitar_images', 'audit_logs', 'catalog_state']
DESTINATION = ROOT / '.local-preview/supabase/setup.atomic.sql'


class SafeError(Exception):
    """Messages must never contain remote response bodies or credential values."""


class SafeArgumentParser(argparse.ArgumentParser):
    def error(self, message):
        # argparse normally echoes unknown arguments, which could contain a
        # mistakenly pasted credential. Never repeat argument values.
        self.exit(2, '{"status":"stopped","message":"Invalid arguments. Use --help. Argument values hidden."}\n')


def inspect_files():
    raw = (ROOT / 'supabase/setup.sql').read_bytes()
    digest = hashlib.sha256(raw).hexdigest()
    if digest != SOURCE_SHA256:
        raise SafeError('SQL changed since review. Review the new file before preparing or executing it.')
    text = raw.decode('utf-8')
    migration = (ROOT / 'supabase/migrations/202610290001_admin_studio.sql').read_text()
    seed = (ROOT / 'supabase/seed.sql').read_text()
    if text != migration + '\n' + seed:
        raise SafeError('setup.sql does not match migration + seed.')
    marker = re.search(r'\$fretline_seed\$(.*?)\$fretline_seed\$::jsonb', seed, re.S)
    if not marker:
        raise SafeError('Seed payload not found.')
    data = json.loads(marker[1])
    rows = data['guitars']
    counts = Counter(row['brand'] for row in rows)
    ids = [row['id'] for row in rows]
    if len(rows) != 200 or len(set(ids)) != 200 or len(counts) != 10 or set(counts.values()) != {20}:
        raise SafeError('Expected 200 unique models / 10 brands x 20.')
    if any(not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', value) for value in ids):
        raise SafeError('Invalid seed IDs.')
    if len(data['brands']) != 10:
        raise SafeError('Invalid seed brand count.')
    prices = [row.get('price') for row in rows]
    if any(p is not None and (type(p) not in [int, float] or p <= 0) for p in prices):
        raise SafeError('An unknown or invalid price must not be represented by zero.')
    if 'on conflict(id) do nothing' not in seed or re.search(r'do\s+update', seed, re.I):
        raise SafeError('Seed conflict behavior changed; manual review required.')
    boundaries = [(i, line.strip().lower()) for i, line in enumerate(text.splitlines())
                  if re.fullmatch(r'(begin|commit|rollback);', line.strip(), re.I)]
    if [line for _, line in boundaries] != ['begin;', 'commit;', 'begin;', 'commit;']:
        raise SafeError('Unexpected transaction boundaries; do not remove them automatically.')
    report = {
        'source_file': 'supabase/setup.sql', 'source_sha256': digest, 'bytes': len(raw),
        'models': len(rows), 'unique_ids': len(set(ids)), 'brands': len(counts),
        'models_per_brand': dict(counts), 'priced': sum(p is not None for p in prices),
        'price_on_request': sum(p is None for p in prices), 'zero_prices': 0,
        'transaction_groups_in_original': 2, 'original_file_changed': False,
        'sql_executed': False, 'database_changed': False,
    }
    return text, boundaries, report


def atomic_sql(text, boundaries):
    # This is NOT a general SQL rewriter. It only accepts the checksum-pinned,
    # reviewed file whose four standalone boundaries are verified above.
    skip = {i for i, _ in boundaries}
    body = '\n'.join(line for i, line in enumerate(text.splitlines()) if i not in skip)
    tables = ','.join("'" + name + "'" for name in TABLES)
    guard = f"""do $fretline_fresh_guard$ begin
  if not pg_try_advisory_xact_lock(hashtextextended('fretline-initial-setup',0)) then
    raise exception 'Another Fretline setup is running';
  end if;
  if exists(select 1 from information_schema.tables where table_schema='public' and table_name in ({tables}))
    or exists(select 1 from storage.buckets where id='guitar-images') then
    raise exception 'Existing Fretline objects require separate review';
  end if;
end $fretline_fresh_guard$;
"""
    check = """do $fretline_verify$ begin
  if (select count(*) from public.guitars)<>200 or (select count(*) from public.brands)<>10
    or (select count(*) from public.guitars where (draft->>'price')::numeric>0)<>27
    or (select bool_and(n=20) from (select count(*) n from public.guitars group by brand_id) b) is distinct from true then
    raise exception 'Fretline import verification failed';
  end if;
end $fretline_verify$;
"""
    return ('-- Prepared offline from reviewed Fretline source ' + SOURCE_SHA256 + '\n'
            "begin;\nset local lock_timeout='5s';\nset local statement_timeout='120s';\n"
            + guard + body + '\n' + check + 'commit;\n')


def credentials():
    ref = os.environ.get(REF_ENV, '').strip()
    token = os.environ.get(TOKEN_ENV, '').strip()
    missing = [name for name, value in [(REF_ENV, ref), (TOKEN_ENV, token)] if not value]
    if missing:
        raise SafeError('Missing Codespaces environment settings: ' + ', '.join(missing)
                        + '. No request or SQL was sent.')
    if not re.fullmatch(r'[a-z]{20}', ref):
        raise SafeError('Invalid project reference. Use Project ID, not a URL or connection string.')
    if not token.startswith('sbp_') or any(c.isspace() for c in token):
        raise SafeError('Use a scoped Supabase personal access token stored in Codespaces Secrets; do not use a frontend/service key.')
    return ref, token


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise SafeError('Unexpected API redirect refused. Credentials were not forwarded.')


class ManagementAPI:
    def __init__(self, ref, token):
        self.ref = ref
        self.token = token
        self.opener = urllib.request.build_opener(NoRedirect())

    def request(self, suffix='', query=None):
        # HTTPS only, fixed origin, validated ref. Never log headers, raw response,
        # exceptions or project.database (which contains connection metadata).
        if suffix not in ['', '/health?services=db', '/database/query']:
            raise SafeError('Unsupported endpoint.')
        if (query is not None) != (suffix == '/database/query'):
            raise SafeError('SQL request mode mismatch.')
        body = json.dumps(query).encode('utf-8') if query is not None else None
        req = urllib.request.Request('https://api.supabase.com/v1/projects/' + self.ref + suffix,
                                     data=body, method='POST' if body is not None else 'GET',
                                     headers={'Authorization': 'Bearer ' + self.token,
                                              'Content-Type': 'application/json'})
        try:
            with self.opener.open(req, timeout=150 if body else 20) as response:
                return json.load(response)
        except urllib.error.HTTPError as error:
            raise SafeError(f'Management API returned HTTP {error.code}. Raw response hidden. Do not retry a setup automatically.') from None
        except (urllib.error.URLError, TimeoutError, OSError, ValueError):
            raise SafeError('API request failed or timed out. Response/connection details hidden. If setup was submitted, its outcome is unconfirmed; inspect before retrying.') from None

    def check_connection(self):
        project = self.request()
        if project.get('ref', project.get('id')) != self.ref or project.get('name', '').strip().casefold() != 'fretline':
            raise SafeError('Project identity does not match Fretline. No SQL sent.')
        health = self.request('/health?services=db')
        db = next((h for h in health if h.get('name') == 'db'), {})
        if db.get('status') != 'ACTIVE_HEALTHY':
            raise SafeError('Database health is not ACTIVE_HEALTHY. No SQL sent.')
        return {'project_name': 'Fretline', 'project_ref': self.ref,
                'database_health': 'ACTIVE_HEALTHY', 'method': 'HTTPS GET metadata/health',
                'sql_executed': False, 'database_changed': False,
                'database_write_permission_tested': False}


def apply(api, payload):
    # Only called AFTER CLI checks project+payload approval. Preflight is SQL and
    # therefore is deliberately not part of --check-connection.
    tables = ','.join("'" + name + "'" for name in TABLES)
    preflight = f"""select
      (select count(*) from information_schema.tables where table_schema='public' and table_name in ({tables})) as existing_app_tables,
      exists(select 1 from storage.buckets where id='guitar-images') as existing_app_bucket;"""
    state = api.request('/database/query', {'query': preflight, 'read_only': True})
    if not isinstance(state, list) or len(state) != 1:
        raise SafeError('Unexpected read-only preflight response. Setup was not submitted.')
    if state[0].get('existing_app_tables') != 0 or state[0].get('existing_app_bucket') is not False:
        raise SafeError('Existing Fretline tables/bucket detected. Setup was NOT submitted; review existing schema/data first.')
    api.request('/database/query', {'query': payload, 'read_only': False})
    verification = api.request('/database/query', {'query': "select (select count(*) from public.guitars) as models,(select count(*) from public.brands) as brands;", 'read_only': True})
    if not isinstance(verification, list) or len(verification) != 1 or verification[0] != {'models': 200, 'brands': 10}:
        raise SafeError('Setup may have committed, but final counts were not confirmed. Inspect; do not retry automatically.')
    return {'setup_submitted': True, 'models': 200, 'brands': 10,
            'admin_account_created': False, 'website_source_changed': False}


def main(argv=None):
    parser = SafeArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument('--check-connection', action='store_true', help='GET identity/health only; no SQL')
    mode.add_argument('--prepare', action='store_true', help='write ignored atomic payload locally; no SQL execution')
    mode.add_argument('--apply', action='store_true', help='AFTER approval only; guarded initial setup of an empty project')
    parser.add_argument('--approve-project')
    parser.add_argument('--approve-sha256')
    args = parser.parse_args(argv)
    try:
        text, boundaries, report = inspect_files()
        payload = atomic_sql(text, boundaries)
        payload_sha = hashlib.sha256(payload.encode()).hexdigest()
        report['atomic_sha256'] = payload_sha
        if args.apply:
            # Reject missing/stale approval BEFORE constructing a network client.
            ref, token = credentials()
            if args.approve_project != ref or args.approve_sha256 != payload_sha:
                raise SafeError('Approval must match the exact project reference and prepared payload SHA-256. No request or SQL sent.')
            api = ManagementAPI(ref, token)
            connection = api.check_connection()
            return print(json.dumps({**connection, **apply(api, payload), 'sql_executed': True, 'database_changed': True, 'database_write_permission_tested': True}, indent=2)) or 0
        if args.approve_project or args.approve_sha256:
            raise SafeError('Approval flags are only valid with --apply. No request or SQL sent.')
        if args.check_connection:
            ref, token = credentials()
            report['connection'] = ManagementAPI(ref, token).check_connection()
        if args.prepare:
            DESTINATION.parent.mkdir(parents=True, exist_ok=True)
            DESTINATION.write_text(payload)
            report['prepared_file'] = str(DESTINATION.relative_to(ROOT))
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return 0
    except SafeError as error:
        print(json.dumps({'status': 'stopped', 'message': str(error),
                          'database_state_not_assumed': True,
                          **({} if args.apply else {'sql_executed': False, 'database_changed': False})}, ensure_ascii=False), file=sys.stderr)
        return 2
    except Exception:
        # Fail closed without logging unexpected data, request bodies or secrets.
        print('{"status":"stopped","message":"Unexpected local validation error. Details hidden; no automatic retry."}', file=sys.stderr)
        return 2


if __name__ == '__main__':
    sys.exit(main())
