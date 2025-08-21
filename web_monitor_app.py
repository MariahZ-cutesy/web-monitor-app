import streamlit as st
import requests
import difflib
import hashlib
from bs4 import BeautifulSoup
# Simulated AI summarization function
def summarize_changes(old_text, new_text):
    diff = difflib.unified_diff(old_text.splitlines(), new_text.splitlines(), lineterm='')
    changes = '\n'.join(diff)
    return f"Summary of changes:\n{changes}"
# Keyword priority scoring
def score_keywords(text, keywords_with_weights):
    score = 0
    for keyword, weight in keywords_with_weights.items():
        if keyword.lower() in text.lower():
            score += weight
    return score
# Monitor a webpage for changes
def monitor_page(url, keywords_with_weights, previous_hash=None, previous_text=""):
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        text = soup.get_text()
        current_hash = hashlib.md5(text.encode('utf-8')).hexdigest()
        if previous_hash and current_hash != previous_hash:
            summary = summarize_changes(previous_text, text)
            score = score_keywords(text, keywords_with_weights)
            return current_hash, text, summary, score
        elif not previous_hash:
            return current_hash, text, "Initial content fetched. No previous version to compare.", 0
        else:
            return current_hash, text, "No change detected.", 0
    except Exception as e:
        return previous_hash, previous_text, f"Error fetching the page: {e}", 0
# Streamlit UI
st.title("Web Page Change Monitor")
url = st.text_input("Enter the website URL to monitor:")
keywords_input = st.text_area("Enter keywords and weights (e.g., press release:5, Gabon:3):")
if "previous_hash" not in st.session_state:
    st.session_state.previous_hash = None
if "previous_text" not in st.session_state:
    st.session_state.previous_text = ""
if st.button("Monitor Page"):
    if url and keywords_input:
        # Parse keywords and weights
        keywords_with_weights = {}
        for item in keywords_input.split(","):
            if ":" in item:
                keyword, weight = item.split(":")
                keywords_with_weights[keyword.strip()] = int(weight.strip())
        new_hash, new_text, summary, score = monitor_page(
            url,
            keywords_with_weights,
            st.session_state.previous_hash,
            st.session_state.previous_text
        )
        st.session_state.previous_hash = new_hash
        st.session_state.previous_text = new_text
        st.subheader("Change Summary")
        st.text(summary)
        st.subheader("Priority Score")
        st.write(score)
    else:
        st.warning("Please enter both the URL and keywords.")

