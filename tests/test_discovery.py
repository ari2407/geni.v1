from crypto_signals.discovery import CandidateGroup, group_candidates, select_candidates


def test_catalog_is_grouped_and_diverse():
    groups = group_candidates()
    assert groups[CandidateGroup.DATA]
    assert groups[CandidateGroup.ORCHESTRATION]
    selected = select_candidates()
    assert {item.group for item in selected} == set(CandidateGroup)


def test_untrusted_or_old_candidate_is_not_ranked_as_best_by_default():
    selected = select_candidates()
    assert selected[0].name == "CCXT"
