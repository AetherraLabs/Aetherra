from Aetherra.consciousness.self_model import who_am_i


def test_who_am_i_contains_identity():
    ident = who_am_i()
    assert "Lyrixa" in ident
    assert "AI" in ident or "Collaborator" in ident
