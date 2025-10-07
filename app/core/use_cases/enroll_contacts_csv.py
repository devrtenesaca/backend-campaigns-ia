import base64
import csv
from io import StringIO
from typing import List, Dict, Any, Tuple
from app.core.domain.errors import ValidationError
from app.core.use_cases.enroll_contacts import EnrollContacts

class EnrollContactsCSV:
    """
    Caso de uso para enrolar contactos desde un archivo CSV en base64.
    El CSV debe tener columnas: phone, name, attributes
    """
    def __init__(self, enroll_contacts_uc: EnrollContacts):
        self.enroll_contacts_uc = enroll_contacts_uc

    def __call__(self, campaign_id: int, csv_base64: str, created_by: str = "system") -> Tuple[int, int]:
        try:
            csv_bytes = base64.b64decode(csv_base64)
            csv_str = csv_bytes.decode("utf-8")
        except Exception:
            raise ValidationError("Invalid base64 or encoding for CSV")

        reader = csv.DictReader(StringIO(csv_str))
        contacts: List[Dict[str, Any]] = []
        import json
        
        for row in reader:
            # Convierte attributes de string JSON a dict si corresponde
            attributes = row.get("attributes")
            if isinstance(attributes, str):
                try:
                    attributes = json.loads(attributes)
                except Exception:
                    attributes = {}
            contacts.append({
                "phone": row.get("phone"),
                "name": row.get("name"),
                "attributes": attributes,
                "created_by": created_by
            })
        if not contacts:
            raise ValidationError("CSV file is empty or invalid format")
        return self.enroll_contacts_uc(campaign_id, contacts, created_by)