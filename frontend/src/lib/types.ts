export type AgentResponse = {
  success: boolean;
  message: string | null;
  error: string | null;
  data: Record<string, unknown>;
};


export type ToolApprovalStatus =
  | "pending"
  | "approved"
  | "rejected"
  | "executed";


export type ToolApproval = {
  id: string;
  organization_id: string;
  requested_by_user_id: string;
  conversation_id: string | null;
  tool_name: string;
  arguments: Record<string, unknown>;
  status: ToolApprovalStatus;
  reviewed_by_user_id: string | null;
  review_note: string | null;
  created_at: string;
  reviewed_at: string | null;
  executed_at: string | null;
};

export type TokenResponse = {
  access_token: string;
  token_type: string;
};


export type OrganizationMembership = {
  organization: {
    id: string;
    name: string;
  };
  role: string;
};
