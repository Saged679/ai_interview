# ================== REQUIRED LIBRARIES ==================
# Install all dependencies using pip:

# Core parsing & data handling
# pip install beautifulsoup4
# pip install lxml

# PDF processing
# pip install pdfplumber

# Environment variables
# pip install python-dotenv

# Web automation (Selenium)
# pip install selenium
# ⚠️ Also install ChromeDriver manually (must match your Chrome version):
# https://chromedriver.chromium.org/downloads

# AI APIs
# pip install google-generativeai
# pip install groq

# Optional (recommended for stability)
# pip install requests
# pip install tqdm
# =======================================================



import os
import re
import json
import pickle
import shutil
import time
from datetime import datetime

import pdfplumber
from bs4 import BeautifulSoup as bs
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException

load_dotenv()

# ─────────────────────────────────────────────────────────────
#  CONFIG
# ─────────────────────────────────────────────────────────────
EMAIL       = os.getenv("EMAIL", "")
PASSWORD    = os.getenv("PASSWORD", "")
GEMINI_KEY  = os.getenv("GEMINI_API_KEY", "")
GROQ_KEY    = os.getenv("GROQ_API_KEY", "")

OUTPUT_DIR  = os.getenv("OUTPUT_DIR",  r"D:\python projects\grad_project_files")
DOWNLOADS   = os.getenv("DOWNLOADS_DIR", os.path.join(os.path.expanduser("~"), "Downloads"))

WAIT_TIMEOUT = 20   # seconds
COOKIES_FILE = "linkedin_cookies.pkl"

# ─────────────────────────────────────────────────────────────
#  DRIVER SETUP  (anti-bot options)
# ─────────────────────────────────────────────────────────────

def get_driver():
    """Create a Chrome driver that looks less like a bot."""
    options = Options()
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)
    options.add_argument("--start-maximized")
    options.add_argument("--disable-infobars")
    options.add_argument("--no-sandbox")

    driver = webdriver.Chrome(options=options)

    # Hide the navigator.webdriver flag LinkedIn detects
    driver.execute_script(
        "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
    )
    return driver


# ─────────────────────────────────────────────────────────────
#  COOKIE-BASED LOGIN
# ─────────────────────────────────────────────────────────────

def save_cookies(driver):
    with open(COOKIES_FILE, "wb") as f:
        pickle.dump(driver.get_cookies(), f)
    print("  ✅ Session cookies saved → next run will skip login.")


def load_cookies(driver):
    """Returns True if cookies loaded and session is still valid."""
    if not os.path.exists(COOKIES_FILE):
        return False
    driver.get("https://www.linkedin.com")
    with open(COOKIES_FILE, "rb") as f:
        for cookie in pickle.load(f):
            try:
                driver.add_cookie(cookie)
            except Exception:
                pass
    driver.refresh()
    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "global-nav"))
        )
        print("  ✅ Logged in via saved cookies.")
        return True
    except TimeoutException:
        print("  ⚠️  Cookies expired or invalid — falling back to manual login...")
        return False


def login(driver):
    """Try cookies first; fall back to username/password + manual CAPTCHA."""
    # ── 1. try saved session ───────────────────────────────────
    if load_cookies(driver):
        return True

    # ── 2. fresh login ─────────────────────────────────────────
    print("🔐 Logging in to LinkedIn...")
    driver.get("https://www.linkedin.com/login")
    driver.find_element(By.ID, "username").send_keys(EMAIL)
    driver.find_element(By.ID, "password").send_keys(PASSWORD)
    driver.find_element(By.XPATH, "//button[@type='submit']").click()

    print("⚠️  Check the browser — solve any CAPTCHA or 2FA now.")
    try:
        WebDriverWait(driver, 120).until(
            EC.presence_of_element_located((By.ID, "global-nav"))
        )
        save_cookies(driver)   # ← persist so next run skips this step
        print("  ✅ Login successful.")
        return True
    except Exception as e:
        print(f"  ❌ Login failed or timed out: {e}")
        return False


# ─────────────────────────────────────────────────────────────
#  HELPERS
# ─────────────────────────────────────────────────────────────

def wait_for(driver, by, selector, timeout=WAIT_TIMEOUT):
    try:
        return WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((by, selector))
        )
    except TimeoutException:
        return None

def scroll_into_view_and_click(driver, element, pause=0.5):
    driver.execute_script(
        "arguments[0].scrollIntoView({block: 'center', behavior: 'smooth'});",
        element
    )
    time.sleep(pause)
    driver.execute_script("arguments[0].click();", element)


def scroll_page(driver, times=15, step=300, pause=0.7):
    try:
        workspace = wait_for(driver, By.ID, "workspace", timeout=5)
        if workspace:
            for _ in range(times):
                driver.execute_script(
                    "arguments[0].scrollTop += arguments[1]", workspace, step
                )
                time.sleep(pause)
            driver.execute_script(
                "arguments[0].scrollTop = arguments[0].scrollHeight", workspace
            )
            time.sleep(1)
        else:
            for _ in range(times):
                driver.execute_script(f"window.scrollBy(0, {step})")
                time.sleep(pause)
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight)")
            time.sleep(1)
    except Exception as e:
        print(f"  [scroll_page] warning: {e}")


def get_soup(driver):
    return bs(driver.page_source, "html.parser")


def wait_for_clickable(driver, by, selector, timeout=WAIT_TIMEOUT):
    try:
        return WebDriverWait(driver, timeout).until(
            EC.element_to_be_clickable((by, selector))
        )
    except TimeoutException:
        return None


# ══════════════════════════════════════════════════════════════
#  NAVIGATE & SCRAPE
# ══════════════════════════════════════════════════════════════

def navigate_to_profile(driver, url):
    """Navigate and wait until the profile content is actually rendered."""
    print(f"🌐 Navigating to: {url}")
    driver.get(url)
    wait_for(driver, By.TAG_NAME, "main")
    try:
        WebDriverWait(driver, WAIT_TIMEOUT).until(
            EC.presence_of_element_located((By.TAG_NAME, "h2"))
        )
    except TimeoutException:
        pass
    time.sleep(3)


def scrape_profile_card(soup, url):
    try:
        main = soup.find("main")
        profile_card = (
            main
            .select_one("div > div > div > div > div > div")
            .find("section")
            .select_one("div > div > div")
            .next_sibling
            .select_one("div > div > div > div > div > div > div")
        )
        name     = profile_card.find("h2").text.strip()
        headline = profile_card.next_sibling.text.strip()
        location = profile_card.next_sibling.next_sibling.next_sibling.text.split("·")[0].strip()
        print(f"  ✅ Profile card → {name}")
        return {"Name": name, "URL": url, "Head Line": headline, "Personal Location": location}
    except Exception as e:
        print(f"  ⚠️  scrape_profile_card failed: {e}")
        return None


def scrape_about(soup):
    try:
        about_tag = soup.find("div", string="About")
        if about_tag is None:
            print("  ⚠️  About section → None (section not found)")
            return None
        about_text = about_tag.next_sibling.get_text(separator="\n").strip()
        print("  ✅ About section scraped.")
        return about_text
    except Exception as e:
        print(f"  ⚠️  scrape_about failed: {e}")
        return None


def scrape_experience(soup, driver):
    time.sleep(3)
    try:
        exp_lst = []

        def get_exp(exp, is_expanded=False):
            company_dec = {}
            local_rules_lst = []

            if exp.find_all('li'):
                exp_title = exp.find('div').find_all('p')
                name = exp_title[0].text.strip() if len(exp_title) > 0 else None
                duration = exp_title[1].text.strip() if len(exp_title) > 1 else None

                rules = exp.find('ul').find_all('li')
                for rule in rules:
                    rule_info_dec = {}
                    rule_tag = rule.find_all(recursive=False)[1].find_all(recursive=False)
                    rule_title = rule_tag[0].find_all('p') if len(rule_tag) > 0 else []
                    rule_desc  = rule_tag[1].find_all('p') if len(rule_tag) > 1 else []

                    rule_info_dec['Rule Name']        = rule_title[0].text.strip() if len(rule_title) > 0 else None
                    rule_info_dec['Rule Time']        = rule_title[1].text.strip() if len(rule_title) > 1 else None
                    rule_info_dec['Rule Destination'] = rule_title[2].text.strip() if len(rule_title) > 2 else None
                    rule_info_dec['Rule Description'] = rule_desc[0].text.strip()  if len(rule_desc)  > 0 else None
                    local_rules_lst.append(rule_info_dec)

                company_dec['Company Name']     = name
                company_dec['Company Duration'] = duration
                company_dec['Company Rules']    = local_rules_lst
            else:
                exp_tag = exp.find_all('p')
                company_dec['Rule Name']        = exp_tag[0].text.strip() if len(exp_tag) > 0 else None
                company_dec['Rule Duration']    = exp_tag[1].text.strip() if len(exp_tag) > 1 else None
                company_dec['Rule Time']        = exp_tag[2].text.strip() if len(exp_tag) > 2 else None
                company_dec['Rule Destination'] = exp_tag[3].text.strip() if len(exp_tag) > 3 else None
                company_dec['Rule Description'] = exp_tag[4].text.strip() if len(exp_tag) > 4 else None

            exp_lst.append(company_dec)

        experience_sec_title = soup.find('div', string='Experience')
        if experience_sec_title is None:
            print("  ⚠️  Experience section → None (section not found)")
            return None

        next_siblings  = experience_sec_title.find_next_siblings('div')
        show_all_button = next_siblings[1] if len(next_siblings) > 1 else None

        if show_all_button is not None:
            more_button = driver.find_element(By.XPATH, '//*[@id="workspace"]/div/div/div[1]/div/div/div[6]/div/div/div[1]/div/section/div/div[2]/div[3]')
            scroll_into_view_and_click(driver, more_button)
            more_button.click()
            time.sleep(10)

            exp_soup = bs(driver.page_source, 'html.parser')
            experience_sec_title = exp_soup.find('p', string='Experience')
            if experience_sec_title is None:
                print("  ⚠️  Experience section → None (expanded page title not found)")
                driver.back()
                return None

            experience_sec_title = experience_sec_title.parent.parent
            experience_sec = experience_sec_title.find_next_siblings('div')
            experience = experience_sec[1:] if experience_sec else []

            for exp in experience:
                get_exp(exp, is_expanded=True)

            time.sleep(3)
            driver.back()

        else:
            experience_sec = experience_sec_title.next_sibling
            experience = experience_sec.contents if experience_sec else []
            for exp in experience:
                get_exp(exp)

        print(f"  ✅ Experience section scraped. ({len(exp_lst)} entries)")
        return exp_lst

    except Exception as e:
        print(f"  ⚠️  scrape_experience failed: {e}")
        return None


def scrape_education(soup):
    print("  🔍 Scraping Education...")
    time.sleep(3)
    try:
        edu_title = soup.find("div", string="Education")
        if edu_title is None:
            print("  ⚠️  Education → None (section not found)")
            return None
        edu_sec   = edu_title.next_sibling
        edu_check = edu_sec.find_all("div", recursive=False)
        if len(edu_check) > 1:
            education = edu_check[0].find_all("div", recursive=False)[0].find_all("div", recursive=False)
        else:
            education = edu_check[0].find_all("div", recursive=False)

        edu_lst = []
        for edu in education:
            tags = edu.find_all("p")
            edu_lst.append({
                "Name of educational institution": tags[0].text.strip() if len(tags) > 0 else None,
                "Specialization"                 : tags[1].text.strip() if len(tags) > 1 else None,
                "The Duration"                   : tags[2].text.strip() if len(tags) > 2 else None,
                "Description"                    : tags[3].text.strip() if len(tags) > 3 else None,
            })
        print(f"  ✅ Education → {len(edu_lst)} entries")
        return edu_lst or None
    except Exception as e:
        print(f"  ⚠️  scrape_education failed: {e}")
        return None


def scrape_certifications(soup, driver):
    print("  🔍 Scraping Certifications...")
    time.sleep(3)
    try:
        crt_lst = []
        certification_sec_title = soup.find('div', string='Licenses & certifications')
        if certification_sec_title is None:
            print("  ⚠️  Certifications section → None (section not found)")
            return None

        show_all_button = None
        next_sibling = certification_sec_title.next_sibling
        if next_sibling:
            divs = next_sibling.find_all('div', recursive=False)
            if len(divs) > 1:
                show_all_button = divs[1]

        if show_all_button is not None:
            more_button = driver.find_element(By.XPATH, '//*[@id="workspace"]/div/div/div[1]/div/div/div[6]/div/div/div[3]/div/section/div/div/div[2]/div[2]')
            scroll_into_view_and_click(driver, more_button)
            more_button.click()
            time.sleep(10)

            crt_soup = bs(driver.page_source, 'html.parser')
            certification_sec_title = crt_soup.find('p', string='Licenses & certifications')
            if certification_sec_title is None:
                print("  ⚠️  Certifications section → None (expanded page title not found)")
                driver.back()
                return None

            certification_sec_title = certification_sec_title.parent.parent
            certification_sec = certification_sec_title.next_sibling
            certification = certification_sec.find_all('div', recursive=False) if certification_sec else []

            def get_cert(crt_num):
                crt_dec = {}
                crt_info_tag = certification[crt_num].find_all('p')
                crt_dec['Certification Title'] = crt_info_tag[0].text.strip() if len(crt_info_tag) > 0 else None
                crt_dec['Company Name']         = crt_info_tag[1].text.strip() if len(crt_info_tag) > 1 else None
                crt_dec['Issued Date']          = crt_info_tag[2].text.strip() if len(crt_info_tag) > 2 else None
                crt_lst.append(crt_dec)

            for crt in range(len(certification)):
                get_cert(crt)

            time.sleep(5)
            driver.back()

        else:
            certification_sec = certification_sec_title.next_sibling
            certification = (
                certification_sec.find_all('div', recursive=False)[0].find_all('div', recursive=False)
                if certification_sec else []
            )

            def get_cert(crt_num):
                crt_dec = {}
                crt_info_tag = certification[crt_num].find_all('p')
                crt_dec['Certification Title'] = crt_info_tag[0].text.strip() if len(crt_info_tag) > 0 else None
                crt_dec['Company Name']         = crt_info_tag[1].text.strip() if len(crt_info_tag) > 1 else None
                crt_dec['Issued Date']          = crt_info_tag[2].text.strip() if len(crt_info_tag) > 2 else None
                crt_lst.append(crt_dec)

            for crt in range(len(certification)):
                get_cert(crt)

        print(f"  ✅ Certifications scraped. ({len(crt_lst)} entries)")
        return crt_lst

    except Exception as e:
        print(f"  ⚠️  scrape_certifications failed: {e}")
        return None


def scrape_projects(soup, driver):
    print("  🔍 Scraping Projects...")
    time.sleep(3)
    try:
        prj_lst = []
        projects_sec_title = soup.find('div', string='Projects')
        if projects_sec_title is None:
            print("  ⚠️  Projects section → None (section not found)")
            return None

        show_all_button = None
        next_sibling = projects_sec_title.next_sibling
        if next_sibling:
            divs = next_sibling.find_all('div', recursive=False)
            if len(divs) > 1:
                show_all_button = divs[1]

        if show_all_button is not None:
            more_button = driver.find_element(By.XPATH, '//*[@id="workspace"]/div/div/div[1]/div/div/div[6]/div/div/div[4]/div/section/div/div[2]/div[2]')
            scroll_into_view_and_click(driver, more_button)
            more_button.click()
            time.sleep(8)

            prj_soup = bs(driver.page_source, 'html.parser')
            projects_sec_title = prj_soup.find('p', string='Projects')
            if projects_sec_title is None:
                print("  ⚠️  Projects section → None (expanded page title not found)")
                driver.back()
                return None

            projects_sec_title = projects_sec_title.parent.parent
            projects_sec = projects_sec_title.next_sibling
            project = projects_sec.find_all('div', recursive=False) if projects_sec else []

            def get_prj(prj_num):
                prj_dec = {}
                prj_info_tag = project[prj_num].find_all('p')
                prj_dec['Project Title']       = prj_info_tag[0].text.strip() if len(prj_info_tag) > 0 else None
                prj_dec['Project Date']        = prj_info_tag[1].text.strip() if len(prj_info_tag) > 1 else None
                prj_dec['Project Description'] = prj_info_tag[2].text.strip() if len(prj_info_tag) > 2 else None
                prj_lst.append(prj_dec)

            for prj in range(len(project)):
                get_prj(prj)

            time.sleep(5)
            driver.back()

        else:
            projects_sec = projects_sec_title.next_sibling
            project = (
                projects_sec.select_one('div > div > div > div').find_all('div', recursive=False)
                if projects_sec else []
            )

            def get_prj(prj_num):
                prj_dec = {}
                prj_info_tag = project[prj_num].find_all('p')
                prj_dec['Project Title']       = prj_info_tag[0].text.strip() if len(prj_info_tag) > 0 else None
                prj_dec['Project Date']        = prj_info_tag[1].text.strip() if len(prj_info_tag) > 1 else None
                prj_dec['Project Description'] = prj_info_tag[2].text.strip() if len(prj_info_tag) > 2 else None
                prj_lst.append(prj_dec)

            for prj in range(len(project)):
                get_prj(prj)

        print(f"  ✅ Projects scraped. ({len(prj_lst)} entries)")
        return prj_lst

    except Exception as e:
        print(f"  ⚠️  scrape_projects failed: {e}")
        return None


def scrape_skills(soup, driver):
    print("  🔍 Scraping Skills...")
    time.sleep(3)
    try:
        skl_lst = []
        skills_sec_title = soup.find('div', string='Skills')
        if skills_sec_title is None:
            print("  ⚠️  Skills section → None (section not found)")
            return None

        show_all_button = None
        next_sibling = skills_sec_title.next_sibling
        if next_sibling:
            divs = next_sibling.find_all('div', recursive=False)
            if len(divs) > 1:
                show_all_button = divs[1]

        if show_all_button is not None:
            more_button = driver.find_element(By.XPATH, '//*[@id="workspace"]/div/div/div[1]/div/div/div[6]/div/div/div[6]/div/section/div/div/div[2]/div[2]')
            scroll_into_view_and_click(driver, more_button)
            more_button.click()
            time.sleep(4)

            scrollable_div = driver.find_element(By.XPATH, '//*[@id="workspace"]')
            for _ in range(11):
                driver.execute_script("arguments[0].scrollTop += 220", scrollable_div)
                time.sleep(2)

            skl_soup = bs(driver.page_source, 'html.parser')
            skills_sec_title = skl_soup.find('p', string='Skills')
            if skills_sec_title is None:
                print("  ⚠️  Skills section → None (expanded page title not found)")
                driver.back()
                return None

            skills_sec_title = skills_sec_title.parent.parent.parent
            skills_sec = skills_sec_title.next_sibling
            skills_tag = skills_sec.find_all('div', recursive=False) if skills_sec else []

            skills = []
            for i in range(len(skills_tag) - 1):
                skills_i = skills_sec.find_all('div', recursive=False)[i + 1].find_all('div', recursive=False)
                skills_i = [num for idx, num in enumerate(skills_i) if idx % 2 == 0]
                skills.extend(skills_i)

            def get_skl(skl_num):
                skill_name = skills[skl_num].find_all('p')[0].text.strip()
                skl_lst.append(skill_name)

            for skl in range(len(skills)):
                get_skl(skl)

            time.sleep(5)
            driver.back()

        else:
            skills_sec = skills_sec_title.next_sibling
            skills = (
                skills_sec.select_one('div > div').find_all('div', recursive=False)
                if skills_sec else []
            )
            skills = [num for idx, num in enumerate(skills) if idx % 2 == 0]

            def get_skl(skl_num):
                skill_name = skills[skl_num].find_all('p')[0].text.strip()
                skl_lst.append(skill_name)

            for skl in range(len(skills)):
                get_skl(skl)

        print(f"  ✅ Skills scraped. ({len(skl_lst)} entries)")
        return skl_lst

    except Exception as e:
        print(f"  ⚠️  scrape_skills failed: {e}")
        return None


def scrape_languages(soup):
    print("  🔍 Scraping Languages...")
    try:
        lang_title = soup.find("div", string="Languages")
        if lang_title is None:
            print("  ⚠️  Languages → None (section not found)")
            return None
        lang_sec = (
            lang_title.next_sibling
            .find_all("div", recursive=False)[0]
            .find_all("div", recursive=False)
        )
        lang_lst = [lang.find_all("p")[0].text.strip() for lang in lang_sec]
        print(f"  ✅ Languages → {lang_lst}")
        return lang_lst or None
    except Exception as e:
        print(f"  ⚠️  scrape_languages failed: {e}")
        return None


# ══════════════════════════════════════════════════════════════
#  PDF SAVE
# ══════════════════════════════════════════════════════════════

def save_pdf(driver, profile_name):
    print("  📄 Saving LinkedIn PDF...")
    try:
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        more_btn = wait_for_clickable(
            driver, By.XPATH,
            '//*[@id="root"]/div[2]/div[2]/div[2]/div/div/div/div/div/div/div/div[1]/button'
        )
        if more_btn:
            more_btn.click()
        pdf_btn = wait_for_clickable(driver, By.XPATH, "//*[contains(text(),'Save to PDF')]")
        if pdf_btn:
            pdf_btn.click()

        snapshot_before = set(os.listdir(DOWNLOADS))
        deadline = time.time() + 30
        latest = None
        while time.time() < deadline:
            time.sleep(1)
            current  = set(os.listdir(DOWNLOADS))
            new_files = current - snapshot_before
            pdf_files = [f for f in new_files if f.lower().endswith(".pdf")]
            if pdf_files:
                latest = os.path.join(DOWNLOADS, pdf_files[0])
                break

        if latest is None:
            files = [os.path.join(DOWNLOADS, f) for f in os.listdir(DOWNLOADS)]
            if files:
                latest = max(files, key=os.path.getctime)

        if latest is None:
            print("  ⚠️  save_pdf: no file found in Downloads")
            return None

        new_name = os.path.join(DOWNLOADS, f"{profile_name}_profile_data.pdf")
        os.rename(latest, new_name)
        dest = shutil.move(new_name, OUTPUT_DIR)
        print(f"  ✅ PDF saved → {dest}")
        return dest
    except Exception as e:
        print(f"  ⚠️  save_pdf failed: {e}")
        return None


# ══════════════════════════════════════════════════════════════
#  JSON & TXT SAVE
# ══════════════════════════════════════════════════════════════

def save_json(profile_data, name):
    try:
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        path = os.path.join(OUTPUT_DIR, f"{name}_profile_data.json")
        with open(path, "w", encoding="utf-8") as f:
            json.dump(profile_data, f, indent=4, ensure_ascii=False)
        print(f"  ✅ JSON saved → {path}")
        return path
    except Exception as e:
        print(f"  ⚠️  save_json failed: {e}")
        return None


def _section(title):
    w = 60
    return f"\n{'='*w}\n  {title.upper()}\n{'='*w}\n"

def _div():
    return "-" * 50 + "\n"

def _val(v):
    return str(v) if v is not None else "None"


def profile_to_text(profile):
    lines = []
    lines.append(_section("Profile"))
    lines.append(f"Name       : {_val(profile.get('Name'))}\n")
    lines.append(f"Headline   : {_val(profile.get('Head Line'))}\n")
    lines.append(f"Location   : {_val(profile.get('Personal Location'))}\n")
    lines.append(f"LinkedIn   : {_val(profile.get('URL'))}\n")

    lines.append(_section("About"))
    lines.append(f"{_val(profile.get('About'))}\n")

    lines.append(_section("Experience"))
    exp = profile.get("Experience")
    if not exp:
        lines.append("None\n")
    else:
        for idx, entry in enumerate(exp):
            if idx > 0:
                lines.append(_div())
            if "Company Name" in entry:
                lines.append(f"Company  : {_val(entry.get('Company Name'))}\n")
                lines.append(f"Duration : {_val(entry.get('Company Duration'))}\n")
                for role in entry.get("Company Rules", []):
                    lines.append(f"    • {_val(role.get('Rule Name'))}\n")
                    lines.append(f"      Time        : {_val(role.get('Rule Time'))}\n")
                    lines.append(f"      Location    : {_val(role.get('Rule Destination'))}\n")
                    lines.append(f"      Description : {_val(role.get('Rule Description'))}\n")
            else:
                lines.append(f"Role     : {_val(entry.get('Rule Name'))}\n")
                lines.append(f"Duration : {_val(entry.get('Rule Duration'))}\n")
                lines.append(f"Time     : {_val(entry.get('Rule Time'))}\n")
                lines.append(f"Location : {_val(entry.get('Rule Destination'))}\n")
                lines.append(f"Desc.    : {_val(entry.get('Rule Description'))}\n")

    lines.append(_section("Education"))
    edu = profile.get("Education")
    if not edu:
        lines.append("None\n")
    else:
        for e in edu:
            lines.append(f"Institution    : {_val(e.get('Name of educational institution'))}\n")
            lines.append(f"Specialization : {_val(e.get('Specialization'))}\n")
            lines.append(f"Duration       : {_val(e.get('The Duration'))}\n")
            lines.append(f"Description    : {_val(e.get('Description'))}\n")

    lines.append(_section("Certifications"))
    certs = profile.get("Certification")
    if not certs:
        lines.append("None\n")
    else:
        for i, c in enumerate(certs, 1):
            lines.append(f"  {i}. {_val(c.get('Certification Title'))}\n")
            lines.append(f"     Issuer : {_val(c.get('Company Name'))}\n")
            lines.append(f"     Date   : {_val(c.get('Issued Date'))}\n")

    lines.append(_section("Projects"))
    projects = profile.get("Projects")
    if not projects:
        lines.append("None\n")
    else:
        for i, p in enumerate(projects, 1):
            lines.append(f"  {i}. {_val(p.get('Project Title'))}\n")
            lines.append(f"     Date        : {_val(p.get('Project Date'))}\n")
            lines.append(f"     Description : {_val(p.get('Project Description'))}\n")

    lines.append(_section("Skills"))
    skills = profile.get("Skills")
    if not skills:
        lines.append("None\n")
    else:
        for s in skills:
            lines.append(f"  • {s}\n")

    lines.append(_section("Languages"))
    langs = profile.get("Languages")
    if not langs:
        lines.append("None\n")
    else:
        for l in langs:
            lines.append(f"  • {l}\n")

    return "".join(lines)


def save_txt(profile_data, name):
    try:
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        path = os.path.join(OUTPUT_DIR, f"{name}_profile_data.txt")
        with open(path, "w", encoding="utf-8") as f:
            f.write(profile_to_text(profile_data))
        print(f"  ✅ TXT saved → {path}")
        return path
    except Exception as e:
        print(f"  ⚠️  save_txt failed: {e}")
        return None


# ══════════════════════════════════════════════════════════════
#  AI SCORING
# ══════════════════════════════════════════════════════════════

SCORE_PROMPT = """
You are a strict, honest AI HR expert evaluating a LinkedIn profile.

IMPORTANT:
- Today's date is: {today}
- Evaluate all experience, roles, and durations relative to this date.
- Do NOT assume future roles or ongoing roles beyond this date.

TASK:
Evaluate this LinkedIn profile and return a WORK READINESS SCORE.

SCORING RULES (be strict and realistic — most profiles score 2–3.5):
- Score range: 0 to 5
- Allowed values ONLY: 0, 0.5, 1, 1.5, 2, 2.5, 3, 3.5, 4, 4.5, 5
- Do NOT give 5/5 unless the profile is exceptional (senior, published, multiple jobs)
- Student or intern profiles rarely exceed 3.5
- Missing sections (languages, open source, volunteer) reduce score
- Vague project descriptions (e.g., "Associated with X") reduce score significantly
- Score ONLY based on what is ACTUALLY in the profile — do NOT assume or invent information

EVALUATION CRITERIA:
1. Technical Skills (are they diverse, deep, and proven?)
2. Real Projects (are they detailed with measurable results?)
3. Experience (internships/jobs — duration and impact)
4. Impact (are there numbers, metrics, and results?)
5. Communication (is the profile clear and professional?)

OUTPUT FORMAT — respond ONLY with valid JSON, no markdown, no explanation outside JSON:
{{
  "score": <number between 0 and 5, halves only>,
  "reason": [
    "Technical Skills (X/5): ...",
    "Real Projects (X/5): ...",
    "Experience (X/5): ...",
    "Impact (X/5): ...",
    "Communication (X/5): ..."
  ],
  "tips": [
    "Tip 1: ...",
    "Tip 2: ...",
    "Tip 3: ...",
    "Tip 4: ...",
    "Tip 5: ..."
  ]
}}

PROFILE DATA:
{profile_json}
"""


def _parse_ai_response(raw):
    raw = raw.strip()
    if raw.startswith("```"):
        parts = raw.split("```")
        raw = parts[1] if len(parts) > 1 else raw
        if raw.startswith("json"):
            raw = raw[4:]
    return json.loads(raw.strip())


def score_with_gemini(profile_data):
    if not GEMINI_KEY:
        print("  ⚠️  Gemini: no API key set → skipping")
        return None
    try:
        import google.generativeai as genai
        genai.configure(api_key=GEMINI_KEY)
        model  = genai.GenerativeModel("models/gemini-2.5-flash")
        prompt = SCORE_PROMPT.format(
            today=datetime.today().strftime('%Y-%m-%d'),
            profile_json=json.dumps(profile_data, indent=2, ensure_ascii=False)
        )
        resp   = model.generate_content(prompt)
        result = _parse_ai_response(resp.text)
        print(f"  ✅ Gemini score: {result['score']}/5")
        return result["score"], result["reason"], result["tips"]
    except Exception as e:
        print(f"  ⚠️  Gemini scoring failed: {e}")
        return None


def score_with_groq(profile_data):
    if not GROQ_KEY:
        print("  ⚠️  Groq: no API key set → skipping")
        return None
    try:
        from groq import Groq
        client = Groq(api_key=GROQ_KEY)
        prompt = SCORE_PROMPT.format(
            today=datetime.today().strftime('%Y-%m-%d'),
            profile_json=json.dumps(profile_data, indent=2, ensure_ascii=False)
        )
        resp   = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
        )
        result = json.loads(resp.choices[0].message.content)
        print(f"  ✅ Groq score: {result['score']}/5")
        return result["score"], result["reason"], result["tips"]
    except Exception as e:
        print(f"  ⚠️  Groq scoring failed: {e}")
        return None


def score_profile(profile_data):
    print("\n🤖 Scoring profile with AI...")
    gemini_result = score_with_gemini(profile_data)
    groq_result   = score_with_groq(profile_data)

    if gemini_result and groq_result:
        g_score, g_reason, g_tips = gemini_result
        r_score, r_reason, r_tips = groq_result
        raw_avg     = (g_score + r_score) / 2
        final_score = round(raw_avg * 2) / 2
        tips        = list(dict.fromkeys(g_tips + r_tips))[:6]
        print(f"  🔁 Both models → Gemini: {g_score}, Groq: {r_score} → Average: {final_score}")
        return final_score, g_reason, tips
    elif gemini_result:
        print("  ℹ️  Using Gemini result only")
        return gemini_result
    elif groq_result:
        print("  ℹ️  Using Groq result only")
        return groq_result
    else:
        print("  ❌ Both AI scoring methods failed.")
        return None


def print_score(score, reason, tips):
    print(f"\n{'='*50}")
    print(f"  WORK READINESS SCORE: {score}/5")
    print(f"{'='*50}\n")
    print("📊 EVALUATION:")
    for r in reason:
        print(f"  • {r}")
    print("\n💡 TIPS TO IMPROVE:")
    for i, tip in enumerate(tips, 1):
        print(f"  {i}. {tip}")


# ══════════════════════════════════════════════════════════════
#  SINGLE PROFILE SCRAPER
# ══════════════════════════════════════════════════════════════

def scrape_one(driver, url):
    """Scrape a single profile URL and return its data dict."""
    profile_data = {}

    navigate_to_profile(driver, url)
    scroll_page(driver, times=15)
    soup = get_soup(driver)

    card = scrape_profile_card(soup, url)
    if card:
        profile_data.update(card)
    else:
        profile_data.update({"Name": None, "URL": url, "Head Line": None, "Personal Location": None})

    profile_name = profile_data.get("Name") or "unknown_profile"

    save_pdf(driver, profile_name)

    profile_data["About"]         = scrape_about(soup)
    profile_data["Experience"]    = scrape_experience(soup, driver)
    soup = get_soup(driver)
    profile_data["Education"]     = scrape_education(soup)
    profile_data["Certification"] = scrape_certifications(soup, driver)
    soup = get_soup(driver)
    profile_data["Projects"]      = scrape_projects(soup, driver)
    soup = get_soup(driver)
    profile_data["Skills"]        = scrape_skills(soup, driver)
    soup = get_soup(driver)
    profile_data["Languages"]     = scrape_languages(soup)

    print("\n💾 Saving files...")
    save_json(profile_data, profile_name)
    save_txt(profile_data, profile_name)

    result = score_profile(profile_data)
    if result:
        score, reason, tips = result
        print_score(score, reason, tips)
        score_path = os.path.join(OUTPUT_DIR, f"{profile_name}_score.json")
        with open(score_path, "w", encoding="utf-8") as f:
            json.dump({"score": score, "reason": reason, "tips": tips}, f, indent=4, ensure_ascii=False)
        print(f"  ✅ Score saved → {score_path}")

    print(f"\n✅ Done with: {profile_name}")
    return profile_data


# ══════════════════════════════════════════════════════════════
#  BULK RUNNER  ← main entry point
# ══════════════════════════════════════════════════════════════

def run_bulk(profile_urls: list):
    """
    Login once, then scrape every URL in the list.
    Cookies are saved after login so subsequent runs skip the login step.
    """
    driver = get_driver()          # anti-bot Chrome

    if not login(driver):          # cookies → fresh login → CAPTCHA → save cookies
        print("❌ Could not log in. Exiting.")
        driver.quit()
        return []

    all_results = []
    total = len(profile_urls)

    for i, url in enumerate(profile_urls, 1):
        print(f"\n{'─'*60}")
        print(f"  📋 Profile {i} / {total}: {url}")
        print(f"{'─'*60}")
        try:
            data = scrape_one(driver, url)
            all_results.append(data)
        except Exception as e:
            print(f"  ⚠️  Failed on {url}: {e}")
        time.sleep(3)   # polite pause between profiles

    driver.quit()
    print(f"\n🏁 All done — {len(all_results)}/{total} profiles scraped.")
    return all_results


# ══════════════════════════════════════════════════════════════
#  ENTRY POINT — edit this list and run the file
# ══════════════════════════════════════════════════════════════

PROFILE_URLS = [
    "https://www.linkedin.com/in/ismail-al-hetimi/",
    # add more URLs here:
    "https://www.linkedin.com/in/hubert-iskra/",
    "https://www.linkedin.com/in/david-d-1418a4219/",
]

run_bulk(PROFILE_URLS)