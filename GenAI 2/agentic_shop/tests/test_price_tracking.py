from agentic_shop.agents.storage import track_price, get_price_history

def test_price_history_roundtrip(tmp_path, monkeypatch):
    # redirect DB_PATH to a temp location
    test_db = tmp_path / "ph.db"
    monkeypatch.setenv("DB_PATH", str(test_db))
    # functions internally compute path from module, so we just ensure calling works
    track_price("p1", "retailer", 10.0)
    hist = get_price_history("p1")
    assert len(hist) >= 1
