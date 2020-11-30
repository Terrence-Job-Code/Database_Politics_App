import os
import pandas as pd
import re
import numpy as np
from requests_html import HTMLSession
from bs4 import BeautifulSoup
from prototyping.utils import dictionary_functions
from pprint import pprint
import time
import requests


def bill_crawl_wrapper(delete_file=True):
    # TODO: can reduce how slow this is by making all the calls earlier in the code
    # and passing the original soups that I need to parse instead of the link

    ######### for debugging
    desired_width = 320
    pd.set_option('display.width', desired_width)
    np.set_printoptions(linewidth=desired_width)
    pd.set_option('display.max_columns', 13)
    #########################

    # purely for while I debug my data, or try to get the csv working at least
    current_separator = '~'

    bill_dict = {}

    senate_summaries_direc = '../data_storage/senate_data/crawled_data/link_summaries/'
    house_summaries_direc = '../data_storage/house_data/summary_data/'
    bill_write_path = '../data_storage/bill_information/bill_title_summaries.csv'

    senate_files = [senate_summaries_direc + x for x in os.listdir(senate_summaries_direc)[1:]]
    house_files = [house_summaries_direc + x for x in os.listdir(house_summaries_direc)[1:]]

    # filling the dictionary with relevant bills and congressional actions
    # maybe this is overwriting information?
    for path in senate_files:
        bill_dict = add_senate_to_bill_dict(path=path, bill_dict=bill_dict)

    for path in house_files:
        bill_dict = add_house_to_bill_dict(path=path, bill_dict=bill_dict)

    # for automating deleting/overwriting the file
    if delete_file:
        try:
            os.remove(bill_write_path)
        except FileNotFoundError:
            print('file does not exist, moving on')

    # TODO: need to modify the check function to include the vote numbers so that I
    # don't skip updates
    file_exists = os.path.exists(bill_write_path)
    if file_exists:
        keys_to_ignore = which_keys_and_votes_to_ignore(bill_write_path, separator=current_separator)
        creating_file = False
    else:
        creating_file = True

    # can try to reduce RAM consumption by making an inbetween dictionary
    # small_bill = bill_dict[key]
    # and then writing everything to small_bill and

    for key in bill_dict:

        if file_exists:
            if key in keys_to_ignore:
                print('ignoring ', key)
                continue

        bill_dict = crawl_bill_links(key=key, bill_dict=bill_dict)
        # pprint(bill_dict[key])
        write_df_t = pd.DataFrame.from_dict(bill_dict[key], orient='index')
        write_df = write_df_t.T

        if creating_file:
            # TODO: The next step in fixing this issue is to properly separate issues
            # as I don't think the separator is the problem
            write_df.to_csv(path_or_buf=bill_write_path, index=False, sep=current_separator)
            creating_file = False
        else:
            write_df.to_csv(path_or_buf=bill_write_path, index=False,
                            mode='a', header=False, sep=current_separator)

    print('completed')

    # for maintainability later, will need a way to make sure automation worked successfully
    completed = True

    return completed


def add_senate_to_bill_dict(path, bill_dict):

    month_to_num = dictionary_functions.month_to_num()
    senate_df = pd.read_csv(path)

    for row in senate_df.itertuples():

        congress = row.congress
        session = row.session
        vote_number = row.vote_number.split('\xa0')[0]
        date_str = row.date
        month = date_str.split('\xa0')[0].lower()
        month_num = month_to_num[month]
        day = date_str.split('\xa0')[1]
        year = 'missing'
        vote_index = 'cn{}sn{}vn{}'.format(congress, session, vote_number)

        issue_box = row.issue
        issue_link_box = row.issue_link

        # consider refactoring these functions
        if pd.isna(issue_box) or len(issue_box.split('\n')) == 1:
            # need to handle issue better before writing to file
            issue = issue_box
            issue_link = issue_link_box

            bill_dict = fill_bill_dict_from_issue(congress=congress, session=session, issue=issue,
                                                  issue_link=issue_link, vote_number=vote_number,
                                                  day=day, month=month, year=year, vote_index=vote_index,
                                                  what_house='senate', bill_dict=bill_dict)

        # for the cases where I have multiple legislative votes

        else:
            issue_split = issue_box.split('\n')
            issue_link_split = issue_link_box.split('\n')

            for i in range(len(issue_split)):
                issue = issue_split[i]
                issue_link = issue_link_split[i]

                bill_dict = fill_bill_dict_from_issue(congress=congress, session=session, issue=issue,
                                                      issue_link=issue_link, vote_number=vote_number,
                                                      day=day, month=month, year=year, vote_index=vote_index,
                                                      what_house='senate', bill_dict=bill_dict)

    return bill_dict


def add_house_to_bill_dict(path, bill_dict):

    month_to_num = dictionary_functions.month_to_num()
    year_congress_dict = dictionary_functions.year_congress_session()
    house_df = pd.read_csv(filepath_or_buffer=path)
    year_for_congress = path.split('/')[4].split('.')[0]

    for row in house_df.itertuples():
        congress = year_congress_dict[year_for_congress]['congress']
        session = year_congress_dict[year_for_congress]['session']
        vote_number = row.roll_call_number
        vote_index = 'cn{}sn{}vn{}'.format(congress, session, vote_number)
        date_str = row.day_month
        day = date_str.split('-')[0]
        month = date_str.split('-')[1].lower()
        month_num = month_to_num[month]
        year = row.year
        issue = row.issue
        issue_link = row.issue_link

        bill_dict = fill_bill_dict_from_issue(congress=congress, session=session, issue=issue,
                                              issue_link=issue_link, vote_number=vote_number,
                                              day=day, month=month, year=year, vote_index=vote_index,
                                              what_house='house', bill_dict=bill_dict)

    return bill_dict


def crawl_bill_links(key, bill_dict):

    issue_link = bill_dict[key]['issue_link']
    issue_type = bill_dict[key]['issue_type']
    print(issue_link)
    bill_direc = '../data_storage/bill_information/bill_text/'

    # TODO:  the no link is apparently in the house files, uggh, need to change that in the future
    # as in, it says no link instead of nan

    # TODO!!!: Need to just have separate dictionaries for bills and pn actions, because something
    # is missing from my dictionaries for pn
    # pn actions are executive business
    if pd.notna(issue_link) and issue_link != 'no link':

        if issue_type != 'pn':
            current_bill_map = get_bill_tile_info(issue_link)

            had_pdf, had_xml, had_txt = download_bill_text(link=issue_link, base_direc=bill_direc, key=key)

            # may want to create a function to fill these dictionaries
            bill_dict[key]['long_heading'] = current_bill_map['long_heading']
            bill_dict[key]['issue_title'] = current_bill_map['issue_title']
            bill_dict[key]['issue_num'] = current_bill_map['issue']
            bill_dict[key]['title'] = current_bill_map['title']
            bill_dict[key]['sponsor'] = current_bill_map['sponsor']
            bill_dict[key]['current_bill_status'] = current_bill_map['current_bill_status']
            bill_dict[key]['pdf_downloaded'] = had_pdf
            bill_dict[key]['xml_downloaded'] = had_xml
            bill_dict[key]['txt_downloaded'] = had_txt
            bill_dict[key]['bill_action_date'] = current_bill_map['action_date']
            bill_dict[key]['bill_action_display_text'] = current_bill_map['display_text']
            bill_dict[key]['bill_action_description'] = current_bill_map['description']

            # specific pn pieces that will be blank
            bill_dict[key]['nominee_name'] = ''
            bill_dict[key]['nominee_position'] = ''
            bill_dict[key]['head_title'] = ''
            bill_dict[key]['meta_description'] = ''
            bill_dict[key]['overview_description'] = ''
            bill_dict[key]['overview_organization'] = ''
            bill_dict[key]['latest_action'] = ''
            bill_dict[key]['date_received_from_president'] = ''
            bill_dict[key]['committee'] = ''
            bill_dict[key]['dates_of_actions'] = ''
            bill_dict[key]['descriptions_of_actions'] = ''
            bill_dict[key]['links_of_actions'] = ''
        else:
            pn_map = nomination_tile_info(issue_link)

            bill_dict[key]['nominee_name'] = pn_map['nominee_name']
            bill_dict[key]['nominee_position'] = pn_map['position']
            bill_dict[key]['head_title'] = pn_map['head_title']
            bill_dict[key]['meta_description'] = pn_map['meta_description']
            bill_dict[key]['overview_description'] = pn_map['overview_description']
            bill_dict[key]['overview_organization'] = pn_map['overview_organization']
            bill_dict[key]['latest_action'] = pn_map['latest_action']
            bill_dict[key]['date_received_from_president'] = pn_map['date_received_from_president']
            bill_dict[key]['committee'] = pn_map['committee']
            bill_dict[key]['dates_of_actions'] = pn_map['dates_of_actions']
            bill_dict[key]['descriptions_of_actions'] = pn_map['descriptions_of_actions']
            bill_dict[key]['links_of_actions'] = pn_map['links_of_actions']

            # normal bill stuff that will be blank if pn
            bill_dict[key]['long_heading'] = ''
            bill_dict[key]['issue_title'] = ''
            bill_dict[key]['issue_num'] = ''
            bill_dict[key]['title'] = ''
            bill_dict[key]['sponsor'] = ''
            bill_dict[key]['current_bill_status'] = ''
            bill_dict[key]['pdf_downloaded'] = ''
            bill_dict[key]['xml_downloaded'] = ''
            bill_dict[key]['txt_downloaded'] = ''
            bill_dict[key]['bill_action_date'] = ''
            bill_dict[key]['bill_action_display_text'] = ''
            bill_dict[key]['bill_action_description'] = ''

        time.sleep(0.5)

    else:
        bill_dict[key]['long_heading'] = ''
        bill_dict[key]['issue_title'] = ''
        bill_dict[key]['issue_num'] = ''
        bill_dict[key]['title'] = ''
        bill_dict[key]['sponsor'] = ''
        bill_dict[key]['current_bill_status'] = ''
        bill_dict[key]['nominee_name'] = ''
        bill_dict[key]['nominee_position'] = ''
        bill_dict[key]['head_title'] = ''
        bill_dict[key]['meta_description'] = ''
        bill_dict[key]['overview_description'] = ''
        bill_dict[key]['overview_organization'] = ''
        bill_dict[key]['latest_action'] = ''
        bill_dict[key]['date_received_from_president'] = ''
        bill_dict[key]['committee'] = ''
        bill_dict[key]['dates_of_actions'] = ''
        bill_dict[key]['descriptions_of_actions'] = ''
        bill_dict[key]['links_of_actions'] = ''
        bill_dict[key]['pdf_downloaded'] = ''
        bill_dict[key]['xml_downloaded'] = ''
        bill_dict[key]['txt_downloaded'] = ''
        bill_dict[key]['bill_action_date'] = ''
        bill_dict[key]['bill_action_display_text'] = ''
        bill_dict[key]['bill_action_description'] = ''

    return bill_dict


def get_bill_tile_info(link):
    # function returns a map/dictionary of the information
    # different issue numbers have different structures
    # there might also be differences between years
    sesh = HTMLSession()

    bill_sess = sesh.get(link)
    bill_soup = BeautifulSoup(bill_sess.html.html, 'html.parser')

    # getting the title and issue of the bill
    long_heading = bill_soup.title.string

    head1_tag = bill_soup.find('h1', {'class': 'legDetail'})
    try:
        for child in head1_tag.children:
            issue_title = child
            break
        issue = issue_title.split('-')[0]
        title = issue_title.split('-')[1]
    except AttributeError:
        issue_title = ''
        issue = ''
        title = ''

    # getting the sponsor of the bill
    overview_tag = bill_soup.find('div', {'class': 'overview'})
    try:
        sponsor_tag = overview_tag.find('a', {'target': '_blank'})
    except AttributeError:
        sponsor_tag = ''
    try:
        # can split on the comma and remove Rep. and the stuff in brackets
        sponsor_info = sponsor_tag.string  # includes more than just their name
    except AttributeError:
        sponsor_info = ''

    # bill progress/ progress bar info
    billprog_tag = bill_soup.find('div', {'class': 'overview_billprogress'})
    try:
        bill_status_tag = billprog_tag.find('p', {'class': 'hide_fromsighted'})
        current_bill_status = bill_status_tag.string
    except AttributeError:
        bill_status_tag = ''
        current_bill_status = ''
    try:
        bill_phases = billprog_tag.find_all('li')
    except AttributeError:
        bill_phases = ''

    action_dates = []
    display_texts = []
    descriptions = []
    for info_tag in bill_phases:

        try:
            bill_stat_string = info_tag.div.string
            bill_stat_list = bill_stat_string.split('\n')

            # these variables may be a little redundant
            action_date = bill_stat_list[2]
            display_text = bill_stat_list[3]
            description = bill_stat_list[5]
        except AttributeError:
            action_date = ''
            display_text = ''
            description = ''

        action_dates.append(action_date)
        display_texts.append(display_text)
        descriptions.append(description)

    bill_map = {'long_heading': long_heading, 'issue_title': issue_title, 'issue': issue, 'title': title,
                'sponsor': sponsor_info, 'current_bill_status': current_bill_status, 'action_date': action_dates,
                'display_text': display_texts, 'description': descriptions}

    # need to grab the txt, pdf, and xml texts of the bills
    # also should add columns for whether or not a bill has xml, pdf, and txt of it

    return bill_map


def fill_bill_dict_from_issue(congress, issue, vote_number, session, what_house,
                              issue_link, month, day, year, vote_index, bill_dict):

    try:
        issue_type = make_issue_type_from_issue(issue)
    except TypeError:
        issue_type = ''  # most likely a nan error

    # hopefully this format makes unique bills, as the same number can be used from year to year
    if not pd.isna(issue):
        issue = normalize_issue_text(issue)
        key = '{}_{}'.format(issue, congress)
    else:
        key = 'cn{}sn{}vn{}'.format(congress, session, vote_number)
    if what_house == 'senate':
        house_vote_number = 'senate_vote_number'
        house_vote_index = 'senate_vote_index'
    else:
        house_vote_number = 'house_vote_number'
        house_vote_index = 'house_vote_index'
    if key in bill_dict:
        bill_dict[key][house_vote_number].append(vote_number)
        bill_dict[key][house_vote_index].append(vote_index)

    if key not in bill_dict and what_house == 'senate':
        bill_dict[key] = {'congress': congress, 'session': session, 'senate_vote_number': [vote_number],
                          'issue': issue, 'issue_link': issue_link, 'month': month, 'issue_type': issue_type,
                          'day': day, 'year': year, 'house_vote_number': [], 'senate_vote_index': [vote_index],
                          'house_vote_index': [], 'key': key}

    if key not in bill_dict and what_house == 'house':
        bill_dict[key] = {'congress': congress, 'session': session, 'senate_vote_number': [],
                          'issue': issue, 'issue_link': issue_link, 'month': month, 'issue_type': issue_type,
                          'day': day, 'year': year, 'house_vote_number': [vote_number],
                          'senate_vote_index': [], 'house_vote_index': [vote_index], 'key': key}

    return bill_dict


def nomination_tile_info(link):
    # will start being used for pn votes, and will expand as necessary
    sesh = HTMLSession()

    # need to start handling the various pages that exist
    # but might still want difference between pn actions and bills
    mod_link = '{}/actions'.format(link)
    pn_sess = sesh.get(mod_link)
    pn_soup = BeautifulSoup(pn_sess.html.html, 'html.parser')

    head_title = pn_soup.title

    try:
        meta_descr = pn_soup.find('meta', {'name': 'description'}).get('content')
    except AttributeError:
        meta_descr = ''

    h1_pn = pn_soup.find('h1')
    for child in h1_pn.children:
        # this is split on the em dash, not a normal dash
        # alt+0151
        title_list = child.split('—')
        break

    # this is kind of a stop gap measure at the moment, as much of the data is found elsewhere and
    # does not have to be found in these specific spots, but it'll work for now until I clean it up
    # later for better details
    try:
        issue_num = title_list[0]
    except IndexError:
        issue_num = ''
    try:
        nominee_name = title_list[1]
    except IndexError:
        nominee_name = ''
    try:
        position = title_list[2]
    except IndexError:
        position = ''

    overview_pn = pn_soup.find('div', {'class': 'overview'})
    i = 0
    overview_desc = ''
    overview_organization = ''
    latest_action = ''
    received_from_pres = ''
    committee = ''
    for li in overview_pn.find_all('li'):
        if i == 0:
            overview_desc = li.string
        elif i == 1:
            overview_organization = li.string
        elif i == 2:
            latest_action = li.string
        elif i == 3:
            received_from_pres = li.string
        elif i == 4:
            committee = li.string
        i += 1

    pn_map = {'issue_number': issue_num, 'nominee_name': nominee_name,
              'position': position, 'head_title': head_title, 'meta_description': meta_descr,
              'overview_description': overview_desc, 'overview_organization': overview_organization,
              'latest_action': latest_action, 'date_received_from_president': received_from_pres,
              'committee': committee}

    # actions table information
    action_table = pn_soup.find('table', {'class': 'expanded-actions item_table'})

    action_dates = ''
    action_description = ''
    action_link = ''
    for tr in action_table.find_all('tr'):
        i = 0
        for td in tr.find_all('td'):
            if i == 0:
                if action_dates == '':
                    action_dates += '{}{}'.format('\n', td.string)
                else:
                    action_dates = td.string
            else:
                if action_description == '':
                    action_description = '\n'
                    for child in td.children:
                        action_description += child.string
                else:
                    action_description += ''
                    for child in td.children:
                        action_description += child.string
                if action_link == '':
                    try:
                        action_link += '{}{}'.format('\n', td.a.get('href'))
                    except AttributeError:
                        action_link += '\n'
                else:
                    try:
                        action_link = td.a.get('href')
                    except AttributeError:
                        action_link = ''

    pn_map['dates_of_actions'] = action_dates
    pn_map['descriptions_of_actions'] = action_description
    pn_map['links_of_actions'] = action_link

    return pn_map


def download_bill_text(link, base_direc, key):
    # TODO: consider adding a method to skip this function
    # if the downloaded files exist
    sesh = HTMLSession()
    bill_sess = sesh.get(link)
    bill_soup = BeautifulSoup(bill_sess.html.html, 'html.parser')

    time.sleep(0.3)

    base_link = 'https://www.congress.gov'
    head_tag = bill_soup.find('head')

    pdf_filename = '{}/pdf_bills/{}'.format(base_direc, key)
    txt_filename = '{}/txt_bills/{}'.format(base_direc, key)
    xml_filename = '{}/xml_bills/{}'.format(base_direc, key)

    # start the actual downloads here
    try:
        pdf_tag = head_tag.find('link', {'type': 'application/pdf'})
        pdf_link = base_link + pdf_tag.get('href')
        pdf_file_name = '{}.pdf'.format(pdf_filename)

        # this part had an error with the connection closing after some time
        # adding some sleeps to see if that was the error, otherwise it might have just
        # been a lapse in connection
        # may need to restructure some of the code so that I can do it in batches
        r = requests.get(pdf_link, stream=True)
        with open(pdf_file_name, 'wb') as pdf:
            for chunk in r.iter_content(chunk_size=1024):
                if chunk:
                    pdf.write(chunk)
        had_pdf_text = True
        time.sleep(0.3)
    except AttributeError:
        print(link, ' had no pdf')
        had_pdf_text = False

    try:
        xml_tag = head_tag.find('link', {'type': 'application/xml'})
        xml_link = base_link + xml_tag.get('href')
        download_xml_file(html_session=sesh, link=xml_link, write_name=xml_filename)
        had_xml_text = True
        time.sleep(0.3)
    except AttributeError:
        print(link, ' had no xml')
        had_xml_text = False

    try:
        txt_link = link + '/text?format=txt'
        download_txt_file(html_session=sesh, link=txt_link, write_name=txt_filename)
        had_txt_text = True
        time.sleep(0.3)
    except AttributeError:
        print(link, ' had no bill text')
        had_txt_text = False

    return had_pdf_text, had_xml_text, had_txt_text


def download_xml_file(html_session, link, write_name):

    xml_sess = html_session.get(link)
    file_write_path = '{}.xml'.format(write_name)
    xml_file = open(file_write_path, 'w', encoding='utf-8')
    xml_file.writelines(xml_sess.html.html)
    xml_file.close()

    return


def download_txt_file(html_session, link, write_name):

    bill_txt_sess = html_session.get(link)
    bill_txt_soup = BeautifulSoup(bill_txt_sess.html.html, 'html.parser')
    bill_contain_tag = bill_txt_soup.find('pre', {'id': 'billTextContainer'})

    txt_write_path = '{}.txt'.format(write_name)
    txt_file = open(txt_write_path, 'w', encoding='utf-8')
    txt_file.writelines(bill_contain_tag.string)
    txt_file.close()

    return


def make_issue_type_from_issue(issue):

    output = re.sub('[0-9]', '', issue)
    output = re.sub(' ', '', output)
    output = re.sub('[.]', '', output)
    output = output.lower()

    return output


def normalize_issue_text(issue):

    output = re.sub(' ', '', issue)
    output = re.sub('[.]', '', output)
    output = output.lower()

    return output


def which_keys_and_votes_to_ignore(read_file_path, separator):
    # checks which keys to remove from dictionary

    df = pd.read_csv(read_file_path, sep=separator)
    keys = []
    keys_and_vote_dict = {}

    for row in df.itertuples():
        keys.append(row.key)

    return keys


# bill_crawl_wrapper(delete_file=False)

