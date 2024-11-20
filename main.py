# import streamlit as st
# import os
# import csv
# from io import StringIO, BytesIO
# from reportlab.lib.pagesizes import letter 
# from reportlab.lib.units import cm
# from reportlab.pdfgen import canvas
# import qrcode

# # Function to generate QR code
# def generate_qr_code(data):
#     qr = qrcode.QRCode(
#         version=1,
#         error_correction=qrcode.constants.ERROR_CORRECT_L,
#         box_size=2,
#         border=1,
#     )
#     qr.add_data(data)
#     qr.make(fit=True)
#     img = qr.make_image(fill='black', back_color='white')
#     return img

# # Function to set layout parameters
# def set_layout_parameters(margin, text_margin, qr_img_size, line_spacing, horizontal_spacing, vertical_spacing):
#     return {
#         'margin': margin,
#         'text_margin': text_margin,
#         'qr_img_size': qr_img_size,
#         'line_spacing': line_spacing,
#         'horizontal_spacing': horizontal_spacing,
#         'vertical_spacing': vertical_spacing
#     }

# # Function to generate child health report
# def generate_child_health_report(input_file, layout_params, fields_to_display):
#     output = BytesIO()
#     c = canvas.Canvas(output, pagesize=letter)

#     # Read the CSV file
#     input_file.seek(0)
#     input_text = input_file.read().decode('utf-8')
#     csvfile = StringIO(input_text)
#     reader = csv.DictReader(csvfile)

#     # Check if the required headers are present
#     required_headers = {'project', 'ID', 'lid'}
#     if not required_headers.issubset(reader.fieldnames):
#         raise ValueError("CSV file is missing required headers")

#     margin = layout_params['margin']
#     text_margin = layout_params['text_margin']
#     qr_img_size = layout_params['qr_img_size']
#     line_spacing = layout_params['line_spacing']
#     horizontal_spacing = layout_params['horizontal_spacing']
#     vertical_spacing = layout_params['vertical_spacing']
#     x_start = margin
#     y_start = letter[1] - margin - qr_img_size  # Start from top-left corner
#     x = x_start
#     y = y_start

#     for row in reader:
#         if y < margin:  # Move to next column if reached the bottom of the page
#             y = y_start
#             x += qr_img_size + horizontal_spacing

#             if x + qr_img_size > letter[0] - margin:  # If reached the right edge, start a new page
#                 c.showPage()
#                 x = x_start
        
#         p_value = row['project']
#         id_value = row['ID']
#         lid_value = row['lid']
        
#         qr_img = generate_qr_code(lid_value)
#         qr_img_path = f"{lid_value}_qrcode.png"
#         qr_img.save(qr_img_path)

#         # Draw QR code
#         c.drawImage(qr_img_path, x, y, width=qr_img_size, height=qr_img_size)
        
#         # Draw text on the right side of QR code, vertically
#         text_x = x + qr_img_size + text_margin
#         c.setFont("Helvetica-Bold", 6)
#         c.setFillColor("black")

#         # Dynamically add fields based on user selection
#         text_y = y + 2.2 * line_spacing
#         if 'Project' in fields_to_display:
#             c.drawString(text_x, text_y, f"Project: {p_value}")
#             text_y -= line_spacing
#         if 'ID' in fields_to_display:
#             c.drawString(text_x, text_y, f"ID: {id_value}")
#             text_y -= line_spacing
#         if 'LID' in fields_to_display:
#             c.drawString(text_x, text_y, f"LID: {lid_value}")

#         os.remove(qr_img_path)  # Remove the temporary QR code image
        
#         y -= (qr_img_size + vertical_spacing + 3 * line_spacing)

#     c.save()
#     output.seek(0)
#     return output

# # Streamlit app  
# st.title('Generate QR Code')

# # Fields to display selection (moved to the top)
# fields_to_display = st.sidebar.multiselect("Fields to Display", ["Project", "ID", "LID"], default=["Project", "LID"])

# # Parameters for layout customization (after Fields to Display)
# st.sidebar.header('Layout Parameters')
# margin = st.sidebar.slider('Margin (cm)', min_value=1.0, max_value=5.0, value=2.8, step=0.1) * cm
# text_margin = st.sidebar.slider('Text Margin (cm)', min_value=0.1, max_value=2.0, value=0.05, step=0.05) * cm
# qr_img_size = st.sidebar.slider('QR Code Size (cm)', min_value=1.0, max_value=5.0, value=0.8, step=0.1) * cm
# line_spacing = st.sidebar.slider('Line Spacing', min_value=6, max_value=15, value=8, step=1)
# horizontal_spacing = st.sidebar.slider('Horizontal Spacing (cm)', min_value=1.0, max_value=5.0, value=2.8, step=0.1) * cm
# vertical_spacing = st.sidebar.slider('Vertical Spacing (cm)', min_value=0.0, max_value=5.0, value=1.0, step=0.1) * cm

# layout_params = set_layout_parameters(margin, text_margin, qr_img_size, line_spacing, horizontal_spacing, vertical_spacing)

# # Upload CSV file
# uploaded_file = st.file_uploader("Choose a CSV file", type="csv")

# if uploaded_file is not None:
#     try:
#         output = generate_child_health_report(uploaded_file, layout_params, fields_to_display)
        
#         st.download_button(
#             label="Download PDF",
#             data=output,
#             file_name="QR_file.pdf",
#             mime="application/pdf"
#         )
#     except Exception as e:
#         st.error(f"An error occurred: {e}")

# #updated code
# import streamlit as st
# import csv
# from io import StringIO, BytesIO
# from reportlab.pdfgen import canvas
# from reportlab.lib.pagesizes import A4  # A4 is in portrait by default
# from reportlab.lib.units import cm
# import qrcode
# import os

# # Function to generate QR code
# def generate_qr_code(data):
#     qr = qrcode.QRCode(
#         version=1,
#         error_correction=qrcode.constants.ERROR_CORRECT_L,
#         box_size=10,
#         border=1,
#     )
#     qr.add_data(data)
#     qr.make(fit=True)
#     img = qr.make_image(fill="black", back_color="white")
#     return img

# # Function to create PDF with QR code and dynamic text for each row
# def create_pdf_with_qr_from_csv(csv_file, label_width, label_height, selected_fields):
#     output = BytesIO()

#     # Define page size and canvas (portrait orientation)
#     page_width, page_height = A4  # Use A4 size in portrait (default orientation)
#     c = canvas.Canvas(output, pagesize=(page_width, page_height))

#     # Read CSV file
#     csv_file.seek(0)
#     csv_content = csv_file.read().decode("utf-8")
#     csv_reader = csv.DictReader(StringIO(csv_content))

#     # Set layout parameters
#     x_start = 1 * cm  # Left margin
#     y_start = page_height - 1 * cm  # Top margin
#     qr_size = 1.5 * cm  # QR code size
#     padding = 0.2 * cm  # Padding between elements and edges

#     x = x_start
#     y = y_start

#     # Process each row
#     for row in csv_reader:
#         # Start a new column if necessary
#         if y - label_height < 1 * cm:  # Bottom margin
#             y = y_start
#             x += label_width + padding
#             if x + label_width > page_width - 1 * cm:  # Right margin
#                 c.showPage()
#                 x = x_start

#         # Draw label box
#         c.rect(x, y - label_height, label_width, label_height)

#         # Generate and place QR code directly on the left side
#         qr_img = generate_qr_code(row["lid"])
#         qr_img_path = f"{row['lid']}_temp_qr.png"
#         qr_img.save(qr_img_path)
        
#         # QR code placed at the very left side, no space on the left
#         qr_x = x + 0.03 * cm  # Position QR code at the left edge
#         qr_y = y - label_height + (label_height - qr_size) / 2  # Vertically center the QR code
#         c.drawImage(qr_img_path, qr_x, qr_y, width=qr_size, height=qr_size)

#         # Place selected fields as text on the right side of the QR code
#         text_x = x + qr_size  # Text starts after the QR code
#         text_y = y - padding - 0.3 * cm
        
#         c.setFont("Helvetica-Bold", 5.2)  # Smaller font size for compact fit
#         for idx, field in enumerate(selected_fields):
#             field_value = row.get(field, "N/A")
#             c.drawString(text_x, text_y - idx * 0.6 * cm, f"{field}: {field_value}")

#         # Remove temporary QR image
#         os.remove(qr_img_path)

#         # Move to next label position
#         y -= label_height + padding

#     # Save the PDF
#     c.save()
#     output.seek(0)
#     return output

# # Streamlit app
# st.title("Zebra Printer QR Label Generator")

# # Zebra printer label size selection
# label_size = st.selectbox(
#     "Select Printer Label Size",
#     ["Zebra 2824", "Zebra ZD420", "Zebra ZT410", "Custom Size"]
# )

# # Set the label dimensions based on the selected printer
# if label_size == "Zebra 2824":
#     label_width = 3.8 * cm  # 3.8 cm wide for Zebra 2824
#     label_height = 1.9 * cm  # 1.9 cm height for Zebra 2824
# elif label_size == "Zebra ZD420":
#     label_width = 5.0 * cm  # 5.0 cm wide for Zebra ZD420
#     label_height = 2.5 * cm  # 2.5 cm height for Zebra ZD420
# elif label_size == "Zebra ZT410":
#     label_width = 6.0 * cm  # 6.0 cm wide for Zebra ZT410
#     label_height = 3.0 * cm  # 3.0 cm height for Zebra ZT410
# else:
#     # Custom size option, get user input
#     label_width = st.number_input("Enter label width in cm", value=3.8)
#     label_height = st.number_input("Enter label height in cm", value=1.9)

# # Upload CSV file
# uploaded_csv = st.file_uploader("Upload CSV File", type=["csv"])

# if uploaded_csv is not None:
#     try:
#         st.success("CSV uploaded successfully. Processing...")

#         # Read CSV to show field options dynamically
#         csv_content = uploaded_csv.read().decode("utf-8")
#         csv_reader = csv.DictReader(StringIO(csv_content))
#         fieldnames = csv_reader.fieldnames

#         # Allow user to select which fields to display in the label
#         selected_fields = st.multiselect("Select fields to display", fieldnames, default=fieldnames)

#         # Generate PDF with QR codes
#         pdf_output = create_pdf_with_qr_from_csv(uploaded_csv, label_width, label_height, selected_fields)

#         # Add download button
#         st.download_button(
#             label="Download QR Code PDF",
#             data=pdf_output,
#             file_name="QR_Labels.pdf",
#             mime="application/pdf"
#         )
#     except Exception as e:
#         st.error(f"An error occurred: {e}")


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
