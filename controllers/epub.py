# Retic
from retic import Request, Response, Next

# Services
from retic.services.validations import validate_obligate_fields
from retic.services.responses import error_response_service, success_response_service
import services.epub.epub as epub


def build_from_html(req: Request, res: Response, next: Next):
    """Validate obligate params"""
    _validate = validate_obligate_fields({
        u'title': req.param('title'),
        u'sections': req.param('sections'),
    })

    """Check if has errors return a error response"""
    if _validate["valid"] is False:
        return res.bad_request(
            error_response_service(
                "The param {} is necesary.".format(_validate["error"])
            )
        )

    """Create book"""
    _book = epub.build_from_html(
        req.param('title'),
        req.param('cover'),
        req.param('sections'),
        req.param('binary_response'),
        req.param('resources'),
    )

    """Check if error exists"""
    if _book['valid'] is False:
        res.not_found(_book)

    """Transform data response"""
    _data_response = {
        u"book": _book['data'],
    }

    """Response to client"""
    res.ok(
        success_response_service(
            data=_data_response,
            msg="Book created."
        )
    )


def download_by_epub_id(req: Request, res: Response):
    """Download a file from a id"""

    _download_file = epub.get_download_from_storage(
        req.param("epub_id")
    )

    """Check if the file was found or response an error message"""
    if _download_file['valid'] is False:
        res.not_found(_download_file)
    else:
        """Response a file data to client"""
        res.set_status(200).send(_download_file['data'])
