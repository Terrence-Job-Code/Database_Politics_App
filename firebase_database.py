import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import pandas as pd
import numpy as np
import os
import datetime
from pprint import pprint
from datetime import date
import unicodedata
import time
from prototyping.utils import dictionary_functions
from prototyping.utils import standardize_index, whatismyname
from prototyping.utils import text_cleaning, constants
import re


class Database:

    def __init__(self):

        if not firebase_admin._apps:
            cred = credentials.Certificate(constants.json_location)
            default_app = firebase_admin.initialize_app(cred)

        self.db = firestore.client()
        self.latest_updates = []  # some kind of reference
        self.batch_size = 0
        self.number_of_writes = 0
        self.writes_of_all_updates = 0

        self.batch = self.db.batch()

        return

    def query_documents_from_collection(self, collection_name, max_documents=10, use_max=False):

        docs = self.db.collection(collection_name).stream()

        i = 0
        for doc in docs:
            print('{} -> {}'.format(doc.id, doc.to_dict()))
            if use_max and i > max_documents:
                break

            i += 1
        # another way of accessing
        # coller = self.db.collection('Senators').document('S009').get()
        # pprint(coller.to_dict())

        return

    # TODO: not presently using the check_doc_exists functions
    def check_document_exist(self, collection_name, document_name):
        # function may not be necessary, but it's not a bad one to have

        coller = self.db.collection(collection_name).document(document_name).get()
        if coller:
            document_exists = True
        else:
            document_exists = False

        return document_exists

    def check_subdoc_exists(self, collection_name, document_name, sub_coll_name, sub_doc_name):
        # this function may go away

        sub_doc = self.db.collection(collection_name).document(document_name).collection(sub_coll_name).document(sub_doc_name).get()

        if sub_doc:
            doc_exists = True
        else:
            doc_exists = False

        return doc_exists

    def choose_collection(self, collection_name):
        self.collection = self.db.collection(collection_name)
        return

    def choose_document(self, document_name):
        self.document = self.collection.document(document_name)
        return

    def set_document(self, collection_name, document_name, doc_dict):

        self.choose_collection(collection_name=collection_name)
        self.document = self.collection.document(document_name)
        self.document.set(doc_dict)

        return

    def update_document(self, collection_name, document_name, doc_dict):
        # there may not be much need for this just yet
        self.choose_collection(collection_name=collection_name)
        self.document = self.collection.document(document_name)
        self.document.update(doc_dict)

        return

    def write_document(self, write_flag, collection_name, document_name, doc_dict):

        # TODO!!
        # there may be no way around the fact that I have to see if a document is actually
        # written in the database, but this shouldn't take too many reads

        if write_flag == 'set':
            self.set_document(collection_name=collection_name, document_name=document_name, doc_dict=doc_dict)
            self.batch_size += 1
            self.early_batch_commit()
            self.number_of_writes += 1
            self.writes_of_all_updates += 1
        elif write_flag == 'update':
            self.update_document(collection_name=collection_name, document_name=document_name, doc_dict=doc_dict)
            self.batch_size += 1
            self.early_batch_commit()
            self.number_of_writes += 1
            self.writes_of_all_updates += 1
        elif write_flag == 'pass':
            print('senator up to date')
            return
        else:
            print('proper flag not provided, aborting run')
            raise ValueError

        return

    def set_subdocument(self, collection_name, document_name, sub_coll_name, sub_doc_name, sub_doc_dict):

        if not self.collection:
            self.choose_collection(collection_name=collection_name)
        if not self.document:
            self.choose_document(document_name=document_name)

        self.sub_doc = self.document.collection(sub_coll_name).document(sub_doc_name)
        self.batch.set(self.sub_doc, sub_doc_dict)

        return

    def update_subdocument(self, collection_name, document_name, sub_coll_name, sub_doc_name, sub_doc_dict):

        if not self.collection:
            self.choose_collection(collection_name=collection_name)
        if not self.document:
            self.choose_document(document_name=document_name)

        self.sub_doc = self.document.collection(sub_coll_name).document(sub_doc_name)
        self.batch.update(self.sub_doc, sub_doc_dict)

        return

    def write_subdocument(self, collection_name, document_name, sub_coll_name,
                          sub_doc_name, sub_doc_dict, write_flag):

        if re.search('/', sub_doc_name):
            sub_doc_name = re.sub('/', ' and ', sub_doc_name)

        flag = write_flag['flag']
        if flag == 'set':
            self.set_subdocument(collection_name=collection_name,
                                 document_name=document_name,
                                 sub_coll_name=sub_coll_name,
                                 sub_doc_name=sub_doc_name,
                                 sub_doc_dict=sub_doc_dict)
            self.batch_size += 1
            self.early_batch_commit()
            self.number_of_writes += 1
            self.writes_of_all_updates += 1
        elif flag == 'update':
            self.update_subdocument(collection_name=collection_name,
                                    document_name=document_name,
                                    sub_coll_name=sub_coll_name,
                                    sub_doc_name=sub_doc_name,
                                    sub_doc_dict=sub_doc_dict)
            self.batch_size += 1
            self.early_batch_commit()
            self.number_of_writes += 1
            self.writes_of_all_updates += 1
        else:
            print('improper subdocument flag')
            print(write_flag)
            print(flag)
            raise ValueError

        return

    def early_batch_commit(self):
        # going to try this to see if this helps
        # won't write to local data files until finished though

        if self.batch_size > 100:
            self.batch.commit()
            self.batch_size = 0
            # self.batch = self.db.batch() # commented out because I don't think I should need to reinitialize it

        return

    def batch_commit(self, df, file_path):
        # going to need to call this sooner it seems
        print('number of writes in batch = ', self.batch_size)  # not really so relevant anymore
        print('number of writes for this rep = ', self.number_of_writes)
        print('total number of writes = ', self.writes_of_all_updates)
        try:
            self.batch.commit()
            self.update_logger(df=df, file_path=file_path)

            self.batch_size = 0
            self.number_of_writes = 0

        # TODO: should find an exception error, add this to the log
        except:
            print('failed and I do not know the error, so retry to check for the fail')
            raise ValueError

        return

    def delete_collection_and_subcollection(self, collection_name, subcollection_name):
        # TODO this is no longer necessary, as deleting the document deletes all subdocuments now!
        # deletes a specific subcollection and collection
        # need another function to just delete a given subcollection
        # this function might no longer be necessary
        docs = self.db.collection(collection_name).stream()

        for doc in docs:
            sub_docs = self.db.collection(collection_name).document(doc.id).collection(subcollection_name).stream()
            for sub_doc in sub_docs:
                sub_doc.reference.delete()
            doc.reference.delete()

        return

    def delete_collection(self, collection_name):

        docs = self.db.collection(collection_name).stream()
        for doc in docs:
            doc.reference.delete()

        return

    def delete_subcollection(self, collection_name, subcollection_name):
        deleted = 0
        batch_size = 500
        docs = self.db.collection(collection_name).stream()
        for doc in docs:
            sub_docs = self.db.collection(collection_name).document(doc.id).collection(subcollection_name).limit(batch_size).stream()
            for sub_doc in sub_docs:
                sub_doc.reference.delete()
                deleted += 1
                if deleted >= batch_size:
                    time.sleep(2)
                    return self.delete_subcollection(collection_name=collection_name,
                                                     subcollection_name=subcollection_name)
        return

    @staticmethod
    def update_logger(df, file_path):

        # this might be too specific at the moment
        if 'database_upload_date' in df:
            # df.loc[df['database_upload_date']==np.nan] = datetime.datetime.now()
            # TODO:: switch to the suggested edit to get rid of the warning
            # but this works for now
            df['database_upload_date'].loc[df['database_upload_date'].isna()==True] = datetime.datetime.now()
        else:
            df['database_upload_date'] = datetime.datetime.now()
        # print(df.head(10))

        df.to_csv(path_or_buf=file_path, index=False)

        return


class Senate:

    def __init__(self, last_name, first_name, lis_member_id,
                 party, state, time_in_congress='NA', age='NA',
                 overwrite=False):
        # created a file that has the info I directly want
        self.last_name = last_name
        self.first_name = first_name

        self.party = party
        self.state = state
        self.time_in_congress = time_in_congress
        self.age = age

        self.unique_id = lis_member_id

        self.keywords = []  # for searching in database

        self.collection_name = None
        self.document_name = None
        self.sub_collection = None
        self.id_file_path = None
        self.sub_collection_name = None
        self.dataframe_to_write = None
        self.cutoff_year = None

        self.class_specific_declarations()

        # need a flag for updating or setting
        self.document_write_flag = 'update'  # should be update or set
        self.overwrite = overwrite
        self.is_there_cutoff_year = False

        # need an overwrite flag in both objects
        self.vote_dict = {}
        self.subdoc_write_flag = {}  # just give it the index

        self.pull_voting_record()
        self.make_voting_record_timestamp()

        return

    def class_specific_declarations(self):
        # a function to minimize how much I need to rewrite
        self.collection_name = 'Senators'
        self.document_name = self.unique_id
        self.sub_collection = 'vote_record_briefs'
        # local file path for loading voting records
        self.id_file_path = '{}/{}.csv'.format(constants.senate_rep_votes, self.unique_id)

        return

    def to_dict(self):
        # to_dict is for the representative, not their votes
        self.generate_keywords()

        this_dict = {'lis_member_id': self.unique_id,
                     'last_name': self.last_name,
                     'first_name': self.first_name,
                     'party': self.party,
                     'state': self.state,
                     'time_in_senate': self.time_in_congress,
                     'age': self.age,
                     'upload_time': datetime.datetime.now(),
                     'keywords': self.keywords}

        return this_dict

    def generate_keywords(self):
        # need to start thinking more about this, and how to get all the variants I could want

        start_search = '{} {} {}'.format(self.first_name, self.last_name, self.state)
        search_string = ''
        for letter in start_search:
            search_string = '{}{}'.format(search_string, letter)
            # print(search_string)
            self.keywords.append(search_string.lower())

        return

    def get_collection_name(self):

        return self.collection_name

    def get_document_name(self):

        return self.document_name

    def get_sub_collection_name(self):

        self.sub_collection_name = 'voting_record'

        return self.sub_collection_name

    def get_list_sub_doc_names(self):

        return self.vote_dict.keys()

    def pull_voting_record(self):
        votes_df = pd.read_csv(filepath_or_buffer=self.id_file_path)
        date_obj = []

        for row in votes_df.itertuples():
            year = int(row.year_day.split('-')[0])
            month = int(row.year_day.split('-')[1])
            day = int(row.year_day.split('-')[2])
            date_obj.append(datetime.date(year=year, month=month, day=day))

        votes_df['date_obj'] = date_obj
        votes_df.sort_values(by='date_obj', inplace=True, ascending=False)
        database_upload_date_name = 'database_upload_date'

        # TODO: This could be an issue, may wish to reconsider the structure of this method
        if database_upload_date_name in votes_df:
            self.document_write_flag = 'update'
            col_there = True
        else:
            self.document_write_flag = 'set'
            col_there = False

        if self.overwrite:
            self.document_write_flag = 'set'
            col_there = False

        # filling the voting dictionary
        if not col_there:
            for row in votes_df.itertuples():
                year_string = row.year_day
                year_month = year_string[:7]

                self.fill_vote_dict(df_row=row)

                self.subdoc_write_flag[year_month] = {'flag': 'set'}

        # if the date column is there
        # don't currently have a method for if it is up to date
        else:
            for row in votes_df.itertuples():
                year_string = row.year_day
                year_month = year_string[:7]

                # need a flag to not update if all year_month are update
                if pd.isna(row.database_upload_date):
                    self.fill_vote_dict(df_row=row)
                    self.subdoc_write_flag[year_month] = {'flag': 'set'}
                else:
                    self.subdoc_write_flag[year_month] = {'flag': 'update'}

        self.dataframe_to_write = votes_df.copy()

        return

    def is_up_to_date(self):

        update = False

        return update

    def fill_vote_dict(self, df_row):
        # function to refactor for loop for vote dict
        issue = df_row.issue
        index = standardize_index.standardize_index(df_row.index)
        question = df_row.question
        result = df_row.result
        title = df_row.title
        vote_cast = df_row.vote_cast
        year_string = df_row.year_day  # yyyy-mm-dd
        year_month = year_string[:7]

        # to only update for so recent a time
        year_int = int(year_month.split('-')[0])
        if self.is_there_cutoff_year and year_int < self.cutoff_year:
            return

        year_int = int(year_string.split('-')[0])
        month_int = int(year_string.split('-')[1])
        day_int = int(year_string.split('-')[2])
        vote_date = datetime.datetime(year=year_int,
                                      month=month_int,
                                      day=day_int,
                                      hour=15,
                                      minute=30,
                                      second=0)

        current_date = datetime.datetime.now()

        if year_month not in self.vote_dict:
            self.vote_dict[year_month] = {index: {'issue': issue,
                                                  'index': index,
                                                  'question': question,
                                                  'result': result,
                                                  'title': title,
                                                  'vote_cast': vote_cast,
                                                  'date_of_vote': vote_date,
                                                  'upload_date': current_date}}
        else:
            self.vote_dict[year_month][index] = {'issue': issue,
                                                 'index': index,
                                                 'question': question,
                                                 'result': result,
                                                 'title': title,
                                                 'vote_cast': vote_cast,
                                                 'date_of_vote': vote_date,
                                                 'upload_date': current_date}

        return

    def give_cutoff_year(self, year):
        # won't write for a given year if it is below this threshold
        self.cutoff_year = year
        self.is_there_cutoff_year = True

        return

    def make_voting_record_timestamp(self):
        # this is important for zach's ability to easily access the votes

        for key in self.vote_dict.keys():
            year = int(key.split('-')[0])
            month = int(key.split('-')[1])
            year_month_stamp = datetime.datetime(year=year, month=month, day=3)

            self.vote_dict[key]['timestamp'] = year_month_stamp
            self.vote_dict[key]['timestamp_string'] = key

        return

    # while these functions aren't necessary, I prefer a C style method for accessing
    # class data objects
    def show_voting_record(self):

        return self.vote_dict

    def show_document_flag(self):

        return self.document_write_flag

    def show_subdocument_flag(self):

        return self.subdoc_write_flag

    def show_dataframe_for_write(self):

        return self.dataframe_to_write

    def show_file_path(self):

        return self.id_file_path


class House(Senate):

    def class_specific_declarations(self):
        # a function to minimize how much I need to rewrite
        self.collection_name = 'House'
        # document name might be better if instead of the state, I put the district behind their name
        self.document_name = '{}_{}'.format(self.first_name, self.unique_id)
        self.sub_collection = 'voting_record'
        # local file path for loading voting records
        self.id_file_path = '{}/{}.csv'.format(constants.house_representative_votes_new, self.unique_id)
        # this shouldn't be necessary anymore, as this has been taken care of now in a previous file
        self.id_file_path = text_cleaning.strip_accents(self.id_file_path)
        first_name_no_accent = text_cleaning.strip_accents(self.first_name)
        self.name_id = '{}_{}'.format(first_name_no_accent, self.unique_id)

        return

    def to_dict(self):

        self.generate_keywords()

        this_dict = {'name_id': self.name_id,
                     'last_name': self.last_name,
                     'first_name': self.first_name,
                     'party': self.party,
                     'state': self.state,
                     'time_in_house': self.time_in_congress,
                     'age': self.age,
                     'upload_time': datetime.datetime.now(),
                     'keywords': self.keywords}

        return this_dict

    # need to fix this so it doesn't remain in this class
    def pull_voting_record(self):

        test_path = self.id_file_path.split(' ')
        print(test_path)
        votes_df = pd.read_csv(filepath_or_buffer=self.id_file_path)
        date_obj = []
        vote_datetime = []

        today_date = datetime.datetime.now()
        fix_by_date = datetime.datetime(year=2020, month=10, day=5, hour=0,
                                        minute=0, second=0, microsecond=0)
        if today_date >= fix_by_date:
            print('merge the vote formats for representatives to the same format')
            print('and get rid of the repetitive code')
            raise ValueError

        print(votes_df.head())

        for row in votes_df.itertuples():
            # year = int(row.year_month_day.split('-')[0])
            # month = int(row.year_month_day.split('-')[1])
            # day = int(row.year_month_day.split('-')[2])
            # date_obj.append(datetime.date(year=year, month=month, day=day))
            vote_datetime.append(row.datetime)

        votes_df['date_obj'] = vote_datetime
        votes_df.sort_values(by='date_obj', inplace=True, ascending=False)
        database_upload_date_name = 'database_upload_date'

        if database_upload_date_name in votes_df:
            self.document_write_flag = 'update'
            col_there = True
        else:
            self.document_write_flag = 'set'
            col_there = False

        if self.overwrite:
            self.document_write_flag = 'set'
            col_there = False

        # filling the voting dictionary
        if not col_there:
            for row in votes_df.itertuples():
                # row.datetime is read as a string
                vote_date = row.datetime
                year_string = vote_date.split('-')[0]
                month_string = vote_date.split('-')[1]
                year_month = '{}-{}'.format(year_string, month_string)

                self.fill_vote_dict(df_row=row)

                self.subdoc_write_flag[year_month] = {'flag': 'set'}

        # if the date column is there
        # don't currently have a method for if it is up to date
        else:
            for row in votes_df.itertuples():
                # year_string = row.year_month_day
                # year_month = year_string[:7]
                vote_date = row.datetime
                year_string = vote_date.split('-')[0]
                month_string = vote_date.split('-')[1]
                year_month = '{}-{}'.format(year_string, month_string)

                # need a flag to not update if all year_month are update
                if pd.isna(row.database_upload_date):
                    self.fill_vote_dict(df_row=row)
                    self.subdoc_write_flag[year_month] = {'flag': 'set'}
                else:
                    self.subdoc_write_flag[year_month] = {'flag': 'update'}

        self.dataframe_to_write = votes_df.copy()

        return

    def fill_vote_dict(self, df_row):
        # function to refactor for loop for vote dict
        # issue = df_row.issue
        issue = df_row.bill_number
        index = standardize_index.standardize_index(df_row.vote_index)
        question = df_row.question
        # result = df_row.result
        result = df_row.vote_status
        title = df_row.bill_description
        # title = df_row.title
        vote_cast = df_row.vote
        vote_date = df_row.datetime
        # year_string = df_row.year_month_day
        year_month = vote_date[:7]

        vote_datetime = datetime.datetime(year=int(vote_date.split('-')[0]),
                                          month=int(vote_date.split('-')[1]),
                                          day=int(vote_date.split('-')[2].split(' ')[0]),
                                          hour=int(vote_date.split(' ')[1].split(':')[0]),
                                          minute=int(vote_date.split(':')[1]),
                                          second=int(vote_date.split(':')[2].split('-')[0]))

        # to only update for so recent a time
        year_int = int(year_month.split('-')[0])
        if self.is_there_cutoff_year and year_int < self.cutoff_year:
            return

        current_date = datetime.datetime.now()

        if year_month not in self.vote_dict:
            self.vote_dict[year_month] = {index: {'issue': issue,
                                                  'index': index,
                                                  'question': question,
                                                  'result': result,
                                                  'title': title,
                                                  'vote_cast': vote_cast,
                                                  'date_of_vote': vote_datetime,
                                                  'upload_date': current_date}}
        else:
            self.vote_dict[year_month][index] = {'issue': issue,
                                                 'index': index,
                                                 'question': question,
                                                 'result': result,
                                                 'title': title,
                                                 'vote_cast': vote_cast,
                                                 'date_of_vote': vote_datetime,
                                                 'upload_date': current_date}

        return


class Bills:
    # may want to split up bills into various actions later
    # at least between bills and pn actions

    def __init__(self, title, issue_number, issue_type, sponsor, status,
                 status_history, topic, vote_totals, senate_votes, house_votes,
                 congress, session, vote_numbers, senate_index, house_index,
                 key, summary, bill_action_dates, bill_action_display_texts,
                 bill_action_descriptions, pdf_downloaded, xml_downloaded,
                 txt_downloaded, standardized_issue, issue_title, long_heading):

        self.congress = congress
        self.session = session
        self.vote_numbers = vote_numbers

        self.title = title
        self.issue_number = issue_number
        self.issue_type = issue_type

        self.sponsor = sponsor
        self.status = status
        self.status_history = status_history
        self.topic = topic
        # this is how the votes were split
        self.vote_totals = vote_totals
        self.key = key
        self.summary = summary

        self.bill_action_dates = bill_action_dates
        self.bill_action_display_texts = bill_action_display_texts
        self.bill_action_descriptions = bill_action_descriptions
        self.latest_action_date = self.get_latest_date_from_date_actions()
        self.latest_action_text = self.get_latest_action_from_actions()
        self.latest_action_description = self.get_latest_action_description_from_descriptions()

        self.senate_votes = self.split_and_clean_csv_array(senate_votes)
        self.house_votes = self.split_and_clean_csv_array(house_votes)

        # not my favorite solution, but I really want to upload
        try:
            self.senate_index = self.standardize_vote_index(senate_index)
        except IndexError:
            self.senate_index = ''
        try:
            self.house_index = self.standardize_vote_index(house_index)
        except IndexError:
            self.house_index = ''

        self.pdf_downloaded = pdf_downloaded
        self.xml_downloaded = xml_downloaded
        self.txt_downloaded = txt_downloaded

        self.standardized_issue = standardized_issue
        self.issue_title = issue_title
        self.long_heading = long_heading

        self.vote_analytics = 'placeholder, this one field is by no means comprehensive, and is just a ' \
                              'general reminder to fill in the appropriate votes later'

        self.collection_name = 'Bills'
        self.document_name = key

        return

    def to_dict(self):

        utc_upload_date = datetime.datetime.now()
        # local_upload_date doesn't work
        local_upload_date = utc_upload_date.replace(tzinfo=datetime.timezone.utc).astimezone(tz=None)

        this_dict = {'title': self.title,
                     'local_upload_date': local_upload_date,
                     'utc_upload_date': utc_upload_date,
                     'issue_number': self.issue_number,
                     'issue_type': self.issue_type,
                     'senate_vote_indexes': self.senate_index,
                     'house_vote_index': self.house_index,
                     'sponsor': self.sponsor,
                     'current_bill_status': self.status,
                     'key': self.key,
                     'topic': self.topic,
                     'latest_action_date': self.latest_action_date,
                     'latest_action_text': self.latest_action_text,
                     'latest_action_description': self.latest_action_description,
                     'pdf_available': self.pdf_downloaded,
                     'xml_available': self.xml_downloaded,
                     'txt_available': self.txt_downloaded,
                     'summary': self.summary,
                     'issue_title': self.issue_title,
                     'standardized_issue_number': self.standardized_issue,
                     'vote_analytics': self.vote_analytics}

        # 'bill_status_history':self.status_history,
        # 'number_of_repub_votes':repub_votes,
        # 'number_of_dem_votes':dem_votes,

        return this_dict

    @staticmethod
    def split_and_clean_csv_array(text):

        temp_arr = text.split(',')
        no_quotes = [text_cleaning.remove_single_quotes(x) for x in temp_arr]
        cleaned_arr = [text_cleaning.remove_square_brackets(x) for x in no_quotes]

        return cleaned_arr

    def standardize_vote_index(self, text):

        # TODO: haven't handled nan values yet

        clean = self.split_and_clean_csv_array(text)
        standard = [standardize_index.standardize_index(x) for x in clean]

        return standard

    def get_latest_date_from_date_actions(self):

        split_dates = self.bill_action_dates.split(',')
        last_date = split_dates[len(split_dates)-1]
        last_search = re.search(' => ', last_date)
        date_numbers = last_date[last_search.end():].split('\'')[0].split('-')
        year = int(date_numbers[0])
        month = int(date_numbers[1])
        day = int(date_numbers[2])

        this_date = datetime.datetime(year=year, month=month, day=day,
                                      hour=15, minute=0, second=0)

        return this_date

    def get_latest_action_from_actions(self):

        split_text = self.bill_action_display_texts.split(' => ')
        last_text = split_text[len(split_text)-1].split('\'')[0]

        return last_text

    def get_latest_action_description_from_descriptions(self):

        split_description = self.bill_action_descriptions.split(' => ')
        last_description = split_description[len(split_description)-1].split('\'')[0]

        return last_description

    def clean_sponsor_details(self):

        return

    def show_collection_name(self):

        return self.collection_name

    def show_document_name(self):

        return self.document_name


class SenateVotes:
    # writing the votes of senators to a separate collection
    # just the votes, not the names
    def __init__(self):

        return


class Finances:

    def __init__(self, first_name, last_name, cash_raised,
                 cash_spent, cash_on_hand, debts, species,
                 state, elections_finances, industries_finances,
                 contributors_finances, unique_id):

        # this is a copy of the human class
        self.first_name = first_name
        self.summary_link = None
        self.elections_csv_link = None
        self.industries_csv_link = None
        self.contributors_csv_link = None
        self.last_name = last_name
        self.cash_raised = cash_raised
        self.cash_spent = cash_spent
        self.cash_on_hand = cash_on_hand
        self.debts = debts
        self.species = species
        self.state = state

        # these will be sub_collections
        self.elections_finances = elections_finances
        self.industries_finances = industries_finances
        self.contributors_finances = contributors_finances

        # need id that corresponds to identifier that uploads
        self.unique_id = unique_id

        self.collection_name = 'Finances'
        if self.species == 'senate':
            self.document_name = unique_id
        elif self.species == 'house':
            test_name = self.first_name[0].upper() + self.first_name[1:]
            self.document_name = '{}_{}'.format(test_name, self.unique_id)

        self.sub_collection_elections = 'elections_finances'
        self.sub_collection_industries = 'industries_finances'
        self.sub_collection_contributors = 'contributors_finances'

        # self.elections_document_name = None
        # self.industries_document_name = None
        # self.contributors_document_name = None

        return

    def to_dict(self):

        this_dict = {'first_name': self.first_name,
                     'last_name': self.last_name,
                     'cash_raised': self.cash_raised,
                     'cash_spent': self.cash_spent,
                     'cash_on_hand': self.cash_on_hand,
                     'species': self.species,
                     'state': self.state,
                     'debts': self.debts,
                     'unique_id': self.unique_id}
        return this_dict

    # will iterate through the related list objects in the method calling this class
    @staticmethod
    def contributors_to_dict(contributors_finances):

        this_dict = {'client': contributors_finances.client,
                     'contributor': contributors_finances.contributor,
                     'individuals': contributors_finances.individuals,
                     'number_of_lobbyists': contributors_finances.numberOfLobbyists,
                     'pacs': contributors_finances.pacs,
                     'registrant': contributors_finances.registrant,
                     'release_date': contributors_finances.release_date}
        return this_dict

    @staticmethod
    def elections_to_dict(elections_finances):
        this_dict = {'cash_opponent_raised': elections_finances.cash_opponent_raised,
                     'cash_opponent_spent': elections_finances.cash_opponent_spent,
                     'cash_raised': elections_finances.cash_raised,
                     'cash_spent': elections_finances.cash_spent,
                     'district': elections_finances.district,
                     'opponent': elections_finances.opponent,
                     'race_results': elections_finances.race_results,
                     'was_incumbent': elections_finances.wasIncumbent,
                     'was_opponent_incumbent': elections_finances.wasOpponent_Incumpent,  # zach has a typo
                     'year': elections_finances.year}
        return this_dict

    @staticmethod
    def industries_to_dict(industries_finances):
        this_dict = {'district_rank': industries_finances.district_rank,
                     'individual': industries_finances.individual,
                     'industry': industries_finances.industry,
                     'pac': industries_finances.pac,
                     'release_date': industries_finances.release_date}
        return this_dict

    def show_collection_name(self):
        return self.collection_name

    def show_document_name(self):
        return self.document_name

    def show_election_sub_coll(self):
        return self.sub_collection_elections

    def show_contributors_sub_coll(self):
        return self.sub_collection_contributors

    def show_industries_sub_coll(self):
        return self.sub_collection_industries


class Bio:
    # TODO this will work the same way as finances in database tester
    def __init__(self, first_name, last_name, species,
                 state, district, is_incumbent, prior_jobs,
                 education, party, office_start_date,
                 birth_date, birth_place, children, spouses,
                 website, other_parties, unique_id, military_service=None):
        # yoinked from human class in wiki crawler
        self.first_name = first_name
        self.last_name = last_name
        self.species = species
        self.state = state
        self.district = district
        self.is_incumbent = is_incumbent
        self.prior_jobs = prior_jobs  # list
        self.education = education  # list
        self.party = party
        self.office_start_date = office_start_date
        self.birth_date = birth_date  # mm/dd/yyyy
        self.birth_place = birth_place
        self.children = children
        self.spouses = spouses  # separated by '\n'
        self.website = website
        self.other_parties = other_parties
        self.military_service = military_service  # this will from a class also in wiki crawler

        self.served_military = None  # boolean
        # these 4 are just the elements in the military class
        self.military_awards = None
        self.military_battles = None
        self.military_branch = None
        self.military_unit = None

        if self.military_service:
            self.served_military = True
            self.military_awards = self.military_service.awards
            self.military_battles = self.military_service.battles
            self.military_branch = self.military_service.branch
            self.military_unit = self.military_service.unit
        else:
            self.served_military = False

        self.collection_name = 'Biography'
        if self.species == 'senate':
            self.document_name = unique_id
        elif self.species == 'house':
            test_name = self.first_name[0].upper() + self.first_name[1:]
            self.document_name = '{}_{}'.format(test_name, unique_id)

        self.sub_collection_elections = 'elections_finances'
        self.sub_collection_industries = 'industries_finances'
        self.sub_collection_contributors = 'contributors_finances'

        return

    def to_dict(self):
        this_dict = {'first_name': self.first_name,
                     'last_name': self.last_name,
                     'species': self.species,
                     'state': self.state,
                     'education': self.education,
                     'party': self.party,
                     'birth_place': self.birth_place,
                     'website': self.website,
                     'unique_id': self.document_name}
        if self.prior_jobs:
            this_dict['prior_jobs'] = self.prior_jobs
        if self.children:
            this_dict['children'] = self.children
        if self.spouses:
            this_dict['spouses'] = self.spouses
        if self.other_parties:
            this_dict['other_parties'] = self.other_parties
        if self.is_incumbent:
            this_dict['is_incumbent'] = self.is_incumbent
        if self.district:
            this_dict['district'] = self.district
        if self.birth_date:
            birth_date_month = int(self.birth_date.split('/')[0])
            birth_date_day = int(self.birth_date.split('/')[1])
            birth_date_year = int(self.birth_date.split('/')[2])
            birth_date_stamp = datetime.datetime(year=birth_date_year,
                                                 month=birth_date_month,
                                                 day=birth_date_day,
                                                 hour=12)
            this_dict['birth_date'] = birth_date_stamp
        if self.office_start_date:
            if re.search('/', self.office_start_date):
                office_month = int(self.office_start_date.split('/')[0])
                office_day = int(self.office_start_date.split('/')[1])
                office_year = int(self.office_start_date.split('/')[2][:4])
                office_start_stamp = datetime.datetime(year=office_year,
                                                       month=office_month,
                                                       day=office_day,
                                                       hour=12)
            elif re.search('-', self.office_start_date):
                office_month = int(self.office_start_date.split('-')[0])
                office_day = int(self.office_start_date.split('-')[1])
                office_year = int(self.office_start_date.split('-')[2][:4])
                office_start_stamp = datetime.datetime(year=office_year,
                                                       month=office_month,
                                                       day=office_day,
                                                       hour=12)

            this_dict['office_start_date'] = office_start_stamp
        if self.military_awards:
            this_dict['military_awards'] = self.military_awards
        if self.military_branch:
            this_dict['military_branch'] = self.military_branch
        if self.military_unit:
            this_dict['military_unit'] = self.military_unit
        if self.military_battles:
            this_dict['military_battles'] = self.military_battles

        return this_dict

    def show_collection_name(self):
        return self.collection_name

    def show_document_name(self):
        return self.document_name


class HouseFloorActivity:

    def __init__(self, pull_date=None, text=None):
        self.pull_date = pull_date
        self.text = text
        self.collection_name = 'House Floor Activity'
        # I want the document name to be the date
        self.document_name = '{}-{}-{}'.format(self.pull_date.year, self.pull_date.month, self.pull_date.day)
        return

    def to_dict(self):

        return

    def show_collection_name(self):

        return

    def show_document_name(self):

        return


class SenateFloorActivity:

    def __init__(self, adjournment=None, cpd=None, given_date=None,
                 executive_business=None, journal=None, legislative_business=None,
                 pull_date=None, tmb=None, opening=None):
        self.adjournment = adjournment
        self.cpd = cpd
        self.date = given_date
        self.executive_business = executive_business
        self.journal = journal
        self.legislative_business = legislative_business
        self.pull_date = pull_date
        self.tmb = tmb
        self.opening = opening

        self.collection_name = 'Senate Floor Activity'
        self.document_name = '{}-{}-{}'.format(self.pull_date.year, self.pull_date.month, self.pull_date.day)
        return

    def to_dict(self):

        return


class LatestUpdate:

    def __init__(self):

        return


# for writing errors that come up while writing to database so that
# we can easily be informed of what went wrong
class DatabaseErrors:

    def __init__(self):

        self.collection_name = 'database_errors'

        self.document_name = ''

        return


