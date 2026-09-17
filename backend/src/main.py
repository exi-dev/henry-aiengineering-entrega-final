"""Run from backend/ with: uvicorn src.main:app --reload --env-file .env"""

import logging

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from langfuse import observe

from src.agents.contextualization_agent import build_context_map
from src.agents.extraction_agent import extract_changes
from src.image_parser import parse_contract_image
from src.models import ContractChangeOutput

logger = logging.getLogger(__name__)
app = FastAPI(title="LegalMove")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4321"],
    allow_methods=["POST"],
    allow_headers=["Content-Type"],
)


@observe(name="validate_contract_changes")
def _validate_output(result: ContractChangeOutput) -> ContractChangeOutput:
    return ContractChangeOutput.model_validate(result)


@app.post("/api/compare", response_model=ContractChangeOutput)
@observe(name="compare_contracts")
def compare_contracts(
    original_image: UploadFile = File(...),
    amendment_image: UploadFile = File(...),
) -> ContractChangeOutput:
    try:
        try:
            original_text = parse_contract_image(
                original_image.file.read(), original_image.filename or ""
            )
            amendment_text = parse_contract_image(
                amendment_image.file.read(), amendment_image.filename or ""
            )
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

        context_map = build_context_map(original_text, amendment_text)
        result = extract_changes(context_map, original_text, amendment_text)
        return _validate_output(result)
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Error al comparar los documentos")
        raise HTTPException(
            status_code=500,
            detail="Error al procesar los documentos o validar el resultado de la comparación.",
        ) from exc
