"""Mantém o app do Streamlit Community Cloud acordado.

Abre o app num navegador headless (uma sessão real, com websocket, é o que
conta como acesso) e, se ele estiver hibernando, clica no botão de despertar.
Executado pelo workflow .github/workflows/keep-alive.yml.
"""

import os
import sys

from playwright.sync_api import sync_playwright

APP_URL = os.environ.get("APP_URL", "https://prova-unicid.streamlit.app/")
BOTAO_DESPERTAR = "Yes, get this app back up"
MAX_TENTATIVAS = 60  # 60 × 5 s = 5 min


def _clicar_despertar(page) -> bool:
    # O botão pode estar no documento principal ou dentro de um iframe
    for frame in page.frames:
        botao = frame.get_by_role("button", name=BOTAO_DESPERTAR)
        if botao.count() > 0:
            botao.first.click()
            return True
    return False


def main() -> int:
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto(APP_URL, wait_until="domcontentloaded", timeout=60_000)
        page.wait_for_timeout(10_000)

        if _clicar_despertar(page):
            print("App estava hibernando — despertando...")
            page.wait_for_timeout(5_000)

        # Espera o app Streamlit renderizar (pode levar minutos no despertar)
        for _ in range(MAX_TENTATIVAS):
            if any(f.locator("[data-testid='stApp']").count() > 0 for f in page.frames):
                print("App no ar.")
                browser.close()
                return 0
            page.wait_for_timeout(5_000)

        page.screenshot(path="keep_alive_falha.png", full_page=True)
        print("O app não respondeu a tempo.", file=sys.stderr)
        browser.close()
    return 1


if __name__ == "__main__":
    sys.exit(main())
