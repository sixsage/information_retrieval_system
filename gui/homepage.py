import streamlit as st

def getLinks(cap):
        links = ["https://www.ics.uci.edu"]*300
        return links[:cap]

def run():
    st.set_page_config(page_title="search")

    st.title("Home page")

    if "user_query" not in st.session_state:
        st.session_state["user_query"] = ""

    user_query = st.text_input("search", st.session_state["user_query"])
    submit = st.button("submit")
    if submit and user_query != "":
        print(user_query)
        st.session_state["user_query"] = user_query
        links = getLinks(300)
        time = len(links)
        st.write("results for ", user_query, ":", "computed in: ", time, "ms")
        for result in links:
            st.write(f'[{result}](%s)' % result)




if __name__ == '__main__':
    run(220)