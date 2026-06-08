<script setup lang="ts">
import { ref } from "vue";
import { onShow } from "@dcloudio/uni-app";
import { api } from "@/utils/request";
import { REMINDER_KINDS, BLESSING_SCENES, labelOf, emojiOf } from "@/utils/constants";
import { todayStr, fmtDate, daysUntil } from "@/utils/format";
import type { Reminder, BlessingTemplate } from "@/types";

const tab = ref<"remind" | "bless">("remind");

// reminders
const reminders = ref<Reminder[]>([]);
const showForm = ref(false);
const f_title = ref("");
const f_kind = ref("event");
const f_date = ref(todayStr());

// blessings
const scene = ref("thanks_wedding");
const templates = ref<BlessingTemplate[]>([]);
const blessName = ref("");

async function loadReminders() {
  try {
    reminders.value = await api.get<Reminder[]>("/api/reminders");
  } catch (e: any) {
    uni.showToast({ title: e.message || "加载失败", icon: "none" });
  }
}
async function loadTemplates() {
  try {
    templates.value = await api.get<BlessingTemplate[]>("/api/blessings", { scene: scene.value });
  } catch (e: any) {
    uni.showToast({ title: e.message || "加载失败", icon: "none" });
  }
}

function pickScene(v: string) {
  scene.value = v;
  loadTemplates();
}

async function addReminder() {
  if (!f_title.value.trim()) {
    uni.showToast({ title: "请填写提醒标题", icon: "none" });
    return;
  }
  try {
    await api.post("/api/reminders", {
      title: f_title.value.trim(),
      kind: f_kind.value,
      remind_date: f_date.value,
    });
    f_title.value = "";
    showForm.value = false;
    uni.showToast({ title: "已添加提醒", icon: "success" });
    loadReminders();
  } catch (e: any) {
    uni.showToast({ title: e.message || "添加失败", icon: "none" });
  }
}

async function delReminder(r: Reminder) {
  const res = await uni.showModal({ title: "删除提醒", content: `删除「${r.title}」？` });
  if (!(res as any).confirm) return;
  await api.del(`/api/reminders/${r.id}`);
  loadReminders();
}

function copyBless(t: BlessingTemplate) {
  const text = t.content.replace("{name}", blessName.value || "");
  uni.setClipboardData({
    data: text,
    success: () => uni.showToast({ title: "已复制，去粘贴发送吧", icon: "none" }),
  });
}

function countdownText(dateStr: string) {
  const d = daysUntil(dateStr);
  if (d === 0) return "就是今天";
  if (d > 0) return `还有 ${d} 天`;
  return `已过 ${-d} 天`;
}

onShow(() => {
  loadReminders();
  loadTemplates();
});
</script>

<template>
  <view class="wrap">
    <view class="seg">
      <view class="seg-item" :class="{ active: tab === 'remind' }" @tap="tab = 'remind'">🔔 节点提醒</view>
      <view class="seg-item" :class="{ active: tab === 'bless' }" @tap="tab = 'bless'">💌 祝福语</view>
    </view>

    <!-- Reminders -->
    <block v-if="tab === 'remind'">
      <button class="lx-btn lx-btn-block" @tap="showForm = !showForm">
        {{ showForm ? "收起" : "＋ 新增提醒（生日 / 节日 / 喜事）" }}
      </button>

      <view v-if="showForm" class="lx-card form">
        <view class="field">
          <text class="label">提醒内容</text>
          <input class="input" v-model="f_title" placeholder="如：奶奶生日 / 给小李回礼" />
        </view>
        <view class="field">
          <text class="label">类型</text>
          <view class="opts">
            <view
              v-for="k in REMINDER_KINDS" :key="k.value"
              class="lx-chip" :class="{ active: f_kind === k.value }"
              @tap="f_kind = k.value"
            >{{ k.emoji }} {{ k.label }}</view>
          </view>
        </view>
        <view class="field">
          <text class="label">日期</text>
          <picker mode="date" :value="f_date" @change="(e:any) => f_date = e.detail.value">
            <view class="picker">{{ f_date }}</view>
          </picker>
        </view>
        <button class="lx-btn lx-btn-block" @tap="addReminder">保存提醒</button>
      </view>

      <view v-if="!reminders.length" class="lx-empty">还没有提醒，添加生日/节日/喜事，不再错过答谢时机 🎈</view>

      <view class="rem" v-for="r in reminders" :key="r.id">
        <view class="rem-icon">{{ emojiOf(REMINDER_KINDS, r.kind) }}</view>
        <view class="rem-main">
          <text class="rem-title">{{ r.title }}</text>
          <text class="lx-muted">{{ fmtDate(r.remind_date) }} · {{ labelOf(REMINDER_KINDS, r.kind) }}</text>
        </view>
        <view class="rem-right">
          <text class="countdown">{{ countdownText(r.remind_date) }}</text>
          <text class="del-x" @tap="delReminder(r)">删除</text>
        </view>
      </view>
    </block>

    <!-- Blessings -->
    <block v-else>
      <view class="bless-intro lx-card">
        <image class="mascot-sm" src="/static/ip/axi-mascot.svg" mode="aspectFit" />
        <view class="intro-text">
          <text class="lx-title">阿喜帮你写祝福</text>
          <text class="lx-muted">挑一个场景，填上称呼，一键复制即可发送。</text>
        </view>
      </view>

      <view class="field">
        <text class="label">称呼（选填，自动填入祝福语）</text>
        <input class="input" v-model="blessName" placeholder="如：张姐 / 王叔 / 小敏" />
      </view>

      <scroll-view class="filter" scroll-x>
        <view
          v-for="s in BLESSING_SCENES" :key="s.value"
          class="lx-chip" :class="{ active: scene === s.value }"
          @tap="pickScene(s.value)"
        >{{ s.label }}</view>
      </scroll-view>

      <view class="tpl" v-for="t in templates" :key="t.id">
        <view class="lx-between">
          <text class="tpl-title">{{ t.title }}</text>
          <text class="copy-btn" @tap="copyBless(t)">复制</text>
        </view>
        <text class="tpl-body">{{ t.content.replace("{name}", blessName || "（称呼）") }}</text>
      </view>
    </block>
  </view>
</template>

<style scoped>
.wrap { padding: 28rpx 32rpx 60rpx; }
.seg { display: flex; background: #f0e8e0; border-radius: 999rpx; padding: 6rpx; margin-bottom: 24rpx; }
.seg-item { flex: 1; text-align: center; padding: 18rpx 0; border-radius: 999rpx; font-size: 28rpx; color: var(--ink-2); }
.seg-item.active { background: #fff; color: var(--brand); font-weight: 700; box-shadow: 0 2rpx 10rpx rgba(0,0,0,0.06); }

.form { margin-top: 20rpx; display: flex; flex-direction: column; gap: 24rpx; }
.field { display: flex; flex-direction: column; gap: 14rpx; }
.label { font-size: 26rpx; color: var(--ink-2); }
.input { background: #f7f3ee; border-radius: 14rpx; padding: 22rpx 24rpx; font-size: 30rpx; }
.picker { background: #f7f3ee; border-radius: 14rpx; padding: 22rpx 24rpx; font-size: 30rpx; }
.opts { display: flex; flex-wrap: wrap; gap: 14rpx; }
.opts .lx-chip { margin-right: 0; }

.rem {
  display: flex; align-items: center; gap: 20rpx; background: var(--card);
  border-radius: 20rpx; padding: 24rpx; margin-top: 18rpx; box-shadow: 0 6rpx 24rpx rgba(168,23,40,0.05);
}
.rem-icon { font-size: 44rpx; }
.rem-main { flex: 1; display: flex; flex-direction: column; gap: 6rpx; }
.rem-title { font-size: 30rpx; font-weight: 600; }
.rem-right { display: flex; flex-direction: column; align-items: flex-end; gap: 10rpx; }
.countdown { font-size: 24rpx; color: var(--brand); font-weight: 600; }
.del-x { font-size: 22rpx; color: var(--ink-2); }

.bless-intro { display: flex; align-items: center; gap: 20rpx; margin-bottom: 24rpx; }
.mascot-sm { width: 96rpx; height: 96rpx; }
.intro-text { display: flex; flex-direction: column; gap: 8rpx; }
.filter { white-space: nowrap; padding: 18rpx 0; }
.tpl { background: var(--card); border-radius: 20rpx; padding: 24rpx; margin-bottom: 18rpx; box-shadow: 0 6rpx 24rpx rgba(168,23,40,0.05); }
.tpl-title { font-size: 28rpx; font-weight: 600; }
.copy-btn { background: var(--brand-soft); color: var(--brand); border-radius: 999rpx; padding: 10rpx 28rpx; font-size: 26rpx; }
.tpl-body { display: block; margin-top: 16rpx; font-size: 28rpx; color: #444; line-height: 1.6; }
</style>
