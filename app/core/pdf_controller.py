from typing import Optional

import fitz


class PdfController:
    def __init__(self, path):
        self.path = path
        self.doc = fitz.open(path)
        self.page_index = 0

    def page_count(self):
        return len(self.doc)

    def render_page(self, zoom: float = 1.0):
        page = self.doc[self.page_index]
        matrix = fitz.Matrix(zoom, zoom)
        return page.get_pixmap(matrix=matrix)

    def get_page_text(self, page_ind: int = None):
        page_ind = page_ind or self.page_index
        return self.doc[page_ind].get_text()

    def get_pages_window(self, middle_page: Optional[int] = None, window_size: int = 2):
        middle_page = middle_page or self.page_index
        pages_content = dict()
        indexes = set()

        for page_ind in range(middle_page - window_size, middle_page + window_size):
            if 0 <= page_ind < self.page_count():
                current_page_content = {
                    "text": self.get_page_text(page_ind),
                    "images": self.get_page_images(page_ind),
                }
                pages_content[page_ind] = current_page_content
                indexes.add(page_ind)

        return {
            "indexes": indexes,
            "current_page_index": middle_page,
            "contents": pages_content,
        }

    def get_page_images(self, page_ind: int = None):
        page_ind = page_ind or self.page_index
        page = self.doc[page_ind]
        images = []
        for img in page.get_images(full=True):
            xref = img[0]
            base = self.doc.extract_image(xref)
            images.append(base["image"])
        return images

    def get_all_text(self, split_by_page: bool = False):
        texts = []
        for i in range(self.page_count()):
            texts.append(self.get_page_text(i))
        if not split_by_page:
            texts = "\n\n".join(texts)
        return texts
