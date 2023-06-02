import streamlit as st

def getLinks(cap):
        links = ["https://www.ics.uci.edu", "https://www.ics.uci.edu/ugrad/", "https://career.uci.edu"]
        return links[:cap]


if __name__ == '__main__':
    st.set_page_config(page_title="search")

    st.title("Home page")

    if "user_query" not in st.session_state:
        st.session_state["user_query"] = ""

    user_query = st.text_input("search", st.session_state["user_query"])
    submit = st.button("submit")
    if submit and user_query != "":
        print(user_query)
        st.session_state["user_query"] = user_query
        links = getLinks(3)
        st.write("results for ", user_query, ":")
        for result in links:
            st.write(f'[{result}](%s)' % result)

