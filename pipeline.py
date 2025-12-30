import os
from PIL import Image
from pydantic import BaseModel, Field
from google import genai
from typing import Optional, List, Union

# --- SCHEMA GIỮ NGUYÊN NHƯ CŨ ---
class ReceiptItem(BaseModel):
    name: str = Field(description="Full description of the item")
    quantity: float = Field(description="Quantity. If not visible, assume 1.")
    unit_price: Optional[float] = Field(description="Price per unit. Return 0 if not visible.")
    total_price: float = Field(description="Total line item price")

class ReceiptData(BaseModel):
    merchant_name: str = Field(description="Name of the store/merchant")
    merchant_address: Optional[str] = Field(description="Full address. Return 'Unknown' if not found.")
    invoice_id: Optional[str] = Field(description="Receipt number / Invoice ID.")
    date: str = Field(description="Transaction date in YYYY-MM-DD format.")
    subtotal: Optional[float] = Field(description="Total before tax.")
    tax_amount: Optional[float] = Field(description="Tax amount. Return 0 if not found.")
    total_amount: float = Field(description="The final grand total paid.")
    currency: str = Field(description="Currency code (e.g., VND, USD)")
    items: List[ReceiptItem] = Field(description="List of all purchased items")
    category: str = Field(description="Infer the category (e.g., Food, Taxi, Grocery).")

class ReceiptExtractor:
    def __init__(self, api_key: str, model_name: str = "gemini-2.5-flash"):
        if not api_key:
            raise ValueError("API Key is missing.")
        self.client = genai.Client(api_key=api_key)
        self.model_name = model_name

    def process(self, image_input: Union[str, Image.Image]) -> Optional[ReceiptData]:
        """Hỗ trợ cả đường dẫn file (str) và ảnh PIL (Image)"""
        try:
            image = None
            if isinstance(image_input, str):
                if not os.path.exists(image_input):
                    print(f"[Error] Image not found: {image_input}")
                    return None
                image = Image.open(image_input)
            elif isinstance(image_input, Image.Image):
                image = image_input
            else:
                return None

            prompt = "Analyze this receipt. Extract items, prices, totals, date, and merchant info."
            
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=[prompt, image],
                config=genai.types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=ReceiptData
                )
            )
            return response.parsed
        except Exception as e:
            print(f"[Pipeline Error] {str(e)}")
            return None