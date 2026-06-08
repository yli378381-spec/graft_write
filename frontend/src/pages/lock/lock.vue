<script setup lang="ts">
import { ref } from "vue";
import { onShow } from "@dcloudio/uni-app";
import { api } from "@/utils/request";
import { BRAND } from "@/config";
import type { LockStatus } from "@/types";

const input = ref("");
const hint = ref<string | null>(null);

async function loadHint() {
  try {
    const s = await api.get<LockStatus>("/api/lock/status");
    hint.value = s.hint || null;
    if (!s.enabled) {
      // No lock set; go straight in.
      uni.reLaunch({ url: "/pages/index/index" });
    }
  } catch (e) {
    // ignore
  }
}

function tap(n: string) {
  if (input.value.length >= 6) return;
  input.value += n;
  if (input.value.length >= 4) verify();
}
function back() {
  input.value = input.value.slice(0, -1);
}

async function verify() {
  try {
    await api.post("/api/lock/verify", { password: input.value });
    uni.reLaunch({ url: "/pages/index/index" });
  } catch (e: any) {
    uni.showToast({ title: "密码错误", icon: "none" });
    input.value = "";
  }
}

const keys = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "", "0", "←"];

onShow(() => loadHint());
</script>

<template>
  <view class="lock">
    <image class="mascot" :src="BRAND.mascotImg" mode="aspectFit" />
    <text class="title">账本已锁定</text>
    <text class="sub">请输入密码查看 {{ BRAND.name }}</text>
    <text v-if="hint" class="hint">提示：{{ hint }}</text>

    <view class="dots">
      <view class="dot" :class="{ filled: input.length > i }" v-for="i in [0,1,2,3,4,5]" :key="i"></view>
    </view>

    <view class="pad">
      <view
        v-for="(k, idx) in keys" :key="idx"
        class="key" :class="{ empty: k === '' }"
        @tap="k === '←' ? back() : (k !== '' && tap(k))"
      >{{ k }}</view>
    </view>
  </view>
</template>

<style scoped>
.lock {
  min-height: 100vh; background: linear-gradient(180deg, #e0224a, #c8102e);
  display: flex; flex-direction: column; align-items: center; padding-top: 120rpx;
}
.mascot { width: 160rpx; height: 160rpx; }
.title { color: #fff; font-size: 40rpx; font-weight: 700; margin-top: 20rpx; }
.sub { color: rgba(255,255,255,0.85); font-size: 26rpx; margin-top: 12rpx; }
.hint { color: #ffe7b3; font-size: 24rpx; margin-top: 12rpx; }
.dots { display: flex; gap: 28rpx; margin: 60rpx 0; }
.dot { width: 28rpx; height: 28rpx; border-radius: 50%; border: 2rpx solid rgba(255,255,255,0.7); }
.dot.filled { background: #fff; }
.pad {
  width: 600rpx; display: flex; flex-wrap: wrap; gap: 24rpx; justify-content: center;
}
.key {
  width: 160rpx; height: 110rpx; background: rgba(255,255,255,0.16); border-radius: 20rpx;
  display: flex; align-items: center; justify-content: center; color: #fff; font-size: 44rpx; font-weight: 600;
}
.key.empty { background: transparent; }
</style>
