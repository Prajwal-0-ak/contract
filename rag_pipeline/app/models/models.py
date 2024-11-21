
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Float
from sqlalchemy.ext.declarative import declarative_base

# Base for SOW contracts
SOWContractBase = declarative_base()

class SOWContract(SOWContractBase):
    """
    Database model for SOW Contracts.
    """
    __tablename__ = "sow_contracts"

    id = Column(Integer, primary_key=True, index=True)
    file_name = Column(String, index=True)
    upload_date = Column(DateTime)
    processed = Column(Boolean, default=False)

    # SOW specific fields
    client_company_name = Column(String)
    currency = Column(String)
    sow_start_date = Column(String)
    sow_end_date = Column(String)
    cola = Column(String)
    credit_period = Column(String)
    inclusive_or_exclusive_gst = Column(String)
    sow_value = Column(String)
    sow_no = Column(String)
    type_of_billing = Column(String)
    po_number = Column(String)
    amendment_no = Column(String)
    billing_unit_type_and_rate_cost = Column(String)
    particular_role_rate = Column(String)

# Base for MSA contracts
MSAContractBase = declarative_base()

class MSAContract(MSAContractBase):
    """
    Database model for MSA Contracts.
    """
    __tablename__ = "msa_contracts"

    id = Column(Integer, primary_key=True, index=True)
    file_name = Column(String, index=True)
    upload_date = Column(DateTime)
    processed = Column(Boolean, default=False)
    
    # MSA specific fields
    client_company_name = Column(String)
    currency = Column(String)
    msa_start_date = Column(String)
    msa_end_date = Column(String)
    info_security = Column(String)
    limitation_of_liability = Column(String)
    data_processing_agreement = Column(String)
    insurance_required = Column(String)
    type_of_insurance_required = Column(String)
    is_cyber_insurance_required = Column(String)
    cyber_insurance_amount = Column(String)
    is_workman_compensation_insurance_required = Column(String)
    workman_compensation_insurance_amount = Column(String)
    other_insurance_required = Column(String)
    other_insurance_amount = Column(String)