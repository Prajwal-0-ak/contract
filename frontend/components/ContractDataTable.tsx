import React from "react";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Button } from "@/components/ui/button";
import { Pen } from "lucide-react";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
  DialogFooter,
  DialogClose,
} from "@/components/ui/dialog";
import { Label } from "@/components/ui/label";
import { Input } from "@/components/ui/input";

interface Field {
  name: string;
  page: number;
  value: string;
}

interface ContractDataTableProps {
  fields: Field[];
  handleEditField: (field: Field) => void;
  handleSaveEdit: (name: string, newValue: string, newPage: string) => void;
  editingField: Field | null;
  setEditingField: React.Dispatch<React.SetStateAction<Field | null>>;
  isDialogOpen: boolean;
  setIsDialogOpen: React.Dispatch<React.SetStateAction<boolean>>;
  closeDialogRef: React.RefObject<HTMLButtonElement>;
}

const ContractDataTable: React.FC<ContractDataTableProps> = ({
  fields,
  handleEditField,
  handleSaveEdit,
  editingField,
  setEditingField,
  isDialogOpen,
  setIsDialogOpen,
  closeDialogRef,
}) => {
  return (
    <div className="mt-8 overflow-x-auto">
      <h2 className="text-xl font-bold text-gray-900 mb-4">Contract Data</h2>
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>Field</TableHead>
            <TableHead>Value</TableHead>
            <TableHead>Page No</TableHead>
            <TableHead>Action</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {fields.map((field, index) => (
            <TableRow key={index} className="hover:bg-gray-100">
              <TableCell className="font-medium">{field.name}</TableCell>
              <TableCell>{field.value}</TableCell>
              <TableCell>{field.page || "N/A"}</TableCell>
              <TableCell>
                <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
                  <DialogTrigger asChild>
                    <Button
                      variant="ghost"
                      size="icon"
                      onClick={() => handleEditField(field)}
                    >
                      <Pen className="h-4 w-4" />
                    </Button>
                  </DialogTrigger>
                  <DialogContent className="sm:max-w-[425px]">
                    <DialogHeader>
                      <DialogTitle>Edit Field</DialogTitle>
                    </DialogHeader>
                    <form
                      onSubmit={(e) => {
                        e.preventDefault();
                        editingField &&
                          handleSaveEdit(
                            editingField.name,
                            editingField.value,
                            editingField.page.toString()
                          );
                      }}
                    >
                      <div className="grid gap-4 py-4">
                        <div className="grid grid-cols-4 items-center gap-4">
                          <Label htmlFor="name" className="text-right">
                            Name
                          </Label>
                          <Input
                            id="name"
                            value={editingField?.name || ""}
                            className="col-span-3"
                            disabled
                          />
                        </div>
                        <div className="grid grid-cols-4 items-center gap-4">
                          <Label htmlFor="value" className="text-right">
                            Value
                          </Label>
                          <Input
                            id="value"
                            value={editingField?.value || ""}
                            className="col-span-3"
                            onChange={(e) =>
                              setEditingField((prev) =>
                                prev
                                  ? {
                                      ...prev,
                                      value: e.target.value,
                                    }
                                  : null
                              )
                            }
                            required
                          />
                        </div>
                        <div className="grid grid-cols-4 items-center gap-4">
                          <Label htmlFor="page" className="text-right">
                            Page
                          </Label>
                          <Input
                            id="page"
                            type="number"
                            value={editingField?.page || ""}
                            className="col-span-3"
                            onChange={(e) =>
                              setEditingField((prev) =>
                                prev
                                  ? {
                                      ...prev,
                                      page: Number(e.target.value),
                                    }
                                  : null
                              )
                            }
                            min="1"
                            required
                            style={{ appearance: "textfield" }}
                          />
                        </div>
                      </div>
                      <DialogFooter>
                        <Button type="submit">Save changes</Button>
                      </DialogFooter>
                    </form>
                    <DialogClose ref={closeDialogRef} />
                  </DialogContent>
                </Dialog>
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </div>
  );
};

export default ContractDataTable;