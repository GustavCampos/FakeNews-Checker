import pandas as pd
import requests
from bs4 import BeautifulSoup
from json import load as json_load
from os.path import dirname, join as joinpath, realpath
from time import sleep


def calc_progress(cur_value: int, end_value: int, size=20) -> str:
    proportion = cur_value / end_value
    
    equals = "=" * round(size * proportion)
    spaces = " " * (size - len(equals))
    progress_bar = "[" + equals + spaces + "]"
    
    return f"{progress_bar} {cur_value}/{end_value} {proportion * 100:2.2f}%"

def check_article(article_url: str) -> str:
    soup_obj = BeautifulSoup(requests.get(article_url).text, "html.parser")
        
    current_selector = "div.rating_title_wrap"
    rating_wrap_div = soup_obj.select_one(current_selector)
    
    if rating_wrap_div:
        return rating_wrap_div.text.strip().split("\n")[0].strip().lower()
    else:
        font_list = soup_obj.find_all("font")
        
        for i in range(len(font_list)):
            if font_list[i].text.strip() == "Status:":
                return font_list[i+1].text.strip(".").lower()
    
    return "undefined"

def main():
    LOCATION = dirname(realpath(__file__))
    CONFIG_PATH = joinpath(LOCATION, "config.json")
    ARTICLES_TO_SCRAP = joinpath(LOCATION,"scrap_topics","scrap_topic_0.csv")

    
    with open(CONFIG_PATH, encoding="utf-8") as file:
        CONFIGS = json_load(file)
    
    # CSV columns _____
    TITLE = 'Title'
    LINK = 'Link'
    BYLINE = 'Byline'
    DATE = 'Date'
    AUTHOR = 'Author'
    IS_TRUTH = "Fact Check"

    print(f"Importing {ARTICLES_TO_SCRAP} as search base...")
    csv_df = pd.read_csv(ARTICLES_TO_SCRAP)
    
    print("GET articles info...")
    export_csv = []
    for index, row in csv_df.iterrows():
        if (index + 1) % CONFIGS["sleep"]['batch'] == 0:
            print(f"Awaiting {CONFIGS['sleep']['time']} seconds to avoid request call limit...", end="\r")
            sleep(CONFIGS["sleep"]['time'])
        
        export_csv.append({
            TITLE: row[TITLE],
            IS_TRUTH: check_article(row[LINK]),
            BYLINE: row[BYLINE],
            DATE: row[DATE],
            AUTHOR: row[AUTHOR],
            LINK: row[LINK],
        })

        print(f"{calc_progress(index+1, len(csv_df), size=50)}", end="\r")
        
    print("GET complete! Exporting to CSV...")
    pd.DataFrame(export_csv).to_csv(joinpath(LOCATION, "fake_news_dataset.csv"), index=False)
    print("Export complete!")
    
if __name__ == '__main__':
    main()