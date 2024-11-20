#add printer
import streamlit as st
import csv
from io import StringIO, BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4  # A4 is in portrait by default
from reportlab.lib.units import cm
import qrcode
import os
from zebra import Zebra  # Zebra printer integration

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

# Function to send labels to Zebra printer
def print_to_zebra(csv_file, label_width, label_height, selected_fields):
    csv_file.seek(0)
    csv_content = csv_file.read().decode("utf-8")
    csv_reader = csv.DictReader(StringIO(csv_content))

    zebra_printer = Zebra()
    printers = zebra_printer.getqueues()
    
    if not printers:
        st.error("No Zebra printers found. Please ensure your Zebra printer is connected.")
        return
    
    # Select a printer
    selected_printer = st.selectbox("Select Zebra Printer", printers)
    zebra_printer.setqueue(selected_printer)

    # ZPL (Zebra Programming Language) template for label printing
    for row in csv_reader:
        qr_data = row.get("lid", "N/A")
        qr_img = generate_qr_code(qr_data)
        qr_img_path = f"{qr_data}_temp_qr.png"
        qr_img.save(qr_img_path)

        # Send ZPL commands to printer
        zpl = f"""
        ^XA
        ^FO10,10^BQN,2,5^FDLA,{qr_data}^FS
        ^FO130,10^A0N,30,30^FD{" | ".join([f"{field}: {row.get(field, 'N/A')}" for field in selected_fields])}^FS
        ^XZ
        """
        zebra_printer.output(zpl)
        os.remove(qr_img_path)

    st.success("Labels sent to Zebra printer.")

# Function to create PDF with QR code and dynamic text for each row
def create_pdf_with_qr_from_csv(csv_file, label_width, label_height, selected_fields):
    output = BytesIO()
    page_width, page_height = A4
    c = canvas.Canvas(output, pagesize=(page_width, page_height))

    csv_file.seek(0)
    csv_content = csv_file.read().decode("utf-8")
    csv_reader = csv.DictReader(StringIO(csv_content))

    x_start = 1 * cm
    y_start = page_height - 1 * cm
    qr_size = 1.5 * cm
    padding = 0.2 * cm
    x, y = x_start, y_start

    for row in csv_reader:
        if y - label_height < 1 * cm:
            y = y_start
            x += label_width + padding
            if x + label_width > page_width - 1 * cm:
                c.showPage()
                x = x_start

        c.rect(x, y - label_height, label_width, label_height)

        qr_img = generate_qr_code(row["lid"])
        qr_img_path = f"{row['lid']}_temp_qr.png"
        qr_img.save(qr_img_path)
        
        qr_x = x + 0.03 * cm
        qr_y = y - label_height + (label_height - qr_size) / 2
        c.drawImage(qr_img_path, qr_x, qr_y, width=qr_size, height=qr_size)

        text_x = x + qr_size
        text_y = y - padding - 0.3 * cm
        
        c.setFont("Helvetica-Bold", 5.2)
        for idx, field in enumerate(selected_fields):
            field_value = row.get(field, "N/A")
            c.drawString(text_x, text_y - idx * 0.55 * cm, f"{field}: {field_value}")

        os.remove(qr_img_path)
        y -= label_height + padding

    c.save()
    output.seek(0)
    return output

# Streamlit app
st.title("QR Label Generator")

label_width = 3.8 * cm
label_height = 1.9 * cm

uploaded_csv = st.file_uploader("Upload CSV File", type=["csv"])

if uploaded_csv is not None:
    try:
        st.success("CSV uploaded successfully. Processing...")
        csv_content = uploaded_csv.read().decode("utf-8")
        csv_reader = csv.DictReader(StringIO(csv_content))
        fieldnames = csv_reader.fieldnames

        selected_fields = st.multiselect("Select fields to display", fieldnames, default=fieldnames)

        action = st.radio("Choose an action", ("Download PDF", "Print to Zebra Printer"))

        if action == "Download PDF":
            pdf_output = create_pdf_with_qr_from_csv(uploaded_csv, label_width, label_height, selected_fields)
            st.download_button(
                label="Download QR Code PDF",
                data=pdf_output,
                file_name="QR_Labels.pdf",
                mime="application/pdf"
            )
        elif action == "Print to Zebra Printer":
            print_to_zebra(uploaded_csv, label_width, label_height, selected_fields)

    except Exception as e:
        st.error(f"An error occurred: {e}")
