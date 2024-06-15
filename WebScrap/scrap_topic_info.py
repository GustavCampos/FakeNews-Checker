import pandas as pd
import requests
from bs4 import BeautifulSoup
from json import load as json_load
from os.path import dirname, join as joinpath, realpath
from time import sleep, time


def calc_progress(cur_value: int, end_value: int, size=20) -> str:
    proportion = cur_value / end_value
    
    equals = "=" * round(size * proportion)
    spaces = " " * (size - len(equals))
    progress_bar = "[" + equals + spaces + "]"
    
    return f"{progress_bar} {cur_value}/{end_value} {proportion * 100:2.2f}%"
    
def check_article(soup_obj) -> str:
    # 1 Method____________________________________________________________
    rating_wrap_div = soup_obj.select_one("div.rating_title_wrap")
    if rating_wrap_div:
        return rating_wrap_div.text.strip().split("\n")[0].strip().lower()
    
    # 2 Method____________________________________________________________
    font_list = soup_obj.find_all("font")
    for i in range(len(font_list)):
        if font_list[i].text.strip() == "Status:":
            return font_list[i+1].text.strip(".").lower()
    
    # 3 Method____________________________________________________________
    font_obj = soup_obj.select_one("font.status_color > b")
    if font_obj:
        return font_obj.text.strip().lower()
    
    return "undefined" 

def get_byline(soup_obj) -> str:
    selector = "h1 + h2"
    h2 = soup_obj.select_one(selector)
    
    if type(h2) == type(None):
        return ""
    
    return h2.text.strip()

def get_article_info(article_url: str) -> dict:
    soup_obj = BeautifulSoup(requests.get(article_url).text, "html.parser")
    
    article_check = check_article(soup_obj)
    full_byline = get_byline(soup_obj)
    
    return {
        "Fact Check": article_check,
        "Byline": full_byline,
    }

def main():
    LOCATION = dirname(realpath(__file__))
    CONFIG_PATH = joinpath(LOCATION, "config.json")
    ARTICLES_TO_SCRAP = joinpath(LOCATION, "undefined.csv") # "scrap_topics", "custom_scrap_topic.csv"
    RESULT_CSV = joinpath(LOCATION, "undefined_fake_news_dataset.csv")
    
    BREAK_PROCESS_UNDEFINED_LIMIT = 1000

    
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
    time_holder = time()
    undefined_count = 0
    for index, row in csv_df.iloc[CONFIGS["starting_point"]:].iterrows():
        if (index + 1) % CONFIGS["sleep"]['batch'] == 0:
            # Awaits sleep time ends            
            while time() - time_holder < CONFIGS["sleep"]['time']:
                print(f"{CONFIGS["sleep"]['batch']} request limit exceeded, awaiting to continue...", end="\r") 
            time_holder = time()         
                
        article_info = get_article_info(row[LINK])
        
        # Stop request process in case of multiples denies_______
        if article_info[IS_TRUTH] == "undefined":undefined_count += 1
        else:undefined_count = 0 
        if undefined_count >= BREAK_PROCESS_UNDEFINED_LIMIT:break
        #________________________________________________________ 
        
        export_csv.append({
            TITLE: row[TITLE],
            IS_TRUTH: article_info[IS_TRUTH],
            BYLINE: article_info[BYLINE],
            DATE: row[DATE],
            AUTHOR: row[AUTHOR],
            LINK: row[LINK],
        })

        print(
            f"{calc_progress(index+1, len(csv_df), size=50)}:: cur_check:{article_info[IS_TRUTH]}",
            " " * 40 
            , end="\r")
        
    print("GET complete! Exporting to CSV...", " " * 80)
    export_csv_df = pd.DataFrame(export_csv)
    
    if CONFIGS["starting_point"] > 0:
        export_csv_df.to_csv(RESULT_CSV, mode="a", header=False, index=False)
    else:
        export_csv_df.to_csv(RESULT_CSV, index=False)
    print("Export complete!")
    
if __name__ == '__main__':
    main()