import os
from bs4 import BeautifulSoup
import pandas as pd
from requests_html import HTMLSession
import time
import datetime
import numpy as np
import re
from pprint import pprint

### URGENT: HOUSE WEBSITE HAS UPDATED! SO STRONG CHANCE NOTHING WORKS

class HouseCrawler:
    # there were enough differences between the house of reps pages and the senate to warrant a different
    # class, at least with how it is written
    # but this will take a lot of inspiration from the previous crawler
    def __init__(self, all_pages=False, year_search='2020'):

        self.sesh = HTMLSession()
        # this no longer works (as of 07/13/2020), new link is https://clerk.house.gov/Votes

        print('Using the wrong house crawler, please switch to the appropriate version')
        raise ValueError

        self.house_roll_base_link =

        # self.years_available = np.linspace(start=2020,stop=1990,num=31)
        self.years_available = np.linspace(start=2020, stop=1990, num=31)

        self.house_roll_call_table_links = []
        self.house_roll_call_vote_links = []

        self.house_roll_call_table_dict = {}
        self.houes_roll_call_votes_dict = {}

        self.house_data_storage_base = 'data_storage/house_data/'

        return

    def roll_call_through_years(self):
        # this is for getting information through all of the years

        all_years = [int(x) for x in self.years_available]
        links = ['{}{}/index.asp'.format(self.house_roll_base_link,year) for year in all_years]

        # the for loop to grab the links for all of the tables
        for link in links:
            # print(link)
            self.grab_table_roll_call_links(link=link)
            time.sleep(0.1)
        # print(self.house_roll_call_table_links)

        # time to go through the tables
        self.iterate_tables()

        for link in self.house_roll_call_vote_links:
            time.sleep(0.5)
            self.examine_individual_vote_pages(link=link)

        return

    def update_house_votes(self):
        #

        house_legislative_home_page = 'http://clerk.house.gov/legislative/legvotes.aspx'
        latest_house_vote_online, year = self.find_latest_house_vote_online(link=house_legislative_home_page)
        latest_house_vote_in_database =  self.find_latest_house_vote_in_database()

        return

    def find_latest_house_vote_online(self, link):

        sesh = self.sesh.get(link)
        soup = BeautifulSoup(sesh.html.html)
        div_tag = soup.find('div', {'id': 'legvote_primary_content_right'})
        current_house_link_tag = div_tag.find('a')

        print(current_house_link_tag)

        return

    def find_latest_house_vote_in_database(self):

        print('function not written')

        return

    def grab_table_roll_call_links(self, link):

        current_session = self.sesh.get(link)
        current_soup = BeautifulSoup(current_session.html.html)
        index_asp = re.search('index.asp', link)
        base_link = link[:index_asp.start()]
        # print(base_link)

        for tag in current_soup.find_all('a'):
            if tag.string[:4] == 'Roll':
                #
                roll_page_link = '{}{}'.format(base_link, tag.get('href'))
                self.house_roll_call_table_links.append(roll_page_link)

        return

    def iterate_tables(self):
        # function to look at the house roll call tables and grab the vote pages and table info

        for link in self.house_roll_call_table_links:
            self.examine_table(link=link)
            time.sleep(0.5)

        # write the tables to csv file
        self.write_vote_table_to_csv()

        return

    def examine_table(self, link):
        table_sesh = self.sesh.get(link)
        table_soup = BeautifulSoup(table_sesh.html.html)

        year = link.split('/')[4]

        counter = 0  # for telling what tag I'm on

        # getting values from the table
        for tag in table_soup.find_all('td'):

            if counter % 6 == 0:
                try:
                    roll_call_number = tag.string
                except AttributeError:
                    # if this occurs, this could be a problem
                    roll_call_number = 'missing'
                    print(tag)
                    print('roll call number is missing')
                try:
                    roll_call_vote_link = tag.find('a').get('href')
                    self.house_roll_call_vote_links.append(roll_call_vote_link)
                except AttributeError:
                    roll_call_vote_link = 'no link'

            elif (counter-1) % 6 == 0:
                try:
                    date_of_vote = tag.string
                except AttributeError:
                    date_of_vote = 'missing'

            elif (counter-2) % 6 == 0:
                try:
                    issue_number = tag.string
                except AttributeError:
                    issue_number = 'missing'
                try:
                    issue_link = tag.find('a').get('href')
                except AttributeError:
                    issue_link = 'no link'

            elif (counter-3) % 6 == 0:
                try:
                    question = tag.string
                except AttributeError:
                    question = 'missing'

            elif (counter-4) % 6 == 0:
                try:
                    result = tag.string
                except AttributeError:
                    result = 'missing'

            elif (counter-5) % 6 == 0:
                # print(tag.string,counter)
                try:
                    title = tag.string
                except AttributeError:
                    title = ''
                # let's fill the dictionary here
                if year not in self.house_roll_call_table_dict:
                    self.house_roll_call_table_dict[year] = {roll_call_number:{'roll_call_number': roll_call_number,
                                                                               'roll_call_link': roll_call_vote_link,
                                                                               'day_month': date_of_vote,
                                                                               'year': year,
                                                                               'issue': issue_number,
                                                                               'issue_link': issue_link,
                                                                               'question': question,
                                                                               'result': result,
                                                                               'title_description': title}}
                else:
                    self.house_roll_call_table_dict[year][roll_call_number] = {'roll_call_number': roll_call_number,
                                                                               'roll_call_link': roll_call_vote_link,
                                                                               'day_month': date_of_vote,
                                                                               'year': year,
                                                                               'issue': issue_number,
                                                                               'issue_link': issue_link,
                                                                               'question': question,
                                                                               'result': result,
                                                                               'title_description': title}

            counter += 1

        return

    def examine_individual_vote_pages(self, link):

        vote_session = self.sesh.get(link)
        vote_soup = BeautifulSoup(vote_session.html.html)

        # print('individual vote page link',link)
        # print(link.split('=')[1].split('&')[0])

        # not the year the vote took place in necessarily,
        # but the year that corresponds mostly to the session,
        # and that is consistent with the website labeling
        session_year = link.split('=')[1].split('&')[0]

        vote_party_totals_dict = {}
        legislator_vote_dict = {}

        vote_meta_soup = vote_soup.find('vote-metadata')
        vote_data_soup = vote_soup.find('vote-data')
        vote_total_soup = vote_meta_soup.find('vote-totals')

        try:
            vote_majority = vote_meta_soup.majority.string
        except AttributeError:
            vote_majority = ''

        try:
            vote_congress = vote_meta_soup.congress.string
        except AttributeError:
            vote_congress = ''

        try:
            vote_session = vote_meta_soup.session.string
        except AttributeError:
            vote_session = ''

        try:
            vote_chamber = vote_meta_soup.chamber.string
        except AttributeError:
            vote_chamber = ''

        try:
            vote_rollcall_num = vote_meta_soup.find('rollcall-num').string
        except AttributeError:
            vote_rollcall_num = ''

        try:
            vote_legis_num = vote_meta_soup.find('legis-num').string
        except AttributeError:
            vote_legis_num = ''

        try:
            vote_question = vote_meta_soup.find('vote-question').string
        except AttributeError:
            vote_question = ''

        try:
            vote_type = vote_meta_soup.find('vote-type').string
        except AttributeError:
            vote_type = ''

        try:
            vote_result = vote_meta_soup.find('vote-result').string
        except AttributeError:
            vote_result = ''

        try:
            vote_action_date = vote_meta_soup.find('action-date').string
            year = vote_action_date.split('-')[2]
        except AttributeError:
            vote_action_date = ''

        try:
            vote_action_time = vote_meta_soup.find('action-time').string
        except AttributeError:
            vote_action_time = ''

        try:
            vote_description = vote_meta_soup.find('vote-desc').string
        except AttributeError:
            vote_description = ''

        for tag in vote_total_soup.find_all('totals-by-party'):
            # print(tag)
            # not presently using this
            try:
                party = tag.party.string
            except AttributeError:
                party = ''
                # print(tag)
            try:
                yeas = tag.find('yea-total').string
            except AttributeError:
                yeas = ''
            try:
                nays = tag.find('nay-total').string
            except AttributeError:
                nays = ''

            try:
                present = tag.find('present-total').string
            except AttributeError:
                present = ''
            try:
                not_voting = tag.find('not-voting-total').string
            except AttributeError:
                not_voting = ''

            vote_party_totals_dict[party] = {'party': party,
                                             'yeas': yeas,
                                             'nays': nays,
                                             'present': present,
                                             'not_voting_total': not_voting}

        try:
            vote_yeas_total = vote_total_soup.find('total-by-vote').find('yea-total').string
        except AttributeError:
            vote_yeas_total = ''
        try:
            vote_nays_total = vote_total_soup.find('total-by-vote').find('nay-total').string
        except AttributeError:
            vote_nays_total = ''
        try:
            vote_present_total = vote_total_soup.find('total-by-vote').find('present-total').string
        except AttributeError:
            vote_present_total = ''
        try:
            vote_not_vote_total = vote_total_soup.find('total-by-vote').find('not-voting-total').string
        except AttributeError:
            vote_not_vote_total = ''

        #### ERROR: before 2003, they have different html

        # grabbing legislator vote information and storing to dictionary, if year>=2003
        if int(session_year) >= 2003:
            for tag in vote_data_soup.find_all('recorded-vote'):
                try:
                    name_id = tag.find('legislator').get('name-id')
                except AttributeError:
                    name_id = ''
                try:
                    party = tag.find('legislator').get('party')
                except AttributeError:
                    party = ''
                try:
                    role = tag.find('legislator').get('role')
                except AttributeError:
                    role = ''
                try:
                    state = tag.find('legislator').get('state')
                except AttributeError:
                    state = ''
                try:
                    unaccented_name = tag.find('legislator').get('unaccented-name')
                except AttributeError:
                    unaccented_name = ''
                try:
                    their_vote = tag.vote.string
                except AttributeError:
                    their_vote = ''

                legislator_vote_dict[name_id] = {'name_id': name_id,
                                                 'party': party,
                                                 'role': role,
                                                 'state': state,
                                                 'name': unaccented_name,
                                                 'vote': their_vote,
                                                 'congress': vote_congress,
                                                 'session': vote_session,
                                                 'year': year,
                                                 'date': vote_action_date,
                                                 'roll_call': vote_rollcall_num}

        # grabbing legislator vote info if year<2003
        elif int(session_year) < 2003:
            for tag in vote_data_soup.find_all('recorded-vote'):

                try:
                    party = tag.find('legislator').get('party')
                except AttributeError:
                    party = ''
                try:
                    role = tag.find('legislator').get('role')
                except AttributeError:
                    role = ''
                try:
                    state = tag.find('legislator').get('state')
                except AttributeError:
                    state = ''
                try:
                    name = tag.find('legislator').string
                except AttributeError:
                    name = ''
                try:
                    their_vote = tag.vote.string
                except AttributeError:
                    their_vote = ''

                name_id = '{}_{}'.format(name, state)

                legislator_vote_dict[name_id] = {'party': party,
                                                 'role': role,
                                                 'state': state,
                                                 'name': name,
                                                 'vote': their_vote,
                                                 'congress': vote_congress,
                                                 'session': vote_session,
                                                 'year': year,
                                                 'date': vote_action_date,
                                                 'roll_call': vote_rollcall_num}

        # write the legislators to a file
        self.write_legislators_to_csv(a_dict=legislator_vote_dict,
                                      vote_num=vote_rollcall_num,
                                      year=session_year)

        return

    def write_vote_table_to_csv(self):

        for keys in self.house_roll_call_table_dict:
            # print(keys)
            # pprint(self.house_roll_call_table_dict[keys])
            df = pd.DataFrame(self.house_roll_call_table_dict[keys])
            file_name = '{}{}{}.csv'.format(self.house_data_storage_base, 'summary_data/', keys)
            df_T = df.T
            df_T.to_csv(path_or_buf=file_name)

        return

    def write_legislators_to_csv(self, a_dict, year, vote_num):

        df = pd.DataFrame(a_dict)
        vote_dir_path = '{}{}{}/'.format(self.house_data_storage_base, 'roll_call_votes/', year)
        try:
            os.mkdir(vote_dir_path)
        except FileExistsError:
            pass
        file_name = '{}{}.csv'.format(vote_dir_path, vote_num)

        df_T = df.T

        df_T.to_csv(path_or_buf=file_name)

        return

