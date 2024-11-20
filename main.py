#run code
import streamlit as st
import csv
from io import StringIO, BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4  # A4 is in portrait by default
from reportlab.lib.units import cm
import qrcode
import os

# Function to generate QR code
def generate_qr_code(data):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=1,
    )
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill="black", back_color="white")
    return img

# Function to create PDF with QR code and dynamic text for each row
def create_pdf_with_qr_from_csv(csv_file, label_width, label_height, selected_fields):
    output = BytesIO()

    # Define page size and canvas (portrait orientation)
    page_width, page_height = A4  # Use A4 size in portrait (default orientation)
    c = canvas.Canvas(output, pagesize=(page_width, page_height))

    # Read CSV file
    csv_file.seek(0)
    csv_content = csv_file.read().decode("utf-8")
    csv_reader = csv.DictReader(StringIO(csv_content))

    # Set layout parameters
    x_start = 1 * cm  # Left margin
    y_start = page_height - 1 * cm  # Top margin
    qr_size = 1.5 * cm  # QR code size
    padding = 0.2 * cm  # Padding between elements and edges

    x = x_start
    y = y_start

    # Process each row
    for row in csv_reader:
        # Start a new column if necessary
        if y - label_height < 1 * cm:  # Bottom margin
            y = y_start
            x += label_width + padding
            if x + label_width > page_width - 1 * cm:  # Right margin
                c.showPage()
                x = x_start

        # Draw label box
        c.rect(x, y - label_height, label_width, label_height)

        # Generate and place QR code directly on the left side
        qr_img = generate_qr_code(row["lid"])
        qr_img_path = f"{row['lid']}_temp_qr.png"
        qr_img.save(qr_img_path)
        
        # QR code placed at the very left side, no space on the left
        qr_x = x + 0.03 * cm  # Position QR code at the left edge
        qr_y = y - label_height + (label_height - qr_size) / 2  # Vertically center the QR code
        c.drawImage(qr_img_path, qr_x, qr_y, width=qr_size, height=qr_size)

        # Place selected fields as text on the right side of the QR code
        text_x = x + qr_size  # Text starts after the QR code
        text_y = y - padding - 0.3 * cm
        
        c.setFont("Helvetica-Bold", 5.2)  # Smaller font size for compact fit
        for idx, field in enumerate(selected_fields):
            field_value = row.get(field, "N/A")
            c.drawString(text_x, text_y - idx * 0.55 * cm, f"{field}: {field_value}")

        # Remove temporary QR image
        os.remove(qr_img_path)

        # Move to next label position
        y -= label_height + padding

    # Save the PDF
    c.save()
    output.seek(0)
    return output

# Streamlit app
st.title("QR Label Generator")

# Set default label dimensions (assuming Zebra 2824 standard)
label_width = 3.8 * cm
label_height = 1.9 * cm

# Upload CSV file
uploaded_csv = st.file_uploader("Upload CSV File", type=["csv"])

if uploaded_csv is not None:
    try:
        st.success("CSV uploaded successfully. Processing...")

        # Read CSV to show field options dynamically
        csv_content = uploaded_csv.read().decode("utf-8")
        csv_reader = csv.DictReader(StringIO(csv_content))
        fieldnames = csv_reader.fieldnames

        # Allow user to select which fields to display in the label
        selected_fields = st.multiselect("Select fields to display", fieldnames, default=fieldnames)

        # Generate PDF with QR codes
        pdf_output = create_pdf_with_qr_from_csv(uploaded_csv, label_width, label_height, selected_fields)

        # Add download button
        st.download_button(
            label="Download QR Code PDF",
            data=pdf_output,
            file_name="QR_Labels.pdf",
            mime="application/pdf"
        )
    except Exception as e:
        st.error(f"An error occurred: {e}")

