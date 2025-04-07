from typing import Any
from mistralai import Mistral
import os

client = Mistral(api_key=os.getenv('MISTRAL_API_KEY'))


class DocumentParserService:
    
    @classmethod
    def parse_pdf_to_markdown(cls, document_url: str, **kwargs: Any) -> str:
        """
        Synchronous version of parse method.
        
        Args:
            document_url: URL to the document to parse
            
        Returns:
            Extracted text from the document
        """
        include_image_base64 = kwargs.get('include_image_base64', False)
        ocr_response = client.ocr.process(
            model="mistral-ocr-latest",
            document={
                "type": "document_url",
                "document_url": document_url,
            },
            include_image_base64=include_image_base64,
        )
        
        markdown = '\n\n'.join([page.markdown for page in ocr_response.pages])
        
        return markdown
