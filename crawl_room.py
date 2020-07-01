from bs4 import BeautifulSoup as soup
import requests
import pandas as pd
import time
import re

page=0

#divided url into 2 part is to handle %2c error.
def get_roomPages(url1,url2):

    room_pages_list=[]

    for i in range(1,21):
        url_n = url2 % i
        url=url1+url_n
        room_pages_list.append(url)

    return room_pages_list

def get_room_list(room_pages_list):

    room_list=[]

    for i in room_pages_list:
        time.sleep(1)
        r = requests.get(i)
        content = soup(r.content, 'html.parser')
        soups=content.select('div.list-enqu-btn ul li a.view')

        for i in soups:
            room_link=i['href']
            room_list.append(room_link)

    return room_list



def get_room_detail(sp):

    phone_num = sp.select('.list-group li span.name')[1].text.strip()
    rental = sp.select('div.room-rental > span')[0].text
    location = sp.select('p')[0].text.strip()
    room_type = sp.select('div.v3-list-ql-inn a h3')[0].text



    return room_type, rental, location, phone_num


def create_df(link, room_type, rental, location, phone_num):
    col = ['link', 'room_type', 'rental', 'location', 'phone_num']
    df = pd.DataFrame(columns=col)
    df_subRoom = df.append(
        {'link': link, 'room_type': room_type, 'rental': rental, 'location': location, 'phone_num': str(phone_num)},
        ignore_index=True)

    return df_subRoom


def parse_html(room_list):
    k = 0
    df_rooms = pd.DataFrame()
    try:
        while k < 1:
            for i in room_list:
                link = i
                r = requests.get(link)
                content = soup(r.content, 'html.parser')
                room_type, rental, location, phone_num = get_room_detail(content)
                df_subRoom = create_df(link, room_type, rental, location, phone_num)
                df_rooms = pd.concat([df_rooms, df_subRoom])
                k += 1
    except:
        pass

    return df_rooms

def data_preprocessing(df):

    df['room'] = df['room_type'].str.extract(r"(Single|Small|Middle|Master)")
    df['addr1'] = df['location'].str.extract(r"(.+(?=\,))")
    df['addr2'] = df['location'].str.extract(r"((?<=\,).*$)")

    df.dropna(
        axis=0,
        how='any',
        thresh=None,
        subset=None,
        inplace=True
    )
    df['price_rm'] = df['rental'].str.extract(r"(\d\d\d.\d\d)")
    # df.drop(columns=['Unnamed: 0', 'Unnamed: 0.1', 'Unnamed: 0.1.1', 'Unnamed: 0.1.1.1','room_type','rental'], inplace=True)
    df['whatappLink'] = 'https://api.whatsapp.com/send?phone=' + df['phone_num'].astype(
        str) + '&text=' + 'Hi,for' + '  ' + df['link'] + '  ' + ',is it still available?'


    return df



if __name__ == "__main__":

    # Dataset
    url1='https://www.ibilik.my/rooms/penang?location_search=4&location_search_name=Penang%2C'
    url2='Malaysia&page=%d'

    pages=get_roomPages(url1,url2)
    list=get_room_list(pages)
    df=parse_html(list)
    df.to_csv('ori_room_list.csv')

    # Data Preprocessing
    df=pd.read_csv('ori_room_list.csv')

    ndf=data_preprocessing(df)

    ndf.to_csv('room_rental_ds.csv')

