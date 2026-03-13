"""
JSON Schema Validator
Ensures API responses match required schema for hackathon
"""

import json
from typing import Tuple, List
from datetime import datetime


PHARMACOGUARD_OUTPUT_SCHEMA = {
    "type": "object",
    "required": ["patient_id", "drug", "timestamp", "risk_assessment", "pharmacogenomic_profile", "clinical_recommendation", "llm_generated_explanation", "quality_metrics"],
    "properties": {
        "patient_id": {
            "type": "string"
        },
        "drug": {
            "type": "string",
            "enum": ["CODEINE", "WARFARIN", "CLOPIDOGREL", "SIMVASTATIN", "AZATHIOPRINE", "FLUOROURACIL"]
        },
        "timestamp": {
            "type": "string"
        },
        "risk_assessment": {
            "type": "object",
            "required": ["risk_label", "confidence_score", "severity"],
            "properties": {
                "risk_label": {
                    "type": "string",
                    "enum": ["Safe", "Adjust Dosage", "Toxic", "Ineffective", "Unknown"]
                },
                "confidence_score": {
                    "type": "number",
                    "minimum": 0,
                    "maximum": 1
                },
                "severity": {
                    "type": "string",
                    "enum": ["none", "mild", "moderate", "high", "critical"]
                }
            }
        },
        "pharmacogenomic_profile": {
            "type": "object",
            "required": ["primary_gene", "phenotype"],
            "properties": {
                "primary_gene": {
                    "type": "string"
                },
                "diplotype": {
                    "type": "string"
                },
                "phenotype": {
                    "type": "string",
                    "enum": ["PM", "IM", "NM", "RM", "URM"]
                },
                "detected_variants": {
                    "type": "array",
                    "items": {
                        "type": "object"
                    }
                }
            }
        },
        "clinical_recommendation": {
            "type": "object",
            "properties": {
                "action": {"type": "string"},
                "cpic_guideline": {"type": "string"},
                "monitoring": {"type": "string"}
            }
        },
        "llm_generated_explanation": {
            "type": "object",
            "properties": {
                "summary": {"type": "string"},
                "biological_mechanism": {"type": "string"},
                "variant_effects": {"type": "object"}
            }
        },
        "quality_metrics": {
            "type": "object",
            "properties": {
                "vcf_parsing_success": {"type": "boolean"},
                "variant_confidence": {"type": "number"},
                "completeness": {"type": "number"}
            }
        }
    }
}


def validate_output(response: dict) -> Tuple[bool, List[str]]:
    """
    Validate output JSON against required schema

    Args:
        response: Response dictionary to validate

    Returns:
        Tuple of (is_valid: bool, error_messages: list)
    """
    errors = []

    # Check required root fields
    required_fields = ["patient_id", "drug", "timestamp", "risk_assessment", "pharmacogenomic_profile", "clinical_recommendation", "llm_generated_explanation", "quality_metrics"]

    for field in required_fields:
        if field not in response:
            errors.append(f"Missing required field: {field}")
        elif response[field] is None:
            errors.append(f"Field '{field}' is null")

    # Validate field types
    if "drug" in response and response["drug"] not in ["CODEINE", "WARFARIN", "CLOPIDOGREL", "SIMVASTATIN", "AZATHIOPRINE", "FLUOROURACIL"]:
        errors.append(f"Invalid drug: {response['drug']}")

    # Validate risk_assessment
    if "risk_assessment" in response:
        risk = response["risk_assessment"]
        if not isinstance(risk, dict):
            errors.append("risk_assessment must be an object")
        else:
            if "risk_label" not in risk:
                errors.append("Missing risk_assessment.risk_label")
            elif risk["risk_label"] not in ["Safe", "Adjust Dosage", "Toxic", "Ineffective", "Unknown"]:
                errors.append(f"Invalid risk_label: {risk['risk_label']}")

            if "confidence_score" not in risk:
                errors.append("Missing risk_assessment.confidence_score")
            elif not isinstance(risk["confidence_score"], (int, float)):
                errors.append("confidence_score must be a number")
            elif not (0 <= risk["confidence_score"] <= 1):
                errors.append(f"confidence_score must be between 0 and 1, got {risk['confidence_score']}")

            if "severity" not in risk:
                errors.append("Missing risk_assessment.severity")
            elif risk["severity"] not in ["none", "mild", "moderate", "high", "critical"]:
                errors.append(f"Invalid severity: {risk['severity']}")

    # Validate pharmacogenomic_profile
    if "pharmacogenomic_profile" in response:
        profile = response["pharmacogenomic_profile"]
        if not isinstance(profile, dict):
            errors.append("pharmacogenomic_profile must be an object")
        else:
            if "primary_gene" not in profile:
                errors.append("Missing pharmacogenomic_profile.primary_gene")

            if "phenotype" not in profile:
                errors.append("Missing pharmacogenomic_profile.phenotype")
            elif profile["phenotype"] not in ["PM", "IM", "NM", "RM", "URM"]:
                errors.append(f"Invalid phenotype: {profile['phenotype']}")

            if "detected_variants" in profile and not isinstance(profile["detected_variants"], list):
                errors.append("detected_variants must be an array")

    # Validate llm_generated_explanation
    if "llm_generated_explanation" in response:
        exp = response["llm_generated_explanation"]
        if not isinstance(exp, dict):
            errors.append("llm_generated_explanation must be an object")
        else:
            if "summary" not in exp:
                errors.append("Missing llm_generated_explanation.summary")
            elif not exp["summary"]:
                errors.append("llm_generated_explanation.summary cannot be empty")

    # Validate quality_metrics
    if "quality_metrics" in response:
        metrics = response["quality_metrics"]
        if not isinstance(metrics, dict):
            errors.append("quality_metrics must be an object")

    return len(errors) == 0, errors


def ensure_schema_compliance(data: dict) -> dict:
    """
    Add missing fields with defaults to ensure compliance

    Args:
        data: Potentially incomplete response data

    Returns:
        Compliant response dictionary
    """
    compliant = data.copy()

    # Add timestamp if missing
    if "timestamp" not in compliant or not compliant["timestamp"]:
        compliant["timestamp"] = datetime.utcnow().isoformat() + "Z"

    # Ensure patient_id exists
    if "patient_id" not in compliant:
        compliant["patient_id"] = "PATIENT_UNKNOWN"

    # Ensure drug exists
    if "drug" not in compliant:
        compliant["drug"] = "UNKNOWN"

    # Ensure risk_assessment structure
    if "risk_assessment" not in compliant:
        compliant["risk_assessment"] = {}

    risk = compliant["risk_assessment"]
    if "risk_label" not in risk:
        risk["risk_label"] = "Unknown"
    if "confidence_score" not in risk:
        risk["confidence_score"] = 0.5
    if "severity" not in risk:
        risk["severity"] = "moderate"

    # Ensure pharmacogenomic_profile structure
    if "pharmacogenomic_profile" not in compliant:
        compliant["pharmacogenomic_profile"] = {}

    profile = compliant["pharmacogenomic_profile"]
    if "primary_gene" not in profile:
        profile["primary_gene"] = "UNKNOWN"
    if "phenotype" not in profile:
        profile["phenotype"] = "Unknown"
    if "detected_variants" not in profile:
        profile["detected_variants"] = []

    # Ensure clinical_recommendation structure
    if "clinical_recommendation" not in compliant:
        compliant["clinical_recommendation"] = {}

    clinical = compliant["clinical_recommendation"]
    if "action" not in clinical:
        clinical["action"] = ""
    if "cpic_guideline" not in clinical:
        clinical["cpic_guideline"] = ""

    # Ensure llm_generated_explanation structure
    if "llm_generated_explanation" not in compliant:
        compliant["llm_generated_explanation"] = {}

    exp = compliant["llm_generated_explanation"]
    if "summary" not in exp:
        exp["summary"] = "Clinical explanation unavailable"
    if "biological_mechanism" not in exp:
        exp["biological_mechanism"] = ""
    if "variant_effects" not in exp:
        exp["variant_effects"] = {}

    # Ensure quality_metrics structure
    if "quality_metrics" not in compliant:
        compliant["quality_metrics"] = {}

    metrics = compliant["quality_metrics"]
    if "vcf_parsing_success" not in metrics:
        metrics["vcf_parsing_success"] = True
    if "variant_confidence" not in metrics:
        metrics["variant_confidence"] = 0.5
    if "completeness" not in metrics:
        metrics["completeness"] = 0.5

    return compliant


def format_output_json(data: dict) -> str:
    """
    Format response data as compliant JSON

    Args:
        data: Response data

    Returns:
        Formatted JSON string
    """
    # Ensure compliance first
    compliant = ensure_schema_compliance(data)

    # Convert to JSON with nice formatting
    return json.dumps(compliant, indent=2)


def validate_and_fix(response: dict) -> Tuple[dict, List[str]]:
    """
    Validate response and auto-fix common issues

    Args:
        response: Response to validate

    Returns:
        Tuple of (fixed_response: dict, remaining_errors: list)
    """
    # First try to ensure compliance
    fixed = ensure_schema_compliance(response)

    # Then validate
    is_valid, errors = validate_output(fixed)

    return fixed, errors
