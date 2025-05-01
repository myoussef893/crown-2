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

def calculate_consumption(hotel, meter_type, position, new_reading):
    con = sqlite3.connect("db.db")
    query = """
        SELECT Reading, Reading_date FROM meter_readings
        WHERE hotel = ? AND Type = ? AND Position = ?
        ORDER BY Reading_date DESC LIMIT 1
    """
    df = pd.read_sql(query, con=con, params=[hotel, meter_type, position])
    con.close()

    if df.empty:
        return None, None  # First reading

    last_reading = df.iloc[0]['Reading']
    last_date = pd.to_datetime(df.iloc[0]['Reading_date'], dayfirst=True)
    new_date = date.now()

    consumption = new_reading - last_reading
    days_between = (new_date - last_date).days

    return consumption, days_between

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
                consumption, days_between = calculate_consumption(hotel, meter_type, position, reading)

                con = sqlite3.connect("db.db")
                df = pd.DataFrame({
                    'Reading_date': [date.now().strftime("%d/%m/%Y, %H:%M")],
                    'Photo': [photo.getvalue()],
                    'hotel': [hotel],
                    'Type': [meter_type],
                    'Reading': [reading],
                    'Position': [position],
                    'Consumption': [consumption if consumption is not None else None],
                    'Days_Since_Last': [days_between if days_between is not None else None]

                })
                df.to_sql('meter_readings', con=con, if_exists='append', index=False)
                con.close()

                st.success(f'✅ Entry Successfully Added! Consumption: {consumption} over {days_between} days' if consumption else '✅ First entry added.')
                wait(1.5)
            except Exception as e:
                st.warning(f'Error: {e}')

    try:
        df = pd.read_sql('select * from meter_readings', con='sqlite:///db.db')
        st.write(df[['Reading_date','hotel','Type','Reading','Position','Consumption','Days_Since_Last']])
    except Exception as e:
        st.write('Readings are empty')

def data_viewer():
    df = pd.read_sql('meter_readings', con='sqlite:///db.db')
    df['Photo'] = df['Photo'].apply(to_base64_img)
    df['Consumption'] = pd.to_numeric(df['Consumption'],errors='coerce')
    st.data_editor(
        df,
        column_config={
            'Photo': st.column_config.ImageColumn('Meter Image', width='small'),
            'Reading_date': st.column_config.TextColumn('Date'),
            'Type': st.column_config.TextColumn('Type'),
            'Position': st.column_config.TextColumn('Position'),
            'hotel': st.column_config.TextColumn('Hotel'),
            'Consumption': st.column_config.NumberColumn('Consumption'),
            'Days_Since_Last': st.column_config.NumberColumn('Days Since Last'),
        },
        hide_index=True
    )



# Navigation
st.navigation([
    meter_reader_updater,
    data_viewer,
]).run()
