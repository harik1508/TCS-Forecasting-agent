import pytest

from app.discovery import (
    quarter,
    quarter_from_url,
    parse_documents,
    discover,
)


@pytest.mark.parametrize(
    "label, expected",
    [
        ("Apr 2026", "2026-03"),
        ("Jul 2026", "2026-06"),
        ("Oct 2026", "2026-09"),
        ("Jan 2027", "2026-12"),
        ("Jan 2026", "2025-12"),
        ("Invalid date", None),
    ],
)
def test_quarter(label, expected):
    """Verify earnings-call month to quarter-end mapping."""
    assert quarter(label) == expected


@pytest.mark.parametrize(
    "path, expected",
    [
        ("2025-26/q4/", "2026-03"),
        ("2026-27/q1/", "2026-06"),
        ("2026-27/q2/", "2026-09"),
        ("2026-27/q3/", "2026-12"),
    ],
)
def test_quarter_from_url(path, expected):
    """Verify Indian financial-year quarter conversion."""
    url = (
        "https://www.tcs.com/financial-statements/"
        + path
        + "Fact%20Sheet.pdf"
    )
    assert quarter_from_url(url) == expected


def test_pairs():
    """Verify discovery of a complete report-transcript pair."""

    html = """
    <section id="documents">
        <div class="concalls">
            <ul>
                <li>
                    <div>Oct 2026</div>
                    <a href="https://example.com/transcript.pdf">
                        Transcript
                    </a>
                    <a href="https://www.tcs.com/financial-statements/2026-27/q2/Presentations/Fact%20Sheet.pdf">
                        PPT
                    </a>
                </li>
            </ul>
        </div>
    </section>
    """

    result = parse_documents(html)

    assert "2026-09" in result
    assert set(result["2026-09"]) == {
        "report",
        "transcript",
    }


def test_split_document_rows():
    """Verify report and transcript links can be paired
    even when they appear in different HTML rows.
    """

    html = """
    <section id="documents">
        <div class="concalls">
            <ul>
                <li>
                    <div>Apr 2026</div>
                    <a href="https://example.com/transcript.pdf">
                        Transcript
                    </a>
                </li>
                <li>
                    <div>Mar 2026</div>
                    <a href="https://www.tcs.com/financial-statements/2025-26/q4/Presentations/Fact%20Sheet.pdf">
                        PPT
                    </a>
                </li>
            </ul>
        </div>
    </section>
    """

    result = parse_documents(html)

    assert set(result["2026-03"]) == {
        "report",
        "transcript",
    }


def test_mismatched_transcript():
    """Reject an old transcript incorrectly listed
    under a newer earnings-call date.
    """

    html = """
    <section id="documents">
        <div class="concalls">
            <ul>
                <li>
                    <div>Jul 2026</div>
                    <a href="https://www.tcs.com/financial-statements/2025-26/q1/transcript.pdf">
                        Transcript
                    </a>
                    <a href="https://www.tcs.com/financial-statements/2026-27/q1/Presentations/Fact%20Sheet.pdf">
                        PPT
                    </a>
                </li>
            </ul>
        </div>
    </section>
    """

    result = parse_documents(html)

    assert "report" in result["2026-06"]
    assert "transcript" not in result["2026-06"]


def test_empty_html():
    """Handle missing document sections safely."""
    assert parse_documents("<html></html>") == {}


def test_invalid_quarter_count():
    """Reject invalid quarter counts."""
    with pytest.raises(ValueError):
        discover(0)


def test_incomplete_document_pair(monkeypatch):
    """Fail safely when a required document is missing."""

    html = """
    <section id="documents">
        <div class="concalls">
            <ul>
                <li>
                    <div>Oct 2026</div>
                    <a href="https://example.com/transcript.pdf">
                        Transcript
                    </a>
                </li>
            </ul>
        </div>
    </section>
    """

    class MockResponse:
        text = html

        def raise_for_status(self):
            pass

    class MockSession:
        def get(self, *args, **kwargs):
            return MockResponse()

    monkeypatch.setattr(
        "app.discovery.session",
        lambda: MockSession(),
    )

    with pytest.raises(RuntimeError):
        discover(1)