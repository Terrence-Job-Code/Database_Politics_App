import unicodedata
import re


def states_to_abbrev_dict():
    # best to use with with the lower operator on incoming strings
    states_to_abbrev = {'alabama': 'AL', 'alaska': 'AK', 'arizona': 'AZ',
                        'arkansas': 'AR', 'california': 'CA',
                        'colorado': 'CO', 'connecticut': 'CT', 'delaware': 'DE',
                        'florida': 'FL', 'georgia': 'GA', 'hawaii': 'HI',
                        'idaho': 'ID', 'mississippi': 'MS',
                        'illinois': 'IL', 'indiana': 'IN', 'iowa': 'IA',
                        'kansas': 'KS', 'kentucky': 'KY', 'louisiana': 'LA',
                        'maine': 'ME', 'maryland': 'MD', 'massachusetts': 'MA',
                        'michigan': 'MI', 'minnesota': 'MN',
                        'missouri': 'MO', 'montana': 'MT', 'nebraska': 'NE',
                        'nevada': 'NV', 'new hampshire': 'NH',
                        'new jersey': 'NJ', 'new mexico': 'NM', 'new york': 'NY',
                        'north carolina': 'NC', 'north dakota': 'ND', 'ohio': 'OH',
                        'oklahoma': 'OK', 'oregon': 'OR', 'pennsylvania': 'PA', 'rhode island': 'RI',
                        'south carolina': 'SC', 'south dakota': 'SD', 'tennessee': 'TN',
                        'texas': 'TX', 'utah': 'UT', 'vermont': 'VT',
                        'virginia': 'VA', 'washington': 'WA', 'west virginia': 'WV',
                        'wisconsin': 'WI', 'wyoming': 'WY'}

    return states_to_abbrev


def abbrev_to_states_dict():
    states_to_abbrev = {'alabama': 'AL', 'alaska': 'AK', 'arizona': 'AZ',
                        'arkansas': 'AR', 'california': 'CA',
                        'colorado': 'CO', 'connecticut': 'CT', 'delaware': 'DE',
                        'florida': 'FL', 'georgia': 'GA', 'hawaii': 'HI',
                        'idaho': 'ID', 'illinois': 'IL', 'indiana': 'IN',
                        'iowa': 'IA', 'kansas': 'KS', 'kentucky': 'KY',
                        'louisiana': 'LA', 'mississippi': 'MS',
                        'maine': 'ME', 'maryland': 'MD', 'massachusetts': 'MA',
                        'michigan': 'MI', 'minnesota': 'MN', 'missouri': 'MO',
                        'montana': 'MT', 'nebraska': 'NE', 'nevada': 'NV', 'new hampshire': 'NH',
                        'new jersey': 'NJ', 'new mexico': 'NM', 'new york': 'NY', 'north carolina': 'NC',
                        'north dakota': 'ND', 'ohio': 'OH', 'oklahoma': 'OK', 'oregon': 'OR',
                        'pennsylvania': 'PA', 'rhode island': 'RI', 'south carolina': 'SC',
                        'south dakota': 'SD', 'tennessee': 'TN', 'texas': 'TX', 'utah': 'UT',
                        'vermont': 'VT', 'virginia': 'VA', 'washington': 'WA',
                        'west virginia': 'WV', 'wisconsin': 'WI', 'wyoming': 'WY'}

    abbrev_to_states = {}
    for key in states_to_abbrev.keys():
        abbrev_to_states[states_to_abbrev[key]] = key

    return abbrev_to_states


def month_to_num():

    months = {'jan': 1, 'feb': 2, 'mar': 3, 'apr': 4, 'may': 5, 'jun': 6,
              'jul': 7, 'aug': 8, 'sep': 9, 'oct': 10, 'nov': 11, 'dec': 12}

    return months


def issue_abbreviation_dictionary():

    # these abbreviations are not yet complete
    bill_dict = {'hr': 'House Bill', 's': 'Senate Bill', 'hjres': 'House Joint Resolution',
                 'sjres': 'Senate Joint Resolution', 'hconres': 'House Concurrent Resolution',
                 'sconres': 'Senate Concurrent Resolution', 'hres': 'House Simple Resolution',
                 'sres': 'Senate Simple Resolution'}

    return bill_dict


def year_congress_session():

    year_dict = {'2020': {'congress': '116', 'session': '2'}, '2019': {'congress': '116', 'session': '1'},
                 '2018': {'congress': '115', 'session': '2'}, '2017': {'congress': '115', 'session': '1'},
                 '2016': {'congress': '114', 'session': '2'}, '2015': {'congress': '114', 'session': '1'},
                 '2014': {'congress': '113', 'session': '2'}, '2013': {'congress': '113', 'session': '1'},
                 '2012': {'congress': '112', 'session': '2'}, '2011': {'congress': '112', 'session': '1'},
                 '2010': {'congress': '111', 'session': '2'}, '2009': {'congress': '111', 'session': '1'},
                 '2008': {'congress': '110', 'session': '2'}, '2007': {'congress': '110', 'session': '1'},
                 '2006': {'congress': '109', 'session': '2'}, '2005': {'congress': '109', 'session': '1'},
                 '2004': {'congress': '108', 'session': '2'}, '2003': {'congress': '108', 'session': '1'},
                 '2002': {'congress': '107', 'session': '2'}, '2001': {'congress': '107', 'session': '1'},
                 '2000': {'congress': '106', 'session': '2'}, '1999': {'congress': '106', 'session': '1'},
                 '1998': {'congress': '105', 'session': '2'}, '1997': {'congress': '105', 'session': '1'},
                 '1996': {'congress': '104', 'session': '2'}, '1995': {'congress': '104', 'session': '1'},
                 '1994': {'congress': '103', 'session': '2'}, '1993': {'congress': '103', 'session': '1'},
                 '1992': {'congress': '102', 'session': '2'}, '1991': {'congress': '102', 'session': '1'},
                 '1990': {'congress': '101', 'session': '2'}, '1989': {'congress': '101', 'session': '1'},
                 }

    return year_dict

