import { z } from "zod";

export const CommissionStatusEnum = z.enum([
  "PENDING",      // 예상 수익 (정산 대기)
  "APPROVED",     // 확정 수익 (정산 확정)
  "PAID",         // 지급 완료 (입금 완료)
  "CANCELLED",    // 주문 취소
  "REVERSED",     // 환수 / 반품 취소
  "REJECTED"      // 거절
]);
export type CommissionStatus = z.infer<typeof CommissionStatusEnum>;

// Revenue 공통 데이터 모델 (Brief 제22조)
export const RevenueMetricSchema = z.object({
  id: z.string(),
  network: z.string(),        // impact, awin, cj, rakuten, direct_gamsgo 등
  brand_id: z.string(),
  brand_name: z.string(),
  clicks: z.number().min(0).default(0),
  orders: z.number().min(0).default(0),
  sales_amount: z.number().min(0).default(0),
  sales_amount_krw: z.number().min(0).default(0),
  commission_pending: z.number().min(0).default(0),
  commission_approved: z.number().min(0).default(0),
  commission_paid: z.number().min(0).default(0),
  commission_reversed: z.number().min(0).default(0),
  currency: z.string().default("KRW"),
  period_start: z.string(),   // YYYY-MM-DD
  period_end: z.string(),     // YYYY-MM-DD
  last_sync: z.string()       // ISO-8601
});
export type RevenueMetric = z.infer<typeof RevenueMetricSchema>;

export interface RevenueSummary {
  total_clicks: number;
  total_orders: number;
  total_sales_krw: number;
  total_pending_krw: number;
  total_approved_krw: number;
  total_paid_krw: number;
  total_reversed_krw: number;
  conversion_rate: number;
  by_network: Record<string, { pending_krw: number; approved_krw: number; paid_krw: number }>;
  by_brand: Record<string, { clicks: number; orders: number; revenue_krw: number }>;
  last_updated: string;
}
