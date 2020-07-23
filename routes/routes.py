# Retic
from retic import Router

# Controllers
import controllers.epub as epub

"""Define router instance"""
router = Router()

"""Define all paths - build"""
router.post("/build/from-html", epub.build_from_html)

"""Define all paths - downloads"""
router \
    .get("/downloads/:epub_id", epub.download_by_epub_id)
