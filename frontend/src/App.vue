<script setup lang="ts">
import { onLaunch } from "@dcloudio/uni-app";

onLaunch(() => {
  // Gate the app behind the ledger lock if one is set.
  try {
    const locked = uni.getStorageSync("lix_need_unlock");
    if (locked) {
      uni.reLaunch({ url: "/pages/lock/lock" });
    }
  } catch (e) {
    // ignore
  }
});
</script>

<style>
/* ---------- Brand palette (喜鹊礼簿) ---------- */
page {
  --brand: #d7263d;
  --brand-deep: #a81728;
  --brand-soft: #fff1f1;
  --gold: #c9a14a;
  --ink: #2b2b33;
  --ink-2: #6b6b73;
  --line: #efe7df;
  --paper: #f6f1ec;
  --card: #ffffff;
  background-color: var(--paper);
  font-family: -apple-system, BlinkMacSystemFont, "PingFang SC", "Microsoft YaHei", sans-serif;
  color: var(--ink);
}

view,
text,
button,
input,
textarea {
  box-sizing: border-box;
}

/* ---------- Reusable utility classes ---------- */
.lx-card {
  background: var(--card);
  border-radius: 20rpx;
  padding: 28rpx;
  box-shadow: 0 6rpx 24rpx rgba(168, 23, 40, 0.06);
}

.lx-row {
  display: flex;
  align-items: center;
}
.lx-between {
  display: flex;
  align-items: center;
  justify-content: space-between;
}
.lx-muted {
  color: var(--ink-2);
  font-size: 26rpx;
}
.lx-title {
  font-size: 32rpx;
  font-weight: 600;
  color: var(--ink);
}

.lx-btn {
  background: var(--brand);
  color: #fff;
  border-radius: 999rpx;
  font-size: 30rpx;
  font-weight: 600;
  text-align: center;
  padding: 22rpx 0;
  border: none;
  line-height: 1.2;
}
.lx-btn::after { border: none; }
.lx-btn-ghost {
  background: var(--brand-soft);
  color: var(--brand);
}
.lx-btn-block { width: 100%; }

.lx-chip {
  display: inline-flex;
  align-items: center;
  padding: 12rpx 26rpx;
  border-radius: 999rpx;
  font-size: 26rpx;
  background: #f3eee8;
  color: var(--ink-2);
  margin-right: 16rpx;
}
.lx-chip.active {
  background: var(--brand);
  color: #fff;
}

.lx-tag {
  font-size: 22rpx;
  padding: 4rpx 14rpx;
  border-radius: 8rpx;
  background: var(--brand-soft);
  color: var(--brand);
}

.lx-amount {
  font-weight: 700;
  color: var(--brand-deep);
}

.lx-empty {
  text-align: center;
  color: var(--ink-2);
  padding: 80rpx 0;
  font-size: 28rpx;
}
</style>
