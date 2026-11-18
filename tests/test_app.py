import json, pathlib
from fastapi.testclient import TestClient
from app import app
c = TestClient(app)
cfg = json.loads(pathlib.Path('config.json').read_text())

def test_metrics():
    r = c.get('/metrics'); assert r.status_code == 200
    m = r.json()
    assert m['student_id'] == cfg['student_id']
    assert m['accuracy'] > 0.5 and m['training_rows'] >= 100

def test_predict():
    rec = {f: 0.0 for f in cfg['features']}
    r = c.post('/predict', json={'records': [rec]})
    assert r.status_code == 200 and len(r.json()['predictions']) == 1
