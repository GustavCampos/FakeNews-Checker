import requests
import pandas as pd
from os.path import join as joinpath, realpath, dirname, exists as path_exists
from json import load as json_load
from bs4 import BeautifulSoup


def calc_progress(cur_value: int, end_value: int, size=20) -> str:
    proportion = cur_value / end_value
    
    equals = "=" * round(size * proportion)
    spaces = " " * (size - len(equals))
    progress_bar = "[" + equals + spaces + "]"
    
    return f"{progress_bar} {cur_value}/{end_value} {proportion * 100:2.2f}%"

def get_article_list(config: dict):
    csv_list = [["Title", "Link", "Byline", "Date", "Author"]]
    
    for page_num in range(config["starting_point"], config["pages_to_check"] + 1):
        request_url = f"{config["main_url"]}?pagenum={page_num}"
        
        try:
            soup_obj = BeautifulSoup(requests.get(request_url).text, "html.parser")
        except ConnectionError as error:
            print(f"GET articles not completed.\nStopped at page: {page_num}\nError: {error}")
            
            # Return the data that has been collected so far
            return pd.DataFrame(csv_list[1:], columns=csv_list[0])
            
            
        css_selector = "div.article_list_cont > div.article_wrapper > a.outer_article_link_wrapper"
        articles_in_page = soup_obj.select(css_selector)
        
        for i in range(len(articles_in_page)):
            link = articles_in_page[i]["href"]
            title = articles_in_page[i].select_one("h3.article_title").text
            byline = articles_in_page[i].select_one("span.article_byline").text.strip()
            date = articles_in_page[i].select_one("span.article_date").text.strip()
            author = articles_in_page[i].select_one("span.author_name").text.strip()
                        
            csv_list.append([title, link, byline, date, author])
            
            print(f"{calc_progress(page_num, config["pages_to_check"])}", end="\r")
            
    return_df = pd.DataFrame(csv_list[1:], columns=csv_list[0])
            
    print("GET articles complete!", " " * 80)
    return return_df

def main():
    LOCATION = dirname(realpath(__file__))
    CONFIG_PATH = joinpath(LOCATION, "config.json")
    ARTICLE_CSV_PATH = joinpath(LOCATION, "articles.csv")

    with open(CONFIG_PATH, encoding="utf-8") as file:
        config_dict = json_load(file)
        
    articles_df = get_article_list(config_dict)
    
    if path_exists(ARTICLE_CSV_PATH):
        articles_df.to_csv(ARTICLE_CSV_PATH, mode="a", header=False, index=False)
    else:
        articles_df.to_csv(ARTICLE_CSV_PATH, index=False)
    
if __name__ == '__main__':
    main()