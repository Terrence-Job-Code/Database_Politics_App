import os
from PIL import Image
from bs4 import BeautifulSoup
from requests_html import HTMLSession
import pandas as pd
import numpy as np
import time
import re
import shutil
import urllib3
from prototyping.utils import dictionary_functions


# zach basically took care of the plans for this function
# may delete in the future
def crawl_wikipedia():

    return


def crawl_list_of_congress():

    list_us_congress = 'https://en.wikipedia.org/wiki/List_of_United_States_Congresses'
    wiki_base_link = 'https://en.wikipedia.org'

    us_congress_sesh = HTMLSession().get(list_us_congress)
    us_congresses_soup = BeautifulSoup(us_congress_sesh.html.html)

    links_to_congress_pages = []

    for table in us_congresses_soup.find_all('table'):
        for tag in table.tbody:

            th_tag = tag.find('th')
            if th_tag != -1 and th_tag != None:

                ath_tag = th_tag.find('a')
                if ath_tag != -1 and ath_tag != None:
                    end_link = ath_tag.get('href')
                    links_to_congress_pages.append( '{}{}'.format(wiki_base_link,end_link) )
    # print(links_to_congress_pages)

    return


def go_through_congress_links(base_link, links):

    return


def simple_html_download(soup):
    # just wanting to make a file copy of the html that is downloaded and used

    return


# current house crawler
def crawl_current_house():
    # easier to go ahead and get started with current page

    wiki_base_link = 'https://en.wikipedia.org'

    house_rep_elect_2016 = 'https://en.wikipedia.org/wiki/2016_United_States_House_of_Representatives_elections'
    house_rep_cong_115 = 'https://en.wikipedia.org/wiki/List_of_members_of_the_United_States_House_of_Representatives_in_the_115th_Congress_by_seniority'
    senate_cong_115 = 'https://en.wikipedia.org/wiki/List_of_United_States_senators_in_the_115th_Congress_by_seniority'

    current_house_page = 'https://en.wikipedia.org/wiki/List_of_current_members_of_the_United_States_House_of_Representatives'
    session = HTMLSession()
    cur_house_sesh = session.get(current_house_page)
    cur_house_soup = BeautifulSoup(cur_house_sesh.html.html)

    house_table = cur_house_soup.find('table',{'id':'votingmembers'})

    wiki_dict = {}

    n_row = 0
    i = 0
    vacancy = 0

    for td in house_table.find_all('td'):

        if (i - (n_row * 9)) == 0:
            district = td.find('a').string
            district_link = '{}{}'.format(wiki_base_link,td.find('a').get('href'))

        elif (i - (n_row * 9 + 1)) == 0:
            try:
                house_rep_name = td.find('b').string
                first_name = house_rep_name.split(' ')[0]

                # so, ran into the problem I was worried about where Jr. and numerals exist
                last_name = house_rep_name.split(' ')[(len(house_rep_name.split(' '))-1)]
                if last_name.lower()=='jr.' or last_name.lower()=='jr':
                    last_name = house_rep_name.split(' ')[(len(house_rep_name.split(' '))-2)]
                if re.search('ii', last_name.lower()) and len(house_rep_name.split(' '))>2:
                    # print(last_name)
                    last_name = house_rep_name.split(' ')[(len(house_rep_name.split(' ')) - 2)]
                    # print(last_name)

                house_rep_link = '{}{}'.format(wiki_base_link, td.find('b').find('a').get('href'))
                name_key = '{}_{}'.format(first_name, last_name)
            except AttributeError:
                house_rep_name = td.string
                first_name = ''
                last_name = ''
                house_rep_link = ''
                name_key = '{}_{}'.format(house_rep_name,vacancy)
                vacancy += 1

        elif (i - (n_row * 9 + 3)) == 0:
            party = td.string

        elif (i - (n_row * 9 + 4)) == 0:
            # this can be a long list of crap
            previous_experience = []
            for exp in td.find_all('a'):
                previous_experience.append(exp.string)

        elif (i - (n_row * 9 + 5)) == 0:
            schooling = []
            for school in td.find_all('a'):
                schooling.append(school.string)

        elif (i - (n_row * 9 + 6)) == 0:
            # some of these will fill in none presently
            # can probably fix it during the reps page scrape
            year_assumed_office = td.string

        elif (i - (n_row * 9 + 7)) == 0:
            try:
                residence = td.find('a').string
            except AttributeError:
                residence = ''

        elif (i - (n_row * 9 + 8)) == 0:
            birth_year = td.string
            wiki_dict[name_key] = {'district': district,
                                   'district_link': district_link,
                                   'rep_name': house_rep_name,
                                   'first_name': first_name,
                                   'last_name': last_name,
                                   'rep_link': house_rep_link,
                                   'party': party,
                                   'experience': previous_experience,
                                   'schooling': schooling,
                                   'residence': residence,
                                   'year_born': birth_year}
            n_row += 1

        i += 1

    write_direc = 'data_storage/wikipedia_data/house_data/congress_116/'
    file_name = '{}{}'.format(write_direc,'wiki_house.csv')

    wiki_fr = pd.DataFrame(wiki_dict)
    wiki_fr_T = wiki_fr.T
    wiki_fr_T.to_csv(path_or_buf=file_name)

    # return
    image_write_path = 'data_storage/images/house_cong116_original/'

    for key in wiki_dict.keys():
        first_name = wiki_dict[key]['first_name']
        last_name = wiki_dict[key]['last_name']
        state = wiki_dict[key]['district'].split(' ')[0]
        link = wiki_dict[key]['rep_link']
        district = wiki_dict[key]['district']
        # need to handle vacancies or blank
        if link != '':

            # going to add a temporary fix, knowing this will stop all reps
            try:
                download_wiki_image(link=link,file_name=district,write_direc=image_write_path)
            except:
                print(link)
                pass
            time.sleep(0.5)

    return


def crawl_current_senate():
    # easier to go ahead and get started with current page

    wiki_base_link = 'https://en.wikipedia.org'

    house_rep_elect_2016 = 'https://en.wikipedia.org/wiki/2016_United_States_House_of_Representatives_elections'
    house_rep_cong_115 = 'https://en.wikipedia.org/wiki/List_of_members_of_the_United_States_House_of_Representatives_in_the_115th_Congress_by_seniority'
    senate_cong_115 = 'https://en.wikipedia.org/wiki/List_of_United_States_senators_in_the_115th_Congress_by_seniority'

    current_senate_page = 'https://en.wikipedia.org/wiki/List_of_United_States_senators_in_the_116th_Congress_by_seniority'
    session = HTMLSession()
    cur_senate_sesh = session.get(current_senate_page)
    cur_senate_soup = BeautifulSoup(cur_senate_sesh.html.html)
    state_to_abbrev = dictionary_functions.states_to_abbrev_dict()
    senate_table = cur_senate_soup.find('table', {'class': 'wikitable sortable'})

    wiki_dict = {}

    i = 0
    n_four_row = 0
    n_five_row = 0
    skip_count = 0
    sen_place = 0
    pick_skip = True  # only for getting through a single gap in the table

    for td in senate_table.find_all('td'):

        #  a specific piece of code to skip an error in the table
        if sen_place == 67 and (i - (n_five_row * 5 + n_four_row * 4)) == 0 and pick_skip:
            pick_skip = False
            continue

        if (i - (n_five_row * 5 + n_four_row * 4)) == 0:
            sen_place += 1
            full_name = td.a.string
            sen_link = wiki_base_link + td.a.get('href')
            first_name = full_name.split(' ')[0]
            last_name = full_name.split(' ')[1]

        elif (i - (n_five_row * 5 + n_four_row * 4 + 1)) == 0:
            sen_party = td.string.split('\n')[0]

        elif (i - (n_five_row * 5 + n_four_row * 4 + 2)) == 0:
            state = td.a.string.lower()
            state_abbrev = state_to_abbrev[state]
            name_id = '{}_{}_{}'.format(first_name, last_name, state_abbrev)
            wiki_dict[name_id] = {'full_name': full_name,
                                  'first_name': first_name,
                                  'last_name': last_name,
                                  'party': sen_party,
                                  'state': state,
                                  'state_abbrev': state_abbrev,
                                  'link': sen_link}

        elif (i - (n_five_row * 5 + n_four_row * 4 + 3)) == 0:

            if skip_count > 0:
                skip_count -= 1
                n_four_row += 1
                i += 1
                continue

            rowspan_amount = td.get('rowspan')
            if rowspan_amount != None:
                skip_count = int(rowspan_amount) - 1

        elif (i - (n_five_row * 5 + n_four_row * 4 + 4)) == 0:
            n_five_row += 1

        i += 1

    write_direc = 'data_storage/wikipedia_data/senate_data/congress_116/'
    file_name = '{}{}'.format(write_direc, 'wiki_senate.csv')

    wiki_fr = pd.DataFrame(wiki_dict)
    wiki_fr_T = wiki_fr.T
    wiki_fr_T.to_csv(path_or_buf=file_name,index=False)

    # return

    image_write_path = 'data_storage/images/senate_cong116_original/'

    for key in wiki_dict.keys():
        first_name = wiki_dict[key]['first_name']
        last_name = wiki_dict[key]['last_name']
        link = wiki_dict[key]['link']
        # need to handle vacancies or blank
        if link != '':

            # going to add a temporary fix, knowing this will stop all reps
            try:
                # download_wiki_image(first_name=first_name, last_name=last_name, state=state, link=link)
                download_wiki_image(link=link, file_name=key, write_direc=image_write_path)
            except:
                print(link)
                pass
            time.sleep(0.5)

    return


def image_type(soup):

    vcard_table = soup.find('table', {'class': 'infobox vcard'})

    # hopefully this is sufficient
    file_string = vcard_table.find('img').get('alt')

    jpeg_type = re.search('jpeg', file_string)
    jpg_type = re.search('jpg', file_string)
    png_type = re.search('png', file_string)

    # just give this a default type, so at worst it works like it did previously
    photo_type = 'jpg'

    if jpg_type:
        photo_type = 'jpg'
    elif jpeg_type:
        photo_type = 'jpeg'
    elif png_type:
        photo_type = 'png'

    return photo_type


def get_image_string(link):

    sesh = HTMLSession()

    wiki_link = link
    wiki_sesh = sesh.get(wiki_link)
    wiki_soup = BeautifulSoup(wiki_sesh.html.html)

    photo_type = image_type(wiki_soup)

    vcard_table = wiki_soup.find('table', {'class': 'infobox vcard'})
    link01 = vcard_table.find('img').get('src')
    jpg = re.search(photo_type, link01)
    link02 = link01[:jpg.end()]
    thumb = re.search('thumb', link02)
    link03 = link02[:thumb.start()] + link02[thumb.end():]

    image_link = 'https:{}'.format(link03)

    return image_link, photo_type


def download_wiki_image(write_direc,link,file_name):

    image_link, photo_type = get_image_string(link=link)
    http = urllib3.PoolManager()
    r = http.request('GET', image_link, preload_content=False)

    # file_path_base = 'data_storage/images/senate_cong116_original/'
    file_path_base = write_direc
    file_path = file_path_base + '{}.jpg'.format(file_name)

    with open(file_path, 'wb') as out:
        while True:
            data = r.read(2 ** 16)
            if not data:
                break
            out.write(data)
    r.release_conn()

    return

# crawl_current_house()
# crawl_list_of_congress()
# crawl_current_senate()
# Zach's code starts here


class Human:

    def __init__(self):
        self.first_name = None
        self.last_name = None
        self.wiki_link = None
        self.species = None
        self.state = None
        self.district = None
        self.isIncumbent = None
        self.priorJobs = None
        self.education = None
        self.party = None
        self.officeStartDate = None
        self.birthDate = None
        self.birthPlace = None
        self.children = None
        self.spouses = None
        self.website = None
        self.otherParties = None
        self.militaryService = None


class MilitaryServices:
    def __init__(self):
        self.branch = None
        self.unit = None
        self.battles = None
        self.awards = None


class WikiBioCrawler:
    ## Start by using get links to start building a list of senators and house reps

    def __init__(self):
        self.sesh = HTMLSession()
        self.current_house_page = "https://en.wikipedia.org/wiki/List_of_current_members_of_the_United_States_House_of_Representatives"
        self.current_senate_page = "https://en.wikipedia.org/wiki/List_of_current_United_States_senators"
        self.base_link = "https://en.wikipedia.org/"
        self.List_of_Senators = []
        self.List_of_HouseReps = []

    def get_links(self):
        html_session = self.sesh.get(self.current_house_page)
        html_soup = BeautifulSoup(html_session.html.html, 'html.parser')
        # find table
        x = html_soup.find("table", id="votingmembers")
        y = x.find_all("tbody")[0]
        z = y.find_all("tr")
        reps = []
        for it in z:
            if "Prior experience" in it.text:
                continue
            hum = Human()
            hum.species = "house"
            x = it.find_all("td")[0]
            xx = x.find_all("span")[0].find_all("a")[0].contents[0]
            xxx = str(xx).replace(u'\xa0', ' ').split(" ")
            hum.state = xxx[0]
            if "at-large" in xxx[1]:
                xxx[1] = 1
            hum.district = xxx[1]
            tds = it.find_all("td")
            party = tds[3].text.replace("\n", "")
            hum.party = party
            priors = []
            p = tds[4].contents
            skipnext = False
            index = 0
            for i in p:
                index += 1
                if skipnext:
                    skipnext=False
                    continue
                try:
                    if len(i.contents)>0:
                        thing = str(i.contents[0])
                        if "House of Representatives" in thing:
                            continue
                        try:
                            fucky = str(i.nextSibling)
                            if "<br/>" not in fucky:
                                ns = str(i.nextSibling)
                                thing += ns
                                skipnext = True
                        except:
                            print('eh')
                        thing = thing.replace("\n", "")
                        if len(thing) > 0:
                            priors.append(thing)

                except:
                    thing = str(i)
                    try:
                        fucky = p[index].contents[0]
                        if "<br/>" not in fucky:
                            ns = fucky
                            thing += ns
                            skipnext = True
                    except:
                        print("caught")
                        thing = thing.replace("\n", "")
                    if len(thing) > 0:
                        priors.append(thing)

            hum.priorJobs = priors
            eduss = tds[5].text.split(")")
            edus = []
            for itt in eduss:
                if "\n" in itt:
                    continue
                itt += ")"
                edus.append(itt)

            hum.education = edus
            a = it.find_all("td")[1]
            if "vacant" in str(a).lower():
                continue
            bb = a.attrs
            bbb = bb["data-sort-value"]
            b = str(bbb).split(",")
            if len(b) <= 1:
                b = b[0].split(" ")
            hum.first_name = b[1].replace(" ", "")
            hum.last_name = b[0]
            c = a.find_all("b")[0]
            d = c.find_all("a")[0]
            e = d.attrs
            f = e["href"]
            hum.wiki_link = self.base_link + f
            reps.append(hum)
        self.List_of_HouseReps = reps

        html_session = self.sesh.get(self.current_senate_page)
        html_soup = BeautifulSoup(html_session.html.html, 'html.parser')
        senators = []
        # find table
        x = html_soup.find("table", id="senators")
        y = x.find_all("tbody")[0]
        z = y.find_all("tr")
        for it in z:
            if "Assumed office" in it.text:
                continue
            hum = Human()
            hum.species = "senate"
            x = it.find_all("td")[0]
            xx = x.find_all("a")[0].contents[0]
            hum.state = xx
            a = it.find_all("th")[0]
            aa = a.find_all("span")[0]
            if ("vacant" in str(aa).lower()):
                continue
            bb = aa.attrs
            bbb = bb["data-sort-value"]
            b = str(bbb).split(",")
            if(len(b)<=1):
                b = b[0].split(" ")
            hum.first_name = b[1].replace(" ","")
            hum.last_name = b[0]
           # c = a.find_all("b")[0]
            d = aa.find_all("a")[0]
            e = d.attrs
            f = e["href"]
            hum.wiki_link=self.base_link + f
            tds = it.find_all("td")
            party = tds[3].text.replace("\n", "")
            txt1 = tds[7].text
            if("age" in party):
                party = tds[2].text.replace("\n", "")
                txt1 = tds[6].text
            txt1 = txt1.replace("Serving", "\n").replace("office", "\n")
            txts = txt1.split("\n")
            dateString = ""
            for ttt in txts:
                if (len(ttt) <= 1):
                    continue
                dateString += ttt + " "
            dateStringarr = dateString.split(" ")
            m = dateStringarr[0]
            d = dateStringarr[1].split(",")[0]
            y = dateStringarr[2]
            mtn = dictionary_functions.month_to_num()
            month = str(mtn[m[0].lower() + m[1] + m[2]])
            if (len(str(month)) == 1):
                month = "0" + str(month)
            day = str(d)
            if (len(day) == 1):
                day = "0" + day
            year = str(y)
            date = month + "/" + day + "/" + year
            hum.officeStartDate = date
            hum.party = party
            priors = []
            p = tds[5].contents
            skipnext = False
            index = 0
            for i in p:
                index += 1
                if (skipnext):
                    skipnext = False
                    continue
                try:
                    if (len(i.contents) > 0):
                        thing = str(i.contents[0])

                        try:
                            fucky = str(i.nextSibling)
                            if ("<br/>" not in fucky):
                                ns = str(i.nextSibling)
                                thing += ns
                                skipnext = True
                        except:
                            print('eh')
                        thing = thing.replace("\n", "")
                        if (len(thing) > 0):
                            priors.append(thing)

                except:
                    thing = str(i)
                    try:
                        fucky = p[index].contents[0]
                        if ("<br/>" not in fucky):
                            ns = fucky
                            thing += ns
                            skipnext = True
                    except:
                        print("caught")
                        thing = thing.replace("\n", "")
                    if (len(thing) > 0):
                        priors.append(thing)

            hum.priorJobs = priors
            senators.append(hum)
        self.List_of_Senators = senators

        return

    def get_bios(self):
        sen = self.List_of_Senators
        reps = self.List_of_HouseReps
        for it in reps:
            html_session = self.sesh.get(it.wiki_link)
            html_soup = BeautifulSoup(html_session.html.html, 'html.parser')
            b = html_soup.find_all("b")
            table = html_soup.find_all("table", {"class": "infobox"})[0]
            trs = table.find_all("tr")
            #find office date
            lookfordatehere = False
            for tr in trs:
                if("Member of the U.S. House of Representatives" in tr.text):
                    lookfordatehere = True
                if(lookfordatehere):
                    if("Assumed office" in tr.text):
                        txt1 = tr.text
                        txt1 = txt1.replace("Serving", "\n").replace("office","\n")
                        txts = txt1.split("\n")
                        txts2 = txts[1].split(" ")
                        dateString = ""
                        for t in txts2:
                            if(len(t)<=1):
                                continue
                            dateString += t + " "
                        dateStringarr = dateString.split(" ")
                        if(len(dateStringarr)<=3):
                            dateStringarr = dateString.split(u'\xa0')
                        m = dateStringarr[0]
                        d = dateStringarr[1].split(",")[0]
                        y = dateStringarr[2]
                        mtn = dictionary_functions.month_to_num()
                        month = str(mtn[m[0].lower()+m[1]+m[2]])
                        if(len(str(month)) == 1):
                            month = "0" + str(month)
                        day = str(d)
                        if(len(day) == 1):
                            day = "0"+day
                        year = str(y)
                        date = month+"/"+day+"/"+year
                        it.officeStartDate = date
                        lookfordatehere = False
                        break

            lookforpersonalhere = False
            for tr in trs:
                if ("Personal details" in tr.text):
                    lookforpersonalhere = True
                elif("Military service" in tr.text):
                    lookforpersonalhere = False
                if (lookforpersonalhere):
                    try:
                        th = tr.find_all("th")[0]
                        if("Born" in th.text):
                            birthshits = tr.find_all("td")[0]
                            bd = birthshits.find_all("span", {"class": "bday"})[0].text
                            bda = bd.split('-')
                            y = bda[0]
                            m = bda[1]
                            d = bda[2]
                            birtdate = m+"/"+d+"/"+y
                            holyfuck = birthshits.text.split(")")[-1]
                            if("]" in holyfuck):
                                holyfuck = holyfuck.split("]")[1].split("[")[0]
                            birthplace = holyfuck
                            it.birthDate = birtdate
                            it.birthPlace = birthplace
                        elif ("Children" in th.text):
                            shits = tr.find_all("td")[0]
                            childs = shits.text
                            it.children = childs
                        elif ("Spouse(s)" in th.text):
                            shits = tr.find_all("td")[0]
                            spouses = shits.text
                            it.spouses = spouses
                        elif ("Website" in th.text):
                            shits = tr.find_all("td")[0]
                            fuck = shits.find_all("a")[0].attrs["href"]
                            website = fuck
                            it.website = website
                        elif ("Other politicalaffiliations" in th.text):
                            shits = tr.find_all("td")[0]
                            otherparties = shits.text
                            it.otherParties = otherparties
                    except:
                        print("couldn't find th in bio")
            lookforpersonalhere = False
            loookformilitaryservicehere = False
            ms = None
            for tr in trs:

                if("Military service" in tr.text):
                    loookformilitaryservicehere = True
                    ms = MilitaryServices()
                if (loookformilitaryservicehere):
                    try:
                        th = tr.find_all("th")[0]
                        if ("Branch/service" in th.text):
                            shits = tr.find_all("td")[0]
                            ms.branch = shits.text
                        elif("Unit" in th.text):
                            shits = tr.find_all("td")[0]
                            ms.unit = shits.text
                        elif("Battles/wars" in th.text):
                            shits = tr.find_all("td")[0]
                            ms.battles = shits.text
                        elif("Awards" in th.text):
                            shits = tr.find_all("td")[0]
                            ms.awards = shits
                    except:
                        print("couldn't find th in bio")
            if(ms!=None):
                it.militaryService = ms

        for it in sen:
            html_session = self.sesh.get(it.wiki_link)
            html_soup = BeautifulSoup(html_session.html.html, 'html.parser')
            b = html_soup.find_all("b")
            table = html_soup.find_all("table", {"class": "infobox"})[0]
            trs = table.find_all("tr")
            #find office date
            lookfordatehere = False
            for tr in trs:
                if("United States senator" in tr.text):
                    lookfordatehere = True
                if(lookfordatehere):
                    if("Assumed office" in tr.text):
                        txt1 = tr.text
                        txt1 = txt1.replace("Serving", "\n").replace("office","\n")
                        txts = txt1.split("\n")
                        txts2 = txts[1].split(" ")
                        dateString = ""
                        for t in txts2:
                            if(len(t)<=1):
                                continue
                            dateString += t + " "
                        dateStringarr = dateString.split(" ")
                        if(len(dateStringarr)<=3):
                            dateStringarr = dateString.split(u'\xa0')
                        m = dateStringarr[0]
                        d = dateStringarr[1].split(",")[0]
                        y = dateStringarr[2]
                        mtn = dictionary_functions.month_to_num()
                        month = str(mtn[m[0].lower()+m[1]+m[2]])
                        if(len(str(month)) == 1):
                            month = "0" + str(month)
                        day = str(d)
                        if(len(day) == 1):
                            day = "0"+day
                        year = str(y)
                        date = month+"/"+day+"/"+year
                        it.officeStartDate = date
                        lookfordatehere = False
                        break

            lookforpersonalhere = False
            for tr in trs:
                if ("Personal details" in tr.text):
                    lookforpersonalhere = True
                elif("Military service" in tr.text):
                    lookforpersonalhere = False
                if (lookforpersonalhere):
                    try:
                        th = tr.find_all("th")[0]
                        if("Born" in th.text):
                            birthshits = tr.find_all("td")[0]
                            bd = birthshits.find_all("span", {"class": "bday"})[0].text
                            bda = bd.split('-')
                            y = bda[0]
                            m = bda[1]
                            d = bda[2]
                            birtdate = m+"/"+d+"/"+y
                            holyfuck = birthshits.text.split(")")[-1]
                            if("]" in holyfuck):
                                holyfuck = holyfuck.split("]")[1].split("[")[0]
                            birthplace = holyfuck
                            it.birthDate = birtdate
                            it.birthPlace = birthplace
                        elif ("Children" in th.text):
                            shits = tr.find_all("td")[0]
                            childs = shits.text
                            it.children = childs
                        elif ("Spouse(s)" in th.text):
                            shits = tr.find_all("td")[0]
                            spouses = shits.text
                            it.spouses = spouses
                        elif ("Website" in th.text):
                            shits = tr.find_all("td")[0]
                            fuck = shits.find_all("a")[0].attrs["href"]
                            website = fuck
                            it.website = website
                        elif ("Other politicalaffiliations" in th.text):
                            shits = tr.find_all("td")[0]
                            otherparties = shits.text
                            it.otherParties = otherparties
                        elif ("Education" in th.text):
                            shits = tr.find_all("td")[0]
                            eduss = shits.text.split(")")
                            edus = []
                            for itt in eduss:
                                if ("\n" in itt):
                                    continue
                                itt += ")"
                                if(len(itt)>1):
                                    edus.append(itt)

                            it.education = edus
                    except:
                        print("couldn't find th in bio")
            lookforpersonalhere = False
            loookformilitaryservicehere = False
            ms = None
            for tr in trs:

                if("Military service" in tr.text):
                    loookformilitaryservicehere = True
                    ms = MilitaryServices()
                if (loookformilitaryservicehere):
                    try:
                        th = tr.find_all("th")[0]
                        if ("Branch/service" in th.text):
                            shits = tr.find_all("td")[0]
                            ms.branch = shits.text
                        elif("Unit" in th.text):
                            shits = tr.find_all("td")[0]
                            ms.unit = shits.text
                        elif("Battles/wars" in th.text):
                            shits = tr.find_all("td")[0]
                            ms.battles = shits.text
                        elif("Awards" in th.text):
                            shits = tr.find_all("td")[0]
                            ms.awards = shits
                    except:
                        print("couldn't find th in bio")
            if(ms!=None):
                it.militaryService = ms

        print("asdf")
        return


def run_all_wiki_bios():
    x = WikiBioCrawler()
    x.get_links()
    x.get_bios()
    print('wiki crawler finished')
    return x

