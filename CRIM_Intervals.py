import streamlit as st
from pathlib import Path
import requests
import pandas as pd
from pandas.io.json import json_normalize
import base64
from crim_intervals import *
import ast
from itertools import tee, combinations
import matplotlib

# download function

@st.cache(allow_output_mutation=True)

#sets up function to call Markdown File for "about"
def read_markdown_file(markdown_file):
    return Path(markdown_file).read_text()

def download_link(object_to_download, download_filename, download_link_text):
    """
    Generates a link to download the given object_to_download.

    object_to_download (str, pd.DataFrame):  The object to be downloaded.
    download_filename (str): filename and extension of file. e.g. mydata.csv, some_txt_output.txt
    download_link_text (str): Text to display for download link.

    Examples:
    download_link(YOUR_DF, 'YOUR_DF.csv', 'Click here to download data!')
    download_link(YOUR_STRING, 'YOUR_STRING.txt', 'Click here to download your text!')

    """
    if isinstance(object_to_download,pd.DataFrame):
        object_to_download = object_to_download.to_csv(index=False)

    # some strings <-> bytes conversions necessary here
    b64 = base64.b64encode(object_to_download.encode()).decode()

    return f'<a href="data:file/txt;base64,{b64}" download="{download_filename}">{download_link_text}</a>'

# functions for pairs of ratios

def pairwise(iterable):
    "s -> (s0,s1), (s1,s2), (s2, s3), ..."
    a, b = tee(iterable)
    next(b, None)
    return zip(a, b)

def get_ratios(input_list):
    ratio_pairs = []
    for a, b in pairwise(input_list):
        ratio_pairs.append(b / a)
    return ratio_pairs

# Here we group the rows in the DF by the Pattern Generating Match
# Each has its own string of durations, and duration ratios
# and then we compare the ratios to get the differences
# the "list(combinations)" method takes care of building the pairs, using data from our dataframe 'results'

def compare_ratios(ratios_1, ratios_2):
    
    ## division of lists 
    # using zip() + list comprehension 
    diffs = [i - j for i, j in zip(ratios_1, ratios_2)] 
    abs_diffs = [abs(ele) for ele in diffs] 
    sum_diffs = sum(abs_diffs)

    return sum_diffs

#results["Pattern_Generating_Match"] = results["Pattern_Generating_Match"].apply(tuple) 

def get_ratio_distances(results, pattern_col, output_cols):
    
    matches = []

    for name, group in results.groupby(pattern_col):

        ratio_pairs = list(combinations(group.index.values, 2))

        for a, b in ratio_pairs:
            
            a_match = results.loc[a]
            b_match = results.loc[b]
            
            sum_diffs = compare_ratios(a_match.duration_ratios, b_match.duration_ratios)
            
            match_dict = {
                "pattern": name,
                "sum_diffs": sum_diffs
            }
            
            for col in output_cols:
                match_dict.update({
                    f"match_1_{col}": a_match[col],
                    f"match_2_{col}": b_match[col]
                })
                
            matches.append(match_dict)
            
    return pd.DataFrame(matches)

# work lists

CRIM_Corpus = ['https://crimproject.org/mei/CRIM_Mass_0001_1.mei',
 'https://crimproject.org/mei/CRIM_Mass_0001_2.mei',
 'https://crimproject.org/mei/CRIM_Mass_0001_3.mei',
 'https://crimproject.org/mei/CRIM_Mass_0001_4.mei',
 'https://crimproject.org/mei/CRIM_Mass_0001_5.mei',
 'https://crimproject.org/mei/CRIM_Mass_0002_1.mei',
 'https://crimproject.org/mei/CRIM_Mass_0002_2.mei',
 'https://crimproject.org/mei/CRIM_Mass_0002_3.mei',
 'https://crimproject.org/mei/CRIM_Mass_0002_4.mei',
 'https://crimproject.org/mei/CRIM_Mass_0002_5.mei',
 'https://crimproject.org/mei/CRIM_Mass_0003_1.mei',
 'https://crimproject.org/mei/CRIM_Mass_0003_2.mei',
 'https://crimproject.org/mei/CRIM_Mass_0003_3.mei',
 'https://crimproject.org/mei/CRIM_Mass_0003_4.mei',
 'https://crimproject.org/mei/CRIM_Mass_0003_5.mei',
 'https://crimproject.org/mei/CRIM_Mass_0004_1.mei',
 'https://crimproject.org/mei/CRIM_Mass_0004_2.mei',
 'https://crimproject.org/mei/CRIM_Mass_0004_3.mei',
 'https://crimproject.org/mei/CRIM_Mass_0004_4.mei',
 'https://crimproject.org/mei/CRIM_Mass_0004_5.mei',
 'https://crimproject.org/mei/CRIM_Mass_0005_1.mei',
 'https://crimproject.org/mei/CRIM_Mass_0005_2.mei',
 'https://crimproject.org/mei/CRIM_Mass_0005_3.mei',
 'https://crimproject.org/mei/CRIM_Mass_0005_4.mei',
 'https://crimproject.org/mei/CRIM_Mass_0005_5.mei',
 'https://crimproject.org/mei/CRIM_Mass_0006_1.mei',
 'https://crimproject.org/mei/CRIM_Mass_0006_2.mei',
 'https://crimproject.org/mei/CRIM_Mass_0006_3.mei',
 'https://crimproject.org/mei/CRIM_Mass_0006_4.mei',
 'https://crimproject.org/mei/CRIM_Mass_0006_5.mei',
 'https://crimproject.org/mei/CRIM_Mass_0007_1.mei',
 'https://crimproject.org/mei/CRIM_Mass_0007_2.mei',
 'https://crimproject.org/mei/CRIM_Mass_0007_3.mei',
 'https://crimproject.org/mei/CRIM_Mass_0007_4.mei',
 'https://crimproject.org/mei/CRIM_Mass_0007_5.mei',
 'https://crimproject.org/mei/CRIM_Mass_0008_1.mei',
 'https://crimproject.org/mei/CRIM_Mass_0008_2.mei',
 'https://crimproject.org/mei/CRIM_Mass_0008_3.mei',
 'https://crimproject.org/mei/CRIM_Mass_0008_4.mei',
 'https://crimproject.org/mei/CRIM_Mass_0008_5.mei',
 'https://crimproject.org/mei/CRIM_Mass_0009_1.mei',
 'https://crimproject.org/mei/CRIM_Mass_0009_2.mei',
 'https://crimproject.org/mei/CRIM_Mass_0009_3.mei',
 'https://crimproject.org/mei/CRIM_Mass_0009_4.mei',
 'https://crimproject.org/mei/CRIM_Mass_0009_5.mei',
 'https://crimproject.org/mei/CRIM_Mass_0010_1.mei',
 'https://crimproject.org/mei/CRIM_Mass_0010_2.mei',
 'https://crimproject.org/mei/CRIM_Mass_0010_3.mei',
 'https://crimproject.org/mei/CRIM_Mass_0010_4.mei',
 'https://crimproject.org/mei/CRIM_Mass_0010_5.mei',
 'https://crimproject.org/mei/CRIM_Mass_0011_1.mei',
 'https://crimproject.org/mei/CRIM_Mass_0011_2.mei',
 'https://crimproject.org/mei/CRIM_Mass_0011_3.mei',
 'https://crimproject.org/mei/CRIM_Mass_0011_4.mei',
 'https://crimproject.org/mei/CRIM_Mass_0011_5.mei',
 'https://crimproject.org/mei/CRIM_Mass_0012_1.mei',
 'https://crimproject.org/mei/CRIM_Mass_0012_2.mei',
 'https://crimproject.org/mei/CRIM_Mass_0012_3.mei',
 'https://crimproject.org/mei/CRIM_Mass_0012_4.mei',
 'https://crimproject.org/mei/CRIM_Mass_0012_5.mei',
 'https://crimproject.org/mei/CRIM_Mass_0013_1.mei',
 'https://crimproject.org/mei/CRIM_Mass_0013_2.mei',
 'https://crimproject.org/mei/CRIM_Mass_0013_3.mei',
 'https://crimproject.org/mei/CRIM_Mass_0013_4.mei',
 'https://crimproject.org/mei/CRIM_Mass_0013_5.mei',
 'https://crimproject.org/mei/CRIM_Mass_0014_1.mei',
 'https://crimproject.org/mei/CRIM_Mass_0014_2.mei',
 'https://crimproject.org/mei/CRIM_Mass_0014_3.mei',
 'https://crimproject.org/mei/CRIM_Mass_0014_4.mei',
 'https://crimproject.org/mei/CRIM_Mass_0014_5.mei',
 'https://crimproject.org/mei/CRIM_Mass_0015_1.mei',
 'https://crimproject.org/mei/CRIM_Mass_0015_2.mei',
 'https://crimproject.org/mei/CRIM_Mass_0015_3.mei',
 'https://crimproject.org/mei/CRIM_Mass_0015_4.mei',
 'https://crimproject.org/mei/CRIM_Mass_0015_5.mei',
 'https://crimproject.org/mei/CRIM_Mass_0016_1.mei',
 'https://crimproject.org/mei/CRIM_Mass_0016_2.mei',
 'https://crimproject.org/mei/CRIM_Mass_0016_3.mei',
 'https://crimproject.org/mei/CRIM_Mass_0016_4.mei',
 'https://crimproject.org/mei/CRIM_Mass_0016_5.mei',
 'https://crimproject.org/mei/CRIM_Mass_0017_1.mei',
 'https://crimproject.org/mei/CRIM_Mass_0017_2.mei',
 'https://crimproject.org/mei/CRIM_Mass_0017_3.mei',
 'https://crimproject.org/mei/CRIM_Mass_0017_4.mei',
 'https://crimproject.org/mei/CRIM_Mass_0017_5.mei',
 'https://crimproject.org/mei/CRIM_Mass_0018_1.mei',
 'https://crimproject.org/mei/CRIM_Mass_0018_2.mei',
 'https://crimproject.org/mei/CRIM_Mass_0018_3.mei',
 'https://crimproject.org/mei/CRIM_Mass_0018_4.mei',
 'https://crimproject.org/mei/CRIM_Mass_0018_5.mei',
 'https://crimproject.org/mei/CRIM_Mass_0019_1.mei',
 'https://crimproject.org/mei/CRIM_Mass_0019_2.mei',
 'https://crimproject.org/mei/CRIM_Mass_0019_3.mei',
 'https://crimproject.org/mei/CRIM_Mass_0019_4.mei',
 'https://crimproject.org/mei/CRIM_Mass_0019_5.mei',
 'https://crimproject.org/mei/CRIM_Mass_0020_1.mei',
 'https://crimproject.org/mei/CRIM_Mass_0020_2.mei',
 'https://crimproject.org/mei/CRIM_Mass_0020_3.mei',
 'https://crimproject.org/mei/CRIM_Mass_0020_4.mei',
 'https://crimproject.org/mei/CRIM_Mass_0020_5.mei',
 'https://crimproject.org/mei/CRIM_Mass_0021_1.mei',
 'https://crimproject.org/mei/CRIM_Mass_0021_2.mei',
 'https://crimproject.org/mei/CRIM_Mass_0021_3.mei',
 'https://crimproject.org/mei/CRIM_Mass_0021_4.mei',
 'https://crimproject.org/mei/CRIM_Mass_0021_5.mei',
 'https://crimproject.org/mei/CRIM_Mass_0022_2.mei',
 'https://crimproject.org/mei/CRIM_Model_0001.mei',
 'https://crimproject.org/mei/CRIM_Model_0008.mei',
 'https://crimproject.org/mei/CRIM_Model_0009.mei',
 'https://crimproject.org/mei/CRIM_Model_0010.mei',
 'https://crimproject.org/mei/CRIM_Model_0011.mei',
 'https://crimproject.org/mei/CRIM_Model_0012.mei',
 'https://crimproject.org/mei/CRIM_Model_0013.mei',
 'https://crimproject.org/mei/CRIM_Model_0014.mei',
 'https://crimproject.org/mei/CRIM_Model_0015.mei',
 'https://crimproject.org/mei/CRIM_Model_0016.mei',
 'https://crimproject.org/mei/CRIM_Model_0017.mei',
 'https://crimproject.org/mei/CRIM_Model_0019.mei',
 'https://crimproject.org/mei/CRIM_Model_0020.mei',
 'https://crimproject.org/mei/CRIM_Model_0021.mei',
 'https://crimproject.org/mei/CRIM_Model_0023.mei',
 'https://crimproject.org/mei/CRIM_Model_0025.mei',
 'https://crimproject.org/mei/CRIM_Model_0026.mei',
]

#WorkList = ['https://crimproject.org/mei/CRIM_Model_0001.mei']
st.header("CRIM Project:  CRIM Intervals")

st.subheader("Python Scripts for Analysis of Similar Soggetti in Citations: The Renaissance Imitation Mass")
st.write("Visit the [CRIM Project](https://crimproject.org) and its [Members Pages] (https://sites.google.com/haverford.edu/crim-project/home)")
st.write("Also see the [Relationship Metadata Viewer] (https://crim-relationship-data-viewer.herokuapp.com/) and [Observation Metadata Viewer] (https://crim-observation-data-viewer.herokuapp.com/)")


st.header("Select One or More Pieces to Analyze")
st.subheader("Step 1: Choose with Menu, or Type ID, such as 'Model_0008'")
selected_works = st.multiselect('', CRIM_Corpus)
print_list = pd.DataFrame(selected_works)
st.write(print_list)
#st.write(selected_works)

# correct URL for MEI 4.0

WorkList_mei = [el.replace("/mei/", "/mei/MEI_4.0/") for el in selected_works]

# Now pass the list of MEI files to Crim intervals

corpus = CorpusBase(WorkList_mei)

# Correct the MEI metadata

import xml.etree.ElementTree as ET
import requests

MEINSURI = 'http://www.music-encoding.org/ns/mei'
MEINS = '{%s}' % MEINSURI

for i, path in enumerate(WorkList_mei):
    
    try:
        if path[0] == '/':
            mei_doc = ET.parse(path)
        else:
            mei_doc = ET.fromstring(requests.get(path).text)

      # Find the title from the MEI file and update the Music21 Score metadata
        title = mei_doc.find('mei:meiHead//mei:titleStmt/mei:title', namespaces={"mei": MEINSURI}).text
        print(path, title)
        corpus.scores[i].metadata.title = title
    except:
        continue

# Header


# Select Actual or Incremental Durations
st.sidebar.subheader("Step 2:  Select Rhythmic Preference")
duration_choice = st.sidebar.radio('Select Actual or Incremental Durations', ["Actual","Incremental@1","Incremental@2", "Incremental@4"])

if duration_choice == 'Actual':
    vectors = IntervalBase(corpus.note_list)
elif duration_choice == 'Incremental@1':
    vectors = IntervalBase(corpus.note_list_incremental_offset(1))
elif duration_choice == 'Incremental@2':
    vectors = IntervalBase(corpus.note_list_incremental_offset(2))
elif duration_choice == 'Incremental@4':
    vectors = IntervalBase(corpus.note_list_incremental_offset(4))
else:
    st.write("Please select duration preference")
# Select Generic or Semitone
st.sidebar.subheader("Step 3:  Select Interval Prefence")
scale_choice = st.sidebar.radio('Select Diatonic or Chromatic', ["Diatonic","Chromatic"])

if scale_choice == 'Diatonic':
    scale = vectors.generic_intervals
elif scale_choice == 'Chromatic':
    scale = vectors.semitone_intervals
else:
    st.write("Please select duration preference")

# Select Vector Length and Minimum Number of Matches
st.sidebar.subheader("Step 4:  Select Vectors, Matches, and Thresholds")

vector_length = st.sidebar.number_input("Enter a Number for the Length of Vector", min_value=1, max_value=20)

minimum_match = st.sidebar.number_input("Enter a Minimum Number of Matches", min_value=1, max_value=20)

close_distance = st.sidebar.number_input("If Close Search, then Enter Threshold", min_value=1, max_value=20)

patterns = into_patterns([scale], vector_length)

# Creates empty variable needed for CSV download below (but which uses content defined)

#results = pd.DataFrame()

# Select Exact or Close

st.sidebar.subheader("Step 5:  Exact or Close Matches AFTER making selections above!") 
exact_close_choice = st.sidebar.radio('Select Exact or Close Match (if Close, then Select Treshold Above)', ["Exact", "Close", "cancel"])

if exact_close_choice == 'Exact':
    find_matches = find_exact_matches(patterns, minimum_match)
elif exact_close_choice == 'Close':
    #close_distance = st.number_input("Enter a Threshold for Similarity", min_value=1, max_value=20)
    find_matches = find_close_matches(patterns, minimum_match, close_distance)
else:
    st.write("Review Choices Before Running Search!")

#minimum_match = st.slider('Minimum Number of Matches for Each Vector', min_value=2, max_value=20)
st.subheader("Step 6: Run Melodic Similarity Search")
if st.button('Run Melodic Search'):
    #patterns = into_patterns([scale], vector_length)
    #exact_matches = find_exact_matches(patterns, minimum_match)
    #find_matches
    output = export_pandas(find_matches)
    #pd.DataFrame(output).head()
    results = pd.DataFrame(output)
    st.write('Output of Melodic Pattern Search')
    st.write(results)

    # Option to download CSV of the first-stage results
    st.subheader("Optional:  Download CSV from Step 6")
    s1 = st.text_input('Provide filename for melodic pattern match download (must include ".csv")')
    tmp_download_link = download_link(results, s1, 'Click here to download your data!')
    st.markdown(tmp_download_link, unsafe_allow_html=True)

    # Stage 2 Rhythmic Simliarities Search
    
st.subheader("Step 7: Filter Previous for Similar Durations")

max_sum_diffs = st.number_input("Enter Maximum Durational Differences", min_value=1, max_value=20)

if st.button('Run Duration Match Filter'):

# clean-up results of melodic match:  chance patterns to tuples 
    output = export_pandas(find_matches)
    #pd.DataFrame(output).head()
    results = pd.DataFrame(output)
    st.write('Output of Melodic Pattern Search for Step 7')
    #st.write(results)

    results["pattern_generating_match"] = results["pattern_generating_match"].apply(tuple)

    # clean-up column titles

    # results.rename(columns=
    #                {'Pattern Generating Match': 'Pattern_Generating_Match', 
    #                 'Pattern matched':'Pattern_Matched',
    #                 'Piece Title': 'Piece_Title',
    #                 'First Note Measure Number': 'Start_Measure',
    #                 'Last Note Measure Number': 'Stop_Measure',
    #                 'Note Durations': 'Note_Durations'
    #                },
    #                 inplace=True)

    # evaluation Note_Durations as literals--only needed if we're importing CSV

    #results['note_durations'] = results['note_durations'].apply(ast.literal_eval)
    
    durations = results['note_durations']
    
    # calculates 'duration ratios' for each soggetto, then adds this to the DF

    results["duration_ratios"] = results.note_durations.apply(get_ratios)
    st.write("Results with Duration Ratios Added")
    st.write(results)

    # now we calculate the _distances_ between pairs of ratios

    ratio_distances = get_ratio_distances(results, "pattern_generating_match", ["piece_title", "part", "start_measure", "end_measure"])

    ratios_filtered = ratio_distances[ratio_distances.sum_diffs <= max_sum_diffs]
    st.write("Results Filtered Distances of Durational Ratios")
    st.write(ratios_filtered)

    st.subheader("Optional:  Download CSV from Step 7")
    s2 = st.text_input('Provide filename for durational match download (must include ".csv")')
    tmp_download_link = download_link(ratios_filtered, s2, 'Click here to download your data!')
    st.markdown(tmp_download_link, unsafe_allow_html=True)

    
