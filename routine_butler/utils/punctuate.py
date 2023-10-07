# FIXME: Use spacy en-sm to or nltk pos-tagger to determine if a sentence's subject comes
# after the verb and should be considered a question: I.E. START -> VERB -> NOUN PHRASE

TOKEN_SWAPS = {
    "i'm": "I'm",
    "i'd": "I'd",
    "i'll": "I'll",
    "i've": "I've",
    "i": "I",
}

QUESTION_STARTERS = [
    "what",
    "when",
    "where",
    "why",
    "how",
    "who",
    "which",
    "whose",
    "does",
    "is",
    "are",
    "can",
    "could",
    "should",
    "would",
]


def apply_punctuation_rules(sentence: str) -> str:
    """Applies basic punction rules to a given sentence."""
    tokens = sentence.split()
    tokens = [TOKEN_SWAPS[t] if t in TOKEN_SWAPS else t for t in tokens]
    res = " ".join(tokens)
    if tokens[0].lower() in QUESTION_STARTERS:
        res += "?"
    else:
        res += "."
    return res[0].upper() + res[1:]
