

# some local directory paths
polic_data_paths = 'D:/Programming/PolySci/Polysci-Backend/prototyping/data_storage/'
house_summary_directory = polic_data_paths + 'house_data/summary_data/'
# for roll call votes, could create a new directory where I reformat some of the data
# given that they now offer new stuff
house_roll_call_votes_directory = polic_data_paths + 'house_data/roll_call_votes/'

# new house directories
house_summary_directory_new = polic_data_paths + 'house_data/new_summary_data/'
house_roll_call_votes_directory_new = polic_data_paths + 'house_data/new_roll_call_votes/'
house_representative_votes_new = polic_data_paths + 'house_data/new_representative_votes/'

# senate directories
senate_storage = polic_data_paths + 'senate_data/'

crawled_senate_base = senate_storage + 'crawled_data/'

senate_vote_sets = crawled_senate_base + 'full_vote_sets/'
senate_vote_summaries = crawled_senate_base + 'link_summaries/'
senate_xml_table = crawled_senate_base + 'xml_summaries/'

senate_rep_votes = senate_storage + 'representative_votes/'
senate_rep_summary_bio = senate_storage + 'representative_summaries/senator_bio.csv'

# wiki house directories
wiki_house_mod_path = polic_data_paths + 'wikipedia_data/house_data/congress_116/wiki_house_mod.csv'
wiki_senate_path = polic_data_paths + 'wikipedia_data/senate_data/congress_116/wiki_senate.csv'
wiki_house_path = polic_data_paths + 'wikipedia_data/house_data/congress_116/wiki_house.csv'

# bill information
bill_title_summary_path = polic_data_paths + 'bill_information/bill_title_summaries.csv'

# some core website stuff
house_base_page = 'https://clerk.house.gov'

# selenium driver location
geckopath = 'D:/Programming/geckodriver-v0.27.0-win64/geckodriver.exe'

# firebase json location
json_location = 'D:/Programming/PolySci/Polysci-Backend/prototyping/polysci-46fd2-firebase-adminsdk-aazrh-5df1614df1.json'

# names.csv
nicknames_path = 'D:/Programming/PolySci/Polysci-Backend/prototyping/utils/names.csv'