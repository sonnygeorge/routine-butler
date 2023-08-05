import pytest

from routine_butler.plugins._flashcards.calculations import (
    THRESHOLD_PROB_MAX_ASYMPTOTE,
    THRESHOLD_PROB_MIN_ASYMPTOTE,
    binomial_cdf,
    binomial_pdf,
    find_binomial_distribution_threshold_value,
    get_n_to_cache,
    get_threshold_probability,
)


def test_threshold_probability_min_asymptote_at_one_million():
    assert get_threshold_probability(1_000_000) == pytest.approx(
        THRESHOLD_PROB_MIN_ASYMPTOTE, abs=1e-2
    )


def test_threshold_probability_max_asymptote_at_zero():
    assert get_threshold_probability(0) == pytest.approx(
        THRESHOLD_PROB_MAX_ASYMPTOTE, abs=1e-2
    )


PDF_CDF_TEST_CASES = [
    {
        "p": 0.5,
        "n_trials": 10,
        "n_successes": 0,
        "expected_pdf": 0.001,
        "expected_cdf": 0.001,
    },
    {
        "p": 0.5,
        "n_trials": 10,
        "n_successes": 7,
        "expected_pdf": 0.117,
        "expected_cdf": 0.945,
    },
]


@pytest.mark.parametrize("case", PDF_CDF_TEST_CASES)
def test_binomial_pdf(case: dict):
    calculated = binomial_pdf(case["n_successes"], case["n_trials"], case["p"])
    approx_expected = pytest.approx(case["expected_pdf"], abs=1e-3)
    assert calculated == approx_expected


@pytest.mark.parametrize("case", PDF_CDF_TEST_CASES)
def test_binomial_cdf(case: dict):
    calculated = binomial_cdf(case["n_successes"], case["n_trials"], case["p"])
    approx_expected = pytest.approx(case["expected_cdf"], abs=1e-3)
    assert calculated == approx_expected


THRESHOLD_VALUE_TEST_CASES = [
    {
        "n_trials": 10,
        "p": 0.5,
    },
    {
        "n_trials": 10,
        "p": 0.75,
    },
    {
        "n_trials": 5,
        "p": 0.5,
    },
    {
        "n_trials": 5,
        "p": 0.75,
    },
]


@pytest.mark.parametrize("case", THRESHOLD_VALUE_TEST_CASES)
def test_find_binomial_distribution_threshold_value_w_threshold_prob_of_zero(
    case: dict,
):
    n, p = case["n_trials"], case["p"]
    assert find_binomial_distribution_threshold_value(n, p, 0) == 0


@pytest.mark.parametrize("case", THRESHOLD_VALUE_TEST_CASES)
def test_find_binomial_distribution_threshold_value_w_threshold_prob_of_one(
    case: dict,
):
    n, p = case["n_trials"], case["p"]
    assert find_binomial_distribution_threshold_value(n, p, 1) == n


arbitrary_avg_seconds_per = 20
arbitrary_selection_prob = 0.5
arbitrary_n_collections = 10
arbitrary_target_minutes = 40


N_TO_CACHE_TEST_CASES = [
    {  # When selection_probability is one & target_seconds is target_minutes
        # * avg_seconds_per_card, n_to_cache should be target_minutes
        "avg_seconds_per_card": arbitrary_avg_seconds_per,
        "selection_probability": 1,
        "n_collections": arbitrary_n_collections,
        "target_seconds": arbitrary_avg_seconds_per * arbitrary_target_minutes,
        "expected_n_to_cache": arbitrary_target_minutes,
    },
    {  # When selection_probability is absolute zero, n_to_cache should be zero
        "avg_seconds_per_card": arbitrary_avg_seconds_per,
        "selection_probability": 0,
        "n_collections": arbitrary_n_collections,
        "target_seconds": arbitrary_avg_seconds_per * arbitrary_target_minutes,
        "expected_n_to_cache": 0,
    },
    {  # When selection_probability is almost zero, n_to_cache should be one
        "avg_seconds_per_card": arbitrary_avg_seconds_per,
        "selection_probability": 0.0001,
        "n_collections": 10,
        "target_seconds": arbitrary_avg_seconds_per * arbitrary_target_minutes,
        "expected_n_to_cache": 1,
    },
]


@pytest.mark.parametrize("case", N_TO_CACHE_TEST_CASES)
def test_get_n_to_cache(case: dict):
    class DummyCollection:
        avg_seconds_per_card = case["avg_seconds_per_card"]

    threshold_probabiliity = get_threshold_probability(case["n_collections"])

    calculated = get_n_to_cache(
        collection=DummyCollection(),
        selection_probability=case["selection_probability"],
        threshold_probability=threshold_probabiliity,
        target_seconds=case["target_seconds"],
    )
    assert calculated == case["expected_n_to_cache"]
