import os
from .connection import sow_engine, msa_engine
from app.models.models import SOWContractBase, MSAContractBase

# Create all tables in the SOW database
SOWContractBase.metadata.create_all(bind=sow_engine)

# Retrieve the path to the SOW database
sow_db_path = sow_engine.url.database
if sow_db_path and os.path.exists(sow_db_path):
    # Set file permissions to be writable
    os.chmod(sow_db_path, 0o664)
    # Change file ownership to the current user and group
    os.chown(sow_db_path, os.getuid(), os.getgid())

# Create all tables in the MSA database
MSAContractBase.metadata.create_all(bind=msa_engine)

# Retrieve the path to the MSA database
msa_db_path = msa_engine.url.database
if msa_db_path and os.path.exists(msa_db_path):
    # Set file permissions to be writable
    os.chmod(msa_db_path, 0o664)
    # Change file ownership to the current user and group
    os.chown(msa_db_path, os.getuid(), os.getgid())