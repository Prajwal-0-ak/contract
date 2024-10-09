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
  onFieldClick: (page: number) => void;
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
  onFieldClick,
}) => {
  return (
    <div>
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>Field Name</TableHead>
            <TableHead>Value</TableHead>
            <TableHead>Page</TableHead>
            <TableHead>Action</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {fields.map((field) => (
            <TableRow 
              key={field.name} 
              className="cursor-pointer hover:bg-gray-100"
              onClick={() => field.page > 0 && onFieldClick(field.page)}
            >
              <TableCell>{field.name}</TableCell>
              <TableCell>{field.value}</TableCell>
              <TableCell>{field.page > 0 ? field.page : 'N/A'}</TableCell>
              <TableCell>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={(e) => {
                    e.stopPropagation();
                    handleEditField(field);
                  }}
                >
                  <Pen className="h-4 w-4" />
                </Button>
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>

      <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
        <DialogTrigger asChild>
          <Button
            variant="ghost"
            size="icon"
            onClick={() => handleEditField(editingField || fields[0])}
          >
            <Pen className="h-4 w-4" />
          </Button>
        </DialogTrigger>
        <DialogContent className="sm:max-w-[425px]">
          <DialogHeader>
            <DialogTitle className="text-black">Edit Field</DialogTitle>
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
                  className="col-span-3 text-black"
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
                  className="col-span-3 text-black"
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
                  className="col-span-3 text-black"
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
          <DialogClose className="text-black" ref={closeDialogRef} />
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default ContractDataTable;