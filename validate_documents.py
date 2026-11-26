
from app.discovery import discover
from pathlib import Path
import hashlib
import pdfplumber

documents = discover(3)

for doc in documents:
    for kind in ["report", "transcript"]:

        url = doc[kind]
        filename = hashlib.sha256(url.encode()).hexdigest() + ".pdf"
        path = Path("data/cache") / filename

        print("\n" + "=" * 80)
        print("Quarter:", doc["quarter"])
        print("Document type:", kind)
        print("File:", path.name)

        if not path.exists():
            print("ERROR: File not found")
            continue

        with pdfplumber.open(path) as pdf:

            texts = [
                page.extract_text() or ""
                for page in pdf.pages
            ]

            full_text = "\n".join(texts)

            print("Total pages:", len(pdf.pages))
            print("Text characters:", len(full_text))
            print("Readable pages:", sum(bool(t.strip()) for t in texts))

            print("\nDOCUMENT PREVIEW:")
            print(full_text[:1500])

            if kind == "report":
                print("\nFINANCIAL KEYWORD CHECK:")

                keywords = [
                    "revenue",
                    "net profit",
                    "operating margin",
                    "operating income",
                    "net income"
                ]

                for keyword in keywords:
                    found = keyword in full_text.lower()
                    print(f"{keyword}: {found}")

print("\nDocument validation completed.")
