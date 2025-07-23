import streamlit as st
from PIL import Image
import pytesseract
from textblob import TextBlob
import pandas as pd
import io
from datetime import date

# Optional: Path to tesseract
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# Define list of known newspaper names (add more as needed)
NEWSPAPER_LIST = [
    "सकाळ", "लोकसत्ता", "लोकमत", "महाराष्ट्र टाईम्स", "तरुण भारत",
    "देशोन्नती", "नवशक्ती", "समना", "नवभारत", "नवाकाळ", "जनप्रवाह",
    "पुण्यनगरी", "शिवनेरी", "प्रभात", "अग्रलेख", "गावकरी"
]

def detect_newspaper(text, newspaper_list):
    for name in newspaper_list:
        if name in text:
            return name
    return ""

st.set_page_config(page_title="News Sentiment Analyzer", layout="wide")
st.title("📰 News Sentiment & Subject Analyzer : Drop Any News Cutting Below")

uploaded_files = st.file_uploader("Upload Marathi News Cutting Images", type=['png', 'jpg', 'jpeg'], accept_multiple_files=True)

if uploaded_files:
    results = []
    st.write("### 🧾 Text + Sentiment Extraction")

    for idx, file in enumerate(uploaded_files, start=1):
        image = Image.open(file)
        st.image(image, caption=f"News #{idx}", use_container_width=True)

        # OCR with Marathi language
        text = pytesseract.image_to_string(image, lang='mar')

        # Detect newspaper from OCR text
        detected_paper = detect_newspaper(text, NEWSPAPER_LIST)

        # Sentiment scoring
        blob = TextBlob(text)
        polarity = blob.sentiment.polarity
        score = round(((polarity + 1) / 2) * 4 + 1, 2)

        # Form inputs
        with st.expander(f"Metadata for News #{idx}"):
            subject_line = st.text_area("Subject (in Marathi)", value=text.strip()[:80], key=f"subject_{idx}")
            pr_date = st.date_input("Date of Publishing", value=date.today(), key=f"date_{idx}")
            newspaper = st.text_input("Newspaper Name", value=detected_paper, key=f"paper_{idx}")
            old_dept = st.text_input("Old Department", key=f"old_dept_{idx}")
            department = st.text_input("Department", key=f"dept_{idx}")
            news_link = st.text_input("News Link", key=f"link_{idx}")

        # Sentiment logic like your example
        i_satisfaction = round(score, 1)
        i_happiness = round(score, 1)
        i_pride = round(min(score + 1, 5), 1)
        i_overall_pos = round((i_satisfaction + i_happiness + i_pride) / 3, 1)

        i_dis = round(5 - score, 1)
        i_angry = round(6 - score, 1)
        i_sad = round(max(1, 5 - score), 1)
        i_overall_neg = round((i_dis + i_angry + i_sad) / 3, 1)


        results.append({
            "News No-": idx,
            "Subject": subject_line,
            "Date of Publishing": pr_date.strftime("%d-%m-%Y"),
            "Newspaper Name": newspaper,
            "Old Department": old_dept,
            "Department": department,
            "News Link": news_link,
            "Satisafaction": i_satisfaction,
            "Happiness": i_happiness,
            "Pride": i_pride,
            "Overall Positive": i_overall_pos,
            "Disatisfaction": i_dis,
            "Angry": i_angry,
            "Sad": i_sad,
            "Overall Negative": i_overall_neg
        })

    df = pd.DataFrame(results)

    st.write("### 📄 Output Table")
    st.dataframe(df)

    buffer = io.BytesIO()
    df.to_excel(buffer, index=False, engine='openpyxl')
    buffer.seek(0)

    st.download_button("📥 Download Excel", data=buffer, file_name="news_sentiment_marathi.xlsx",
                       mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
