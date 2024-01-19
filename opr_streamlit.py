# Import convention
import streamlit as st
# Use the full page instead of a narrow central column

import pandas as pd

from opr_calculator import *

if 'weapon_names' not in st.session_state:
    st.session_state['weapon_names'] = []
if 'weapons' not in st.session_state:
    st.session_state['weapons'] = {}

specials_name2class = {"Blast[3]": Blast(name="Blast[3]", modifier=3),
                       "Blast[6]": Blast(name="Blast[6]", modifier=3),
                       'Deadly[3]': Deadly(name='Deadly[3]', modifier=3),
                       'Deadly[6]': Deadly(name='Deadly[6]', modifier=6),
                       'Sniper': Sniper(name='Sniper', modifier=2),
                       'Reliable': Reliable(name='Reliable', modifier=2),
                       'Regeneration': Regeneration(name='Regeneration', modifier=5),
                       'Rending': Rending(name='Rending')
                       }


def add_weapon():
    sp = Special([specials_name2class[special] for special in specials_wp])
    weapon = Weapon(f"Weapon {len(st.session_state['weapons'])}", attacks=attacks, ap=ap, special=sp, points=wp_points)
    st.session_state['weapon_names'].append(str(weapon))
    st.session_state['weapons'][str(weapon)] = weapon


import base64


def get_base64_of_bin_file(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()


def set_bg_hack_url(png_file):
    '''
    A function to unpack an image from url and set as bg.
    Returns
    -------
    The background.
    '''
    bin_str = get_base64_of_bin_file(png_file)

    st.markdown(
        f"""
         <style>
         .stApp {{
             background:  url("data:image/png;base64,%s");
             background-size: cover
         }}
         </style>
         """  % bin_str,
        unsafe_allow_html=True
    )

st.set_page_config(layout="wide")

set_bg_hack_url('./opr_streamlit.png')

st.title("OnePageRules Calculat0r :collision:")
#st.markdown(set_png_as_page_bg('./opr_streamlit.png'), unsafe_allow_html=True)

# Space out the maps so the first one is 2x the size of the other three
unit1, unit2 = st.columns((1, 1))

with unit1:
    with st.container():
        st.header('Attacker')
        quality = st.slider("Quality", min_value=1, max_value=6, value=3, step=1, key="quality_unit1")
        defense = st.slider("Defense", min_value=1, max_value=6, value=3, step=1, key="defense_unit1")
        n_models = st.number_input(label="Models", value=1, step=1, format="%d", key='n_models_unit1')
        toughness = st.number_input(label="Toughness", value=1, step=1, format="%d",  key='toughness_unit1')
        specials = st.multiselect("Special", ["Regeneration"],
                                  placeholder="Choose specialities",
                                  disabled=False, label_visibility="visible", key='specials_unit1')
        points = st.number_input(label="Points", value=10, step=10, format="%d",  key='points_unit1')
        weapons = st.multiselect("Weapons", st.session_state['weapon_names'], placeholder="Choose weapons",
                                  disabled=False, label_visibility="visible")
    with st.container():
        st.header('Weapon')
        attacks = st.number_input("Attacks [of complete unit]", min_value=1, value=1, step=1, format="%d", key='attacks_wp')
        ap = st.number_input("Ability power", min_value=0, value=0, step=1, format="%d", key='ap_wp')
        specials_wp = st.multiselect("Special", ["Blast[3]", "Blast[6]", "Deadly[3]", "Deadly[6]",
                                                 "Rending", "Reliable", "Sniper"], placeholder="Choose specialities",
                                      disabled=False, label_visibility="visible")
        wp_points = st.number_input(label="Points", value=0, step=5, format="%d", key='points_wp')
        st.button("Add weapon", on_click=add_weapon)


with unit2:
    with st.container():
        st.header('Defender')
        quality_def = st.slider("Quality", min_value=1, max_value=6, value=3, step=1, key="quality_unit2")
        defense_def = st.slider("Defense", min_value=1, max_value=6, value=3, step=1, key="defense_unit2")
        n_models_def = st.number_input(label="Models", value=1, step=1, format="%d", key='n_models_unit2')
        toughness_def = st.number_input(label="Toughness", value=1, step=1, format="%d", key='toughness_unit2')
        specials_def = st.multiselect("Special", ["Regeneration"],
                                  placeholder="Choose specialities",
                                  disabled=False, label_visibility="visible", key='specials_unit2')
        points_def = st.number_input(label="Points", value=10, step=10, format="%d", key='points_unit2')

with st.container():
    st.header('Attack stats')
    attacker = Unit(name='Attacker',
                       n_models=n_models,
                       quality=quality,
                       defense=defense,
                       points=points,
                       tough=toughness,
                       special= Special([specials_name2class[special] for special in specials]))

    defender = Unit(name='Defender',
                    n_models=n_models_def,
                    quality=quality_def,
                    defense=defense_def,
                    points=points_def,
                    tough=toughness_def,
                    special=Special([specials_name2class[special] for special in specials_def]))

    attacker.equip([st.session_state['weapons'][weapon] for weapon in weapons])
    results = Attack.fight(attacker, defender)
    print(results)
    df = pd.DataFrame.from_dict(results).T
    st.dataframe(df)