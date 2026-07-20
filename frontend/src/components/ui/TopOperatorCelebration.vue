<template>
  <Teleport to="body">
    <transition name="top-op-fade">
      <div v-if="visible" class="top-op-overlay" @click="dismiss">
        <div v-if="stage === 'countdown'" class="top-op-countdown" @click.stop>
          <div class="top-op-countdown__label">Kunning eng zo'r operatori...</div>
          <transition name="top-op-count-pop" mode="out-in">
            <div :key="countdownValue" class="top-op-countdown__number">{{ countdownValue }}</div>
          </transition>
        </div>

        <template v-else-if="stage === 'reveal' && topOperator">
          <div class="top-op-fireworks" aria-hidden="true">
            <span v-for="burst in fireworkBursts" :key="burst.id" class="top-op-firework" :style="burst.style">
              <span v-for="p in 12" :key="p" class="top-op-firework__spark" :style="sparkStyle(p, burst.color)"></span>
            </span>
          </div>
          <div class="top-op-confetti" aria-hidden="true">
            <span v-for="n in 32" :key="n" class="top-op-confetti__piece" :style="confettiStyle(n)"></span>
          </div>

          <div class="top-op-card" @click.stop>
            <div class="top-op-card__glow"></div>
            <div class="top-op-card__crown">👑</div>
            <div class="top-op-card__eyebrow">Kunning eng zo'r operatori</div>
            <h2 class="top-op-card__name">{{ topOperator.operator_name }}</h2>
            <div class="top-op-card__stat">
              <strong>{{ topOperator.sale_count }}</strong>
              <span>ta sotuv bugun</span>
            </div>
            <p class="top-op-card__caption">Ajoyib natija! Shunday davom eting 🔥</p>
            <button type="button" class="top-op-card__close" @click="dismiss">Yopish</button>
          </div>
        </template>
      </div>
    </transition>
  </Teleport>
</template>

<script setup>
import { onBeforeUnmount, onMounted, ref } from 'vue'
import client from '../../api/client'

const visible = ref(false)
const stage = ref('countdown') // 'countdown' | 'reveal'
const countdownValue = ref(3)
const topOperator = ref(null)
let intervalId = null
let countdownTimer = null

const fireworkColors = ['#ff6b6b', '#4f7cff', '#22c55e', '#eab308', '#a855f7', '#06b6d4', '#f97316']
const fireworkBursts = [
  { id: 1, color: fireworkColors[0], style: { left: '18%', top: '28%', animationDelay: '0s' } },
  { id: 2, color: fireworkColors[1], style: { left: '78%', top: '22%', animationDelay: '0.35s' } },
  { id: 3, color: fireworkColors[2], style: { left: '50%', top: '38%', animationDelay: '0.7s' } },
  { id: 4, color: fireworkColors[4], style: { left: '30%', top: '58%', animationDelay: '1.1s' } },
  { id: 5, color: fireworkColors[5], style: { left: '68%', top: '55%', animationDelay: '1.5s' } },
]

function todayKey() {
  const d = new Date()
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`
}

function storageKey() {
  return `top-operator-celebration-shown-${todayKey()}`
}

function alreadyShownToday() {
  try {
    return localStorage.getItem(storageKey()) === '1'
  } catch (e) {
    return false
  }
}

function markShownToday() {
  try {
    localStorage.setItem(storageKey(), '1')
  } catch (e) {
    // ignore storage errors
  }
}

async function checkAndShow() {
  if (alreadyShownToday()) return
  const now = new Date()
  const hours = now.getHours()
  if (hours < 17) return
  try {
    const { data } = await client.get('stats/daily-top-operator/')
    if (data?.top_operator) {
      topOperator.value = data.top_operator
      markShownToday()
      startCountdown()
    }
  } catch (e) {
    // silent fail - celebration is non-critical
  }
}

function startCountdown() {
  stage.value = 'countdown'
  countdownValue.value = 3
  visible.value = true
  clearInterval(countdownTimer)
  countdownTimer = window.setInterval(() => {
    if (countdownValue.value <= 1) {
      clearInterval(countdownTimer)
      stage.value = 'reveal'
      return
    }
    countdownValue.value -= 1
  }, 800)
}

function dismiss() {
  visible.value = false
  stage.value = 'countdown'
  clearInterval(countdownTimer)
}

function confettiStyle(n) {
  const colors = ['#4f7cff', '#ff6b6b', '#22c55e', '#a855f7', '#f97316', '#eab308', '#06b6d4', '#ec4899']
  const left = (n * 31) % 100
  const delay = (n % 14) * 0.14
  const duration = 2.4 + (n % 5) * 0.3
  const color = colors[n % colors.length]
  return {
    left: `${left}%`,
    animationDelay: `${delay}s`,
    animationDuration: `${duration}s`,
    background: color,
  }
}

function sparkStyle(index, color) {
  const angle = (index / 12) * 360
  return {
    '--spark-angle': `${angle}deg`,
    background: color,
  }
}

onMounted(() => {
  checkAndShow()
  intervalId = window.setInterval(checkAndShow, 60000)
})

onBeforeUnmount(() => {
  if (intervalId) window.clearInterval(intervalId)
  if (countdownTimer) window.clearInterval(countdownTimer)
})
</script>

<style scoped>
.top-op-overlay {
  position: fixed;
  inset: 0;
  z-index: 9999;
  display: flex;
  align-items: center;
  justify-content: center;
  background: radial-gradient(circle at center, rgba(15, 23, 42, 0.55), rgba(15, 23, 42, 0.85));
  backdrop-filter: blur(6px);
  overflow: hidden;
}

.top-op-fade-enter-active { animation: topOpFadeIn 0.5s ease; }
.top-op-fade-leave-active { animation: topOpFadeIn 0.3s ease reverse; }
@keyframes topOpFadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

/* --- Countdown stage --- */
.top-op-countdown {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 18px;
}

.top-op-countdown__label {
  color: rgba(255, 255, 255, 0.85);
  font-size: 16px;
  font-weight: 700;
  letter-spacing: 0.04em;
}

.top-op-countdown__number {
  font-size: 140px;
  font-weight: 900;
  line-height: 1;
  color: white;
  text-shadow: 0 0 40px rgba(79, 124, 255, 0.7), 0 0 80px rgba(168, 85, 247, 0.5);
}

.top-op-count-pop-enter-active {
  animation: topOpCountPop 0.75s cubic-bezier(.34,1.56,.64,1);
}

@keyframes topOpCountPop {
  0% { transform: scale(0.3); opacity: 0; }
  60% { transform: scale(1.15); opacity: 1; }
  100% { transform: scale(1); opacity: 1; }
}

/* --- Fireworks --- */
.top-op-fireworks {
  position: absolute;
  inset: 0;
  overflow: hidden;
  pointer-events: none;
}

.top-op-firework {
  position: absolute;
  width: 0;
  height: 0;
  animation: topOpFireworkPop 1.4s ease-out infinite;
}

.top-op-firework__spark {
  position: absolute;
  width: 6px;
  height: 6px;
  border-radius: 50%;
  top: 0;
  left: 0;
  transform: rotate(var(--spark-angle)) translateY(0);
  animation: topOpSparkFly 1.4s ease-out infinite;
  opacity: 0;
}

@keyframes topOpFireworkPop {
  0%, 100% { opacity: 0; }
}

@keyframes topOpSparkFly {
  0% { transform: rotate(var(--spark-angle)) translateY(0) scale(1); opacity: 1; }
  70% { opacity: 1; }
  100% { transform: rotate(var(--spark-angle)) translateY(-70px) scale(0.3); opacity: 0; }
}

/* --- Confetti --- */
.top-op-confetti {
  position: absolute;
  inset: 0;
  overflow: hidden;
  pointer-events: none;
}

.top-op-confetti__piece {
  position: absolute;
  top: -10%;
  width: 10px;
  height: 16px;
  border-radius: 3px;
  opacity: 0.9;
  animation-name: topOpFall;
  animation-timing-function: linear;
  animation-iteration-count: infinite;
}

@keyframes topOpFall {
  0% { transform: translateY(-10vh) rotate(0deg); opacity: 0.9; }
  100% { transform: translateY(110vh) rotate(540deg); opacity: 0.3; }
}

/* --- Reveal card --- */
.top-op-card {
  position: relative;
  z-index: 2;
  width: min(92vw, 440px);
  padding: 44px 32px 36px;
  border-radius: 28px;
  text-align: center;
  background: linear-gradient(160deg, rgba(255,255,255,0.98), rgba(248,250,252,0.98));
  box-shadow: 0 40px 90px rgba(15, 23, 42, 0.45), 0 0 0 1px rgba(255,255,255,0.4) inset;
  animation: topOpPop 0.6s cubic-bezier(.34,1.56,.64,1);
  overflow: hidden;
}

@keyframes topOpPop {
  0% { transform: scale(0.7) translateY(30px); opacity: 0; }
  100% { transform: scale(1) translateY(0); opacity: 1; }
}

.top-op-card__glow {
  position: absolute;
  top: -60%;
  left: 50%;
  width: 260px;
  height: 260px;
  transform: translateX(-50%);
  background: radial-gradient(circle, rgba(251, 191, 36, 0.55), transparent 70%);
  filter: blur(10px);
  animation: topOpGlowPulse 2.4s ease-in-out infinite;
}

@keyframes topOpGlowPulse {
  0%, 100% { opacity: 0.6; transform: translateX(-50%) scale(1); }
  50% { opacity: 1; transform: translateX(-50%) scale(1.12); }
}

.top-op-card__crown {
  position: relative;
  font-size: 56px;
  line-height: 1;
  margin-bottom: 6px;
  animation: topOpBounce 1.6s ease-in-out infinite;
}

@keyframes topOpBounce {
  0%, 100% { transform: translateY(0) rotate(-4deg); }
  50% { transform: translateY(-8px) rotate(4deg); }
}

.top-op-card__eyebrow {
  position: relative;
  font-size: 12.5px;
  font-weight: 700;
  letter-spacing: .14em;
  text-transform: uppercase;
  color: #b45309;
  margin-bottom: 10px;
}

.top-op-card__name {
  position: relative;
  margin: 0 0 14px;
  font-size: 30px;
  font-weight: 800;
  background: linear-gradient(90deg, #4f7cff, #a855f7, #f97316);
  -webkit-background-clip: text;
  background-clip: text;
  color: transparent;
}

.top-op-card__stat {
  position: relative;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 2px;
  margin-bottom: 14px;
}

.top-op-card__stat strong {
  font-size: 44px;
  font-weight: 900;
  color: #0f172a;
  line-height: 1;
}

.top-op-card__stat span {
  font-size: 13px;
  color: #64748b;
  font-weight: 600;
}

.top-op-card__caption {
  position: relative;
  margin: 0 0 22px;
  color: #475569;
  font-size: 14.5px;
}

.top-op-card__close {
  position: relative;
  border: none;
  cursor: pointer;
  padding: 12px 28px;
  border-radius: 999px;
  font-weight: 700;
  font-size: 14px;
  color: white;
  background: linear-gradient(90deg, #4f7cff, #7c9dff);
  box-shadow: 0 12px 24px rgba(79, 124, 255, 0.35);
  transition: transform 0.15s ease;
}

.top-op-card__close:hover {
  transform: translateY(-2px);
}
</style>
