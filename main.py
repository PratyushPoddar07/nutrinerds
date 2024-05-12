import streamlit as st
from streamlit_option_menu import option_menu

import about,account,home,history

st.set_page_config(
    page_title="DociFy",

)

class MultiApp:
    def __init__(self):
        self.apps =[]
    def add_app(self,title,function):
        self.apps.append({
            "title":title,
            "function": function
        })

    def run():
        with st.sidebar:
             app =option_menu(
                 menu_title='DociFy',
                 options= ['Home','Account','History','About'],
                 icons =['house-fill','person-circle','clock-history','chat-fill'],
                 menu_icon='chat-text-fill',
                 default_index=1,
                 styles={
                     "container":{"padding":"1!important","background-color":'#C3F1DB'},
                     "icons":{"color":"white","font-size":"23px"},
                     "nav-link": {"color":"black","font-size":"20px","text-align":"left"},
                     "nav-link-selected":{"background-color":"#02ab21"},
                 }
             )

        if app == 'Home':
                home.app()
        if app =='Account':
                account.app()
        if app =='History':
                history.app()
        if app == 'About':
                about.app()

    run()



