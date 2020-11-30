from prototyping.web_crawlers import senate_crawler
from prototyping.web_crawlers import house_rep_crawl_javascript
from prototyping.web_crawlers import wiki_crawler
from prototyping.web_crawlers import opensecrets_crawler
from prototyping.web_crawlers import HouseRecentFloorCrawler
from prototyping.web_crawlers import SenateRecentFloorCrawler


def senate_crawl():

    for i in range(116, 100, -1):
        for j in range(1, 3):
            test_crawl = senate_crawler.SenateCrawler(all_pages=False, congress_search=i,
                                                      session_search=j, only_congress_summary=True)
            test_crawl.gather_old_data()
            print(i, j)

    return


def senate_update():

    test_crawl = senate_crawler.SenateCrawler(update_mode=True)
    test_crawl.update_votes()

    return


# senate_crawl()
# senate_update()

# house_rep_crawl_javascript.full_crawl_house_votes_selenium()
# wiki_crawler.run_all_wiki_bios()

h_floor = HouseRecentFloorCrawler.HouseFloorActivity()
h_act = h_floor.something()
print('a')
s_floor = SenateRecentFloorCrawler.SenateFloorActivity()
s_brief = s_floor.something()

print('pause')
