import streamlit as st
from PIL import Image
import os
import io
from rembg import remove

# Set Streamlit page layout
st.set_page_config(layout="wide")

st.title("🖼️ Image Background Removal & Replacement")
st.write("Upload an image to remove its background and optionally replace it with another image.")

# Ensure directories exist
os.makedirs('original', exist_ok=True)
os.makedirs('masked', exist_ok=True)

# Upload subject image
subject_file = st.file_uploader("📂 Upload Subject Image (JPG, PNG, JPEG)", type=["jpg", "png", "jpeg"])

# Upload background image (optional)
replace_background = st.checkbox("Replace Background with Another Image?")
background_file = None
if replace_background:
    background_file = st.file_uploader("📂 Upload Background Image (JPG, PNG, JPEG)", type=["jpg", "png", "jpeg"])

# Threshold slider for adjusting accuracy
threshold = st.slider("🔍 Adjust Background Removal Accuracy", 0, 255, 100, step=5)

# Process the uploaded subject image
if subject_file:
    try:
        # Read image
        subject_bytes = subject_file.read()
        subject_img = Image.open(io.BytesIO(subject_bytes)).convert("RGBA")  # Ensure transparency support

        # Display original subject image
        st.image(subject_img, caption="📷 Original Image", use_column_width=True)

        # Remove background with fine-tuning
        st.subheader("🔍 Removing Background...")
        processed_img_bytes = remove(subject_bytes, 
                                     alpha_matting=True, 
                                     alpha_matting_foreground_threshold=threshold,
                                     alpha_matting_background_threshold=255-threshold,
                                     alpha_matting_erode_size=2)  # Improved accuracy
        processed_img = Image.open(io.BytesIO(processed_img_bytes)).convert("RGBA")  # Convert back to PIL format

        # Save and show processed image
        output_path = "masked/processed.png"
        processed_img.save(output_path)
        st.image(processed_img, caption="✅ Background Removed", use_column_width=True)

        # Background Replacement
        if replace_background and background_file:
            try:
                background_bytes = background_file.read()
                background_img = Image.open(io.BytesIO(background_bytes)).convert("RGBA")  # Open the background image

                # Resize background to match the subject
                background_img = background_img.resize(processed_img.size)

                # Paste subject onto background
                final_img = Image.alpha_composite(background_img, processed_img)
                final_output_path = "masked/final_output.png"
                final_img.save(final_output_path)

                # Display merged image
                st.image(final_img, caption="🎨 Image with New Background", use_column_width=True)
                st.success("✔ Background successfully replaced!")

            except Exception as e:
                st.error(f"❌ Error processing background image: {e}")

    except Exception as e:
        st.error(f"❌ Error processing subject image: {e}")
