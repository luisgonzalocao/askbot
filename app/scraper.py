from bs4 import BeautifulSoup
import asyncio
import logging
import random
import time

logger = logging.getLogger(__name__)


async def stealth_navigation(page):
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0"
    ]
    await page.set_extra_http_headers({
        'User-Agent': random.choice(user_agents),
        'Accept-Language': 'en-US,en;q=0.9',
        'Referer': 'https://www.google.com/'
    })

    # Bypass WebDriver detection
    await page.add_init_script("""
        delete Object.getPrototypeOf(navigator).webdriver;
        window.navigator.chrome = { runtime: {} };
        Object.defineProperty(navigator, 'languages', {
            get: () => ['en-US', 'en']
        });
        Object.defineProperty(navigator, 'plugins', {
            get: () => [1, 2, 3, 4, 5]
        });
    """)


async def human_like_interaction(page):

    # Random mouse movements
    viewport_size = page.viewport_size
    for _ in range(random.randint(2, 5)):
        x = random.randint(0, viewport_size['width'])
        y = random.randint(0, viewport_size['height'])
        await page.mouse.move(x, y)
        await asyncio.sleep(random.uniform(0.2, 1.0))

    # Randomize scroll
    scroll_steps = random.randint(3, 8)
    for _ in range(scroll_steps):
        scroll_amount = random.randint(200, 800)
        await page.mouse.wheel(0, scroll_amount)
        await asyncio.sleep(random.uniform(0.5, 2.0))


async def scrape_promptior():

    from playwright.async_api import async_playwright

    urls = [
        "https://www.promtior.ai/",
        "https://www.promtior.ai/service/",
        "https://www.promtior.ai/use-cases/",
        "https://www.promtior.ai/blog",
    ]

    all_content = []

    async with async_playwright() as p:
        # Stealth browser settings
        browser = await p.chromium.launch(
            headless=True,
            args=[
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-blink-features=AutomationControlled',
                '--disable-dev-shm-usage',
                '--disable-web-security',
                '--disable-features=IsolateOrigins,site-per-process',
                '--disable-ipc-flooding-protection',
                '--disable-background-timer-throttling',
                '--disable-backgrounding-occluded-windows',
                '--disable-renderer-backgrounding'
            ],
            timeout=180000
        )

        context = await browser.new_context(
            viewport={'width': 1366, 'height': 768},
            locale='en-US',
            timezone_id='America/New_York',
            color_scheme='light',
            bypass_csp=True
        )

        # Stealth global settings
        await stealth_navigation(context)

        for url in urls:
            page = None
            try:
                logger.info(f"Initializing scraping: {url}")
                start_time = time.time()

                page = await context.new_page()
                await stealth_navigation(page)

                page.set_default_timeout(90000)
                page.set_default_navigation_timeout(90000)

                max_retries = 3
                loaded = False

                for attempt in range(max_retries):
                    try:
                        # Randomize waiting times
                        await asyncio.sleep(random.uniform(1.0, 5.0))

                        # differents strategies navigation
                        wait_options = ["domcontentloaded", "load", "networkidle"]
                        await page.goto(
                            url,
                            timeout=60000,
                            wait_until=random.choice(wait_options),
                            referer="https://www.google.com/"
                        )

                        # Human interaction
                        await human_like_interaction(page)
                        await asyncio.sleep(random.uniform(2.0, 8.0))
                        loaded = True
                        break

                    except Exception as e:
                        logger.warning(f"Tried {attempt + 1} fail: {str(e)}")
                        if attempt == max_retries - 1:
                            raise
                        await asyncio.sleep(random.uniform(5.0, 15.0))

                if not loaded:
                    raise Exception("The page could not be loaded")

                html = await page.content()
                soup = BeautifulSoup(html, 'html.parser')

                content_selectors = [
                    {'name': 'main', 'type': 'tag'},
                    {'name': 'article', 'type': 'tag'},
                    {'name': 'div.content', 'type': 'css'},
                    {'name': 'div.container', 'type': 'css'},
                    {'name': 'body', 'type': 'tag'}
                ]

                main_content = None
                for selector in content_selectors:
                    try:
                        if selector['type'] == 'tag':
                            main_content = soup.find(selector['name'])
                        else:
                            main_content = soup.select_one(selector['name'])
                        if main_content:
                            break
                    except:
                        continue

                if not main_content:
                    raise Exception("No main content found")

                for element in main_content(['script', 'style', 'nav', 'footer',
                                           'iframe', 'form', 'svg', 'button',
                                           'img', 'figure', 'noscript']):
                    element.decompose()

                text_parts = []
                for tag in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'li']:
                    elements = main_content.find_all(tag)
                    for el in elements:
                        text = el.get_text(' ', strip=True)
                        if text and len(text.split()) > 1:
                            text_parts.append(text)

                content = '\n\n'.join(text_parts) if text_parts else main_content.get_text(' ', strip=True)

                if not content.strip():
                    raise Exception("Empty content after extraction")

                all_content.append({
                    'url': url,
                    'content': content[:20000],  # Limitar tamaño
                    'scrape_time': time.time() - start_time
                })

                logger.info(f"Scraping completed for {url} at {time.time() - start_time:.2f}s")

            except Exception as e:
                logger.error(f"Critical error in {url}: {str(e)}", exc_info=True)
                if url == urls[0]:
                    raise
                continue

            finally:
                if page:
                    await page.close()

        await browser.close()

    if not all_content:
        raise Exception("Could not get content from any URL")

    return all_content
