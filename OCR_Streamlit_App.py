# Arabic OCR Model Comparison App
# Compare EasyOCR vs Tesseract on Arabic text
import os

os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

import streamlit as st
import easyocr
import pytesseract
from PIL import Image, ImageDraw, ImageFont
import cv2
import numpy as np
import re

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# Set up the Streamlit page
st.set_page_config(page_title="Arabic OCR Comparison", layout="centered")
st.title("Arabic OCR Comparison (EasyOCR vs Tesseract)")


# Clean Detected Text
# Remove unwanted symbols
def clean_text(text):
    return re.sub(r"[^\u0600-\u06FFa-zA-Z0-9\s]", "", text).strip()


# OCR using EasyOCR
def easyocr_ocr(image_np):
    reader = easyocr.Reader(['ar', 'en'], gpu=False)
    results = reader.readtext(image_np)
    cleaned_texts = [clean_text(t) for (_, t, _) in results]
    full_text = "\n".join(cleaned_texts)
    return full_text, results


#  OCR using Tesseract
def tesseract_ocr(image_np):
    image_rgb = cv2.cvtColor(image_np, cv2.COLOR_BGR2RGB)
    text = pytesseract.image_to_string(image_rgb, lang="ara")
    return clean_text(text)


# Draw Bounding Boxes from EasyOCR
# Returns annotated image with text
def overlay_easyocr(image_np, results):
    for (bbox, text, _) in results:
        text = clean_text(text)
        (tl, tr, br, bl) = bbox  
        tl = tuple(map(int, tl))  
        br = tuple(map(int, br))

        img_pil = Image.fromarray(image_np)
        draw = ImageDraw.Draw(img_pil)
        font = ImageFont.load_default()

        draw.rectangle([tl, br], outline=(0, 255, 0), width=2)
        draw.text((tl[0], tl[1] - 10), text, fill=(255, 0, 0), font=font)

        image_np = np.array(img_pil)

    return image_np


#  File Upload 
upload = st.file_uploader("Upload an image", type=["png", "jpg", "jpeg"])


#  OCR Processing
if upload:
    # Load and display uploaded image
    image = Image.open(upload).convert("RGB")
    image_np = np.array(image)
    st.image(image, caption="Uploaded Image", use_column_width=True)

    # Run EasyOCR
    with st.spinner("Running EasyOCR..."):
        easy_text, easy_results = easyocr_ocr(image_np.copy())

    # Run Tesseract
    with st.spinner("Running Tesseract..."):
        tesseract_text = tesseract_ocr(image_np.copy())

   
    #  Show OCR Results
    st.subheader("EasyOCR Output")
    st.text_area("EasyOCR Text", easy_text, height=200)

    st.subheader("Tesseract Output")
    st.text_area("Tesseract Text", tesseract_text, height=200)

   
    #  Show Annotated Image
    annotated_image = overlay_easyocr(image_np.copy(), easy_results)
    st.image(annotated_image, caption="🖼️ EasyOCR Overlay", use_column_width=True)

    #  Save and Download Results
    os.makedirs("outputs", exist_ok=True)

    # Save text and image outputs
    easy_txt_path = "outputs/easyocr_result.txt"
    tess_txt_path = "outputs/tesseract_result.txt"
    image_out_path = "outputs/easyocr_image.jpg"

    cv2.imwrite(image_out_path, cv2.cvtColor(annotated_image, cv2.COLOR_RGB2BGR))
    with open(easy_txt_path, "w", encoding="utf-8") as f:
        f.write(easy_text)
    with open(tess_txt_path, "w", encoding="utf-8") as f:
        f.write(tesseract_text)

    # Provide download buttons
    st.subheader("Download Results")
    with open(easy_txt_path, "rb") as f:
        st.download_button("EasyOCR Text", f, file_name="easyocr_result.txt")
    with open(tess_txt_path, "rb") as f:
        st.download_button("Tesseract Text", f, file_name="tesseract_result.txt")
    with open(image_out_path, "rb") as f:
        st.download_button("Annotated Image", f, file_name="easyocr_overlay.jpg", mime="image/jpeg")
