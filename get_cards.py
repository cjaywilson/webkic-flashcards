
from argparse import ArgumentParser
from concurrent.futures import ThreadPoolExecutor
from csv import writer
from functools import partial
from getpass import getpass
from os import system
from pathlib import Path
from urllib.error import HTTPError
from pkg_resources import get_distribution
from time import sleep
from urllib.request import urlopen
from uuid import uuid4

import json
import re
import sys

from tqdm import tqdm
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options as GeckoOptions
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.firefox import GeckoDriverManager

class LoginError(Exception):
    pass

__yn = re.compile(r"y(es)?|no?", re.I)

def prompt_yn(prompt: str) -> bool:
    r = ""
    while not __yn.match(r):
        r = input(prompt)
    return r.lower()[0] == "y"

def download_cards(args):
    # Initialize the selenium driver
    opts = GeckoOptions()
    opts.headless = args.headless

    # Download the web driver, if necessary
    # See: https://github.com/SergeyPirogov/webdriver_manager
    if get_distribution("selenium").version[0] == "4":
        from selenium.webdriver.firefox.service import Service as FirefoxService
        driver = webdriver.Firefox(options=opts, service=FirefoxService(GeckoDriverManager().install()))
    else:
        driver = webdriver.Firefox(options=opts, executable_path=GeckoDriverManager().install())

    # Check the backup file
    backup_file = Path("cards.bak")

    if args.backup and backup_file.exists():
        print("starting from backup...")
        with open(backup_file) as b:
            flashcards = json.load(b)
        start = max(flashcards, key=lambda f: f[3])[3] + 1
    else:
        flashcards = []
        start = 1
    
    if start > args.lesson:
        return flashcards

    try:
        # Navigate to the login page
        driver.get(args.site)
        driver.find_element(By.ID, "login-email").send_keys(input("login email: "))
        driver.find_element(By.ID, "login-password").send_keys(getpass("password: "))
        driver.find_element(By.ID, "login-submit-button").click()

        # Login
        print("waiting for login...")
        try:
            WebDriverWait(driver, args.timeout).until(
                EC.presence_of_element_located((By.ID, "login-me"))
            )
            
            driver.find_element(By.CLASS_NAME, "on-state")
        except Exception:
            raise LoginError("failed to login")
        
        def get_flashcards(lesson):
            # Set flashcard options
            driver.find_element(By.ID, "flashcard").click()

            WebDriverWait(driver, args.timeout).until(
                EC.visibility_of( driver.find_element(By.ID, "from_form_flashcard") )
            )

            driver.find_element(By.ID, "from_form_flashcard").clear()
            driver.find_element(By.ID, "from_form_flashcard").send_keys(str(lesson))
            driver.find_element(By.ID, "to_form_flashcard").clear()
            driver.find_element(By.ID, "to_form_flashcard").send_keys(str(lesson))

            kihon_box = driver.find_element(By.ID, "skip_only_form_flashcard")

            if args.plus:
                if kihon_box.is_selected():
                    kihon_box.click()
            else:
                if not kihon_box.is_selected():
                    kihon_box.click()

            star_box = driver.find_element(By.ID, "star_only_form_flashcard")
            ignore_box = driver.find_element(By.ID, "ignore_check_form_flashcard")
            order_box = driver.find_element(By.ID, "kic_order_form_flashcard")
            
            if star_box.is_selected():
                star_box.click()
            
            if ignore_box.is_selected():
                ignore_box.click()

            if not order_box.is_selected():
                order_box.click()
            
            driver.find_element(By.ID, "tango_front_form_flashcard").click()
            driver.find_element(By.ID, "sakusei_button_flashcard").click()

            # Get all flashcards
            for card in WebDriverWait(driver, args.timeout).until(
                EC.presence_of_all_elements_located((By.CLASS_NAME, "dual-sided-flashcard"))
            ):
                _, info = card.get_attribute("data-wid").split("|", 1)
                _, tango = info.split(",", 1)

                flashcards.append(
                    [
                        tango,
                        card.find_element(By.CLASS_NAME, "flashcard-text-yomi").get_attribute("innerHTML"),
                        card.find_element(By.CLASS_NAME, "flashcard-text-english").get_attribute("innerHTML"),
                        lesson
                    ]
                )

                with open(backup_file, "w", encoding="utf8") as b:
                    json.dump(flashcards, b, ensure_ascii=False)
        
        print("creating flashcards...")
        for i in tqdm(range(start, args.lesson + 1)):
            get_flashcards(i)
    
    finally:
        driver.quit()
    
    return flashcards

def download_svg(char, site, folder, overwrite):
    base_url = site + "fonts/stroke_font/stroke_"
    save_file = Path(folder, char + ".svg")

    if save_file.exists() and not overwrite:
        return
    
    try:
        with urlopen(base_url + hex(ord(char)).upper()[2:] + ".svg") as r:
            svg = r.read().decode("utf8").replace("fill=\"currentColor\"", "")
            with open(save_file, "w", encoding="utf8") as f:
                f.write(svg)
    except HTTPError as err:
        print(err, file=sys.stderr)
    
    sleep(0.1)

if __name__ == "__main__":
    # Parse arguments
    parser = ArgumentParser(description="Downloads flashcards from WebKIC and saves them in CSV format for use in Anki. Combines flashcard information with SVG files from WebKIC.")
    parser.add_argument("site", type=str, help="the link to WebKIC")
    parser.add_argument("output", type=Path, help="the file to save flashcard info to in CSV format")
    parser.add_argument("anki", type=Path, help="the path to save/check SVG files (your Anki resources folder)")
    parser.add_argument("-l, --lesson", dest="lesson", type=int, default=156, help="the number of lessons to fetch flashcards for (max 156)")
    parser.add_argument("-o, --overwrite-svg", dest="overwrite", action="store_true", help="overwrite existing SVG files in the resources (Anki) folder")
    parser.add_argument("-t, --timeout", dest="timeout", type=float, default=10.0, help="the maximum amount of time to wait for web scraping actions")
    parser.add_argument("-x, --extra", dest="plus", action="store_true", help="include black (extra) vocabulary words")
    parser.add_argument("--optimize", dest="optimize", action="store_true", help="optimize downloaded SVG files (requires https://github.com/svg/svgo)")
    parser.add_argument("--no-headless", dest="headless", action="store_false", help="show the web driver's browser windows")
    parser.add_argument("--no-backup", dest="backup", action="store_false", help="download all cards from WebKIC (ignore prior backups)")

    args = parser.parse_args()

    # Check arguments
    if not "//" in args.site:
        args.site = "https://" + args.site
    if not args.site.endswith("/"):
        args.site += "/"
    
    if args.output.exists() and \
        not prompt_yn(f"`{args.output.as_posix()}` already exists. overwrite? (y/n): "):
        sys.exit()
    
    if not args.anki.exists():
        print(f"`{args.anki.as_posix()}` does not exist")
        sys.exit()
    
    args.lesson = min(max(1, args.lesson), 156)
    args.timeout = max(1, args.timeout)

    # Download flashcards
    if args.lesson == 1:
        print("downloading flashcards for lesson 1...")
    else:
        print(f"downloading flashcards for lessons 1 through {args.lesson}...")

    flashcards = None
    while flashcards is None:
        try:
            flashcards = download_cards(args)
        except LoginError as e:
            print(e)
            if not prompt_yn("try again? (y/n)"):
                sys.exit()
    
    chars = set(c for f in flashcards for c in f[0])

    print(f"found {len(flashcards)} cards with {len(chars)} unique characters...")

    # Download SVG files
    print("downloading SVG files...")
    with ThreadPoolExecutor(3) as ex:
        for _ in tqdm(ex.map(partial(download_svg, folder=args.anki, site=args.site, overwrite=args.overwrite), chars), total=len(chars)):
            pass
    
    # Optimize SVG files
    if args.optimize:
        # TODO: check cross-platform functionality
        print("optimizing SVG files...")
        system(f"svgo -f {args.anki} -o {args.anki}")
    
    # Link SVG files to flashcards
    print("combining card info...")
    for card in tqdm(flashcards):
        card.append( "".join( k if not Path(args.anki, k + ".svg").exists() else f"<img src='{k}.svg'>" for k in card[0] ) )
        card.insert( 0, uuid4().urn )
    
    # Write results to CSV
    with open(args.output, "w", encoding="utf8") as f:
        w = writer(f)
        w.writerows(flashcards)
    
    print(f"wrote {len(flashcards)} cards to `{args.output.as_posix()}`")
