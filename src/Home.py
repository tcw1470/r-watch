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
  print( 'Directory of Home.py',  os.getcwd() ) 
  
  intro_markdown = utils.read_markdown_file( utils.Path( gparent_dir, "README.md") )
  utils.st.markdown(intro_markdown, unsafe_allow_html=True)

  if 0:    

    from pip.operations import freeze    
    modules = list(
        map(lambda x: x.split('=='), freeze.freeze(local_only=True))
    )  
  elif 0:    
    import pip
    modules = []
    for i in pip.utils.get_installed_distributions():
        modules.append((i.key, i.version))
  else:
    try:
      from pip._internal.operations import list
    except Exception as e:
      print( 'cannot load list', e ) 
      
    try: 
      from pip._internal.operations import freeze      
    except ImportError: # pip < 10.0
      from pip.operations import freeze

    
    pkgs = freeze.freeze()
    
    s = '''
    <details> 
      <summary>Python packages used by this app </summary>
    '''
    s = ' '.join(pkgs) # + '</details>'
    utils.st.markdown( s )
     

if __name__ == '__main__':
  main()



 
