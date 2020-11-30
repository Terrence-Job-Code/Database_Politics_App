
def standardize_index(index):

    # index has form
    # cn###sn#vn#
    # will make it
    # cn###sn#vn#####
    # print('index_type = {}, index = {}'.format(type(index), index))

    congress_number = int(index.split('cn')[1].split('sn')[0])
    session_number = index.split('sn')[1].split('vn')[0]
    vote_number = int(index.split('vn')[1])

    if congress_number >= 100:
        congress_text = str(congress_number)
    elif 10 <= congress_number < 100:
        congress_text = '0{}'.format(congress_number)
    else:
        congress_text = '00{}'.format(congress_number)

    if vote_number >= 1000:
        vote_text = '0{}'.format(vote_number)
    elif 100 <= vote_number < 1000:
        vote_text = '00{}'.format(vote_number)
    elif 10 <= vote_number < 100:
        vote_text = '000{}'.format(vote_number)
    else:
        vote_text = '0000{}'.format(vote_number)

    final_index = 'cn{}sn{}vn{}'.format(congress_text, session_number, vote_text)

    return final_index


def standardize_vote_number(vote_number):

    vote_number = int(vote_number)

    if vote_number >= 1000:
        vote_text = '0{}'.format(vote_number)
    elif 100 <= vote_number < 1000:
        vote_text = '00{}'.format(vote_number)
    elif 10 <= vote_number < 100:
        vote_text = '000{}'.format(vote_number)
    else:
        vote_text = '0000{}'.format(vote_number)

    return vote_text
