# 07/31/2020 because the house updated its webpage, the old crawler no longer works

from selenium import webdriver
import selenium
from bs4 import BeautifulSoup
from requests_html import HTMLSession
import re
import time
import numpy as np
import os
import pandas as pd
from pprint import pprint
from pytz import timezone
import datetime
from prototyping.utils import dictionary_functions, constants, standardize_index
from selenium.common.exceptions import NoSuchElementException


# TODO crawler misses the first page of any congress but the latest URGENT
# even in the summary, of which it got most links
def establish_webdriver():

    path = constants.geckopath

    driver = webdriver.Firefox(executable_path=path)

    return driver


def update_house_votes_selenium():

    base_html = 'https://clerk.house.gov/Votes'
    base_house = 'https://clerk.house.gov'
    driver = establish_webdriver()

    # TODO a different wait that zach used that looks like it works better
    # need some libraries for this as well that are imported
    # x = WebDriverWait(driver, 100)
    # condition = EC.presence_of_all_elements_located((By.TAG_NAME, "tr"))
    # x.until(condition)
    # time.sleep(2)

    driver.implicitly_wait(10)

    driver.get(base_html)

    time.sleep(1)

    should_update_occur = is_local_up_to_date(driver=driver)
    if not should_update_occur:
        print('no need to update, closing driver and exiting')
        driver.close()
        return

    last_local_congress = check_latest_local_congress()
    last_local_session = check_latest_local_session(congress=last_local_congress)
    last_local_vote = check_latest_local_vote(congress=last_local_congress,
                                              session=last_local_session)

    latest_local_tuple = (last_local_congress, last_local_session, last_local_vote)

    link_pages = []
    roll_call_summary_dictionary = {}

    explore_pages(driver=driver,
                  local_vote=latest_local_tuple,
                  link_pages=link_pages,
                  roll_call_summary_dictionary=roll_call_summary_dictionary)

    # TODO consider adding this in between congress/session grabs
    # But this is honestly kind of okay as well
    for link in link_pages:
        pull_vote_page_info(link=link,
                            summary_dictionary=roll_call_summary_dictionary)
        time.sleep(1)

    # end of function running
    driver.close()

    return


def full_crawl_house_votes_selenium():

    base_html = 'https://clerk.house.gov/Votes'
    base_house = 'https://clerk.house.gov'
    driver = establish_webdriver()

    driver.implicitly_wait(15)

    driver.get(base_html)

    time.sleep(1)
    # wait_longer(driver=driver)

    link_pages = []
    roll_call_summary_dictionary = {}
    garbage_vote = (0, 0, 0)

    explore_pages(driver=driver,
                  local_vote=garbage_vote,
                  link_pages=link_pages,
                  roll_call_summary_dictionary=roll_call_summary_dictionary,
                  full_explore=True)

    for link in link_pages:
        pull_vote_page_info(link=link,
                            summary_dictionary=roll_call_summary_dictionary)
        time.sleep(1)

    # end of function running
    driver.close()

    return


def is_local_up_to_date(driver):

    should_update = False

    most_recent_local_congress = check_latest_local_congress()
    most_recent_online_congress = check_latest_online_congress(driver=driver)

    most_recent_local_session = check_latest_local_session(congress=most_recent_local_congress)
    most_recent_online_session = check_latest_online_session(driver=driver)

    most_recent_local_vote = check_latest_local_vote(congress=most_recent_local_congress,
                                                     session=most_recent_local_session)
    most_recent_online_vote = check_latest_online_vote(driver=driver)

    # debugging test, since debugger isn't working
    print('local = {}, {}, {}'.format(most_recent_local_congress,
                                      most_recent_local_session,
                                      most_recent_local_vote))
    print('online = {}, {}, {}'.format(most_recent_online_congress,
                                       most_recent_online_session,
                                       most_recent_online_vote))

    if most_recent_online_congress > most_recent_local_congress:
        should_update = True

    elif most_recent_online_congress >= most_recent_local_congress and \
            most_recent_online_session > most_recent_local_session:
        should_update = True

    elif most_recent_online_congress >= most_recent_local_congress and \
            most_recent_online_session >= most_recent_local_session and \
            most_recent_online_vote > most_recent_local_vote:
        should_update = True

    return should_update


# TODO need to fill out logic here so that the update can work as intended
# can maybe reduce this for it to say latest_local_index
def check_latest_local_vote(congress, session):

    # get latest vote from roll call votes_directory
    path = constants.house_roll_call_votes_directory_new + '{}/{}/'.format(congress, session)
    list_of_votes = os.listdir(path=path)
    int_votes_list = [int(x.split('.')[0]) for x in list_of_votes]
    latest_vote_num = max(int_votes_list)

    return latest_vote_num


def check_latest_online_vote(driver):

    latest_vote_num = 0

    roll_call_xpath = '//*[@id="votes"]/div[1]/div[1]/div[1]/div[2]/a[1]'
    roll_call_element = driver.find_element_by_xpath(roll_call_xpath)
    roll_call_vote_text = roll_call_element.text

    latest_vote_num = int(roll_call_vote_text)

    return latest_vote_num


def check_latest_online_congress(driver):

    congress_date_xpath = '//*[@id="votes"]/div[1]/div[1]/div[1]/div[1]'
    congress_date_element = driver.find_element_by_xpath(congress_date_xpath)
    vote_date_info = congress_date_element.text

    congress_info = vote_date_info.split(' | ')[1]
    congress_num = congress_info.split(' ')[0][0:3]

    latest_congress = int(congress_num)

    return latest_congress


def check_latest_local_congress():

    path = constants.house_roll_call_votes_directory_new
    list_of_congress = os.listdir(path=path)
    int_congress_list = [int(x) for x in list_of_congress]
    latest_congress = max(int_congress_list)

    return latest_congress


def check_latest_online_session(driver):

    congress_date_xpath = '//*[@id="votes"]/div[1]/div[1]/div[1]/div[1]'
    congress_date_element = driver.find_element_by_xpath(congress_date_xpath)
    vote_date_info = congress_date_element.text

    congress_info = vote_date_info.split(' | ')[1]
    session_num = congress_info.split(' ')[2][0]

    latest_session = int(session_num)

    return latest_session


def check_latest_local_session(congress):

    path = constants.house_roll_call_votes_directory_new + '{}/'.format(congress)
    list_of_session = os.listdir(path=path)
    int_session_list = [int(x) for x in list_of_session]
    latest_session = max(int_session_list)

    return latest_session


def get_vote_block_info(vote_block_position, driver, link_pages):
    # grabs all of the info off of a vote block

    try:
        congress_date_xpath = '//*[@id="votes"]/div[{}]/div[1]/div[1]/div[1]'.format(vote_block_position)
        congress_date_element = driver.find_element_by_xpath(congress_date_xpath)
        vote_date_info = congress_date_element.text
    except selenium.common.exceptions.NoSuchElementException:
        vote_date_info = ''

    try:
        roll_call_xpath = '//*[@id="votes"]/div[{}]/div[1]/div[1]/div[2]/a[1]'.format(vote_block_position)
        roll_call_element = driver.find_element_by_xpath(roll_call_xpath)
        roll_call_vote_text = roll_call_element.text
        roll_call_vote_text = str(standardize_index.standardize_vote_number(roll_call_vote_text))
        roll_call_vote_page = roll_call_element.get_property('href')
    except selenium.common.exceptions.NoSuchElementException:
        roll_call_vote_text = ''
        roll_call_vote_page = ''

    try:
        bill_num_xpath = '//*[@id="votes"]/div[{}]/div[1]/div[1]/div[2]/a[2]'.format(vote_block_position)
        bill_num_element = driver.find_element_by_xpath(bill_num_xpath)
        bill_number_text = bill_num_element.text
        bill_number_page = bill_num_element.get_property('href')
    except selenium.common.exceptions.NoSuchElementException:
        bill_number_text = ''
        bill_number_page = ''

    try:
        vote_question_xpath = '//*[@id="votes"]/div[{}]/div[1]/div[1]/p[1]'.format(vote_block_position)
        vote_question_element = driver.find_element_by_xpath(vote_question_xpath)
        vote_question_text = vote_question_element.text
    except selenium.common.exceptions.NoSuchElementException:
        vote_question_text = ''

    try:
        bill_descr_xpath = '//*[@id="votes"]/div[{}]/div[1]/div[1]/p[2]'.format(vote_block_position)
        bill_descr_element = driver.find_element_by_xpath(bill_descr_xpath)
        bill_description_text = bill_descr_element.text
    except selenium.common.exceptions.NoSuchElementException:
        bill_description_text = ''

    try:
        vote_type_xpath = '//*[@id="votes"]/div[{}]/div[1]/div[1]/p[3]'.format(vote_block_position)
        vote_type_element = driver.find_element_by_xpath(vote_type_xpath)
        vote_type_text = vote_type_element.text
    except selenium.common.exceptions.NoSuchElementException:
        vote_type_text = ''

    try:
        vote_status_xpath = '//*[@id="votes"]/div[{}]/div[1]/div[1]/p[4]'.format(vote_block_position)
        vote_status_element = driver.find_element_by_xpath(vote_status_xpath)
        vote_status_text = vote_status_element.text
    except selenium.common.exceptions.NoSuchElementException:
        vote_status_text = ''

    try:
        yeas_xpath = '//*[@id="votes"]/div[{}]/div[1]/div[2]/div[2]'.format(vote_block_position)
        yeas_element = driver.find_element_by_xpath(yeas_xpath)
        number_yeas = yeas_element.text
    except selenium.common.exceptions.NoSuchElementException:
        number_yeas = ''

    try:
        nays_xpath = '//*[@id="votes"]/div[{}]/div[1]/div[2]/div[3]'.format(vote_block_position)
        nays_element = driver.find_element_by_xpath(nays_xpath)
        number_nays = nays_element.text
    except selenium.common.exceptions.NoSuchElementException:
        number_nays = ''

    try:
        present_xpath = '//*[@id="votes"]/div[{}]/div[1]/div[2]/div[4]'.format(vote_block_position)
        present_element = driver.find_element_by_xpath(present_xpath)
        number_present = present_element.text
    except selenium.common.exceptions.NoSuchElementException:
        number_present = ''

    try:
        not_vote_xpath = '//*[@id="votes"]/div[{}]/div[1]/div[2]/div[5]'.format(vote_block_position)
        not_vote_element = driver.find_element_by_xpath(not_vote_xpath)
        number_not_vote = not_vote_element.text
    except selenium.common.exceptions.NoSuchElementException:
        number_not_vote = ''

    # need to format date info and bill number to pass on
    datetime_str = vote_date_info.split('|')[0]

    month = datetime_str.split(' ')[0].lower()
    day = int(datetime_str.split(' ')[1].split(',')[0])
    year = int(datetime_str.split(' ')[2].split(',')[0])
    am_pm = datetime_str.split(' ')[4].lower()
    hour = int(datetime_str.split(' ')[3].split(':')[0])
    minutes = int(datetime_str.split(' ')[3].split(':')[1])

    if am_pm == 'am' and hour == 12:
        hour = 0
    elif am_pm == 'pm' and hour < 12:
        hour += 12

    month_to_num = dictionary_functions.month_to_num()
    month_int = month_to_num[month]

    tz = timezone('EST')
    vote_time = datetime.datetime(year=year, month=month_int, day=day, hour=hour, minute=minutes, tzinfo=tz)

    congress_info = vote_date_info.split(' | ')[1]
    congress_num = congress_info.split(' ')[0][0:3]
    session_num = congress_info.split(' ')[2][0]

    vote_index = 'cn{}sn{}vn{}'.format(congress_num, session_num, roll_call_vote_text)

    vote_tile_info = {'datetime': vote_time,
                      'congress': congress_num,
                      'session': session_num,
                      'vote_number': roll_call_vote_text,
                      'vote_link': roll_call_vote_page,
                      'bill_number': bill_number_text,
                      'bill_link': bill_number_page,
                      'vote_question': vote_question_text,
                      'bill_description': bill_description_text,
                      'vote_type': vote_type_text,
                      'vote_status': vote_status_text,
                      'yeas': number_yeas,
                      'nays': number_nays,
                      'present': number_present,
                      'not_voting': number_not_vote,
                      'vote_index': vote_index}

    link_pages.append(roll_call_vote_page)

    return vote_tile_info


def explore_pages(driver, local_vote, link_pages, roll_call_summary_dictionary, full_explore=False):
    # a page is one of the pages that has multiple vote instances, and where you might try to find
    # which vote you wanted to find more information about

    move_through_page(driver=driver,
                      local_vote=local_vote,
                      link_pages=link_pages,
                      roll_call_summary_dictionary=roll_call_summary_dictionary)

    condition = True
    while condition:
        condition = move_to_next_page(driver=driver)
        current_congress, current_session, end_condition = move_through_page(driver=driver,
                                                                             local_vote=local_vote,
                                                                             link_pages=link_pages,
                                                                             roll_call_summary_dictionary=roll_call_summary_dictionary)

        if end_condition:
            write_roll_call_summary(summary_dictionary=roll_call_summary_dictionary,
                                    congress=current_congress,
                                    session=current_session)
            break

        if not condition and full_explore:

            if str(current_congress) == '101' and str(current_session) == '2':
                condition = False
                continue

            elif str(current_session) == '2':
                next_congress = current_congress
                next_session = '1st'  # needs to be 1st or 2nd
            elif str(current_session) == '1':
                next_congress = int(current_congress) - 1
                next_session = '2nd'

            next_html = 'https://clerk.house.gov/Votes/?CongressNum={}&Session={}'.format(next_congress,
                                                                                          next_session)
            driver.get(next_html)

            # determine next session and congress
            condition = True

            print('stuff here only for debugging')
            write_roll_call_summary(summary_dictionary=roll_call_summary_dictionary,
                                    congress=current_congress,
                                    session=current_session)

    # could potentially write the summary here

    return


def move_through_page(driver, local_vote, link_pages, roll_call_summary_dictionary):

    end_condition = False

    num_results_element = driver.find_element_by_xpath('//*[@id="membersvotes"]/nav[1]/div')
    num1 = int(num_results_element.text.split(' ')[0])
    num2 = int(num_results_element.text.split(' ')[2])
    num_tiles = num2 - num1
    print(num_results_element.text, num_tiles)  # for checking runtime progress

    local_congress = local_vote[0]
    local_session = local_vote[1]
    local_vote_number = local_vote[2]

    for i in range(1, num_tiles + 2):
        vote_tile_block = get_vote_block_info(vote_block_position=i,
                                              driver=driver,
                                              link_pages=link_pages)

        vote_index = 'cn{}sn{}vn{}'.format(vote_tile_block['congress'],
                                           vote_tile_block['session'],
                                           vote_tile_block['vote_number'])

        congress = vote_tile_block['congress']
        session = vote_tile_block['session']
        vote_number = vote_tile_block['vote_number']

        if int(congress) >= local_congress and int(session) >= local_session and int(vote_number) > local_vote_number:
            end_condition = False
        else:
            end_condition = True

        if end_condition:
            print('finished updating')
            break

        if congress not in roll_call_summary_dictionary:
            roll_call_summary_dictionary[congress] = {session: {vote_number: vote_tile_block}}
        elif session not in roll_call_summary_dictionary[congress]:
            roll_call_summary_dictionary[congress][session] = {vote_number: vote_tile_block}
        else:
            roll_call_summary_dictionary[congress][session][vote_number] = vote_tile_block

    return congress, session, end_condition


def move_to_next_page(driver):

    # time.sleep(2)
    current_loc = driver.find_element_by_partial_link_text('current')
    current_loc_text = current_loc.text
    current_number = int(current_loc_text.split('\n')[0])
    next_number = current_number + 1

    a_heading_xpath = '//*[@id="votes"]/div[1]/div[1]/div[1]/div[1]'
    a_heading_element = driver.find_element_by_xpath(a_heading_xpath)
    next_congress = a_heading_element.text.split(' ')[6][0:3]
    next_session = a_heading_element.text.split(' ')[8]

    # print(current_loc.text)
    print('current number = ', current_number, '\tnext number = ', next_number)

    next_html = 'https://clerk.house.gov/Votes/?CongressNum={}&Session={}&page={}'.format(next_congress,
                                                                                          next_session,
                                                                                          next_number)

    # this allows for an interesting method, but will be somewhat time consuming to figure out at present
    # next_loc = driver.find_element_by_partial_link_text('{}'.format(next_number))
    # next_loc.click()
    # print(next_loc.get_attribute('data-action')[:-2])
    # next_link = 'https://clerk.house.gov' + next_loc.get_attribute('data-action')[:-2]
    # uggh, so, discovered a better way from this link, a link set that will allow me to use requests_html

    driver.get(next_html)
    # driver.manage().timeouts().implicitlyWait
    # wait_longer(driver=driver)

    # time.sleep(2)

    results_element = driver.find_element_by_xpath('//*[@id="membersvotes"]/nav[1]/div')
    # results_element = wait_longer(driver=driver, xpath='//*[@id="membersvotes"]/nav[1]/div')
    current_results = results_element.text.split(' ')[2]
    total_results = results_element.text.split(' ')[4]

    if current_results == total_results:
        return False

    return True


def pull_vote_page_info(link, summary_dictionary):
    # TODO summary dictionary never incorporated
    sesh = HTMLSession()
    page = sesh.get(link)
    soup = BeautifulSoup(page.html.html)

    # some roll call number and bill number
    title_tag = soup.find('meta', {'name': 'twitter:title'})
    try:
        vote_number = title_tag.get('content').split(' ')[2].split(',')[0]
    except AttributeError:
        vote_number = ''
    try:
        bill_number = title_tag.get('content').split(': ')[1].split(',')[0]
    except AttributeError:
        bill_number = ''
    except IndexError:
        print('index exception at ', vote_number)
        bill_number = title_tag.get('content')

    # some starting information from the page, to make sure everything is grand
    row_heading_tag = soup.find('div', {'class': 'first-row heading'})
    congress_date = row_heading_tag.string
    congress_info = congress_date.split('|')[1]
    congress_info = re.sub(' ', '', congress_info)
    congress_info = re.sub('\r\n', '', congress_info)

    congress_num = congress_info[0:3]
    session_num = congress_info.split(',')[1][0]

    vote_index = 'cn{}sn{}vn{}'.format(congress_num,
                                       session_num,
                                       vote_number)

    vote_index = standardize_index.standardize_index(vote_index)

    votes_by_party_table = soup.find('div', {'class': 'votes-by-party'})
    vote_table_dictionary = {}

    # TODO actually use this information and write it to local database for use
    # getting vote summary information for the parties
    for row in votes_by_party_table.find_all('tr'):
        for entry in row.find_all('td'):
            if entry.get('data-label').lower() == 'party':
                party = entry.get('aria-label').lower()
            if party in vote_table_dictionary:
                vote_table_dictionary[party][entry.get('data-label').lower()] = entry.get('aria-label').split(' ')[0]
            else:
                vote_table_dictionary[party] = {entry.get('data-label').lower(): entry.get('aria-label').split(' ')[0]}

    member_table = soup.find('tbody', {'id': 'member-votes'})
    base_house = constants.house_base_page
    members = {}

    # getting votes cast from members for a given action/vote
    for row in member_table.find_all('tr'):

        member_link = ''
        member_id = ''
        try:
            member_link = base_house + row.a.get('href')
            member_id = row.a.get('href').split('/')[2]
        except AttributeError:
            # print(row)
            pass
        member_name = ''
        member_state = ''
        member_party = ''
        member_vote = ''

        for entry in row.find_all('td'):

            if pd.notna(entry.string) and pd.notna(entry.get('data-label')):
                if entry.get('data-label').lower() == 'member':
                    member_name = entry.string

                if entry.get('data-label').lower() == 'party':
                    member_party = entry.string.lower()

                if entry.get('data-label').lower() == 'state' and len(entry.string) == 2:
                    member_state = entry.string.lower()

                if entry.get('data-label').lower() == 'vote':
                    member_vote = entry.string.lower()

        member_key = '{}_{}'.format(member_name, member_state)
        members[member_key] = {'last_name': member_name,
                               'page_link': member_link,
                               'party': member_party,
                               'state': member_state,
                               'vote': member_vote,
                               'member_id': member_id,
                               'vote_index': vote_index,
                               'congress': congress_num,
                               'session': session_num,
                               'vote_number': vote_number}

    # could write the specific vote info here
    write_roll_call_vote(member_dict=members)

    return


def write_roll_call_vote(member_dict):

    keys = list(member_dict.keys())
    vote_index = member_dict[keys[0]]['vote_index']
    congress_num = member_dict[keys[0]]['congress']
    session_num = member_dict[keys[0]]['session']
    vote_number = standardize_index.standardize_vote_number(member_dict[keys[0]]['vote_number'])

    # create some directories
    house_base_write_directory = constants.house_roll_call_votes_directory_new
    house_congress_directory = house_base_write_directory + '/{}'.format(congress_num)
    house_session_directory = house_congress_directory + '/{}'.format(session_num)
    file_path = house_session_directory + '/{}.csv'.format(vote_number)

    if not os.path.exists(house_base_write_directory):
        os.mkdir(house_base_write_directory)

    if not os.path.exists(house_congress_directory):
        os.mkdir(house_congress_directory)

    if not os.path.exists(house_session_directory):
        os.mkdir(house_session_directory)

    member_frame = pd.DataFrame(member_dict)
    member_frame = member_frame.T
    member_frame.to_csv(file_path, index=False)

    return


def write_roll_call_summary(summary_dictionary, congress, session):

    # TODO need to incorporate the extra info from the vote pages into the summary dictionary
    # though that will necessarily change the flow of the program, so maybe I just add it to the roll call
    # votes and take care of it in post

    summary_path = constants.house_summary_directory_new
    congress_path = summary_path + '{}_{}.csv'.format(congress, session)

    if not os.path.exists(summary_path):
        os.mkdir(summary_path)

    write_dictionary = summary_dictionary[congress][session]
    write_frame = pd.DataFrame(write_dictionary)
    write_frame = write_frame.T

    if not os.path.exists(congress_path):
        write_frame.to_csv(congress_path,)
                           # index=False)
    else:
        write_frame.to_csv(path_or_buf=congress_path,
                           mode='a',
                           header=False,)
                           # index=False)

    return


# format to match my old crawler data, can be used for the moment to get the database up to speed
def old_format_write_roll_call_summary():

    return


def old_format_write_roll_call_vote():

    return


def wait_longer(driver, xpath):
    # waits in a while loop until the page is done loading
    # could try to apply this to every xpath thing

    condition = True
    while condition:
        try:
            button = driver.find_element_by_xpath(xpath)
            label = driver.find_element_by_xpath('//*[@id="membersvotes"]/nav[1]/div')
            label02 = driver.find_element_by_partial_link_text('current')
            print('not waiting')
            condition = False
        except NoSuchElementException:
            time.sleep(2)
            print('stopping')
            condition = True

    return button


def get_missing_votes():
    # this function is for looking through my summaries, and then grabbing and writing the missing votes
    # from the links stored there


    return


# may not be the way to proceed at the moment
class HouseCrawler:

    def __init__(self, ):
        self.base_link_format = 'https://clerk.house.gov/Votes/MemberVotes?Page=1&CongressNum=116&Session=2nd#'

        return

# TODO, can no longer use these as a test, they cause too many bugs
# debug with the congress crawler file
# update_house_votes_selenium()
# full_crawl_house_votes_selenium()
