import asyncio
from starlette.testclient import TestClient
from api.main import app
from api.main import RequestBodyLimitMiddleware, configured_cors_origins, configured_allowed_hosts

client = TestClient(app)

def test_health_discloses_no_live_ingestion():
    r=client.get('/api/health')
    assert r.status_code == 200
    assert r.json()['live_nasa_ingestion'] is False

def test_study_area_endpoint_returns_candidates_and_discloses_metadata_only():
    r = client.get('/api/study-areas')
    assert r.status_code == 200
    body = r.json()
    assert body['data_mode'] == 'archive_metadata_only'
    assert body['analysis_ready'] is False
    assert len(body['areas']) == 16
    assert sum(area['region'] == 'United States' for area in body['areas']) == 8
    assert sum(area['region'] == 'International' for area in body['areas']) == 8
    assert all(area['analysis_ready'] is False for area in body['areas'])
    assert all(area['metadata_acquisition_dates'] >= 90 for area in body['areas'])
    assert all(area['empirical_evidence'] for area in body['areas'])
    assert all(area['public_value_dimensions'] for area in body['areas'])
    assert all(area['validation_path'] for area in body['areas'])
    assert all(area['evidence_limit'] for area in body['areas'])
    assert 'does not establish QA-valid pixels' in body['disclaimer']

def test_cors_deployment_setting_requires_exact_origins(monkeypatch):
    monkeypatch.setenv('ATLAS_CORS_ORIGINS', 'https://atlas.example, https://staging.atlas.example/')
    assert configured_cors_origins() == ['https://atlas.example', 'https://staging.atlas.example']
    monkeypatch.setenv('ATLAS_CORS_ORIGINS', '*')
    try:
        configured_cors_origins()
    except RuntimeError as exc:
        assert 'non-wildcard' in str(exc)
    else:
        raise AssertionError('wildcard CORS must fail closed')

def test_temporal_aggregate_and_single_return_fixture_rows():
    single=client.post('/api/analyses',json={'method':'single'}).json()
    agg=client.post('/api/analyses',json={'method':'aggregate'}).json()
    assert single['asset_count']==12 and agg['asset_count']==12
    assert single['ranked_assets'][0]['observed_overlap_pct']==28.6
    assert agg['ranked_assets'][0]['observed_overlap_pct']==21.4
    assert 'not proof of damage' in single['warning']

def test_missing_coverage_filter_is_applied():
    r=client.post('/api/analyses',json={'min_coverage_pct':95})
    assert r.status_code==200 and r.json()['asset_count']==3

def test_invalid_percent_is_rejected():
    assert client.post('/api/analyses',json={'min_coverage_pct':101}).status_code==422

def test_unknown_remote_url_field_is_rejected():
    r=client.post('/api/analyses',json={'image_url':'http://127.0.0.1:9000/private'})
    assert r.status_code==422
    assert any(error['type']=='extra_forbidden' for error in r.json()['detail'])

def test_request_body_over_limit_is_rejected_before_json_parsing():
    r=client.post('/api/analyses',content=b' '* (16*1024+1),headers={'Content-Type':'application/json','Origin':'http://localhost:8000'})
    assert r.status_code==413
    assert r.headers['access-control-allow-origin']=='http://localhost:8000'

def test_streaming_request_body_limit_applies_without_content_length():
    async def downstream(scope, receive, send):
        await receive()
        await send({'type':'http.response.start','status':200,'headers':[]})
        await send({'type':'http.response.body','body':b'ok'})

    messages=[{'type':'http.request','body':b'12345','more_body':False}]
    sent=[]
    async def receive(): return messages.pop(0)
    async def send(message): sent.append(message)
    middleware=RequestBodyLimitMiddleware(downstream,max_bytes=4)
    scope={'type':'http','method':'POST','path':'/','headers':[]}
    asyncio.run(middleware(scope,receive,send))
    assert sent[0]['status']==413

def test_export_is_csv_and_discloses_fixture():
    r=client.post('/api/exports/csv',json={'method':'aggregate'})
    assert r.status_code==200 and 'text/csv' in r.headers['content-type']
    assert 'asset_id' in r.text and 'TX-001' in r.text


def test_second_scenario_has_distinct_synthetic_asset_ids():
    r=client.post('/api/analyses',json={'area_id':'baton_rouge_fixture'})
    assert r.status_code==200
    assert r.json()['ranked_assets'][0]['asset_id'].startswith('LA-')

def test_analysis_is_idempotent_for_identical_fixture_request():
    payload={'area_id':'houston_fixture','method':'aggregate','min_coverage_pct':50}
    first=client.post('/api/analyses',json=payload)
    second=client.post('/api/analyses',json=payload)
    assert first.status_code==second.status_code==200
    assert first.json()==second.json()


def test_invalid_json_is_rejected_with_422():
    r = client.post('/api/analyses', content=b'{invalid', headers={'Content-Type': 'application/json'})
    assert r.status_code == 422
    assert r.json()['detail'] == 'Invalid JSON body'


def test_deployed_host_setting_requires_exact_hosts(monkeypatch):
    monkeypatch.setenv('ATLAS_ALLOWED_HOSTS', 'api.example.com, api.staging.example.com')
    assert configured_allowed_hosts() == ['api.example.com', 'api.staging.example.com']
    monkeypatch.setenv('ATLAS_ALLOWED_HOSTS', '*')
    try:
        configured_allowed_hosts()
    except RuntimeError as exc:
        assert 'non-wildcard' in str(exc)
    else:
        raise AssertionError('wildcard host allowlists must fail closed')

def test_untrusted_host_is_rejected():
    r = client.get('/api/health', headers={'host': 'attacker.example'})
    assert r.status_code == 400
