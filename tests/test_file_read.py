import io
import unittest
import zipfile
from pathlib import Path

from app import app
from officex import extract_office_images
from pdfx import convert_pdf


ROOT = Path(__file__).resolve().parents[1]


class NexcoreFileReadTests(unittest.TestCase):
    def test_app_is_local_file_read_service(self):
        self.assertEqual(app.title, "NexcoreFileRead")

    def test_pdf_pipeline_returns_structured_markdown(self):
        data = (ROOT / "samples" / "sample_formula.pdf").read_bytes()
        result = convert_pdf(data, None)
        self.assertGreater(len(result.markdown), 100)
        self.assertIn("## 第 1 页", result.markdown)
        self.assertFalse(result.is_scanned)

    def test_office_media_is_extracted_without_reencoding(self):
        image = (ROOT / "samples" / "sample_photo.png").read_bytes()
        buffer = io.BytesIO()
        with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as archive:
            archive.writestr("word/media/photo.png", image)
            archive.writestr("word/media/notes.txt", "not an image")
        images = extract_office_images(buffer.getvalue())
        self.assertEqual(len(images), 1)
        self.assertEqual(images[0].name, "photo.png")
        self.assertEqual(images[0].data, image)


if __name__ == "__main__":
    unittest.main()
