"""Discover paired quarterly documents from Screener's TCS document section."""
import re
import hashlib
from pathlib import Path
from urllib.parse import urljoin, urlparse
import requests
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import pdfplumber

URL = 'https://www.screener.in/company/TCS/consolidated/'
MONTHS = {m:i for i,m in enumerate('Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec'.split(),1)}

def session():
    s = requests.Session()
    s.headers['User-Agent'] = 'TCSForecastResearch/1.0'
    s.mount('https://', HTTPAdapter(max_retries=Retry(total=2, backoff_factor=1, status_forcelist=[429,500,502,503,504])))
    return s


def quarter(label):
    """Convert an earnings-call month to a quarter end."""
    match = re.search(
        r"\b(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)"
        r"[a-z]*\s*['’ -]?\s*(20\d{2}|\d{2})\b",
        label,
        re.I
    )

    if not match:
        return None

    month = MONTHS[match[1].title()]
    year = int(match[2])

    if year < 100:
        year += 2000

    mapping = {
        1: 12,
        4: 3,
        7: 6,
        10: 9
    }

    if month not in mapping:
        return None

    if month == 1:
        year -= 1

    return f"{year:04d}-{mapping[month]:02d}"


def quarter_from_url(url):
    """Extract financial quarter from official TCS URLs."""
    match = re.search(
        r"/financial-statements/(20\d{2})-\d{2}/q([1-4])/",
        url,
        re.I
    )

    if not match:
        return None

    year = int(match[1])
    fiscal_quarter = int(match[2])

    mapping = {
        1: 6,
        2: 9,
        3: 12,
        4: 3
    }

    if fiscal_quarter == 4:
        year += 1

    return f"{year:04d}-{mapping[fiscal_quarter]:02d}"


def parse_documents(html):
    """Discover quarterly transcripts and financial fact sheets."""
    soup = BeautifulSoup(html, "html.parser")
    result = {}

    section = soup.select_one("#documents .concalls")

    if section is None:
        section = soup.select_one(".concalls")

    if section is None:
        return result

    for row in section.select("li"):
        date_element = row.find("div", recursive=False)

        if date_element is None:
            continue

        label = date_element.get_text(" ", strip=True)
        row_quarter = quarter(label)

        for link in row.select("a[href]"):
            text = link.get_text(" ", strip=True).lower()
            href = urljoin(URL, link["href"])

            if urlparse(href).scheme != "https":
                continue

            if ".pdf" not in href.lower():
                continue

            url_quarter = quarter_from_url(href)

            if text == "transcript":
                if not row_quarter:
                    continue

                # Reject official transcript URLs that refer
                # to a different quarter than the row.
                if url_quarter and url_quarter != row_quarter:
                    continue

                result.setdefault(
                    row_quarter, {}
                ).setdefault("transcript", href)

            elif text == "ppt":
                # Only accept identifiable official fact sheets.
                if not url_quarter:
                    continue

                normalized_url = href.lower().replace("%20", " ")

                if "fact sheet" not in normalized_url:
                    continue

                result.setdefault(
                    url_quarter, {}
                ).setdefault("report", href)

    return result


def discover(n):
    """Return the latest n complete quarterly document pairs."""
    if n < 1:
        raise ValueError("Number of quarters must be positive")

    response = session().get(URL, timeout=30)
    response.raise_for_status()

    docs = parse_documents(response.text)

    latest = sorted(docs, reverse=True)[:n]

    if len(latest) < n:
        raise RuntimeError(
            f"Expected {n} quarters, found {len(latest)}"
        )

    for q in latest:
        missing = {"report", "transcript"} - set(docs[q])

        if missing:
            raise RuntimeError(
                f"Quarter {q} is missing: {sorted(missing)}"
            )

    return [
        {"quarter": q, **docs[q]}
        for q in sorted(latest)
    ]

def pages(url):
    root = Path('data/cache'); root.mkdir(parents=True, exist_ok=True)
    path = root / (hashlib.sha256(url.encode()).hexdigest()+'.pdf')
    if not path.exists():
        with session().get(url, timeout=60, stream=True) as r:
            r.raise_for_status(); content = bytearray()
            for chunk in r.iter_content(65536):
                content.extend(chunk)
                if len(content)>30_000_000: raise ValueError('PDF too large')
        if not content.startswith(b'%PDF'): raise ValueError('Expected PDF')
        path.write_bytes(content)
    with pdfplumber.open(path) as pdf:
        out = [{'page':i,'text':p.extract_text(layout=False) or ''} for i,p in enumerate(pdf.pages,1)]
    if sum(len(p['text']) for p in out)<100: raise ValueError('PDF has insufficient text; OCR not implemented')
    return out
