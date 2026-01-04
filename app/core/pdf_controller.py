import fitz


class PdfController:
    def __init__(self, path):
        self.doc = fitz.open(path)
        self.page_index = 0

    def page_count(self):
        return len(self.doc)

    def render_page(self, zoom=1.0):
        page = self.doc[self.page_index]
        matrix = fitz.Matrix(zoom, zoom)
        return page.get_pixmap(matrix=matrix)

    def get_page_text(self):
        return self.doc[self.page_index].get_text()

    def get_page_images(self):
        page = self.doc[self.page_index]
        images = []
        for img in page.get_images(full=True):
            xref = img[0]
            base = self.doc.extract_image(xref)
            images.append(base["image"])
        return images
