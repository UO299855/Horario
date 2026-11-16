from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    page = browser.new_page()

    for url in [
        "https://login.microsoftonline.com/",
        "https://www.office.com/",
        "https://m365.cloud.microsoft/"
    ]:
        try:
            response = page.goto(
                url,
                wait_until="domcontentloaded",
                timeout=30000
            )

            print(
                f"{url} -> "
                f"{response.status if response else 'No response'}"
            )

        except Exception as e:
            print(f"{url} -> ERROR: {e}")

    input("Pulsa ENTER para cerrar...")
    browser.close()