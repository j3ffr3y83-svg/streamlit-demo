import streamlit as st
import requests
import openai
from openai import OpenAI

# --- Load API keys from Streamlit secrets ---
google_api_key = st.secrets["GOOGLE_API_KEY"]
google_cse_id = st.secrets["GOOGLE_CSE_ID"]
openai.api_key = st.secrets["OPENAI_API_KEY"]

# --- App Title ---
st.set_page_config(page_title="AskGov SG - CPF Q&A", layout="wide")
st.title("🇸🇬 AskGov SG - CPF Policy Q&A")

# --- Disclaimer ---
with st.expander("📢 Important Disclaimer"):
    st.markdown("""# 1. Stage the file(s) you changed
git add requirements.txt

# 2. Commit the changes with a message
git commit -m "Cleaned up requirements.txt for deployment"

# 3. Push to the remote repository (default branch, e.g. main or master)
git push

    **IMPORTANT NOTICE:** This web application is a prototype developed for educational purposes only. The information provided here is **NOT** intended for real-world usage and should **not** be relied upon for making any decisions, especially those related to **financial, legal, or healthcare matters**.

    Furthermore, please be aware that the LLM may generate **inaccurate or incorrect information**. You assume full responsibility for how you use any generated output.

    Always consult with **qualified professionals** for accurate and personalized advice.
    """)

# --- Sidebar ---
st.sidebar.header("User Info")
location = st.sidebar.selectbox("Where are you from?", ["Singapore", "Others"])
need = st.sidebar.selectbox("What do you need?", ["CPF"])

# --- Google CSE Function ---
def fetch_gov_info_google(query):
    url = f"https://www.googleapis.com/customsearch/v1?q={query}&cx={google_cse_id}&key={google_api_key}"
    res = requests.get(url)
    res.raise_for_status()
    data = res.json()

    sources = []
    if "items" in data:
        for item in data["items"][:3]:
            sources.append({
                "title": item["title"],
                "snippet": item["snippet"],
                "url": item["link"]
            })
    return sources

# --- GPT Function using OpenAI v1 SDK ---
def ask_llm(query, sources, need, location):
    client = OpenAI(api_key=openai.api_key)

    # Prepare sources as Markdown links
    context_text = "\n".join([f"- [{s['title']}]({s['url']})" for s in sources])

    prompt = (
        f"You are a helpful assistant trained in Singapore government processes "
        f"(CPF, ICA, HDB). Always answer clearly and cite official sources using clickable URLs in Markdown.\n\n"
        f"User is from: {location}\n"
        f"User need: {need}\n"
        f"Question: {query}\n\n"
        f"Official sources:\n{context_text}\n\n"
        "Write a concise, easy-to-read answer and include the URLs inline where relevant."
    )

    response = client.chat.completions.create(
        model="gpt-4o",  # You can also use "gpt-3.5-turbo"
        messages=[{"role": "user", "content": prompt}],
        max_tokens=500,
        temperature=0
    )
    return response.choices[0].message.content

# --- User Input ---
user_query = st.text_input("Ask a question about any Singapore Government process:")

if st.button("Get Answer"):
    if user_query:
        with st.spinner("Searching official government sources..."):
            sources = fetch_gov_info_google(user_query)
            if not sources:
                st.warning("No official results found. Please try a different query.")
            else:
                answer = ask_llm(user_query, sources, need, location)
                st.success("Here’s a simplified explanation:")
                st.markdown(answer, unsafe_allow_html=True)  # render clickable links
    else:
        st.warning("Please type your question first.")

# --- Quick Links ---
st.markdown("### 📌 Quick Links")
st.markdown("- [ICA Services](https://www.ica.gov.sg)")
st.markdown("- [CPF Board](https://www.cpf.gov.sg)")
st.markdown("- [HDB Info](https://www.hdb.gov.sg)")
