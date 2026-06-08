<script setup lang="ts">
import { ref } from "vue";
import { onShow } from "@dcloudio/uni-app";
import { api } from "@/utils/request";
import { BRAND } from "@/config";
import type { LockStatus, Stats } from "@/types";

const lock = ref<LockStatus>({ enabled: false });
const stats = ref<Stats | null>(null);

async function load() {
  try {
    [lock.value, stats.value] = await Promise.all([
      api.get<LockStatus>("/api/lock/status"),
      api.get<Stats>("/api/stats"),
    ]);
  } catch (e) {
    // ignore
  }
}

async function setLock() {
  const r = await uni.showModal({
    title: "设置密码锁",
    editable: true,
    placeholderText: "输入 4-6 位数字密码",
  });
  if (!(r as any).confirm) return;
  const pwd = ((r as any).content || "").trim();
  if (!/^\d{4,6}$/.test(pwd)) {
    uni.showToast({ title: "请输入4-6位数字", icon: "none" });
    return;
  }
  try {
    await api.post("/api/lock/set", { password: pwd });
    uni.setStorageSync("lix_need_unlock", true);
    uni.showToast({ title: "密码已开启", icon: "success" });
    load();
  } catch (e: any) {
    uni.showToast({ title: e.message || "设置失败", icon: "none" });
  }
}

async function disableLock() {
  const r = await uni.showModal({
    title: "关闭密码锁",
    editable: true,
    placeholderText: "输入当前密码以关闭",
  });
  if (!(r as any).confirm) return;
  const pwd = ((r as any).content || "").trim();
  try {
    await api.post("/api/lock/disable", { password: pwd });
    uni.setStorageSync("lix_need_unlock", false);
    uni.showToast({ title: "已关闭密码锁", icon: "success" });
    load();
  } catch (e: any) {
    uni.showToast({ title: e.message || "密码错误", icon: "none" });
  }
}

function goItems() {
  uni.navigateTo({ url: "/pages/items/items" });
}
function goStats() {
  uni.switchTab({ url: "/pages/stats/stats" });
}

function aboutIp() {
  uni.showModal({
    title: `吉祥物 · ${BRAND.mascot}`,
    content:
      "阿喜是一只衔着红包的小喜鹊。喜鹊报喜，自古是中式婚嫁的吉祥象征。它会陪你记好每一份心意，也会提醒你别忘了答谢与回礼。",
    showCancel: false,
  });
}
</script>

<template>
  <view class="wrap">
    <view class="profile">
      <image class="avatar" :src="BRAND.mascotImg" mode="aspectFit" />
      <view class="p-main">
        <text class="p-name">{{ BRAND.name }}</text>
        <text class="p-sub">基础版 · 免费</text>
      </view>
    </view>

    <view class="mini-stats lx-card">
      <view class="ms-item">
        <text class="ms-value">{{ stats?.total_count || 0 }}</text>
        <text class="ms-label">礼金笔数</text>
      </view>
      <view class="ms-divider"></view>
      <view class="ms-item">
        <text class="ms-value">{{ stats?.item_count || 0 }}</text>
        <text class="ms-label">实物礼</text>
      </view>
      <view class="ms-divider"></view>
      <view class="ms-item">
        <text class="ms-value">¥{{ Math.round(stats?.total_amount || 0) }}</text>
        <text class="ms-label">收礼总额</text>
      </view>
    </view>

    <view class="lx-card group">
      <view class="row" @tap="lock.enabled ? disableLock() : setLock()">
        <text class="row-icon">🔒</text>
        <view class="row-main">
          <text class="row-title">账本密码锁</text>
          <text class="lx-muted">{{ lock.enabled ? "已开启，点此关闭" : "未开启，点此设置" }}</text>
        </view>
        <text class="row-arrow">{{ lock.enabled ? "已开启" : "›" }}</text>
      </view>

      <view class="row" @tap="goItems">
        <text class="row-icon">🎁</text>
        <view class="row-main">
          <text class="row-title">实物礼登记</text>
          <text class="lx-muted">文字记录礼品名称</text>
        </view>
        <text class="row-arrow">›</text>
      </view>

      <view class="row" @tap="goStats">
        <text class="row-icon">📊</text>
        <view class="row-main">
          <text class="row-title">账单统计与导出</text>
          <text class="lx-muted">复制账单摘要分享</text>
        </view>
        <text class="row-arrow">›</text>
      </view>
    </view>

    <view class="lx-card group">
      <view class="row" @tap="aboutIp">
        <text class="row-icon">🐦</text>
        <view class="row-main">
          <text class="row-title">认识吉祥物「阿喜」</text>
          <text class="lx-muted">喜鹊报喜 · 记好每份心意</text>
        </view>
        <text class="row-arrow">›</text>
      </view>
    </view>

    <view class="upsell lx-card">
      <text class="up-title">想要更省心？</text>
      <text class="lx-muted">升级版支持 AI 语音/截图记账、双向人情账、AI 答谢文案；高级版还有婚礼现场互动与纪念影像。敬请期待。</text>
    </view>

    <view class="ver lx-muted">喜鹊礼簿 v0.1.0 · 基础版</view>
  </view>
</template>

<style scoped>
.wrap { padding: 28rpx 32rpx 60rpx; }
.profile { display: flex; align-items: center; gap: 24rpx; padding: 16rpx 8rpx 28rpx; }
.avatar { width: 128rpx; height: 128rpx; }
.p-main { display: flex; flex-direction: column; gap: 8rpx; }
.p-name { font-size: 38rpx; font-weight: 700; }
.p-sub { font-size: 24rpx; color: #fff; background: var(--brand); border-radius: 999rpx; padding: 4rpx 18rpx; align-self: flex-start; }

.mini-stats { display: flex; align-items: center; margin-bottom: 24rpx; }
.ms-item { flex: 1; display: flex; flex-direction: column; align-items: center; gap: 8rpx; }
.ms-value { font-size: 38rpx; font-weight: 800; color: var(--brand-deep); }
.ms-label { font-size: 24rpx; color: var(--ink-2); }
.ms-divider { width: 1px; height: 56rpx; background: var(--line); }

.group { padding: 8rpx 28rpx; margin-bottom: 24rpx; }
.row { display: flex; align-items: center; gap: 20rpx; padding: 28rpx 0; border-bottom: 1px solid var(--line); }
.row:last-child { border-bottom: none; }
.row-icon { font-size: 40rpx; }
.row-main { flex: 1; display: flex; flex-direction: column; gap: 6rpx; }
.row-title { font-size: 30rpx; font-weight: 600; }
.row-arrow { color: var(--ink-2); font-size: 28rpx; }

.upsell { margin-bottom: 24rpx; display: flex; flex-direction: column; gap: 12rpx; background: linear-gradient(160deg, #fff6f0, #fff1f1); }
.up-title { font-size: 30rpx; font-weight: 700; color: var(--brand-deep); }
.ver { text-align: center; margin-top: 16rpx; }
</style>
