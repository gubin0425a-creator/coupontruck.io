import fs from "fs";
import path from "path";
import { RevenueMetric, RevenueMetricSchema, RevenueSummary } from "./types.js";

const BASE_DIR = process.cwd();
// 격리된 비공개 저장소 (.gitignore 에 등록되어 공개 배포 금지)
const PRIVATE_DIR = path.join(BASE_DIR, "revenue_private");
const PRIVATE_DB_FILE = path.join(PRIVATE_DIR, "revenue_db.json");

/**
 * RevenueProvider 인터페이스 (Brief 제25조)
 * 추후 Supabase, Cloudflare D1, PostgreSQL 등으로 교체 가능한 추상화 계층
 */
export interface RevenueProvider {
  syncNetwork(networkId: string): Promise<{ success: boolean; recordsUpdated: number }>;
  recordMetric(metric: RevenueMetric): Promise<void>;
  getSummary(periodStart?: string, periodEnd?: string): Promise<RevenueSummary>;
  getMetricsByBrand(brandId: string): Promise<RevenueMetric[]>;
}

export class LocalPrivateRevenueStore implements RevenueProvider {
  constructor() {
    if (!fs.existsSync(PRIVATE_DIR)) {
      fs.makedirsSync ? fs.mkdirSync(PRIVATE_DIR, { recursive: true }) : fs.mkdirSync(PRIVATE_DIR);
    }
    if (!fs.existsSync(PRIVATE_DB_FILE)) {
      fs.writeFileSync(PRIVATE_DB_FILE, JSON.stringify([], null, 2), "utf-8");
    }
  }

  private loadAll(): RevenueMetric[] {
    try {
      return JSON.parse(fs.readFileSync(PRIVATE_DB_FILE, "utf-8"));
    } catch {
      return [];
    }
  }

  private saveAll(metrics: RevenueMetric[]) {
    fs.writeFileSync(PRIVATE_DB_FILE, JSON.stringify(metrics, null, 2), "utf-8");
  }

  async recordMetric(metric: RevenueMetric): Promise<void> {
    const validated = RevenueMetricSchema.parse(metric);
    const list = this.loadAll();
    const existingIdx = list.findIndex(m => m.id === validated.id);
    if (existingIdx >= 0) {
      list[existingIdx] = validated;
    } else {
      list.push(validated);
    }
    this.saveAll(list);
  }

  async syncNetwork(networkId: string): Promise<{ success: boolean; recordsUpdated: number }> {
    console.log(`📡 [Revenue Hub] 동기화 실행: 네트워크 [${networkId}]`);
    // MVP: Direct Partner (GamsGo) 및 시뮬레이션 지표 동기화
    const now = new Date().toISOString();
    const today = now.substring(0, 10);

    const sampleMetric: RevenueMetric = {
      id: `rev-${networkId}-${today}`,
      network: networkId,
      brand_id: "gamsgo",
      brand_name: "겜스고 (GamsGo)",
      clicks: 42,
      orders: 3,
      sales_amount: 54000,
      sales_amount_krw: 54000,
      commission_pending: 5400,
      commission_approved: 2700,
      commission_paid: 0,
      commission_reversed: 0,
      currency: "KRW",
      period_start: today,
      period_end: today,
      last_sync: now
    };

    await this.recordMetric(sampleMetric);
    return { success: true, recordsUpdated: 1 };
  }

  async getSummary(periodStart?: string, periodEnd?: string): Promise<RevenueSummary> {
    const all = this.loadAll();
    const filtered = all.filter(m => {
      if (periodStart && m.period_start < periodStart) return false;
      if (periodEnd && m.period_end > periodEnd) return false;
      return true;
    });

    let totalClicks = 0;
    let totalOrders = 0;
    let totalSales = 0;
    let totalPending = 0;
    let totalApproved = 0;
    let totalPaid = 0;
    let totalReversed = 0;
    const byNetwork: RevenueSummary["by_network"] = {};
    const byBrand: RevenueSummary["by_brand"] = {};

    for (const m of filtered) {
      totalClicks += m.clicks;
      totalOrders += m.orders;
      totalSales += m.sales_amount_krw;
      totalPending += m.commission_pending;
      totalApproved += m.commission_approved;
      totalPaid += m.commission_paid;
      totalReversed += m.commission_reversed;

      if (!byNetwork[m.network]) {
        byNetwork[m.network] = { pending_krw: 0, approved_krw: 0, paid_krw: 0 };
      }
      byNetwork[m.network].pending_krw += m.commission_pending;
      byNetwork[m.network].approved_krw += m.commission_approved;
      byNetwork[m.network].paid_krw += m.commission_paid;

      if (!byBrand[m.brand_id]) {
        byBrand[m.brand_id] = { clicks: 0, orders: 0, revenue_krw: 0 };
      }
      byBrand[m.brand_id].clicks += m.clicks;
      byBrand[m.brand_id].orders += m.orders;
      byBrand[m.brand_id].revenue_krw += (m.commission_approved + m.commission_paid);
    }

    return {
      total_clicks: totalClicks,
      total_orders: totalOrders,
      total_sales_krw: totalSales,
      total_pending_krw: totalPending,
      total_approved_krw: totalApproved,
      total_paid_krw: totalPaid,
      total_reversed_krw: totalReversed,
      conversion_rate: totalClicks > 0 ? (totalOrders / totalClicks) * 100 : 0,
      by_network: byNetwork,
      by_brand: byBrand,
      last_updated: new Date().toISOString()
    };
  }

  async getMetricsByBrand(brandId: string): Promise<RevenueMetric[]> {
    return this.loadAll().filter(m => m.brand_id === brandId);
  }
}
