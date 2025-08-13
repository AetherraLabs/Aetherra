from Aetherra.hub.federation import FederationManager


def test_federation_add_and_list_peers():
    fm = FederationManager(self_url="http://self:3001", peers=["http://p1:3001"])
    fm.add_peer("http://self:3001")  # should be ignored
    fm.add_peer("http://p2:3001")
    peers = {p["url"] for p in fm.list_peers()}
    assert "http://p1:3001" in peers
    assert "http://p2:3001" in peers
    assert "http://self:3001" not in peers
