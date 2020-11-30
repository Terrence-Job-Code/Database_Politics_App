import re
import unicodedata


def strip_accents(text):
    # for removing accents
    text = unicodedata.normalize('NFD',text).encode('ascii','ignore').decode('utf-8')
    return str(text)


def strip_commas(text):
    final_text = re.sub('\,', '', text)
    return final_text


def strip_periods(text):
    final_text = re.sub('\.', '', text)
    return final_text


def remove_parenths(text):
    final_text = re.sub('\(.*?\)', '', text)
    return final_text


def remove_unwanted_text(text):
    # this is designed to clean house rep names for processing
    # removes periods, commas, and text in ()
    final_text = re.sub('\,', '', text)
    final_text = re.sub('\.', '', final_text)
    final_text = re.sub('_\(.*?\)', '', final_text)
    # final_text = re.sub('\(.*?\)', '', final_text)

    return final_text


def remove_single_quotes(text):

    final_text = re.sub('[\']', '', text)

    return final_text


def remove_square_brackets(text):

    final_text = re.sub('[\[\]]', '', text)

    return final_text


def string_short(text):
    while text[len(text)-1] == ' ':
        text = text[:len(text)-1]
    return text


def comma_replace_text(text):
    # this is to replace text in the csv with a place holder for commas
    # so that I can store it without ruining csv structure
    # or, maybe just change delimiter
    final_text = re.sub('\,', '\t&comma\t', text)

    return final_text
