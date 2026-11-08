from playwright.async_api import async_playwright
from urllib.parse import urljoin
import asyncio

async def extract_text_and_links_from_page(page_url):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto(page_url, wait_until="networkidle", timeout=30000)

        text = await page.inner_text("body")
        text = "\n".join(line.strip() for line in text.splitlines() if line.strip())

        anchors = await page.eval_on_selector_all(
            "a[href]",
            "els => els.map(a => ({text: a.innerText.trim(), href: a.getAttribute('href')}))",
        )

        await browser.close()

    links, seen = [], set()
    for a in anchors:
        full_url = urljoin(page_url, a["href"])
        if full_url not in seen:
            seen.add(full_url)
            links.append({"text": a["text"], "url": full_url})

    return text, links


async def main():
    url = input("Enter a URL: ").strip()
    text, links = await extract_text_and_links_from_page(url)

    print("\n=== TEXT ===\n")
    print(text)

    print(f"\n=== LINKS ({len(links)}) ===\n")
    for link in links:
        print(f"{link['text'] or '[no text]'} -> {link['url']}")


if __name__ == "__main__":
    asyncio.run(main())