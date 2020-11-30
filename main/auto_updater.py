# The goal of this file is to try to provide some of the glue for updating the database
# at first, I'll write this as a skeleton with desired functions, and I'll start filling them in and correcting the
# files in other directories as progress is made

import pandas as pd
import numpy as np
import os
import shutil
from prototyping.web_crawlers import bill_crawler, senate_crawler, house_rep_crawl_javascript, opensecrets_crawler
import prototyping.firebase_database as firebase_database
import prototyping.database_tester as database_tester
from prototyping.data_managing import write_house_bios, write_senate_bios
# import statements


# this will be the 'brain' of the auto updating function
def run_update():

    # error_logger = firebase_database.DatabaseErrors()

    # congress_update_scrape(error_logger=error_logger)

# for debugging
    congress_update_scrape()
    print('checked congress scrape')
    process_congress_data()
    print('processed congress')
    scrape_bill_updates()
    print('scraped new bills')

    push_updates_to_database()
    print('pushed updates')
    backup_data_on_server()
    print('backed up on server, but currently defunct')

    return


# first, need to scrape
# def congress_update_scrape(error_logger):
def congress_update_scrape():

    try:
        wiki_update()
        print('wiki scrape done')
    except:
        print('an error occurred during wiki update, needs to be investigated')
        # error_logger.log_error()

    try:
        senate_update()
        print('senate scrape done')
    except:
        print('an error occurred during senate update, needs to be investigated')
        # error_logger.log_error()

    try:
        house_update()
        print('house scrape done')
    except:
        print('an error occurred during house update, needs to be investigated')
        # error_logger.log_error()

    return


def senate_update():

    senate_updater = senate_crawler.SenateCrawler(update_mode=True)
    senate_updater.update_votes()

    return


def house_update():
    # currently not written as a class, so it will look a little differently
    # want to change that later
    house_rep_crawl_javascript.update_house_votes_selenium()

    return


def wiki_update():

    return


def process_congress_data():

    # TODO there is an error with write senate bios
    write_senate_bios.write_senator_bios()
    print('write senate bios')
    write_house_bios.write_house_bios()
    print('write house bios')
    # TODO if I need merge_house_wiki, use that
    # merge_house_wiki_data.merge_wiki_house()
    # may need it for

    return


def scrape_bill_updates():

    bill_crawler.bill_crawl_wrapper(delete_file=False)

    return


def backup_data_on_server():
    # TODO need to rework backing up to server since I'm no longer connected

    return


def push_updates_to_database():
    # TODO fix and make more custom or bullet proof
    # but for now, just using my testing upload functions

    # currently, need to delete firebase object each time
    database_tester.write_house_cong116()
    database_tester.write_house_cong116_no_votes()
    # writing error because of a data issue with write_senate_bios
    database_tester.write_senators_no_votes()
    database_tester.write_current_senators_no_votes()
    database_tester.write_bills()

    return


# next, need to clean and produce my various

