# Import libraries and packages
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
sns.set_theme(style='white')
import plotly.express as px

import re
from collections import Counter
import emoji
from io import BytesIO
import xlsxwriter
import collections
import datetime
from os import path
from PIL import Image
from wordcloud import WordCloud, STOPWORDS, ImageColorGenerator

import nltk 
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.probability import FreqDist

import warnings
warnings.simplefilter(action='ignore', category=UserWarning)


# Create a Streamlit app
st.set_page_config(
    page_title="WhatsApp Chats Analyzer",
    page_icon="icons8-whatsapp-48.png",
    layout="wide",
)

# Center-align subheading and image using HTML <div> tags
st.markdown(
    """
    <div style="display: flex; flex-direction: column; align-items: center; text-align: center;">
        <h2>WhatsApp Chats Analyzer</h2>

    </div>
    """,
    unsafe_allow_html=True
)
st.image("rachit-tank-lZBs-lD9LPQ-unsplash.jpg")

# # Add the subheading and image in a container
# with st.container():
#     st.subheader("WhatsApp Chats Analyzer")
#     st.image("wa1.jpg")


# Add an introductory paragraph
st.markdown("""
Hey there! Ever wondered what's really going on in your WhatsApp chats? Introducing the WhatsApp Chats Analyzer, brought to you by Raqib (aka raqibcodes)! This nifty tool takes your WhatsApp chat and works its magic, revealing all sorts of cool stuff. Check out message stats, member interactions, and even the vibe with sentiment analysis. It's like a chat detective! Just upload your chatand have fun with it!
""")

# Display a GIF video with a caption and custom dimensions
st.subheader("Demo Video")
video_url = "demo.mp4" 
video_width = 600  # Adjust the width as needed
st.video(video_url)

# Function to remove emojis from a string
def remove_emojis(text):
    emoji_pattern = re.compile(pattern="["
                                       u"\U0001F600-\U0001F64F"  # emoticons
                                       u"\U0001F300-\U0001F5FF"  # symbols & pictographs
                                       u"\U0001F680-\U0001F6FF"  # transport & map symbols
                                       u"\U0001F700-\U0001F77F"  # alchemical symbols
                                       u"\U0001F780-\U0001F7FF"  # Geometric Shapes Extended
                                       u"\U0001F800-\U0001F8FF"  # Supplemental Arrows-C
                                       u"\U0001F900-\U0001F9FF"  # Supplemental Symbols and Pictographs
                                       u"\U0001FA00-\U0001FA6F"  # Chess Symbols
                                       u"\U0001FA70-\U0001FAFF"  # Symbols and Pictographs Extended-A
                                       u"\U0001F004-\U0001F0CF"  # Additional emoticons
                                       u"\U0001F170-\U0001F251"  # Enclosed characters
                                       "]+", flags=re.UNICODE)
    return emoji_pattern.sub(r'', text)

def extract_member_name(message):
    match = re.match(r'^([^:]+)(:.+)?$', message)
    if match:
        return match.group(1).strip()
    return ''


# Create a file uploader button for TXT files
uploaded_file = st.file_uploader("Upload a Text(.txt) File", type=["txt"])

# Check if a file was uploaded
if uploaded_file:
    st.success("File successfully uploaded.")
    
    # Process the uploaded file and convert to a Pandas DataFrame
    with st.spinner("Loading📍..."):
        chat_data = uploaded_file.read().decode('utf-8').splitlines()
        
        # Initialize data lists (your existing code)
        dates = []
        times = []
        members = []
        messages = []
        message_types = []
        message_lengths = []
        reaction_counts = []
        word_counts = []
        mentions = []
        emojis = []
        
        # Define regular expressions to extract data
        message_regex = re.compile(r'^(\d{2}\/\d{2}\/\d{4}, \d{2}:\d{2}) - ([^:]+): (.+)$')
        system_message_regex = re.compile(r'^(\d{2}\/\d{2}\/\d{4}, \d{2}:\d{2}) - (.+)$')
        media_message_regex = re.compile(r'^(\d{2}\/\d{2}\/\d{4}, \d{2}:\d{2}) - ([^:]+) attached (\S+) \(.*\)$')
        # Loop through chat data and extract required information (your existing code)
        for line in chat_data:
            match = message_regex.match(line)
            if match:
                dates.append(match.group(1)[:10])
                times.append(match.group(1)[11:])
                member = extract_member_name(match.group(2))
                members.append(member)
                message_text = match.group(3)
                message_text = remove_emojis(message_text)  # Remove emojis from the message text
                messages.append(message_text)
                message_types.append('text')
                message_lengths.append(len(message_text))
                reaction_counts.append(0)
                word_counts.append(len(message_text.split()))
                mentions.append(re.findall(r'@(\w+)', message_text))
                emojis.append([])  # Emojis have already been removed from the message_text
            else:
                # Check if line contains a system message
                match = system_message_regex.match(line)
                if match:
                    dates.append(match.group(1)[:10])
                    times.append(match.group(1)[11:])
                    members.append('System')
                    messages.append(match.group(2))
                    message_types.append('system')
                    message_lengths.append(len(match.group(2)))
                    reaction_counts.append(0)
                    word_counts.append(len(match.group(2).split()))
                    mentions.append([])
                    emojis.append([])
                else:
                    # Check if line contains a media message
                    match = media_message_regex.match(line)
                    if match:
                        dates.append(match.group(1)[:10])
                        times.append(match.group(1)[11:])
                        member = emoji.demojize(match.group(2)).strip()
                        members.append(member)
                        messages.append(match.group(3))
                        message_types.append('media')
                        message_lengths.append(0)
                        reaction_counts.append(0)
                        word_counts.append(0)
                        mentions.append([])
                        emojis.append([])

        # Create pandas dataframe from extracted data (your existing code)
        df = pd.DataFrame({
            'date': dates,
            'time': times,
            'member': members,
            'message': messages,
            'message_type': message_types,
            'message_length': message_lengths,
            'reaction_count': reaction_counts,
            'word_count': word_counts,
            'mentions': mentions,
            'emojis': emojis
        })
        
        st.markdown(
    f"""
    <style>
        div.stButton > button:first-child {{
            background-color: #636EFA;
            color: white;
            font-weight: bold;
            font-size: 18px;
        }}
    </style>
    """,
    unsafe_allow_html=True,
)

    # Create a checkbox to toggle the visibility of the DataFrame
    show_data = st.checkbox("Display Data")

    # Display the DataFrame if the checkbox is checked
    if show_data:
        st.dataframe(df)
        
        # Create a multiselect widget to select columns for unique values
        selected_columns = st.multiselect("Display Unique Values of Columns", df.columns.tolist())

        # Create an expander for displaying unique values
        with st.expander("Unique Values", expanded=False):
            for column in selected_columns:
                st.subheader(f"Unique Values in {column}")
                unique_values = pd.unique(df[column])
                # Use custom CSS to enable scrolling
                st.markdown(f'<div style="max-height: 300px; overflow-y: scroll;">{pd.DataFrame(unique_values, columns=[column]).to_html(index=False)}</div>', unsafe_allow_html=True)
        
    # export the dataset to Excel format
    if st.button("Export to Excel File"):
        # Create a BytesIO buffer for writing the Excel file
        excel_buffer = BytesIO()
        with pd.ExcelWriter(excel_buffer, engine="xlsxwriter") as writer:
            df.to_excel(writer, sheet_name="WhatsApp_Chat", index=False)

        # Set the filename and download button label
        excel_filename = "whatsapp_chats.xlsx"
        st.write(f"Exporting to {excel_filename}...")
        
        # Prepare the Excel data for download
        excel_data = excel_buffer.getvalue()
        st.download_button(label="Click here to download the Excel file", data=excel_data, file_name=excel_filename, key="excel_download")

# Quick Stats
st.title("Stats")

st.subheader("Overall Stats")

def split_count(text):

    emoji_list = []
    data = re.findall(r'[^\s\u1f300-\u1f5ff]', text)
    for word in data:
        if any(char in emoji.distinct_emoji_list(text) for char in word):
            emoji_list.append(word)

    return emoji_list

# Calculate total messages
total_messages = df.shape[0]

# Calculate media messages
media_messages = df[df['message'] == '<Media omitted>'].shape[0]

# Calculate emojis
df["emoji"] = df["message"].apply(split_count)
emojis = sum(df['emoji'].str.len())

# Calculate URL links
URLPATTERN = r'(https?://\S+)'
df['urlcount'] = df.message.apply(lambda x: re.findall(URLPATTERN, x)).str.len()
links = np.sum(df.urlcount)

# Display quick stats
st.write(f"Total Messages: {total_messages}")
st.write(f"Media Messages: {media_messages}")
st.write(f"Total Emojis: {emojis}")
st.write(f"Total Links: {links}")

st.subheader("Member Stats")

# Get unique member names
unique_members = df['member'].unique()

# Create a dropdown to select a member
selected_member = st.selectbox("Select a Group Participant", unique_members)

# Display individual member stats when a member is selected
if selected_member:
    st.subheader(f"Stats for {selected_member}")
    member_df = df[df['member'] == selected_member]
    
    # Calculate Messages Sent
    messages_sent = member_df.shape[0]

    # Calculate Words per message
    words_per_message = member_df['word_count'].mean()

    # Calculate Media Messages Sent
    media_messages_sent = member_df[member_df['message'] == '<Media omitted>'].shape[0]

    # Calculate Emojis Sent
    member_df["emoji"] = member_df["message"].apply(split_count)
    emojis_sent = sum(member_df['emoji'].str.len())

    # Calculate Links Sent
    URLPATTERN = r'(https?://\S+)'
    member_df['urlcount'] = member_df.message.apply(lambda x: re.findall(URLPATTERN, x)).str.len()
    links_sent = np.sum(member_df.urlcount)

    # Display individual member stats
    st.write(f"Messages Sent: {messages_sent}")
    st.write(f"Words per Message: {words_per_message}")
    st.write(f"Media Messages Sent: {media_messages_sent}")
    st.write(f"Emojis Sent: {emojis_sent}")
    st.write(f"Links Sent: {links_sent}")

st.title('Visualizations')

# the top 20 participants
with st.expander('Most Active Group Participants'):
    # Calculate activity count for each member
    activity_count = df['member'].value_counts().reset_index()
    activity_count.columns = ['Member', 'Activity Count']

    # display the top 20 participants
    st.plotly_chart(
        px.bar(activity_count.head(20), x='Member', y='Activity Count', title='Most Active Group Members')
        .update_traces(marker_color='rgb(63, 72, 204)')
        .update_layout(xaxis_title='Member', yaxis_title='Activity Count', xaxis_tickangle=-45, font=dict(size=14)),
        use_container_width=True
    )

# Emoji dist
# with st.expander('Emoji Distribution'):
#     # Extract emojis from messages
#     emoji_pattern = r'[\U0001F600-\U0001F650]'
#     df['emojis'] = df['message'].str.findall(emoji_pattern)

#     # Flatten the list of emojis
#     all_emojis = [emoji for emojis in df['emojis'] for emoji in emojis]

#     # Count emoji frequencies
#     emoji_counts = pd.Series(all_emojis).value_counts().reset_index()
#     emoji_counts.columns = ['Emoji', 'Count']

#     # Define custom colors for the pie chart
#     colors = ['#ffd700', '#ff69b4', '#1e90ff', '#ff8c00', '#00ced1']

#     # Create a pie chart of the emoji frequencies with custom colors
#     fig = px.pie(
#         emoji_counts,
#         names='Emoji',
#         values='Count',
#         title='Overall Emoji Distribution',
#         color_discrete_sequence=colors
#     )
#     fig.update_traces(textposition='inside', textinfo='percent+label')
#     fig.update_layout(width=800, height=500, showlegend=True)

#     # Show the pie chart in Streamlit
#     st.plotly_chart(fig, use_container_width=True)

# Most commonly Used Words

# Filter out messages that contain media files
non_media = df[~df['message'].str.contains('<Media omitted>')]

with st.expander('Most Used Words (Excluding Media)'):
    all_messages = ' '.join(non_media['message'].astype(str).tolist())
    all_words = all_messages.split()
    word_freq = collections.Counter(all_words)
    top_words = word_freq.most_common(20)
    words = [word[0] for word in top_words]
    counts = [count[1] for count in top_words]
    
    st.bar_chart(pd.DataFrame({'Word': words, 'Count': counts}).set_index('Word'))
