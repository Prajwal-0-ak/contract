from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

# Initialize database engine for SOW (Statement of Work)
sow_engine = create_engine(
    settings.SOW_DATABASE_URL,
    connect_args={"check_same_thread": False}
)

# Initialize database engine for MSA (Master Service Agreement)
msa_engine = create_engine(
    settings.MSA_DATABASE_URL,
    connect_args={"check_same_thread": False}
)

# Configure session factory for SOW database interactions
SOWSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=sow_engine
)

# Configure session factory for MSA database interactions
MSASessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=msa_engine
)