export type APIValidation = {
  is_valid: boolean;
  errors: string[];
  warnings: string[];
};

export type APIMeta = {
  request_id: string;
  method: string;
  page_count: number | null;
  timings_ms: Record<string, number>;
};

export type ExtractionResponse = {
  status: "completed" | "queued";
  job_id: string | null;
  data: unknown | null;
  validation: APIValidation | null;
  meta: APIMeta;
};
