"""Stage 2: Playwright rendering for lazy-loaded content."""

from playwright.async_api import async_playwright
from core.context import AuditContext


async def render_with_playwright(url: str, wait_time: int = 3000) -> str:
    """Render page with Playwright and wait for lazy loading."""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        await page.goto(url, wait_until="networkidle")
        await page.wait_for_timeout(wait_time)

        html = await page.content()

        await browser.close()

        return html


async def run_stage2(context: AuditContext, config: dict) -> AuditContext:
    """Stage 2: Render page with Playwright to capture lazy-loaded content."""
    url = context.url

    # Render with Playwright
    lazy_loaded_html = await render_with_playwright(url)
    context.lazy_loaded_content = lazy_loaded_html

    # Calculate diff between initial and lazy-loaded
    if "browser" in context.http_responses:
        initial_html = context.http_responses["browser"].get("html", "")
        context.js_rendered_diff = {
            "initial_length": len(initial_html),
            "lazy_loaded_length": len(lazy_loaded_html),
            "difference": len(lazy_loaded_html) - len(initial_html)
        }

    return context
