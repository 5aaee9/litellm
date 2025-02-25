import { ColumnDef } from "@tanstack/react-table";
import { Badge, Grid, Icon } from "@tremor/react";
import { Tooltip } from "antd";
import { UserInfo } from "./types";
import { PencilAltIcon, TrashIcon } from "@heroicons/react/outline";

export const columns = (
  possibleUIRoles: Record<string, Record<string, string>>,
  handleEdit: (user: UserInfo) => void,
  handleDelete: (userId: string) => void,
): ColumnDef<UserInfo>[] => [
  {
    header: "User ID",
    accessorKey: "user_id",
    cell: ({ row }) => (
      <span className="text-xs">{row.original.user_id || "-"}</span>
    ),
  },
  {
    header: "User Email",
    accessorKey: "user_email",
    cell: ({ row }) => (
      <span className="text-xs">{row.original.user_email || "-"}</span>
    ),
  },
  {
    header: "Role",
    accessorKey: "user_role",
    cell: ({ row }) => (
      <span className="text-xs">
        {possibleUIRoles?.[row.original.user_role]?.ui_label || "-"}
      </span>
    ),
  },
  {
    header: "User Spend ($ USD)",
    accessorKey: "spend",
    cell: ({ row }) => (
      <span className="text-xs">
        {row.original.spend ? row.original.spend.toFixed(2) : "-"}
      </span>
    ),
  },
  {
    header: "User Max Budget ($ USD)",
    accessorKey: "max_budget",
    cell: ({ row }) => (
      <span className="text-xs">
        {row.original.max_budget !== null ? row.original.max_budget : "Unlimited"}
      </span>
    ),
  },
  {
    header: "API Keys",
    accessorKey: "key_count",
    cell: ({ row }) => (
      <Grid numItems={2}>
        {row.original.key_count > 0 ? (
          <Badge size="xs" color="indigo">
            {row.original.key_count} Keys
          </Badge>
        ) : (
          <Badge size="xs" color="gray">
            No Keys
          </Badge>
        )}
      </Grid>
    ),
  },
  {
    header: "Created At",
    accessorKey: "created_at",
    sortingFn: "datetime",
    cell: ({ row }) => (
      <span className="text-xs">
        {row.original.created_at ? new Date(row.original.created_at).toLocaleDateString() : "-"}
      </span>
    ),
  },
  {
    header: "Updated At",
    accessorKey: "updated_at",
    sortingFn: "datetime",
    cell: ({ row }) => (
      <span className="text-xs">
        {row.original.updated_at ? new Date(row.original.updated_at).toLocaleDateString() : "-"}
      </span>
    ),
  },
  {
    header: "Updated By",
    accessorKey: "updated_by",
    cell: ({ row }) => (
      <span className="text-xs">{row.original.updated_by || "-"}</span>
    ),
  },
  {
    id: "actions",
    header: "",
    cell: ({ row }) => (
      <div className="flex gap-2">
        <Icon
          icon={PencilAltIcon}
          size="sm"
          onClick={() => handleEdit(row.original)}
        />
        <Icon
          icon={TrashIcon}
          size="sm"
          onClick={() => handleDelete(row.original.user_id)}
        />
      </div>
    ),
  },
]; 