import logging
from data.models.sql.inventory import ProductosDB, VariantesDB, TrazabilidadDB
from data.db.utils import get_session
from sqlalchemy import and_

db = get_session()