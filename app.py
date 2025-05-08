import streamlit as st 
import pandas as pd 
from datetime import datetime as date
from time import sleep as wait 
import base64
import sqlite3

st.set_page_config(layout='wide')
hotels = ['Kensington Olympia', 'Luxurious Air Conditioned Apt High Street Kensington', 'Barrington Lodge', 'Wembar Hotel', 'Marble Arch Apartments', 'Cozy 1 Bedroom Flats in Paddington', 'Comfy Apartment near Hyde Park and Marble Arch', 'Two Bedroom Apartment near Hyde Park and Oxford Street', 'Superb Apartments opposite Edgware Road Station', 'Beautiful 4 Bedroom House near Paddington Station', 'Superb 2 Bedroom Apartment near Edgware Road Station', 'London Central Studios', 'Homely 3 Bedroom House in Hammersmith', 'Marylebone Apartments', 'Elegant 3 Bedrooms Apartment Near Hyde Park & Oxford St', 'Bright Apartments near Marble Arch and Hyde Park', 'Amazing 2 Bedroom Apartment near Paddington Station', 'Apartments in the Heart of High Street Kensington', '2 Bedrooms Apartment In the Heart of Oxford Street/Selfridges', 'Central Apartments near Marble Arch', 'Fabulous House near the Science Museum', 'Nice 3 Bedrooms Apartment Near Hyde Park & Oxford St', 'Comfy Apartments near Marble Arch', 'Hyde Park Apartments', 'Wonderful Apartments near Portobello Road', 'Luxury Apartments Near Harrods and the Science Museum', 'Comfortable Apartments near Harrods', 'Gorgeous Apartment Near Hyde Park And Oxford St', 'Hyde Park Studios', 'Lovely Apartments in Landward Court', 'Bright Apartment near Hyde Park', 'Natural History Museum Apartments', 'Modern studios Malvern Road', 'Portobello Road Artistic Studios', 'Modern Studios Close To Hyde Park', 'Holland Road Stays', 'Amesterdam Hotel', 'Harbour Flats', 'Dubai Creek Harbour', 'Salmon Street', 'The Dolphin Hotel', 'St Elmo Hotel', 'Avalon Guest house', 'The Rose and Crown Hotel', 'Alumhurst Hotel', 'Green Gables Hotel', 'The Richmond Hotel', 'Crofton House Hotel', 'Number 19 Brighton', 'Bank St Hotel', 'Swan Lake Hotel', 'Harbour Flats', 'Amsterdam Hotel', 'Sea Side Hotel', 'Sea Shell Hotel', 'Bonair Hotel', 'Harbour Hotel', 'Cambria Hotel', 'The Cumberland Hotel', 'North Coast Hotel', 'Royal Hotel', 'Citi Hotel', 'Number 13 Brighton']


def to_base64_img(byte_data):
    if isinstance(byte_data, memoryview):
        byte_data = byte_data.tobytes()
    base64_str = base64.b64encode(byte_data).decode()
    return f"data:image/png;base64,{base64_str}"


def meter_reader_updater():
    with st.form(key='uploader'): 
        meter_type = st.selectbox('Meter Type', ['Gas', 'Electricity'])
        position = st.selectbox('Select Meter Position', ['Meter A', 'Meter B', 'Meter C'])
        reading = st.number_input('Put the meter reading', min_value=1)
        hotel = st.selectbox('Select Your Hotel', options=hotels)
        photo = st.file_uploader('Upload your file:')
        submit = st.form_submit_button('Submit')

        if submit:
            if photo is None:
                st.warning("Please upload an image.")
                return

            try:

                con = 'sqlite:///db.db'
                df = pd.DataFrame({
                    'Reading_date': [date.now().strftime("%Y-%m-%d")],
                    'Photo': [photo.getvalue()],
                    'hotel': [hotel],
                    'Type': [meter_type],
                    'Reading': [reading],
                    'Position': [position],

                })
                df.to_sql('readings', con=con, if_exists='append', index=False)


                st.success(f'✅ Entry Successfully Added!')
                wait(1.5)
            except Exception as e:
                st.write(e)
    try:
        df = pd.read_sql('select * from readings', con='sqlite:///db.db')
        st.write(df[['Reading_date','hotel','Type','Reading','Position']])
    except Exception as e:
        st.write('Readings are empty')

def data_viewer():

    col1,col2 = st.columns(2)

    with col1: 
        hotel_selection = st.selectbox('Select Hotel:',options = hotels)
        from_date = st.date_input('From: ',value = '2025-01-01',)
    with col2: 
        meter_type = st.selectbox('Select Meter Type:',options = ['Gas', 'Electricity'])
        to_date = st.date_input('To: ','today')


    df = pd.read_sql_query(f'select * from readings where "Hotel" = "{hotel_selection}"  and "Type" = "{meter_type}" ', con='sqlite:///db.db')
    df['Photo'] = df['Photo'].apply(to_base64_img)
    st.data_editor(
        df,
        column_config={
            'Photo': st.column_config.ImageColumn('Meter Image', width='small'),
            'Reading_date': st.column_config.TextColumn('Date'),
            'Type': st.column_config.TextColumn('Type'),
            'Position': st.column_config.TextColumn('Position'),
            'hotel': st.column_config.TextColumn('Hotel'),
        },
        hide_index=True
    )



# Navigation
st.navigation([
    meter_reader_updater,
    data_viewer,
]).run()
