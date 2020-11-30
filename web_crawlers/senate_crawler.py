import os
from bs4 import BeautifulSoup
import pandas as pd
import re
import numpy as np
import requests
import urllib3
from urllib3 import util
import certifi
from requests_html import HTMLSession
import time
import datetime
from pprint import pprint


class SenateCrawler:
    # EDIT: need to adjust operation so that I can just add specific dates into the csv files

    def __init__(self, all_pages=False, congress_search=101,
                 session_search=1, only_congress_summary=False, update_mode=True):
        # headers and http probably won't be used
        self.headers = util.make_headers(accept_encoding='gzip, deflate',
                                         keep_alive=True,
                                         user_agent="Mozill/5.0 (X11; Linux x86_64; rv:47.0) Gecko/20100101 Firefox/47.0")

        self.http = urllib3.PoolManager(cert_reqs='CERT_REQUIRED',
                                        ca_certs=certifi.where())

        self.sesh = HTMLSession()

        self.senate_page_base = 'https://www.senate.gov'

        self.senate_new_votes_page = 'https://www.senate.gov/legislative/votes_new.htm'

        self.get_roll_call_lists()

        self.all_pages = all_pages

        if type(congress_search) != 'str':
            congress_search = str(congress_search)
        if type(session_search) != 'str':
            session_search = str(session_search)

        self.wanted_congress = congress_search
        self.wanted_session = session_search
        self.only_congress_summary = only_congress_summary

        # need to make variable to keep directory stuff together
        self.path_to_data = 'D:/Programming/PolySci/Polysci-Backend/prototyping/data_storage/'
        self.senate_data_path_top = self.path_to_data + 'senate_data/'

        self.xml_summary_direc = '../data_storage/senate_data/crawled_data/xml_summaries/'
        self.summaries_with_links = '../data_storage/senate_data/crawled_data/link_summaries/'
        self.senate_vote_page_direc = '../data_storage/senate_data/crawled_data/full_vote_sets/'

        self.skip_writing_to_database = False
        self.update_mode = update_mode

        if self.skip_writing_to_database:
            print('WILL NOT WRITE TO DATABASE, HAVE SET VARIABLE TO PREVENT WRITING')

        return

    def check_for_update(self, link):

        available_senate_directories = os.listdir(self.senate_vote_page_direc)

        # removing directories that don't contain relevant information
        for direc in available_senate_directories:
            if not re.search('congress', direc):
                available_senate_directories.remove(direc)

        latest_congress_session = available_senate_directories[len(available_senate_directories)-1]
        latest_congress = int(latest_congress_session.split('_')[1])
        latest_session = int(latest_congress_session.split('_')[2])

        latest_path = self.senate_vote_page_direc + latest_congress_session + '/'
        vote_files = os.listdir(latest_path)

        last_vote_number_in_database = 0
        for file in vote_files:
            if re.search('vote', file):
                current_vote_number = int(file.split('_')[1].split('.')[0])
                if current_vote_number > last_vote_number_in_database:
                    last_vote_number_in_database = current_vote_number

        last_vote_on_website = self.get_latest_vote_number_from_xml_table(htm_link=link)

        print('last vote in database = ', last_vote_number_in_database)
        print('last vote on website = ', last_vote_on_website)

        if last_vote_on_website > last_vote_number_in_database:
            should_database_update = True
            update_links_to_be_crawled = self.get_links_for_update(htm_link=link,
                                                                   congress=latest_congress,
                                                                   session=latest_session,
                                                                   vote_cutoff=last_vote_number_in_database)
        else:
            should_database_update = False

        return should_database_update, update_links_to_be_crawled

    def update_votes(self):
        # will check if an update needs to be performed, and then update local files

        roll_call_update_link = self.get_to_current_roll_call_table_link()
        should_database_update, senate_votes_for_update = self.check_for_update(link=roll_call_update_link)

        if should_database_update:
            for vote_links in senate_votes_for_update:
                print(vote_links)
                current_congress = vote_links.split('=')[1].split('&')[0]
                current_session = vote_links.split('=')[2].split('&')[0]
                self.examine_the_proposed_vote(link=vote_links,
                                               give_congress=current_congress,
                                               give_session=current_session)

        return

    def get_links_for_update(self, htm_link, congress, session, vote_cutoff):

        senate_table_dictionary = self.pull_info_from_senate_roll_call_table(link=htm_link,
                                                                             congress=congress,
                                                                             session=session)
        self.update_xml_table_summary(link=htm_link)

        senate_vote_links_to_pass = []
        senate_vote_links = senate_table_dictionary['vote_link']

        for vote_link in senate_vote_links:
            vote_number = int(vote_link.split('=')[3])
            if vote_number > vote_cutoff:
                senate_vote_links_to_pass.append(vote_link)

        return senate_vote_links_to_pass

    def pull_info_from_senate_roll_call_table(self, link, congress, session):
        # this is not for the table in xml, but for the html so I can grab the links
        # returns a dictionary with links and votes

        html_session = self.sesh.get(link)  # need this for links to next pages
        html_soup = BeautifulSoup(html_session.html.html, features='lxml')
        html_table = html_soup.table  # keeping in because it currently also performs a second function

        senate_summary_table_tag = html_soup.find('table', {'id': 'listOfVotes'})
        senate_vote_num = []
        senate_roll_call_link = []
        senate_vote_result = []
        senate_vote_desc = []
        senate_issue_num_arr = []
        senate_issue_link_arr = []
        senate_date_str = []
        for row in senate_summary_table_tag.find_all('tr'):

            cur_col = 0
            for space in row.find_all('td'):

                if cur_col == 0:
                    vote_tally = space
                    vote_num = vote_tally.a.string
                    roll_call_page_link = self.senate_page_base + vote_tally.a.get('href')

                    senate_vote_num.append(vote_num)
                    senate_roll_call_link.append(roll_call_page_link)

                elif cur_col == 1:
                    result_tag = space
                    result = result_tag.string
                    senate_vote_result.append(result)

                elif cur_col == 2:
                    description_tag = space
                    description = ''
                    desc_count = 0
                    for child in description_tag.children:
                        if child.string is not None:
                            if desc_count > 0:
                                description += '\n'
                            description += child.string
                            desc_count += 1

                    senate_vote_desc.append(description)

                elif cur_col == 3:
                    issue_tag = space
                    senate_issue_num = ''
                    senate_issue_link = ''
                    senate_row_count = 0
                    for a_tag in issue_tag.find_all('a'):
                        if senate_row_count > 0:
                            senate_issue_num += '\n'
                            senate_issue_link += '\n'
                        senate_issue_num += a_tag.string
                        senate_issue_link += a_tag.get('href')
                        senate_row_count += 1
                    senate_issue_num_arr.append(senate_issue_num)
                    senate_issue_link_arr.append(senate_issue_link)

                elif cur_col == 4:
                    date_tag = space
                    date = date_tag.string
                    senate_date_str.append(date)

                cur_col += 1

        # write link summary
        senate_link_summary_filename = '{}{}_{}_{}.csv'.format(self.summaries_with_links,
                                                               'congress', congress, session)

        senate_summary_dict = {'congress': congress, 'session': session, 'vote_number': senate_vote_num,
                               'vote_link': senate_roll_call_link, 'result': senate_vote_result,
                               'description': senate_vote_desc, 'issue': senate_issue_num_arr,
                               'issue_link': senate_issue_link_arr, 'date': senate_date_str}

        # should append this as well
        senate_summary_df = pd.DataFrame(senate_summary_dict)
        if not self.skip_writing_to_database:
            # TODO appending isn't working currently, so it should be left false
            self.write_dataframe_to_database(dataframe=senate_summary_df,
                                             file_path=senate_link_summary_filename,
                                             appending=False)

        return senate_summary_dict

    def update_xml_table_summary(self, link):
        # updates/rewrites the congress summary
        xml_link = link[:-3] + 'xml'

        xml_session = self.sesh.get(xml_link)
        xml_soup = BeautifulSoup(xml_session.html.html, 'xml')

        # making a bunch of variables for a csv now

        congress = xml_soup.congress.text
        try:
            session = xml_soup.session.text
        except AttributeError:
            # this is a known issue
            if congress == '103':
                session = '1'
            else:
                session = ''
        try:
            congress_year = xml_soup.congress_year.text
        except AttributeError:
            congress_year = ''

        vote_congress = []
        vote_session = []
        vote_year = []
        vote_nums = []
        vote_dates = []
        issues = []
        vote_questions = []
        vote_result = []
        vote_yeas = []
        vote_nays = []
        vote_title = []

        # this is all done through an xml table which lacks any html
        for vote in xml_soup.find_all('vote'):
            vote_congress.append(congress)
            vote_session.append(session)
            vote_year.append(congress_year)
            try:
                vote_number_temp = vote.vote_number.text
            except AttributeError:
                vote_number_temp = ''
            try:
                vote_date_temp = vote.vote_date.text
            except AttributeError:
                vote_date_temp = ''
            try:
                issue_temp = vote.issue.temp
            except AttributeError:
                issue_temp = ''
            try:
                vote_question_temp = vote.question.text
            except AttributeError:
                vote_question_temp = ''
            try:
                vote_result_temp = vote.result.text
            except AttributeError:
                vote_result_temp = ''
            try:
                vote_yeas_temp = vote.yeas.text
            except AttributeError:
                vote_yeas_temp = ''
            try:
                vote_nays_temp = vote.nays.text
            except AttributeError:
                vote_nays_temp = ''
            try:
                vote_title_temp = vote.title.text
            except AttributeError:
                vote_title_temp = ''

            vote_nums.append(vote_number_temp)
            vote_dates.append(vote_date_temp)
            issues.append(issue_temp)
            vote_questions.append(vote_question_temp)
            vote_result.append(vote_result_temp)
            vote_yeas.append(vote_yeas_temp)
            vote_nays.append(vote_nays_temp)
            vote_title.append(vote_title_temp)

        # I don't think these should be here right now
        congress_dict = {'congress': vote_congress, 'session': vote_session, 'year': vote_year,
                         'vote_number': vote_nums, 'dates': vote_dates, 'issue': issues,
                         'question': vote_questions, 'result': vote_result, 'yeas': vote_yeas,
                         'nays': vote_nays, 'title': vote_title}

        congress_df = pd.DataFrame(congress_dict)
        congress_directory = self.xml_summary_direc + 'congress_' + congress + '_' + session
        self.create_directory(path=congress_directory)
        congress_fname = congress_directory + '/congress_' + congress + '_' + session + '_xml_table.csv'

        if not self.skip_writing_to_database:
            self.write_dataframe_to_database(dataframe=congress_df,
                                             file_path=congress_fname,
                                             appending=False)

        return

    def get_latest_vote_number_from_xml_table(self, htm_link):

        xml_link = htm_link[:-3] + 'xml'
        xml_session = self.sesh.get(xml_link)
        xml_soup = BeautifulSoup(xml_session.html.html, 'xml')

        vote_tag = xml_soup.find('vote_number')
        vote_num = int(vote_tag.string)

        return vote_num

    def get_to_current_roll_call_table_link(self):

        current_senate_soup = self.get_soup(link=self.senate_new_votes_page)
        for tag in current_senate_soup.find_all('a'):
            try:
                tag_text_check = tag.string
                if re.search('Detailed Session List', tag_text_check):
                    roll_call_update_link = self.senate_page_base + tag.get('href')
                    break
            except (AttributeError, TypeError):
                pass

        return roll_call_update_link

    def get_roll_call_lists(self):
        senate_roll_call_tables_page = 'https://www.senate.gov/legislative/common/generic/roll_call_lists.htm'
        senate_roll_call_table_sesh = self.sesh.get(senate_roll_call_tables_page)
        senate_roll_call_tables_soup = BeautifulSoup(senate_roll_call_table_sesh.html.html, features='lxml')

        self.roll_call_html_links = []

        senate_roll_call_story = senate_roll_call_tables_soup.full_story
        for tags in senate_roll_call_story.find_all('a'):
            self.roll_call_html_links.append(tags.get('href'))

        for i in range(0, len(self.roll_call_html_links)):
            self.roll_call_html_links[i] = self.senate_page_base + self.roll_call_html_links[i]

        # getting the latest page too, which isn't on this page
        session_value = self.roll_call_html_links[0][-5]
        congress_number = int(self.roll_call_html_links[0][-9:-6])

        if session_value == '1':
            self.current_roll_call = self.roll_call_html_links[0][:-5] + '2' + self.roll_call_html_links[0][-4:]

        elif session_value == '2':
            congress_number += 1
            self.current_roll_call = self.roll_call_html_links[0][:-9] + \
                                     str(congress_number) + self.roll_call_html_links[0][-6:]

        else:
            print('value error in senate roll call links. Check get_roll_call_lists')
            raise ValueError

        return

    def gather_old_data(self):
        # this will be the loop to go through all of the old roll calls
        # a similar function will be created for updating on the most recent roll call too

        # the function update now allows for pointed data gathering, and better debugging

        if self.all_pages:
            for link in self.roll_call_html_links:

                time.sleep(0.5)
                self.examine_roll_call_votes_page(link=link)

        else:
            is_roll_there = False
            for link in self.roll_call_html_links:
                cur_congress_num = link.split('_')[4]
                cur_session_num = link.split('_')[5].split('.')[0]
                if self.wanted_congress == cur_congress_num and self.wanted_session == cur_session_num:
                    print('in if statement')
                    wanted_link = link
                    is_roll_there = True
                    break

            if is_roll_there:
                self.examine_roll_call_votes_page(link=wanted_link)
            else:
                print('desired congress session was not found')
                print('function ended')
                print(self.roll_call_html_links)
                return

        return

    def examine_roll_call_votes_page(self, link):
        # looks at the table of votes put forth in given congress
        # will likely rewrite/refactor some of this later

        # The top portion of this might be unnecessary now that I collect data from
        # the html tables

        xml_link = link[:-3] + 'xml'

        xml_session = self.sesh.get(xml_link)
        xml_soup = BeautifulSoup(xml_session.html.html, 'xml')

        # making a bunch of variables for a csv now

        congress = xml_soup.congress.text
        try:
            session = xml_soup.session.text
        except AttributeError:
            # this is a known issue
            if congress == '103':
                session = '1'
            else:
                session = ''
        try:
            congress_year = xml_soup.congress_year.text
        except AttributeError:
            congress_year = ''

        vote_congress = []
        vote_session = []
        vote_year = []
        vote_nums = []
        vote_dates = []
        issues = []
        vote_questions = []
        vote_result = []
        vote_yeas = []
        vote_nays = []
        vote_title = []

        # this is all done through an xml table which lacks any html
        for vote in xml_soup.find_all('vote'):
            vote_congress.append(congress)
            vote_session.append(session)
            vote_year.append(congress_year)
            try:
                vote_number_temp = vote.vote_number.text
            except AttributeError:
                vote_number_temp = ''
            try:
                vote_date_temp = vote.vote_date.text
            except AttributeError:
                vote_date_temp = ''
            try:
                issue_temp = vote.issue.temp
            except AttributeError:
                issue_temp = ''
            try:
                vote_question_temp = vote.question.text
            except AttributeError:
                vote_question_temp = ''
            try:
                vote_result_temp = vote.result.text
            except AttributeError:
                vote_result_temp = ''
            try:
                vote_yeas_temp = vote.yeas.text
            except AttributeError:
                vote_yeas_temp = ''
            try:
                vote_nays_temp = vote.nays.text
            except AttributeError:
                vote_nays_temp = ''
            try:
                vote_title_temp = vote.title.text
            except AttributeError:
                vote_title_temp = ''

            vote_nums.append(vote_number_temp)
            vote_dates.append(vote_date_temp)
            issues.append(issue_temp)
            vote_questions.append(vote_question_temp)
            vote_result.append(vote_result_temp)
            vote_yeas.append(vote_yeas_temp)
            vote_nays.append(vote_nays_temp)
            vote_title.append(vote_title_temp)

            # this format goes to a dataframe very nicely
            congress_dict = {'congress': vote_congress, 'session': vote_session, 'year': vote_year,
                             'vote_number': vote_nums, 'dates': vote_dates, 'issue': issues,
                             'question': vote_questions, 'result': vote_result, 'yeas': vote_yeas,
                             'nays': vote_nays, 'title': vote_title}

            congress_df = pd.DataFrame(congress_dict)
            congress_directory = self.xml_summary_direc + 'congress_' + congress + '_' + session
            self.create_directory(path=congress_directory)
            congress_fname = congress_directory + '/congress_' + congress + '_' + session + '_xml_table.csv'

            if not self.skip_writing_to_database:
                # congress_df.to_csv(index=False, path_or_buf=congress_fname)
                self.write_dataframe_to_database(dataframe=congress_df,
                                                 file_path=congress_fname,
                                                 appending=False)

        # ----------------------------------------------------------------------
        # ----------------------------------------------------------------------
        # could consider splitting this into smaller functions
        # getting links for next pages

        html_session = self.sesh.get(link)  # need this for links to next pages
        html_soup = BeautifulSoup(html_session.html.html, features='lxml')
        html_table = html_soup.table  # keeping in because it currently also performs a second function

        senate_summary_table_tag = html_soup.find('table', {'id': 'listOfVotes'})
        senate_vote_num = []
        senate_roll_call_link = []
        senate_vote_result = []
        senate_vote_desc = []
        senate_issue_num_arr = []
        senate_issue_link_arr = []
        senate_date_str = []
        for row in senate_summary_table_tag.find_all('tr'):

            cur_col = 0
            for space in row.find_all('td'):

                if cur_col == 0:
                    vote_tally = space
                    vote_num = vote_tally.a.string
                    roll_call_page_link = self.senate_page_base + vote_tally.a.get('href')

                    senate_vote_num.append(vote_num)
                    senate_roll_call_link.append(roll_call_page_link)

                elif cur_col == 1:
                    result_tag = space
                    result = result_tag.string
                    senate_vote_result.append(result)

                elif cur_col == 2:
                    description_tag = space
                    description = ''
                    # description = []
                    desc_count = 0
                    for child in description_tag.children:
                        if child.string is not None:
                            # description.append(child.string)
                            if desc_count > 0:
                                description += '\n'
                            description += child.string
                            desc_count += 1

                    senate_vote_desc.append(description)

                elif cur_col == 3:
                    issue_tag = space
                    # senate_issue_num = []
                    # senate_issue_link = []
                    senate_issue_num = ''
                    senate_issue_link = ''
                    senate_row_count = 0
                    for a_tag in issue_tag.find_all('a'):
                        if senate_row_count > 0:
                            senate_issue_num += '\n'
                            senate_issue_link += '\n'
                        senate_issue_num += a_tag.string
                        senate_issue_link += a_tag.get('href')
                        senate_row_count += 1
                        # senate_issue_num.append(a_tag.string)
                        # senate_issue_link.append(a_tag.get('href'))
                    senate_issue_num_arr.append(senate_issue_num)
                    senate_issue_link_arr.append(senate_issue_link)

                elif cur_col == 4:
                    date_tag = space
                    date = date_tag.string
                    senate_date_str.append(date)

                cur_col += 1

        # write link summary
        senate_link_summary_filename = '{}{}_{}_{}.csv'.format(self.summaries_with_links,
                                                               'congress', congress, session)

        senate_summary_dict = {'congress': congress, 'session': session, 'vote_number': senate_vote_num,
                               'vote_link': senate_roll_call_link, 'result': senate_vote_result,
                               'description': senate_vote_desc, 'issue': senate_issue_num_arr,
                               'issue_link': senate_issue_link_arr, 'date': senate_date_str}

        senate_summary_df = pd.DataFrame(senate_summary_dict)
        if not self.skip_writing_to_database:
            self.write_dataframe_to_database(dataframe=senate_summary_df,
                                             file_path=senate_link_summary_filename,
                                             appending=True)

        vote_links = []
        issue_links = []  # not using just yet
        # EDIT: this for loop should be removed soon due to change in method
        for tags in html_table.find_all('a'):

            if tags.get('href')[0] == '/':
                vote_links.append(self.senate_page_base + tags.get('href'))
            else:
                issue_links.append(tags.get('href'))

        if self.only_congress_summary:
            return

        for link in vote_links:
            time.sleep(0.1)  # might be too small
            self.examine_the_proposed_vote(link=link, give_congress=congress, give_session=session)

        return

    def examine_the_proposed_vote(self, link, give_congress, give_session):
        # pulls voting information from the xml page of the vote

        html_session = self.sesh.get(link)
        html_soup = BeautifulSoup(html_session.html.html, features='lxml')

        xml_link = ''
        for tags in html_soup.find_all('a'):
            middle_string = tags.text.split(' ')

            if len(middle_string) >= 2 and middle_string[1] == 'XML':
                xml_link = self.senate_page_base + tags.get('href')

        xml_vote_number = link[-5:]
        if len(xml_link) < 35:
            xml_link = 'https://www.senate.gov/legislative/LIS/roll_call_votes/vote' + \
                               give_congress + give_session + '/vote_' + give_congress + \
                               '_' + give_session + '_' + xml_vote_number + '.xml'
            print(link)
            print(xml_link)

        xml_session = self.sesh.get(xml_link)
        xml_soup = BeautifulSoup(xml_session.html.html, 'xml')

        congress = xml_soup.congress.text
        session = xml_soup.session.text

        try:
            year = xml_soup.congress_year.text
        except AttributeError:
            print(link)
            print(xml_link)
            print('failed to get year')
            year = ''

        vote_number = xml_soup.vote_number.text
        try:
            vote_date = xml_soup.vote_date.text
        except AttributeError:
            print(link)
            print(xml_link)
            print('failed to get vote date')
            vote_date = ''
        try:
            modify_date = xml_soup.modify_date.text
        except AttributeError:
            modify_date = ''

        try:
            vote_question_text = xml_soup.vote_question_text.text
        except AttributeError:
            vote_question_text = ''
        try:
            vote_document_text = xml_soup.vote_document_text.text
        except AttributeError:
            vote_document_text = ''
        try:
            vote_result_text = xml_soup.vote_result_text.text
        except AttributeError:
            vote_result_text = ''
        try:
            question = xml_soup.question.text
        except AttributeError:
            question = ''

        try:
            vote_title = xml_soup.vote_title.text
        except AttributeError:
            vote_title = ''
        try:
            majority_requirement = xml_soup.majority_requirement.text
        except AttributeError:
            majority_requirement = ''
        try:
            vote_result = xml_soup.vote_result.text
        except AttributeError:
            vote_result = ''

        try:
            document_congress = xml_soup.document_congress.text
        except AttributeError:
            document_congress = ''
        try:
            document_type = xml_soup.document_type.text
        except AttributeError:
            document_type = ''
        try:
            document_number = xml_soup.document_number.text
        except AttributeError:
            document_number = ''
        try:
            document_name = xml_soup.document_name.text
        except AttributeError:
            document_name = ''
        try:
            document_title = xml_soup.document_title.text
        except AttributeError:
            document_title = ''
        try:
            document_short_title = xml_soup.document_short_title.text
        except AttributeError:
            document_short_title = ''

        try:
            amendment_number = xml_soup.amendment_number.text
        except AttributeError:
            amendment_number = ''
        try:
            amendment_to_number = xml_soup.amendment_to_amendment_number.text
        except AttributeError:
            amendment_to_number = ''
        try:
            atatan = xml_soup.amendment_to_amendment_to_amendment_number.text
        except AttributeError:
            atatan = ''
        try:
            amendment_to_document_number = xml_soup.amendment_to_document_number.text
        except AttributeError:
            amendment_to_document_number = ''
        try:
            amendment_to_document_short_title = xml_soup.amendment_to_document_short_title.text
        except AttributeError:
            amendment_to_document_short_title = ''
        try:
            amendment_purpose = xml_soup.amendment_purpose.text
        except AttributeError:
            amendment_purpose = ''

        try:
            yeas = xml_soup.yeas.text
        except AttributeError:
            yeas = ''
        try:
            nays = xml_soup.nays.text
        except AttributeError:
            nays = ''
        try:
            present = xml_soup.present.text
        except AttributeError:
            present = ''
        try:
            absent = xml_soup.absent.text
        except AttributeError:
            absent = ''

        try:
            who_broke_tie = xml_soup.tie_breaker.by_whom.text
        except AttributeError:
            who_broke_tie = ''
        try:
            tie_break_vote = xml_soup.tie_breaker.tie_breaker_vote.text
        except AttributeError:
            tie_break_vote = ''

        # on to senate votes
        last_name = []
        first_name = []
        party = []
        state = []
        vote_cast = []
        lis_member_id = []
        i = 0

        for members in xml_soup.members:
            try:
                last_name.append(members.last_name.text)
                first_name.append(members.first_name.text)
                party.append(members.party.text)
                state.append(members.state.text)
                vote_cast.append(members.vote_cast.text)
                lis_member_id.append(members.lis_member_id.text)
            except AttributeError:
                pass

        # EDIT: could add info in here to make managing the database easier, but I might end up
        # working around it, so this comment may be meaningless
        votes_dict = {'last_name': last_name, 'first_name': first_name, 'party': party,
                      'state': state, 'vote_cast': vote_cast, 'lis_member_id': lis_member_id}
        votes_df = pd.DataFrame(votes_dict)
        # votes_fname = 'data_storage/congress_' + congress + '_' + session + '/vote_' + vote_number + '.csv'
        vote_direc = self.senate_vote_page_direc + 'congress_' + congress + '_' + session + '/'
        self.create_directory(vote_direc)
        votes_fname = vote_direc + 'vote_' + vote_number + '.csv'

        if not self.skip_writing_to_database:
            # votes_df.to_csv(index=False, path_or_buf=votes_fname)
            self.write_dataframe_to_database(dataframe=votes_df,
                                             file_path=votes_fname,
                                             appending=False)

        return

    @staticmethod
    def create_directory(path):

        try:
            os.mkdir(path=path)
        except FileExistsError:
            pass

        return

    def get_soup(self, link):
        # a function to get the soup back from an html link
        sesh = self.sesh.get(link)
        soup = BeautifulSoup(sesh.html.html)
        return soup

    def print_list(self):
        # this is just a testing function
        print(self.current_roll_call)
        for links in self.roll_call_html_links:
            print(links)

        return

    @staticmethod
    def write_dataframe_to_database(dataframe, file_path, appending):

        if appending:
            header = False
            mode = 'a'
        else:
            header = True
            mode = 'w'

        dataframe.to_csv(index=False, path_or_buf=file_path, header=header, mode=mode)

        return

