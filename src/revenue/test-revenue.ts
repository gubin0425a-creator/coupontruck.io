import { LocalPrivateRevenueStore } from "./provider.js";

async function run() {
  console.log("🧪 Testing Revenue Hub Provider & DB Isolation...");
  const store = new LocalPrivateRevenueStore();
  const syncRes = await store.syncNetwork("direct_gamsgo");
  if (!syncRes.success) throw new Error("Sync failed");

  const summary = await store.getSummary();
  console.log("✅ Revenue Summary:", {
    total_clicks: summary.total_clicks,
    total_orders: summary.total_orders,
    total_sales_krw: summary.total_sales_krw,
    total_pending_krw: summary.total_pending_krw,
    total_approved_krw: summary.total_approved_krw,
    conversion_rate: summary.conversion_rate.toFixed(2) + "%"
  });
  console.log("🎉 Revenue Hub tests completed successfully!\n");
}

run();
