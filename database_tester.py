
from prototyping import firebase_database
import pandas as pd
import datetime
import numpy as np
import time
from prototyping.utils import dictionary_functions, constants
from prototyping.web_crawlers import opensecrets_crawler as osc
from prototyping.web_crawlers import wiki_crawler

# test1 = firebase_database.database()
# test1.query_documents_from_collection(collection_name='senate03')
# test1.write_test()
# test1.query_test()
# time.sleep(3)
# test1.update_test()
# test1.query_test()


def try_write01():
    # let's write out a few different functions to test writing with these objects
    data_manage = firebase_database.Database()

    df = pd.read_csv(filepath_or_buffer='data_storage/senate_data/representative_summaries/senator_bio.csv')
    for row in df.itertuples():

        last_name = row.last_name
        first_name = row.first_name
        lis_id = row.lis_member_id
        party = row.party
        state = row.state

        senate_obj = firebase_database.Senate(last_name=last_name, first_name=first_name,
                                              lis_member_id=lis_id, party=party, state=state)

        data_manage.set_collection(collection_name=senate_obj.get_collection_name())
        data_manage.set_document(document_name=senate_obj.get_document_name(),
                                 doc_dict=senate_obj.to_dict())

        sub_dict = senate_obj.get_voting_record()

        keys = senate_obj.get_list_sub_doc_names()
        for key in keys:

            data_manage.set_subdocument(sub_coll_name='voting_record',
                                        sub_doc_name=key,
                                        sub_doc_dict=sub_dict[key])

    return


def query_check_test():
    # let's write out a few different functions to test writing with these objects
    data_manage = firebase_database.Database()

    df = pd.read_csv(filepath_or_buffer='data_storage/senate_data/representative_summaries/senator_bio.csv')
    for row in df.itertuples():

        last_name = row.last_name
        first_name = row.first_name
        lis_id = row.lis_member_id
        party = row.party
        state = row.state

        senate_obj = firebase_database.Senate(last_name=last_name, first_name=first_name,
                                              lis_member_id=lis_id, party=party, state=state)

        data_manage.set_collection(collection_name=senate_obj.get_collection_name())
        data_manage.set_document(collection_name=senate_obj.get_collection_name(),
                                 document_name=senate_obj.get_document_name(),
                                 doc_dict=senate_obj.to_dict())

        sub_dict = senate_obj.get_voting_record()

        keys = senate_obj.get_list_sub_doc_names()

        # break

    # data_manage.check_document_exist(collection_name='Senators',document_name='S009')

        for key in keys:

            data_manage.set_subdocument(collection_name=senate_obj.get_collection_name(),
                                        document_name=senate_obj.get_document_name(),
                                        sub_coll_name='voting_record', sub_doc_name=key, sub_doc_dict=sub_dict[key])

        # break

    return


def update_test():

    data_manager = firebase_database.Database()

    df = pd.read_csv(filepath_or_buffer='data_storage/senate_data/representative_summaries/senator_bio.csv')

    i = 0
    for row in df.itertuples():

        last_name = row.last_name
        first_name = row.first_name
        lis_id = row.lis_member_id
        party = row.party
        state = row.state

        senate_obj = firebase_database.Senate(last_name=last_name, first_name=first_name,
                                              lis_member_id=lis_id, party=party, state=state)

        sub_dict = senate_obj.show_voting_record() # should make it so that all of this is done when initialized

        data_manager.write_document(collection_name=senate_obj.get_collection_name(),
                                    document_name=senate_obj.get_document_name(),
                                    doc_dict=senate_obj.to_dict(),
                                    write_flag=senate_obj.show_document_flag())

        keys = senate_obj.get_list_sub_doc_names()
        sub_doc_write_flags = senate_obj.show_subdocument_flag()

        print(sub_doc_write_flags)

        for key in keys:

            data_manager.write_subdocument(collection_name=senate_obj.get_collection_name(),
                                           document_name=senate_obj.get_document_name(),
                                           sub_coll_name='voting_record',
                                           sub_doc_name=key,
                                           sub_doc_dict=sub_dict[key],
                                           write_flag=sub_doc_write_flags[key])

        data_manager.batch_commit(df=senate_obj.show_dataframe_for_write(),
                                  file_path=senate_obj.show_file_path())

        # if i>3:
        #     break
        # i += 1

        print(senate_obj.show_file_path())

        # break # only do this for one senate object
        # the sub documents can all be updated if

    del data_manager

    return


def write_senators_no_votes():
    # unsure if this function needs to worry about update or writes

    data_manager = firebase_database.Database()

    # df = pd.read_csv(filepath_or_buffer='data_storage/senate_data/representative_summaries/senator_bio.csv')
    df = pd.read_csv(filepath_or_buffer=constants.senate_rep_summary_bio)

    for row in df.itertuples():

        last_name = row.last_name
        first_name = row.first_name
        lis_id = row.lis_member_id
        party = row.party
        state = row.state

        print(last_name)
        senate_obj = firebase_database.Senate(last_name=last_name, first_name=first_name,
                                              lis_member_id=lis_id, party=party, state=state)

        data_manager.write_document(collection_name='Senators_no_votes',
                                    document_name=senate_obj.get_document_name(),
                                    doc_dict=senate_obj.to_dict(),
                                    write_flag='set')

    del data_manager

    return


def write_current_senators_no_votes():
    # unsure if this function needs to worry about update or writes

    data_manager = firebase_database.Database()

    # df = pd.read_csv(filepath_or_buffer='data_storage/senate_data/representative_summaries/senator_bio.csv')
    df = pd.read_csv(filepath_or_buffer=constants.senate_rep_summary_bio)

    for row in df.itertuples():

        last_name = row.last_name
        first_name = row.first_name
        lis_id = row.lis_member_id
        party = row.party
        state = row.state

        print(last_name, lis_id)
        senate_obj = firebase_database.Senate(last_name=last_name, first_name=first_name,
                                              lis_member_id=lis_id, party=party, state=state)

        data_manager.write_document(collection_name='Senators_current',
                                    document_name=senate_obj.get_document_name(),
                                    doc_dict=senate_obj.to_dict(),
                                    write_flag='set')

    del data_manager

    return


def write_house_cong116():

    ######### for debugging
    desired_width = 320
    pd.set_option('display.width', desired_width)
    np.set_printoptions(linewidth=desired_width)
    pd.set_option('display.max_columns', 20)
    #########################

    print('this function does not write correctly')
    # may need a representative written column as a check
    # will tell which reps are in congress by the bio file

    state_to_abbrev = dictionary_functions.states_to_abbrev_dict()

    data_manager = firebase_database.Database()

    # may change this access method later
    # df = pd.read_csv(filepath_or_buffer='data_storage/wikipedia_data/house_data/congress_116/wiki_house_mod.csv')
    df = pd.read_csv(filepath_or_buffer=constants.wiki_house_mod_path)

    i = 0
    for row in df.itertuples():

        last_name = row.last_name
        first_name = row.first_name
        party = row.party
        district = row.district
        # districts from wikipedia all likely have this issue examine the print statement to observe
        district = district.replace(u'\xa0', u' ')
        # print(district.split(' '))
        file_name_id = row.file_name_id

        if pd.isna(file_name_id) or file_name_id == 0 or file_name_id == '0':
            continue

        if len(district.split(' ')) == 2:
            key = district.split(' ')[0]
            key = key.lower()
        elif len(district.split(' ')) == 3:
            key = '{} {}'.format(district.split(' ')[0], district.split(' ')[1]).lower()

        if last_name == '' or first_name == '' or pd.isna(last_name) or pd.isna(first_name):
            print('name thing here')
            print(last_name, first_name, district)

            continue

        state_abb = state_to_abbrev[key]
        name_state = '{}_{}'.format(last_name, state_abb)

        try:
            house_obj = firebase_database.House(last_name=last_name, first_name=first_name,
                                            lis_member_id=file_name_id, party=party,
                                            state=state_abb, overwrite=False)
        except FileNotFoundError:
            print('file {} not found'.format(file_name_id))
            print('skipping this loop')
            # TODO need to add something in about error catching and a logger
            continue

        house_obj.give_cutoff_year(year='2019')

        sub_dict = house_obj.show_voting_record()

        print(house_obj.show_document_flag())

        data_manager.write_document(collection_name='House_current',
                                    # collection_name=house_obj.get_collection_name(),
                                    document_name=house_obj.get_document_name(),
                                    doc_dict=house_obj.to_dict(),
                                    write_flag=house_obj.show_document_flag())

        keys = house_obj.get_list_sub_doc_names()
        sub_doc_write_flags = house_obj.show_subdocument_flag()

        for key in keys:
            data_manager.write_subdocument(collection_name='House_current',
                                           # collection_name=house_obj.get_collection_name(),
                                           document_name=house_obj.get_document_name(),
                                           sub_coll_name='voting_record',
                                           sub_doc_name=key,
                                           sub_doc_dict=sub_dict[key],
                                           write_flag=sub_doc_write_flags[key])

        data_manager.batch_commit(df=house_obj.show_dataframe_for_write(),
                                  file_path=house_obj.show_file_path())

        # if i>3:
        #     break
        # i += 1

        print(house_obj.show_file_path())

        # break # only do this for one senate object
        # the sub documents can all be updated if

    del data_manager

    return


def write_bills():
    # this will only be for bills
    data_manager = firebase_database.Database()

    df = pd.read_csv(filepath_or_buffer=constants.bill_title_summary_path, sep='~')
    write_df = df.copy()

    for row in df.itertuples():

        row_index = row.Index

        title = row.title
        issue_number = row.issue_num
        issue_type = row.issue_type

        # temporary stop gap
        if issue_type == 'pn':
            continue

        congress = row.congress
        sponsor = row.sponsor
        session = row.session
        status = row.current_bill_status
        vote_numbers = row.senate_vote_number
        status_history = 'missing'
        topic = 'missing'
        vote_totals = 'missing'
        senate_votes = row.senate_vote_number
        house_votes = row.house_vote_number
        senate_index = row.senate_vote_index
        house_index = row.house_vote_index
        key = row.key
        summary = 'soon to be here'
        pdf_downloaded = row.pdf_downloaded
        xml_downloaded = row.xml_downloaded
        txt_downloaded = row.txt_downloaded
        bill_action_dates = row.bill_action_date
        bill_action_display_texts = row.bill_action_display_text
        bill_action_descriptions = row.bill_action_description
        # issue number that has a lot of other text room
        standardized_issue = row.issue
        issue_title = row.issue_title
        long_heading = row.long_heading

        print(key)
        # need to handle the data better to get rid of this problem
        if key[:2] == 'cn' or key[:2] == 'tr' or key[:2] == 'pn':
            print('skipping ', key)
            continue

        if 'database_upload_date' in df and pd.notna(row.database_upload_date):
            print(row.database_upload_date)
            continue

        try:
            bill_obj = firebase_database.Bills(title=title, issue_number=issue_number,
                                               issue_type=issue_type, congress=congress,
                                               sponsor=sponsor, status=status, session=session,
                                               status_history=status_history, topic=topic,
                                               vote_numbers=vote_numbers, vote_totals=vote_totals,
                                               senate_votes=senate_votes, house_votes=house_votes,
                                               senate_index=senate_index, house_index=house_index,
                                               key=key, summary=summary,
                                               bill_action_dates=bill_action_dates,
                                               bill_action_display_texts=bill_action_display_texts,
                                               bill_action_descriptions=bill_action_descriptions,
                                               pdf_downloaded=pdf_downloaded, xml_downloaded=xml_downloaded,
                                               txt_downloaded=txt_downloaded, standardized_issue=standardized_issue,
                                               issue_title=issue_title, long_heading=long_heading)

            data_manager.write_document(collection_name=bill_obj.show_collection_name(),
                                        document_name=bill_obj.show_document_name(),
                                        doc_dict=bill_obj.to_dict(),
                                        write_flag='set')

            if 'database_upload_date' in write_df:
                write_df['database_upload_date'].loc[row_index] = datetime.datetime.now()
            else:
                write_df['database_upload_date'] = ''
                write_df['database_upload_date'].loc[row_index] = datetime.datetime.now()

            # print(write_df.head())
        except AttributeError:

            if 'database_upload_date' in write_df:
                write_df['database_upload_date'].loc[row_index] = ''
            else:
                write_df['database_upload_date'] = ''

            # need to create a log file
            print('data format was bad for {}'.format(key))

        # break

    write_df.to_csv(path_or_buf=constants.bill_title_summary_path, sep='~', index=False)

    del data_manager

    return


def delete_house():

    data_manager = firebase_database.Database()
    data_manager.delete_collection_and_subcollection(collection_name='House_current',
                                                     subcollection_name='voting_record')

    del data_manager

    return


def delete_bills():

    data_manager = firebase_database.Database()
    for i in range(0, 40):
        data_manager.delete_collection(collection_name='Bills')

    return


def delete_finances():
    # TODO can just delete the collection from the console, the delete now works recursively
    data_manager = firebase_database.Database()
    data_manager.delete_collection(collection_name='Finances')

    return


def write_house_cong116_no_votes():

    print('this function does not write correctly')
    # may need a representative written column as a check
    # will tell which reps are in congress by the bio file

    state_to_abbrev = dictionary_functions.states_to_abbrev_dict()

    # calling this multiple times creates a problem, even if I delete the object
    data_manager = firebase_database.Database()

    # may change this access method later
    # df = pd.read_csv(filepath_or_buffer='data_storage/wikipedia_data/house_data/congress_116/wiki_house_mod.csv')
    df = pd.read_csv(filepath_or_buffer=constants.wiki_house_mod_path)

    i = 0
    for row in df.itertuples():

        last_name = row.last_name
        first_name = row.first_name
        party = row.party
        district = row.district
        # districts from wikipedia all likely have this issue examine the print statement to observe
        district = district.replace(u'\xa0', u' ')
        # print(district.split(' '))
        file_name_id = row.file_name_id

        if pd.isna(file_name_id) or file_name_id == 0 or file_name_id == '0':
            continue

        if len(district.split(' ')) == 2:
            key = district.split(' ')[0]
            key = key.lower()
        elif len(district.split(' ')) == 3:
            key = '{} {}'.format(district.split(' ')[0], district.split(' ')[1]).lower()

        if last_name == '' or first_name == '' or pd.isna(last_name) or pd.isna(first_name):
            print('name thing here')
            print(last_name, first_name, district)

            continue

        state_abb = state_to_abbrev[key]
        name_state = '{}_{}'.format(last_name, state_abb)

        # house_obj = firebase_database.House(last_name=last_name, first_name=first_name,
        #                                     lis_member_id=file_name_id, party=party,
        #                                     state=state_abb, overwrite=True)

        try:
            house_obj = firebase_database.House(last_name=last_name, first_name=first_name,
                                                lis_member_id=file_name_id, party=party,
                                                state=state_abb, overwrite=False)
        except FileNotFoundError:
            print('file {} not found'.format(file_name_id))
            print('skipping this loop')
            # TODO need to add something in about error catching and a logger
            continue

        house_obj.give_cutoff_year(year='2019')

        sub_dict = house_obj.show_voting_record()

        print(house_obj.show_document_flag())

        data_manager.write_document(collection_name='House_current_no_votes',
                                    # collection_name=house_obj.get_collection_name(),
                                    document_name=house_obj.get_document_name(),
                                    doc_dict=house_obj.to_dict(),
                                    write_flag=house_obj.show_document_flag())

        keys = house_obj.get_list_sub_doc_names()
        sub_doc_write_flags = house_obj.show_subdocument_flag()

        data_manager.batch_commit(df=house_obj.show_dataframe_for_write(),
                                  file_path=house_obj.show_file_path())

        # if i>3:
        #     break
        # i += 1

        print(house_obj.show_file_path())

        # break # only do this for one senate object
        # the sub documents can all be updated if

    del data_manager

    return


def write_finances():

    data_manager = firebase_database.Database()

    house_df = pd.read_csv(filepath_or_buffer=constants.wiki_house_mod_path)
    senate_df = pd.read_csv(filepath_or_buffer=constants.senate_rep_summary_bio)

    # house_df doesn't have state, it has district, so, for now, going to create a state column
    state_abbrev = dictionary_functions.states_to_abbrev_dict()
    create_state = lambda x: state_abbrev[x.split('\xa0')[0].lower()]
    house_df['state'] = house_df['district'].apply(create_state)

    # have to get rid of some nan values first
    house_df['last_name'].loc[pd.isna(house_df['last_name'])] = 'Vacant'
    house_df['first_name'].loc[pd.isna(house_df['first_name'])] = 'Vacant'

    senate_df['last_name'].loc[pd.isna(senate_df['last_name'])] = 'Vacant'
    senate_df['first_name'].loc[pd.isna(senate_df['first_name'])] = 'Vacant'

    # need to make lower case names for comparison
    lower_names = lambda x: x.lower()
    house_df['lower_first'] = house_df['first_name'].apply(lower_names)
    house_df['lower_last'] = house_df['last_name'].apply(lower_names)
    senate_df['lower_first'] = senate_df['first_name'].apply(lower_names)
    senate_df['lower_last'] = senate_df['last_name'].apply(lower_names)

    finance_crawl_obj = osc.runOSC()
    all_peoples = finance_crawl_obj.runSOC()

    print(all_peoples)

    for person in all_peoples.humans:
        # TODO instead of putting all three restrictions, could start with just last name
        # and then if the frame is larger than one, add the state, then first name
        if person.species == 'senate':
            if senate_df.loc[(senate_df['lower_last']==person.last_name) &
                             (senate_df['lower_first']==person.first_name) &
                             (senate_df['state']==person.state)].shape[0] == 0:
                print('senate dataframe was empty')
                continue

            unique_id = senate_df['lis_member_id'].loc[(senate_df['lower_last']==person.last_name) &
                                                       (senate_df['lower_first']==person.first_name) &
                                                       (senate_df['state']==person.state)].values
        elif person.species == 'house':
            unique_id = house_df['file_name_id'].loc[(house_df['lower_last']==person.last_name) &
                                                     (house_df['lower_first']==person.first_name) &
                                                     (house_df['state']==person.state)].values
            if house_df.loc[(house_df['lower_last']==person.last_name) &
                            (house_df['lower_first']==person.first_name) &
                            (house_df['state']==person.state)].shape[0] == 0:
                print('house dataframe was empty')
                continue
        else:
            print('problem with the person, not house or senate')
            continue

        # TODO need to have cases if unique_id returns an empty dataframe
        # this could happen due to nicknames or alternative names

        if pd.isna(unique_id[0]):
            print('unique id didnt exist for a person')
            continue

        their_info = firebase_database.Finances(first_name=person.first_name,
                                                last_name=person.last_name,
                                                cash_raised=person.cash_raised,
                                                cash_spent=person.cash_spent,
                                                cash_on_hand=person.cash_on_hand,
                                                debts=person.debts,
                                                species=person.species,
                                                state=person.state,
                                                elections_finances=person.elections_finances,
                                                contributors_finances=person.contributors_finances,
                                                industries_finances=person.industries_finances,
                                                unique_id=unique_id[0])

        data_manager.write_document(collection_name=their_info.show_collection_name(),
                                    document_name=their_info.show_document_name(),
                                    doc_dict=their_info.to_dict(),
                                    write_flag='set')

        # this is because of how I wrote the Database class
        write_flag_dict = {'flag': 'set'}

        # putting a limit on each field so that some information on every person will be available
        ele_count = 0
        for election in their_info.elections_finances:
            if ele_count > 5:
                break
            if pd.isna(their_info.elections_to_dict(elections_finances=election)['year']):
                print('skipped election finance upload')
                continue
            data_manager.write_subdocument(collection_name=their_info.show_collection_name(),
                                           document_name=their_info.show_document_name(),
                                           sub_coll_name=their_info.show_election_sub_coll(),
                                           sub_doc_dict=their_info.elections_to_dict(elections_finances=election),
                                           sub_doc_name=str(their_info.elections_to_dict(elections_finances=
                                                                                         election)['year']),
                                           write_flag=write_flag_dict)
            ele_count += 1

        ind_count = 0
        for industry in their_info.industries_finances:
            if ind_count > 5:
                break
            if pd.isna(their_info.industries_to_dict(industries_finances=industry)['industry']):
                print('skipped industry finance upload')
                continue
            data_manager.write_subdocument(collection_name=their_info.show_collection_name(),
                                           document_name=their_info.show_document_name(),
                                           sub_coll_name=their_info.show_industries_sub_coll(),
                                           sub_doc_name=their_info.industries_to_dict(industries_finances=
                                                                                      industry)['industry'],
                                           sub_doc_dict=their_info.industries_to_dict(industries_finances=industry),
                                           write_flag=write_flag_dict)
            ind_count += 1

        cont_count = 0
        for contributor in their_info.contributors_finances:
            if cont_count > 5:
                break
            if pd.isna(their_info.contributors_to_dict(contributors_finances=contributor)['contributor']):
                print('skipped contributor upload')
                continue
            data_manager.write_subdocument(collection_name=their_info.show_collection_name(),
                                           document_name=their_info.show_document_name(),
                                           sub_coll_name=their_info.show_contributors_sub_coll(),
                                           sub_doc_name=their_info.contributors_to_dict(contributors_finances=
                                                                                        contributor)['contributor'],
                                           sub_doc_dict=their_info.contributors_to_dict(contributors_finances=
                                                                                        contributor),
                                           write_flag=write_flag_dict)
            cont_count += 1

    return


def write_bios():

    data_manager = firebase_database.Database()

    house_df = pd.read_csv(constants.wiki_house_mod_path)
    senate_df = pd.read_csv(constants.senate_rep_summary_bio)

    # house_df doesn't have state, it has district, so, for now, going to create a state column
    state_abbrev = dictionary_functions.states_to_abbrev_dict()
    create_state = lambda x: state_abbrev[x.split('\xa0')[0].lower()]
    house_df['state'] = house_df['district'].apply(create_state)

    # have to get rid of some nan values first
    house_df['last_name'].loc[pd.isna(house_df['last_name'])] = 'Vacant'
    house_df['first_name'].loc[pd.isna(house_df['first_name'])] = 'Vacant'

    senate_df['last_name'].loc[pd.isna(senate_df['last_name'])] = 'Vacant'
    senate_df['first_name'].loc[pd.isna(senate_df['first_name'])] = 'Vacant'

    # need to make lower case names for comparison
    lower_names = lambda x: x.lower()
    house_df['lower_first'] = house_df['first_name'].apply(lower_names)
    house_df['lower_last'] = house_df['last_name'].apply(lower_names)
    senate_df['lower_first'] = senate_df['first_name'].apply(lower_names)
    senate_df['lower_last'] = senate_df['last_name'].apply(lower_names)

    list_of_congress_people = wiki_crawler.run_all_wiki_bios()
    senators = list_of_congress_people.List_of_Senators
    representatives = list_of_congress_people.List_of_HouseReps

    for person in senators:
        try:
            if senate_df.loc[(senate_df['last_name'] == person.last_name) &
                             (senate_df['first_name'] == person.first_name) &
                             (senate_df['state'] == state_abbrev[person.state.lower()])].shape[0] == 0:
                print('senate dataframe was empty')
                continue

            unique_id = senate_df['lis_member_id'].loc[(senate_df['last_name'] == person.last_name) &
                                                       (senate_df['first_name'] == person.first_name) &
                                                       (senate_df['state'] == state_abbrev[person.state.lower()])].values

            biography = firebase_database.Bio(first_name=person.first_name,
                                              last_name=person.last_name,
                                              species='senate',
                                              state=person.state,
                                              district=person.district,
                                              is_incumbent=person.isIncumbent,
                                              prior_jobs=person.priorJobs,
                                              education=person.education,
                                              party=person.party,
                                              office_start_date=person.officeStartDate,
                                              birth_date=person.birthDate,
                                              birth_place=person.birthPlace,
                                              children=person.children,
                                              spouses=person.spouses,
                                              website=person.website,
                                              other_parties=person.otherParties,
                                              military_service=person.militaryService,
                                              unique_id=unique_id[0])

            data_manager.write_document(collection_name=biography.show_collection_name(),
                                        document_name=biography.show_document_name(),
                                        doc_dict=biography.to_dict(),
                                        write_flag='set')
        except TypeError:
            print('had type error on {} {}'.format(person.first_name, person.last_name))

    for person in representatives:
        try:
            if house_df.loc[(house_df['last_name'] == person.last_name) &
                            (house_df['first_name'] == person.first_name) &
                            (house_df['state'] == state_abbrev[person.state.lower()])].shape[0] == 0:
                print('house dataframe was empty')
                continue

            unique_id = house_df['file_name_id'].loc[(house_df['last_name'] == person.last_name) &
                                                     (house_df['first_name'] == person.first_name) &
                                                     (house_df['state'] == state_abbrev[person.state.lower()])].values

            biography = firebase_database.Bio(first_name=person.first_name,
                                              last_name=person.last_name,
                                              species='house',
                                              state=person.state,
                                              district=person.district,
                                              is_incumbent=person.isIncumbent,
                                              prior_jobs=person.priorJobs,
                                              education=person.education,
                                              party=person.party,
                                              office_start_date=person.officeStartDate,
                                              birth_date=person.birthDate,
                                              birth_place=person.birthPlace,
                                              children=person.children,
                                              spouses=person.spouses,
                                              website=person.website,
                                              other_parties=person.otherParties,
                                              military_service=person.militaryService,
                                              unique_id=unique_id[0])

            data_manager.write_document(collection_name=biography.show_collection_name(),
                                        document_name=biography.show_document_name(),
                                        doc_dict=biography.to_dict(),
                                        write_flag='set')
        except (TypeError, KeyError):
            print('type error or key error(the state) on {} {}'.format(person.first_name, person.last_name))

    return


def write_house_floor():

    return


def write_senate_floor():

    return

# write_senators_no_votes()
# update_test()
# write_house_cong116()
# write_house_cong116_no_votes()
# delete_house()
# query_check_test()
# try_write01()
# write_bills()
# delete_bills()
# delete_finances()
# write_finances()
write_bios()


