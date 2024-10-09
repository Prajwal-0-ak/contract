import React from "react";
import { Label } from "@/components/ui/label";
import { Input } from "@/components/ui/input";

interface ContractFormProps {
  formData: {
    remark: string;
    subContractClause: string;
  };
  handleInputChange: (e: React.ChangeEvent<HTMLInputElement>) => void;
}

const ContractForm: React.FC<ContractFormProps> = ({ formData, handleInputChange }) => {
  return (
    <form className="space-y-6 text-black">
      <div className="grid grid-cols-1 gap-y-6 gap-x-4 sm:grid-cols-2">
        <div>
          <Label htmlFor="remark">Remark</Label>
          <Input
            id="remark"
            name="remark"
            value={formData.remark}
            onChange={handleInputChange}
          />
        </div>
        <div>
          <Label htmlFor="subContractClause">Sub Contract Clause</Label>
          <Input
            id="subContractClause"
            name="subContractClause"
            value={formData.subContractClause}
            onChange={handleInputChange}
          />
        </div>
      </div>
    </form>
  );
};

export default ContractForm;