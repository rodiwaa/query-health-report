"""Markdown node — convert uploaded file to markdown using docling."""

from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import PdfPipelineOptions
from docling.document_converter import DocumentConverter, PdfFormatOption

from src.graph.state import State

# FIXME: fixing latency — disable OCR and table structure models (not needed for digital PDFs)
_pipeline_options = PdfPipelineOptions()
_pipeline_options.do_ocr = False
_pipeline_options.do_table_structure = False

_converter = DocumentConverter(
    format_options={
        InputFormat.PDF: PdfFormatOption(pipeline_options=_pipeline_options)
    }
)


def markdown_node(state: State) -> dict:
    """Convert the uploaded file to markdown using docling."""
    result = _converter.convert(state.file_path)
    markdown = result.document.export_to_markdown()
    print(f"[markdown] converted {len(markdown)} chars")
    return {
        "raw_markdown": markdown,
        "messages": [{"role": "assistant", "content": "Converted to markdown."}],
    }
