
import re


def fiscal_quarter(quarter):
    year, month = map(int, quarter.split("-"))

    if month == 3:
        return f"Q4 FY{year % 100:02d}"

    q = {6: 1, 9: 2, 12: 3}[month]
    return f"Q{q} FY{(year + 1) % 100:02d}"


def parse_financial_pages(pages, quarter):
    target = fiscal_quarter(quarter)
    metrics = {}

    def save(name, value, page, quote):
        metrics[name] = {
            "value": float(value),
            "page": page,
            "quote": quote
        }

    # Extract current-quarter performance highlights.
    for p in pages:
        text = p["text"]

        if not re.search(
            rf"{target}\s+Performance Highlights",
            text,
            re.I
        ):
            continue

        revenue = re.search(
            r"INR Revenue of\s*₹?\s*([\d,]+)"
            r"\s*(Mn|Million|Crore|Cr)\b",
            text,
            re.I
        )

        if revenue:
            value = float(
                revenue.group(1).replace(",", "")
            )

            if revenue.group(2).lower() in (
                "mn", "million"
            ):
                value /= 10

            save(
                "revenue_from_operations",
                value,
                p["page"],
                revenue.group(0)
            )

        margin = re.search(
            r"Operating Margin\s+(?:at|of)\s*"
            r"([\d.]+)\s*%",
            text,
            re.I
        )

        if margin:
            save(
                "operating_margin",
                margin.group(1),
                p["page"],
                margin.group(0)
            )

    # Extract profit from consolidated quarterly tables.
    for p in pages:
        text = p["text"]

        if "Ind AS Income Statement" not in text:
            continue

        if not re.search(r"₹\s*Crore", text):
            continue

        quarters = re.findall(
            r"Q[1-4]\s+FY\s*\d{2}\b",
            text
        )

        quarters = [
            re.sub(r"\s+", " ", q)
            for q in quarters
        ]

        if target not in quarters:
            continue

        index = quarters.index(target)

        match = re.search(
            r"^Net Profit\s+(.+)$",
            text,
            re.I | re.M
        )

        if not match:
            continue

        # Handles values such as "1 3,718".
        values = re.findall(
            r"\d(?:\s*\d)*\s*,\s*\d{3}\b",
            match.group(1)
        )

        if len(values) != 3 or index >= 3:
            continue

        value = float(
            re.sub(r"[\s,]", "", values[index])
        )

        save(
            "net_profit",
            value,
            p["page"],
            match.group(0)
        )

    return metrics
