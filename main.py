import os
import sys
import argparse
import json
import textwrap
from dotenv import load_dotenv
from PIL import Image, ImageDraw

# Local imports
from pipeline import ReceiptExtractor
from eval import Evaluator

# --- CONFIGURATION ---
load_dotenv()
API_KEY = os.getenv("GOOGLE_API_KEY")

# ==========================================
# 0. HÀM FORMAT TEXT (CORE LOGIC)
# ==========================================
def generate_receipt_text(data):
    """
    Tạo format hóa đơn dạng text thuần (Monospace) cho cả CLI và UI.
    """
    lines = []
    width = 45 
    
    # 1. Header
    lines.append("=" * width)
    lines.append(" EXTRACTED RECEIPT DATA ".center(width))
    lines.append("=" * width)
    
    # 2. Meta info
    lines.append(f"MERCHANT:   {data.merchant_name}")
    
    # Xử lý Address: Tự động xuống dòng nếu quá dài
    addr = data.merchant_address if data.merchant_address else "Unknown"
    wrapped_addr = textwrap.wrap(addr, width=width - 12) 
    if wrapped_addr:
        lines.append(f"Address:    {wrapped_addr[0]}")
        for line in wrapped_addr[1:]:
            lines.append(f"            {line}")
    else:
         lines.append(f"Address:    {addr}")
    
    lines.append(f"Invoice ID: {data.invoice_id if data.invoice_id else 'N/A'}")
    lines.append(f"Date:       {data.date}")
    lines.append(f"Category:   {data.category}")
    
    # 3. Items Table
    lines.append("-" * width)
    header = f"{'Qty':<4} {'Description':<20} {'Unit Price':<10} {'Total':<10}"
    lines.append(header)
    lines.append("-" * width)
    
    # Items Rows
    for item in data.items:
        qty = f"{item.quantity}"
        
        name = item.name
        if len(name) > 19:
            name = name[:17] + ".."
            
        u_price = f"{item.unit_price:,.0f}" if item.unit_price is not None else "0"
        t_price = f"{item.total_price:,.0f}"
        
        line = f"{qty:<4} {name:<20} {u_price:<10} {t_price:<10}"
        lines.append(line)
        
    lines.append("-" * width)
    
    # 4. Footer / Totals
    sub = f"{data.subtotal:,.0f}" if data.subtotal is not None else "0"
    tax = f"{data.tax_amount:,.0f}" if data.tax_amount is not None else "0"
    total = f"{data.total_amount:,.0f}"
    
    lines.append(f"Subtotal:   {sub:>32}")
    lines.append(f"Tax:        {tax:>32}")
    lines.append(f"TOTAL:      {total:>28} {data.currency}")
    lines.append("=" * width)
    
    return "\n".join(lines)

# ==========================================
# 1. LOGIC GIAO DIỆN (STREAMLIT UI)
# ==========================================
def run_ui():
    import streamlit as st
    
    st.set_page_config(page_title="Receipt OCR", layout="centered")
    st.title("Receipt Scanner")
    
    with st.sidebar:
        st.header("Settings")
        current_key = API_KEY
        if not current_key:
            current_key = st.text_input("Google API Key", type="password")
            if not current_key:
                st.warning("Input API Key required.")
                st.stop()
        else:
            st.info("API Key loaded from env")
            
    uploaded_file = st.file_uploader("Upload Image", type=["jpg", "png", "jpeg"])

    if uploaded_file:
        image = Image.open(uploaded_file)
        st.image(image, caption="Preview", width=400)
        
        if st.button("Analyze Receipt", type="primary"):
            with st.spinner("Processing..."):
                try:
                    extractor = ReceiptExtractor(api_key=current_key)
                    result = extractor.process(image)
                    
                    if result:
                        tab_summary, tab_json, tab_eval = st.tabs(["Summary", "Raw JSON", "Evaluation"])
                        
                        with tab_summary:
                            receipt_text = generate_receipt_text(result)
                            st.text(receipt_text) 
                            
                        with tab_json:
                            # 1. Hiển thị JSON
                            json_str = result.model_dump_json(indent=4)
                            st.json(json_str)
                            
                            # 2. Nút Download (MỚI THÊM)
                            st.download_button(
                                label="Download JSON",
                                data=json_str,
                                file_name="extracted_receipt.json",
                                mime="application/json"
                            )
                            
                        with tab_eval:
                            _, report = Evaluator.validate(result)
                            st.write(f"Verdict: **{report['status']}**")
                            for check in report["checks"]:
                                status = "[PASS]" if check["passed"] else "[FAIL]"
                                st.write(f"**{status}** {check['rule']}")
                                if "info" in check:
                                    st.caption(f"Details: {check['info']}")

                except Exception as e:
                    st.error(f"Error: {e}")

# ==========================================
# 2. LOGIC DÒNG LỆNH (CLI)
# ==========================================
def run_cli():
    parser = argparse.ArgumentParser()
    parser.add_argument("image_path", nargs="?", default="sample_receipt.jpg")
    parser.add_argument("--output", default="output.json")
    args = parser.parse_args()
    
    input_path = args.image_path
    
    if input_path == "sample_receipt.jpg" and not os.path.exists(input_path):
        create_dummy_image_if_missing(input_path)

    if not os.path.exists(input_path):
        print(f"[ERROR] File '{input_path}' not found")
        return

    if not API_KEY:
        print("[ERROR] API Key missing")
        return

    print(f"[INFO] Processing: {input_path}...")
    try:
        extractor = ReceiptExtractor(api_key=API_KEY)
        result = extractor.process(input_path)
        
        if result:
            print("\n" + generate_receipt_text(result))
            
            with open(args.output, "w", encoding="utf-8") as f:
                f.write(result.model_dump_json(indent=4))
            print(f"\n[INFO] Saved result to {args.output}")
            
            print("-" * 45)
            print("EVALUATION REPORT")
            _, report = Evaluator.validate(result)
            for check in report["checks"]:
                status = "[PASS]" if check["passed"] else "[FAIL]"
                print(f"{status} {check['rule']}")
            print(f"VERDICT: {report['status']}")
            print("-" * 45)
            
    except Exception as e:
        print(f"[ERROR] {e}")

def create_dummy_image_if_missing(path):
    if os.path.exists(path): return
    img = Image.new('RGB', (400, 500), color='white')
    d = ImageDraw.Draw(img)
    d.text((20, 50), "DUMMY RECEIPT", fill='black')
    d.text((20, 100), "Total: 100", fill='black')
    img.save(path)

# ==========================================
# 3. ENTRY POINT
# ==========================================
if __name__ == "__main__":
    try:
        from streamlit.runtime.scriptrunner import get_script_run_ctx
        if get_script_run_ctx():
            run_ui()
        else:
            run_cli()
    except ImportError:
        run_cli()