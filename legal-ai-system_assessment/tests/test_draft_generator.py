from src.draft_generator import DraftGenerator


def test_invalid_citation_detection() -> None:
    out = DraftGenerator._invalid_citations("Claim [doc:chunk:1] and [bad:chunk:9]", ["doc:chunk:1"])
    assert out == ["bad:chunk:9"]


def test_section_citation_detection() -> None:
    draft = (
        "1. Parties Involved\nHarvey [doc:chunk:0]\n"
        "2. Key Dates\nNo citation line\n"
        "3. Core Facts\nFact [doc:chunk:1]"
    )
    missing = DraftGenerator._sections_missing_citation(draft)
    assert missing == ["2. Key Dates"]
