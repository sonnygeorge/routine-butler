"""calculations.py Calcuations for the flashcards plugin."""

from math import factorial
from typing import TYPE_CHECKING

import numpy as np

if TYPE_CHECKING:
    from routine_butler.plugins.flashcards import FlashcardCollection


# NOTE: Lower these for improved loading performance
THRESHOLD_PROB_MIN_ASYMPTOTE = 0.1
THRESHOLD_PROB_MAX_ASYMPTOTE = 0.9


def calculate_flashcard_selection_weight(
    mastery: int, appetite: int, has_bad_formatting: bool
) -> float:
    assert 0 <= mastery <= 10, "mastery must be between 0 and 10"
    assert 0 <= appetite <= 10, "appetite must be between 0 and 10"
    assert isinstance(
        has_bad_formatting, bool
    ), "has_bad_formatting must be a bool"

    m, a = mastery / 10, appetite / 10  # normalize to 0-1
    mastery_multiplier = np.arctan(-10 * m + 2.2) / (np.pi * m ** (-m))
    mastery_multiplier += 0.7 - 1.05 * m**10
    mastery_multiplier = max(mastery_multiplier, 0.25)
    appetite_multiplier = (2 * a) ** 2.8 + a + 0.5
    has_bad_formatting_multiplier = 0.05 if has_bad_formatting else 1
    weight = (
        mastery_multiplier
        * appetite_multiplier
        * has_bad_formatting_multiplier
    )
    return weight


def get_threshold_probability(n_collections: int) -> float:
    """Calculate the threshold probability for the binomial distribution
    that will be used to determine how many flashcards to cache for each
    collection.

    The function looks roughly like this:

    1   |
        |__                  ... (THRESHOLD_PROB_MAX_ASYMPTOTE)
    .75 |  `\   
        |    |
    .5  |    |
        |    |
    .25 |     \
        |      `------------ ... (THRESHOLD_PROB_MIN_ASYMPTOTE)
        |___________________
        0   5   10   15   20

    Parameters:
    n_collections (int): Number of collections to cache flashcards for.

    Returns:
    int: The threshold probability.
    """
    coeff = THRESHOLD_PROB_MAX_ASYMPTOTE - THRESHOLD_PROB_MIN_ASYMPTOTE
    exponent = 0 - (0.1 * n_collections) ** 2
    addend = THRESHOLD_PROB_MIN_ASYMPTOTE
    return coeff * 2.71828**exponent + addend


def binomial_pdf(x: int, n: int, p: float) -> float:
    """Calculate the probability density function for a binomial distribution
    with the given parameters.

    Parameters:
    x (int): The value to calculate the probability density function for.
    n (int): Number of trials.
    p (float): Probability of success in each trial.

    Returns:
    float: The probability density function for the given parameters.
    """
    return (
        (factorial(n) / (factorial(x) * factorial(n - x)))
        * (p**x)
        * ((1 - p) ** (n - x))
    )


def binomial_cdf(x: int, n: int, p: float) -> float:
    """Calculate the cumulative distribution function for a binomial distribution
    with the given parameters.

    Parameters:
    x (int): The value to calculate the cumulative distribution function for.
    n (int): Number of trials.
    p (float): Probability of success in each trial.

    Returns:
    float: The cumulative distribution function for the given parameters.
    """
    return sum(binomial_pdf(i, n, p) for i in range(x + 1))


def find_binomial_distribution_threshold_value(
    binomial_n: int, binomial_p: int, threshold_probability: int
) -> int:
    """
    Calculate the threshold value Y such that threshold_probability * 100 percent of the
    time, a randomaly sample from a binomial distribution with the given parameters will
    be below Y.

    Parameters:
    binomial_n (int): Number of trials.
    binomial_p (float): Probability of success in each trial.
    threshold_probability (float): The probability of a random sample being below Y.

    Returns:
    int: The threshold value Y for the given threshold_probability.
    """
    if threshold_probability < 0 or threshold_probability > 1:
        raise ValueError("threshold_probability must be between 0 and 1")

    threshold_value = None
    for y in range(binomial_n + 1):
        cumulative_prob = binomial_cdf(y, binomial_n, binomial_p)
        if cumulative_prob >= threshold_probability:
            threshold_value = y
            return threshold_value


def get_n_to_cache(
    collection: "FlashcardCollection",
    selection_probability: float,
    threshold_probability: int,
    target_seconds: int,
) -> int:
    """Calculate the number of flashcards to cache for a collection.

    Parameters:
    collection (FlashcardCollection): The collection to cache flashcards for.
    selection_probability (float): The probability of a collection being selected from a
        probabiliity distribution of collections.
    threshold_prob (float): The (rough) probability of the number selected from the
        collections probability distribution being below n_to_cache.
    target_minutes (int): The target number of minutes for the flashcard program.

    Returns:
    int: The number of flashcards to cache.
    """
    if selection_probability == 0:
        return 0
    bionomial_n = int(target_seconds / collection.avg_seconds_per_card)
    n_to_cache = find_binomial_distribution_threshold_value(
        binomial_n=bionomial_n,
        binomial_p=selection_probability,
        threshold_probability=threshold_probability,
    )
    return max(n_to_cache, 1)
