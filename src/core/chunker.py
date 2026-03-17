from src.core.parser import DocumentParser
from pathlib import Path

class Chunker:
    def __init__(self):
        self.parser = DocumentParser()

    def chunking_by_pages(self, file_path):
        all_chunks = []
        path_obj = Path(file_path)
        results = self.parser.get_raw_text_pdf(file_path=str(path_obj))
        for res in results:
            all_chunks.append({
                "text": res['content'],
                "metadata": {
                    "page_no": res['page'],
                    "file_name": path_obj.name
                }
            })
        return all_chunks
