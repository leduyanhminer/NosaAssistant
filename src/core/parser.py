import fitz

class DocumentParser:
    def __init__(self):
        pass
    
    def get_raw_text_pdf(self, file_path):
        results = []
        try:
            doc = fitz.open(self.file_path)
            
            for page_num, page in enumerate(doc):
                text = page.get_text("text")
                clean_text = " ".join(text.split())
                if clean_text:
                    results.append({
                        "page": page_num + 1,
                        "content": clean_text
                    })
            doc.close()
            return results
        
        except Exception as e:
            print(f"Lỗi khi đọc file PDF: {e}")
            return []
    
    
