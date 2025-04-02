import sys, os

# Get the parent directory
parent_dir = os.path.dirname(os.path.realpath(__file__))

gparent_dir = os.path.dirname( parent_dir )
sys.path.append(gparent_dir)
sys.path.append(parent_dir)

# app.py
# Current . 
# parent: /workspaces/refugee-watch/rcamps 
# Granny: /workspaces/refugee-watch

print( 'apps.py\n Current',os.curdir, 'parent:', parent_dir, 'Granny:', gparent_dir)

import utils
from importlib import reload
reload( utils )

def main():
  # ================== header ==================
  tit='Refugee Watch @streamlit'
  utils.st.set_page_config(
    page_title=tit, 
    page_icon="^-^",     
    initial_sidebar_state='expanded'
  )
  utils.st.html( os.getcwd() ) 
  
  intro_markdown = utils.read_markdown_file( utils.Path( gparent_dir, "README.md") )
  utils.st.markdown(intro_markdown, unsafe_allow_html=True)


if __name__ == '__main__':
  main()



 
