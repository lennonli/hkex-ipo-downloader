import os
import time
import re
import urllib.parse
from datetime import datetime
from playwright.sync_api import sync_playwright

BASE_DIR = '/Users/licheng/Documents/港股IPO自动文档'
if not os.path.exists(BASE_DIR):
    os.makedirs(BASE_DIR)

def clean_filename(name):
    # Remove invalid path characters
    return re.sub(r'[\\/*?:"<>|]', "", name).strip()

def get_new_listings(page):
    print("Fetching new listings...")
    page.goto('https://www2.hkexnews.hk/New-Listings/New-Listing-Information/Main-Board?sc_lang=zh-HK')
    page.wait_for_selector('table.table-mobile-list')
    rows = page.locator('table.table-mobile-list tbody tr').all()
    
    companies = []
    for row in rows:
        cells = row.locator('div.mobile-list-body').all_inner_texts()
        if len(cells) >= 2:
            code = cells[0].strip()
            name = cells[1].strip().replace('\n', '')
            if code and name:
                 companies.append({'code': code, 'name': name})
    return companies

def get_today_str():
    return datetime.now().strftime('%Y%m%d')

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        # Using a context with a generous timeout and user-agent
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            accept_downloads=True
        )
        page = context.new_page()
        page.set_default_timeout(30000)

        companies = get_new_listings(page)
        print(f"Found {len(companies)} new listings.")

        for comp in companies:
            code = comp['code']
            name = comp['name']
            
            # Since listing date isn't directly in the table, we'll prefix with today's date as asked in the example
            # IF the folder already exists, we skip it
            folder_name = clean_filename(f"{get_today_str()}+{name}")
            folder_path = os.path.join(BASE_DIR, folder_name)

            # Let's check if there is an existing folder with the company name to avoid strictly relying on the exact date.
            # Example: check if any folder ends with `+name`
            existing_folders = [f for f in os.listdir(BASE_DIR) if os.path.isdir(os.path.join(BASE_DIR, f)) and f.endswith(f"+{name}")]
            
            if existing_folders:
                print(f"[{code} {name}] Folder already exists: {existing_folders[0]}. Skipping.")
                continue

            print(f"[{code} {name}] Processing. Folder will be: {folder_name}")

            # Collect all PDF URLs to download
            pdf_tasks = [] # list of dict {'url': url, 'title': title, 'is_prospectus': bool}

            categories = [
                {'value': '30700', 'name': '發售以供認購(招股章程)', 'is_prospectus': True},
                {'value': '56000', 'name': '展示文件', 'is_prospectus': False}
            ]

            for cat in categories:
                cat_val = cat['value']
                cat_name = cat['name']
                is_prospectus = cat['is_prospectus']

                try:
                    # Go to advanced search page
                    page.goto('https://www1.hkexnews.hk/search/titlesearch.xhtml?lang=zh')
                    
                    # Fill stock code
                    stock_input = page.locator('#searchStockCode')
                    stock_input.fill(code)
                    
                    # Wait for autocomplete (using a relatively short timeout as it may fail)
                    page.wait_for_selector('.autocomplete-suggestion', state='visible', timeout=10000)
                    page.locator('.autocomplete-suggestion').first.click()
                    
                    # Click category via JS evaluate
                    page.locator(f'.droplist-item[data-value="{cat_val}"] a').evaluate('node => node.click()')
                    
                    # Search
                    page.locator('.filter__btn-applyFilters-js').click()
                    
                    # Wait for results
                    page.wait_for_selector('.doc-link', timeout=10000)
                except Exception as e:
                    print(f"[{code} {name}] [{cat_name}] Error or no display documents found: {e}")
                    continue

                # Check if there are results
                doc_links = page.locator('.doc-link a').all()
                if not doc_links:
                    print(f"[{code} {name}] [{cat_name}] No display documents found.")
                    continue
                
                print(f"[{code} {name}] [{cat_name}] Found {len(doc_links)} result link(s). Processing...")
                
                for doc_a in doc_links:
                    href_attr = doc_a.get_attribute('href')
                    if not href_attr:
                        continue
                    
                    full_link = urllib.parse.urljoin(page.url, href_attr)
                    
                    if full_link.lower().endswith('.htm') or full_link.lower().endswith('.html'):
                        # This is an index page (e.g., "(多檔案)")
                        print(f"[{code} {name}] [{cat_name}] Opening index page: {full_link}")
                        
                        sub_page = context.new_page()
                        try:
                            sub_page.goto(full_link, wait_until='networkidle')
                            pdf_nodes = sub_page.locator('a[href$=".pdf"]').all()
                            for pdf_node in pdf_nodes:
                                pdf_href = pdf_node.get_attribute('href')
                                pdf_title = pdf_node.inner_text().strip()
                                if pdf_href:
                                    pdf_url = urllib.parse.urljoin(sub_page.url, pdf_href)
                                    pdf_tasks.append({'url': pdf_url, 'title': pdf_title, 'is_prospectus': is_prospectus, 'company_name': name})
                        except Exception as e:
                            print(f"[{code} {name}] [{cat_name}] Error crawling index page: {e}")
                        finally:
                            sub_page.close()
                    elif full_link.lower().endswith('.pdf'):
                        # Direct PDF link
                        pdf_title = doc_a.inner_text().strip()
                        pdf_tasks.append({'url': full_link, 'title': pdf_title, 'is_prospectus': is_prospectus, 'company_name': name})
                        
            if not pdf_tasks:
                print(f"[{code} {name}] No PDFs to download.")
                continue

            # Now we have results, so we create the folder
            if not os.path.exists(folder_path):
                os.makedirs(folder_path)

            # Now download all PDFs
            print(f"[{code} {name}] Found total {len(pdf_tasks)} PDF(s) to download.")
            for task in pdf_tasks:
                pdf_url = task['url']
                is_prospectus = task['is_prospectus']
                comp_name = task['company_name']
                
                if is_prospectus:
                    pdf_title_clean = clean_filename(f"{comp_name}招股说明书")
                else:
                    pdf_title_clean = clean_filename(task['title']) or "document_untitled"
                
                # Avoid overwriting if they have the same name
                save_path = os.path.join(folder_path, f"{pdf_title_clean}.pdf")
                counter = 1
                while os.path.exists(save_path):
                    save_path = os.path.join(folder_path, f"{pdf_title_clean}_{counter}.pdf")
                    counter += 1
                    
                print(f"  - Downloading: {os.path.basename(save_path)}")
                try:
                    resp = context.request.get(pdf_url)
                    if resp.ok:
                        with open(save_path, 'wb') as f:
                            f.write(resp.body())
                        print(f"    Saved: {save_path}")
                    else:
                        print(f"    Failed to download {pdf_url} (HTTP {resp.status})")
                except Exception as e:
                    print(f"    Error downloading {pdf_url}: {e}")

        browser.close()
        print("All done!")

if __name__ == '__main__':
    run()
