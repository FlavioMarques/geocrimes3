import streamlit as st

HIDE_ST_STYLE = """
                <style>
                div[data-testid="stToolbar"] {
                visibility: hidden;
                height: 0%;
                position: fixed;
                }
                div[data-testid="stDecoration"] {
                visibility: hidden;
                height: 0%;
                position: fixed;
                }
                div[data-testid="stStatusWidget"] {
                visibility: hidden;
                height: 0%;
                position: fixed;
                }
                #MainMenu {
                visibility: hidden;
                height: 0%;
                }
                header {
                visibility: hidden;
                height: 0%;
                }
                footer {
                visibility: hidden;
                height: 0%;
                }
                .block-container {
                padding-top: 0rem;
                }
                </style>
                """
def init_style():
    st.set_page_config(
        page_title="stlite PWA",
        page_icon="🚀",
        layout="wide",
        initial_sidebar_state="auto",
        menu_items=None,
    )
    st.markdown(HIDE_ST_STYLE,unsafe_allow_html=True)


def main():
    st.title("stlite PWA")
    name=st.text_input("Name")
    if name:
        st.write(f"Hello!{name}.")

if __name__ == "__main__":
    init_style()
    main()
