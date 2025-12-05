import fitz  # PyMuPDF
import io
from sentence_transformers import SentenceTransformer, util
from src.utils.pdf_utils import get_page_content
import numpy as np
from PIL import Image
import hashlib

_model = None
DEFAULT_MODEL_NAME = 'all-MiniLM-L6-v2'


def _load_model(name=DEFAULT_MODEL_NAME):
    global _model
    if _model is None:
        _model = SentenceTransformer(name)
    return _model


def _is_blank_image(pil_image, threshold=250):
    try:
        gray = pil_image.convert('L')
        arr = np.array(gray)
        return arr.mean() > threshold
    except Exception:
        return False


def _hash_image(pil_image):
    try:
        b = pil_image.tobytes()
        return hashlib.sha256(b).hexdigest()
    except Exception:
        return None


def split_pdf_packet(pdf_bytes, similarity_threshold=0.6, consecutive_low_pages=2, model_name=DEFAULT_MODEL_NAME):
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")

    if doc.page_count == 0:
        return []

    loader = _load_model(model_name)

    page_contents = []
    page_embeddings = []
    image_hashes = []

    for i in range(doc.page_count):
        text, img = get_page_content(doc, i)
        page_contents.append((i, text, img))
        text_for_embedding = (text or '').strip()[:1500] or 'blank page'
        emb = loader.encode(text_for_embedding, convert_to_numpy=True)
        page_embeddings.append(emb)
        image_hashes.append(_hash_image(img) if img else None)

    similarities = []
    for i in range(len(page_embeddings) - 1):
        sim = util.cos_sim(page_embeddings[i], page_embeddings[i+1]).item()
        if image_hashes[i] and image_hashes[i] == image_hashes[i+1]:
            sim = max(sim, 0.98)
        similarities.append(sim)

    split_indices = [0]
    low_counter = 0
    for i, sim in enumerate(similarities):
        if sim < similarity_threshold:
            low_counter += 1
        else:
            low_counter = 0
        if low_counter >= consecutive_low_pages:
            split_page_num = (i + 1) - (consecutive_low_pages - 1)
            if split_page_num not in split_indices:
                split_indices.append(split_page_num)
            low_counter = 0

    logical_docs = []
    for idx in range(len(split_indices)):
        start = split_indices[idx]
        end = split_indices[idx+1] if idx+1 < len(split_indices) else len(page_contents)
        chunk = page_contents[start:end]
        if chunk:
            logical_docs.append(chunk)

    doc.close()
    return logical_docs
