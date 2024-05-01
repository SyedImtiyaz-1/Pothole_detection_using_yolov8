import streamlit as st
import cv2
import numpy as np
import pandas as pd
import random
import os
from PIL import Image
from utils import detect_potholes
import geocoder
from ultralytics import YOLO
from utils import detect_potholes, send_email
import shutil 




page = st.sidebar.selectbox("Pages Menu",options=['Home','Using Image','Using Video'])

model = YOLO('./models/best.pt')

g = geocoder.ip('me')
print(g.latlng)


def register(location,higway_type,size,position, img_path=None):
    dic = {"location":location,"highway_type":higway_type,"size":size,"position":position}
    send_email(dic, img_path)
    
    st.info("Reported")
   
def get_pothole_info():
    st.sidebar.markdown("***")
    st.info(f"Getting Location of pothole using your IP Address {g.ip}")
    df = pd.DataFrame([g.latlng],columns=['lat', 'lon'])

    st.map(df)
    st.info(f"Location According to IP address {g.city},{g.state}")
    location = (g.city,g.state)
    highway_type = st.sidebar.selectbox(label="Select Road Type:",options=["National Highway","Local Road"])
    size = st.sidebar.selectbox(label="Approx. Size of Pothole",options=["Small Pothole","Medium Pothole","Large Pothole"])
    position = st.sidebar.selectbox(label="Position of Pothole",options=["Center","Sideways"])

    return location,highway_type,size,position

def save_image(image_file):
    img = Image.open(image_file)
    img.save("uploads/image.jpg")
    return img

def save_video(video_file):
    path_name = "uploads/video.mp4"
    with open(path_name,'wb') as f:
        f.write(video_file.read())

if page == 'Using Image':
    
    st.title("Pothole Detection Using Image")
    
    image_file = st.file_uploader('Upload Image',accept_multiple_files=False,type=['png','jpg','JPG','jpeg'])

    if image_file is not None:
    
        a,b = st.columns(2)
        file_details = {"filename":image_file.name, "filetype":image_file.type,"filesize":image_file.size}
        st.write(file_details)
        a.image(save_image(image_file))

        if 'image_name' not in st.session_state or st.session_state['image_name']!=image_file.name:
            img_res_path = detect_potholes(model, "uploads/image.jpg")
            st.session_state['image_name'] = image_file.name
            st.session_state['img_res_path'] = img_res_path

        if 'img_res_path' in st.session_state:
            res_path = st.session_state['img_res_path']
            if res_path:
                img_path = f"{res_path}/image.jpg"
                b.image(Image.open(img_path))

            location,highway_type,size,position = get_pothole_info()

            submit_report = st.sidebar.button("Submit Report")
            if submit_report:
                register(location,highway_type,size,position, img_path)



elif page == 'Using Video':
    st.title("Pothole Detection Using Video")

    st.warning("Video Processing will Take lot of Computization power. Please wait till processing completes")
    video_file = st.file_uploader(label="Upload Video",accept_multiple_files=False,type=["mp4"])
    

    if video_file is not None:
        save_video(video_file)
        
        if 'video_name' not in st.session_state or st.session_state['video_name']!=video_file.name:
            
            res = detect_potholes(model, "uploads/video.mp4")
            st.session_state['res'] = res

            rest = st.session_state['res']
            res_vdo_path = rest+'/video.mp4'
            shutil.copy(os.path.join('runs/segment/predict2', 'video.mp4'), os.path.join('./results/'))

            os.system(f'ffmpeg -i ./results/video.mp4 -vcodec libx264 ./results/video.mp4 -y')
            st.session_state['video_name'] = video_file.name



        # st.snow()
        if 'res' in st.session_state:
            rest = st.session_state['res']
            
            if rest:

                video_result = open("results/video.mp4",'rb')
                video_bytes = video_result.read()
                st.video(video_bytes)

                location,highway_type,size,position = get_pothole_info()

                submit_report = st.sidebar.button("Submit Report")
                if submit_report:
                    register(location,highway_type,size,position)

# elif page == 'Using Live Feed':
#     detect_potholes(model, 0)        


else:
    st.title('Pothole Detection')
    st.markdown("> Select any Choice from sidebar to procced")

    # st.image("model_files/out.jpg")
    cont = """

    ## Detecting Potholes on road using YOLO Model
    
    *Features:*
    - Detects Pothole From Image
    - Detects Potholes From Uploaded Video
    - Report Potholes 
    - Automatically Gets Location Information using IP Address.
    
    """

    st.markdown(cont)

    
