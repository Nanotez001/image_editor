import streamlit as st
import pandas as pd
import re

def generate_tv_spec_html(spec_text, category_headers_str):
    """
    Parses the TV specification text and generates HTML content.

    Args:
        spec_text (str): The raw text containing TV specifications.
        category_headers_str (str): A comma-separated string of category headers.

    Returns:
        str: The generated HTML content as a string.
    """
    # 1. Clean and Prepare Lines from spec_text
    lines = [line.strip() for line in spec_text.strip().split('\n') if line.strip()]

    # 2. Define Category Headers from input string
    adjusted_category_headers = [h.strip() for h in category_headers_str.split(',') if h.strip()]
    if not adjusted_category_headers:
        st.warning("Please provide at least one category header.")
        return "<p>Error: No category headers provided.</p>"

    # 3. Parsing Logic
    data_rows = []
    current_category = None
    skip_next = False

    for i in range(len(lines)):
        if skip_next:
            skip_next = False
            continue

        line = lines[i].strip()
        if not line:
            continue

        if line in adjusted_category_headers:
            current_category = line
            continue

        spec_name = line
        spec_value = ""

        if (i + 1 < len(lines)) and (lines[i+1].strip() not in adjusted_category_headers):
            spec_value = lines[i+1].strip()
            skip_next = True

        data_rows.append({"Category": current_category, "Specification": spec_name, "Value": spec_value})

    # Create the DataFrame
    df = pd.DataFrame(data_rows)

    # Clean up initial "สเปค" and "ย่อ" (if they are still in the headers and parsed)
    # This part assumes "สเปค" and "ย่อ" are just top-level titles
    df_cleaned = df[~df['Category'].isin(['สเปค', 'ย่อ'])].copy()

    # Adjust the 'ภาพรวม' entries to avoid duplication
    # You might want to make this mapping configurable or remove if not desired
    df_cleaned.loc[df_cleaned['Category'] == 'ภาพรวม', 'Category'] = 'Overall Summary'
    df_cleaned.loc[(df_cleaned['Category'] == 'Overall Summary') & (df_cleaned['Specification'] == 'Refresh Rate'), 'Specification'] = 'Overall Refresh Rate'
    df_cleaned.loc[(df_cleaned['Category'] == 'Overall Summary') & (df_cleaned['Specification'] == 'Resolution'), 'Specification'] = 'Overall Resolution'
    df_cleaned.loc[(df_cleaned['Category'] == 'Overall Summary') & (df_cleaned['Specification'] == 'Video'), 'Specification'] = 'Overall Video Processor'
    df_cleaned.loc[(df_cleaned['Category'] == 'Overall Summary') & (df_cleaned['Specification'] == 'Design'), 'Specification'] = 'Overall Design Style'
    df_cleaned.loc[(df_cleaned['Category'] == 'Overall Summary') & (df_cleaned['Specification'] == 'Product Type'), 'Specification'] = 'Overall Product Type'

    # Reset index for clean DataFrame
    df_cleaned = df_cleaned.reset_index(drop=True)

    # --- HTML Generation ---

    html_head = """
    <!DOCTYPE html>
    <html lang="th">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <title>Samsung QLED TV Specifications</title>
        <style>
            body {
                font-family: sans-serif;
                margin: 20px;
                background-color: #f9f9f9;
                color: #333;
            }
            .container {
                max-width: 900px;
                margin: auto;
                background: #fff;
                padding: 20px;
                border-radius: 12px;
                box-shadow: 0 0 12px rgba(0,0,0,0.1);
            }
            h1 {
                font-size: 1.8rem;
                color: #111;
            }
            h2 {
                font-size: 1.4rem;
                margin-top: 30px;
                border-bottom: 2px solid #ddd;
                padding-bottom: 5px;
            }
            ul {
                list-style: disc;
                padding-left: 20px;
            }
            table {
                width: 100%;
                border-collapse: collapse;
                margin-top: 15px;
            }
            th, td {
                padding: 10px;
                border: 1px solid #ddd;
                text-align: left;
            }
            th {
                background-color: #f0f0f0;
            }
            @media (max-width: 600px) {
                body { margin: 10px; }
                .container { padding: 15px; }
            }
        </style>
    </head>
    <body>
        <div class="container">
    """

    # Product Name (can be made configurable or derived from data)
    product_name = "Samsung QLED TV Specifications (2025 Model)"

    # Summary List Items (adjust logic as needed)
    summary_list_items = []
    # Example: Check if specific specs exist and add to summary
    if 'Screen Size' in df_cleaned['Specification'].values:
        size = df_cleaned[df_cleaned['Specification'] == 'Screen Size']['Value'].iloc[0]
        summary_list_items.append(f"<li>ขนาดหน้าจอ: {size}</li>")
    if 'Overall Refresh Rate' in df_cleaned['Specification'].values:
        refresh_rate = df_cleaned[df_cleaned['Specification'] == 'Overall Refresh Rate']['Value'].iloc[0]
        summary_list_items.append(f"<li>Refresh Rate: {refresh_rate}</li>")
    if 'Resolution' in df_cleaned['Specification'].values:
        resolution = df_cleaned[df_cleaned['Specification'] == 'Resolution']['Value'].iloc[0]
        summary_list_items.append(f"<li>ความละเอียด: {resolution}</li>")
    if 'Operating System' in df_cleaned['Specification'].values:
        os = df_cleaned[df_cleaned['Specification'] == 'Operating System']['Value'].iloc[0]
        summary_list_items.append(f"<li>ระบบปฏิบัติการ: {os}</li>")
    if 'Product Type' in df_cleaned['Specification'].values:
        p_type = df_cleaned[df_cleaned['Specification'] == 'Product Type']['Value'].iloc[0]
        summary_list_items.append(f"<li>ประเภทผลิตภัณฑ์: {p_type}</li>")

    # Start building HTML body content
    html_body_content = f"<h1>{product_name}</h1>\n"

    if summary_list_items:
        html_body_content += "    <ul>\n" + "\n".join(summary_list_items) + "\n    </ul>\n"

    # Group data by Category to create tables
    grouped_data = df_cleaned.groupby('Category')

    for category_name, group in grouped_data:
        # Skip categories not intended for separate table display or already handled
        if category_name in ['สเปค', 'ย่อ']:
            continue

        # Map category names to more readable Thai
        display_category_name_map = {
            'Overall Summary': 'ภาพรวม',
            'Display': 'จอภาพ',
            'Video': 'ภาพ',
            'Audio': 'เสียง',
            'Smart Service': 'บริการสมาร์ททีวี',
            'Smart Feature': 'คุณสมบัติสมาร์ท',
            'Game Feature': 'คุณสมบัติสำหรับเล่นเกม',
            'Tuner/Broadcasting': 'จูนเนอร์/การกระจายเสียง',
            'Connectivity': 'การเชื่อมต่อ',
            'Design': 'ดีไซน์',
            'Additional Feature': 'คุณสมบัติเพิ่มเติม',
            'Accessibility': 'การเข้าถึง',
            'Power & Eco Solution': 'พลังงานและโซลูชันประหยัดพลังงาน',
            'Dimension': 'ขนาด',
            'Weight': 'น้ำหนัก',
            'Accessory': 'อุปกรณ์เสริม',
            # Add more mappings as needed
        }
        display_category_name = display_category_name_map.get(category_name, category_name)


        html_body_content += f"    <h2>{display_category_name}</h2>\n"
        html_body_content += "    <table>\n"

        for _, row in group.iterrows():
            spec = row['Specification']
            value = row['Value']

            # Handle empty values for "Yes" or "Support"
            if value == "Yes":
                display_value = "มี"
            elif value == "Support":
                display_value = "รองรับ"
            elif value == "":
                display_value = "-"
            else:
                display_value = value

            html_body_content += f"        <tr><th>{spec}</th><td>{display_value}</td></tr>\n"
        html_body_content += "    </table>\n"

    html_footer = """
        </div>
    </body>
    </html>
    """

    full_html_content = html_head + html_body_content + html_footer
    return full_html_content

# --- Streamlit UI ---
st.set_page_config(layout="wide", page_title="TV Spec HTML Generator")

st.title("TV Specification to HTML Converter")

st.write("วางข้อความสเปคทีวีของคุณที่นี่:")
# Default spec text for convenience
default_spec_text = """
สเปค
ย่อ
ภาพรวม
Refresh Rate
Up to 60Hz
Resolution
4K (3,840 x 2,160)
Video
Q4 Lite Processor
Design
Metal Stream
Product Type
QLED
Display
Screen Size
85"
Refresh Rate
Up to 60Hz
Resolution
4K (3,840 x 2,160)
Video
Picture Engine
Q4 Lite Processor
HDR (High Dynamic Range)
Quantum HDR
HDR 10+
Support
AI Upscale
4K Upscaling
Contrast
Mega Contrast
Micro Dimming
UHD Dimming
Contrast Enhancer
Yes
Motion Technology
Motion Xcelerator
Filmmaker Mode (FMM)
Yes
Color Booster
Yes
Audio
Object Tracking Sound
OTS Lite
Q-Symphony
Yes
Sound Output (RMS)
20W
Speaker Type
2CH
Adaptive Sound
Yes
Smart Service
Operating System
Tizen™ Smart TV
Bixby
Yes
Samsung TV Plus
Yes
Web Browser
Yes
SmartThings Hub / Matter Hub / IoT-Sensor Functionality / Quick Remote
Yes
Smart Feature
Multi Device Experience
Mobile to TV, Sound Mirroring, Wireless TV On
Apple AirPlay
Yes
Daily+
Yes
Storage Share
Yes
Game Feature
Auto Game Mode (ALLM)
Yes
VRR
Yes
HGiG
Yes
Tuner/Broadcasting
Digital Broadcasting
DVB-T2
Analog Tuner
Yes
TV Key Support
Yes
Connectivity
HDMI
3
USB
1 x USB-A
HDMI (High Frame Rate)
4K 60Hz (for HDMI 1/2/3)
Ethernet (LAN)
1
RF In (Terrestrial / Cable input)
1/1(Common Use for Terrestrial)/0
Wi-Fi
Yes (Wi-Fi 5)
Bluetooth
Yes(5.3)
Anynet+ (HDMI-CEC)
Yes
HDMI Audio Return Channel
eARC/ARC
Design
Design
Metal Stream
Bezel Type
3 Bezel-less
Front Color
BLACK
Stand Type
BASIC FEET
Stand Color
TITAN GRAY
Additional Feature
Embeded POP
Yes
EPG
Yes
IP Control
Yes
OSD Language
Local Languages
Accessibility
Accessibillity - Voice Guide
Chinese (China),English (UK),French (France),German (Germany),Hindi (India),Indonesian (Indonesia),Italian (Italy),Korean (Korea),Malay (Malaysia),Portuguese (Portugal),Russian (Russia),Spanish (Spain),Thai (Thailand),Vietnamese (Vietnam)
Low Vision Support
Audio Description, Zoom Menu and Text, High Contrast, SeeColors, Color Inversion, Grayscale, Auto Picture Off
Hearing Impaired Support
Closed Caption (Subtitle), Multi-output Audio, Sign Language Zoom
Motor Impaired Support
Slow Button Repeat, Remote Control App. for All
Power & Eco Solution
Eco Sensor
Yes
Power Supply
AC100-240V~ 50/60Hz
Power Consumption (Max)
280 W
Auto Power Off
Yes
Auto Power Saving
Yes
Dimension
Package Size (WxHxD)
2075 x 1200 x 171 mm
Set Size with Stand (WxHxD)
1889.9 x 1132.8 x 326 mm
Set Size without Stand (WxHxD)
1889.9 x 1083.5 x 77 mm
Stand (Basic) (WxD)
1411 x 326 mm
Stand (Minimum) (WxD)
954 x 326 mm
VESA Spec
400 x 300 mm
Weight
Package Weight
40.7 kg
Set Weight with Stand
29.2 kg
Set Weight without Stand
28.7 kg
Accessory
Remote Controller Model
TM2360E
User Manual
Yes
Full Motion Slim Wall Mount (Y22)
Yes
Webcam Support
Yes
Zigbee / Thread Module
Dongle Support
Power Cable
Yes
"""

spec_text_input = st.text_area("ข้อความสเปคทีวี:", default_spec_text, height=400)

st.write("ป้อนหัวข้อหมวดหมู่ที่ปรับแล้ว คั่นด้วยคอมมา (ตัวอย่าง: สเปค, ย่อ, ภาพรวม, Display):")
default_headers = "สเปค, ย่อ, ภาพรวม, Display, Video, Audio, Smart Service, Smart Feature, Game Feature, Tuner/Broadcasting, Connectivity, Design, Additional Feature, Accessibility, Power & Eco Solution, Dimension, Weight, Accessory"
category_headers_input = st.text_input("หัวข้อหมวดหมู่:", default_headers)

if st.button("สร้าง HTML"):
    if spec_text_input and category_headers_input:
        generated_html = generate_tv_spec_html(spec_text_input, category_headers_input)

        st.subheader("HTML Code Output:")
        st.code(generated_html, language="html")

        st.subheader("HTML Preview:")
        # Use st.components.v1.html for rendering full HTML documents
        # This isolates the HTML, preventing potential conflicts with Streamlit's styling
        st.components.v1.html(generated_html, height=800, scrolling=True)
    else:
        st.warning("โปรดใส่ข้อความสเปคและหัวข้อหมวดหมู่")

