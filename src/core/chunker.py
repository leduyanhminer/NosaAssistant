from parser import DocumentParser

class Chunker:
    def __init__(self):
        self.parser = DocumentParser()

    def chunking_by_pages(self, file_path):
        all_chunks = []
        results = self.parser.get_raw_text_pdf(file_path=file_path)
        for res in results:
            all_chunks.append({
                "text": res['content'],
                "metadata": {
                    "page_no": res['page'],
                    "file_name": file_path.split('\\')[-1]
                }
            })
        return all_chunks
