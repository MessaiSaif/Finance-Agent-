import os
from typing import List, Optional
from pydantic import BaseModel, Field
import pdfplumber
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv

load_dotenv()

class InvoiceItem(BaseModel):
    description: str = Field(description="Description of the item")
    quantity: float = Field(description="Quantity of the item")
    unit_price: float = Field(description="Price per unit")
    total_price: float = Field(description="Total price for this item line")

class InvoiceData(BaseModel):
    invoice_id: str = Field(description="The invoice number or ID")
    date: str = Field(description="The date of the invoice (e.g., DD/MM/YYYY)")
    client_name: Optional[str] = Field(description="Name of the client or company")
    total_ht: float = Field(description="Total Hors Taxe (Total before tax)")
    tva_amount: float = Field(description="Total VAT/TVA amount")
    timbre_fiscal: float = Field(description="Timbre fiscal amount")
    total_ttc: float = Field(description="Total Toutes Taxes Comprises (Grand total)")
    items: List[InvoiceItem] = Field(description="List of items in the invoice")

from langchain_core.messages import HumanMessage
from PIL import Image

def extract_text_from_pdf(pdf_path):
    try:
        with pdfplumber.open(pdf_path) as pdf:
            text = ""
            for page in pdf.pages:
                text += page.extract_text() + "\n"
        return text
    except Exception as e:
        return ""

import base64

def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def process_invoice(file_path):
    """Processes an invoice (PDF or Image) using Gemini to extract structured data."""
    is_image = file_path.lower().endswith(('.png', '.jpg', '.jpeg'))
    llm = ChatGoogleGenerativeAI(model="gemini-flash-lite-latest", temperature=0)
    structured_llm = llm.with_structured_output(InvoiceData)
    
    try:
        if is_image:
            # Encode image to base64 for secure transfer
            b64_image = encode_image(file_path)
            mime_type = "image/png" if file_path.lower().endswith('.png') else "image/jpeg"
            
            message = HumanMessage(
                content=[
                    {"type": "text", "text": "Extract structured data from this invoice image. If a value is missing, use reasonable defaults or 0."},
                    {"type": "image_url", "image_url": f"data:{mime_type};base64,{b64_image}"}
                ]
            )
            result = structured_llm.invoke([message])
        else:
            # Process PDF by extracting text first
            text = extract_text_from_pdf(file_path)
            if not text.strip():
                # Fallback: Treat PDF as image (OCR) if text extraction fails
                raise Exception("Could not extract text from PDF. Please ensure it's a valid document.")
                
            prompt = ChatPromptTemplate.from_messages([
                ("system", "You are an expert at extracting data from invoices. Extract the following information from the text provided. If a value is missing, use reasonable defaults or 0."),
                ("user", "{text}")
            ])
            chain = prompt | structured_llm
            result = chain.invoke({"text": text})
            
        return result.dict()
    except Exception as e:
        if "RESOURCE_EXHAUSTED" in str(e):
            raise Exception("API Quota exceeded. Please try again later or check your API plan.")
        raise Exception(f"Error processing invoice: {str(e)}")
