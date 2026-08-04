def test_health_endpoint(client):
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json()["status"] == "ok"


def test_assemble_context(client):
    res = client.post("/api/v1/context/assemble", json={
        "system_prompt": "sys",
        "user_input": "hello",
        "session_id": "test",
        "model_name": "m1",
        "max_tokens": 1000,
    })
    assert res.status_code == 200
    assert "final_context" in res.json()


def test_compress_context(client):
    res = client.post("/api/v1/context/compress", json={
        "text": "test",
        "target_tokens": 10,
    })
    assert res.status_code == 200


def test_store_memory(client):
    res = client.post("/api/v1/memory/test_sess", json={"role": "user", "content": "hi"})
    assert res.status_code == 200


def test_retrieve_memory(client):
    client.post("/api/v1/memory/test_sess2", json={"role": "user", "content": "hi"})
    res = client.get("/api/v1/memory/test_sess2")
    assert res.status_code == 200
    assert len(res.json()) > 0


def test_clear_memory(client):
    client.post("/api/v1/memory/test_sess3", json={"role": "user", "content": "hi"})
    client.delete("/api/v1/memory/test_sess3")
    res = client.get("/api/v1/memory/test_sess3")
    assert len(res.json()) == 0


def test_render_template(client):
    res = client.post("/api/v1/templates/render", json={
        "template_id": "default_system",
        "variables": {"system_prompt": "hello"},
    })
    assert res.status_code == 200


def test_list_templates(client):
    res = client.get("/api/v1/templates")
    assert res.status_code == 200


def test_budget_estimate(client):
    res = client.post("/api/v1/budget/estimate", json={
        "max_tokens": 1000,
        "system_prompt": "sys",
        "user_input": "user",
    })
    assert res.status_code == 200


def test_audit_events(client):
    client.get("/health")  # Random call
    res = client.get("/api/v1/audit/events")
    assert res.status_code == 200
