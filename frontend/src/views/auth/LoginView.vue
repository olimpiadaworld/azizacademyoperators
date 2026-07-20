<template>
  <div class="login-page">
    <div class="login-page__orb login-page__orb--top"></div>
    <div class="login-page__orb login-page__orb--bottom"></div>
    <div class="login-page__dots login-page__dots--top"></div>
    <div class="login-page__line login-page__line--right"></div>
    <div class="login-page__line login-page__line--left"></div>

    <main class="login-shell">
      <section class="login-card" aria-label="Tizimga kirish oynasi">
        <button
          class="login-brand"
          type="button"
          title="Bosh sahifaga qaytish"
          aria-label="Bosh sahifaga qaytish"
          @click="goHome"
        >
          <span class="login-brand__logo" aria-hidden="true">
            <span class="login-brand__mark">A</span>
          </span>
          <span class="login-brand__text">
            <strong>AZIZ ACADEMY</strong>
            <small>Lead boshqaruvi</small>
          </span>
        </button>

        <div class="login-card__title">
          <h1>Tizimga kirish</h1>
          <p>Hisobingizga kirish uchun ma’lumotlaringizni kiriting</p>
        </div>

        <form class="login-form" @submit.prevent="submit">
          <label class="login-field">
            <span class="login-field__label">Login</span>
            <span class="login-field__control">
              <span class="login-field__icon" aria-hidden="true">
                <svg viewBox="0 0 24 24" fill="none">
                  <path d="M12 12.2a4.2 4.2 0 1 0 0-8.4 4.2 4.2 0 0 0 0 8.4Z" />
                  <path d="M4.7 20.2c.78-3.2 3.43-5.25 7.3-5.25s6.52 2.05 7.3 5.25" />
                </svg>
              </span>
              <input
                v-model.trim="form.username"
                type="text"
                autocomplete="username"
                placeholder="Loginni kiriting"
              />
            </span>
          </label>

          <label class="login-field">
            <span class="login-field__label">Parol</span>
            <span class="login-field__control">
              <span class="login-field__icon" aria-hidden="true">
                <svg viewBox="0 0 24 24" fill="none">
                  <path d="M7.7 10.4V8.2a4.3 4.3 0 0 1 8.6 0v2.2" />
                  <path d="M6.9 10.4h10.2a2.3 2.3 0 0 1 2.3 2.3v5.4a2.3 2.3 0 0 1-2.3 2.3H6.9a2.3 2.3 0 0 1-2.3-2.3v-5.4a2.3 2.3 0 0 1 2.3-2.3Z" />
                </svg>
              </span>
              <input
                v-model="form.password"
                :type="showPassword ? 'text' : 'password'"
                autocomplete="current-password"
                placeholder="Parolni kiriting"
              />
              <button
                type="button"
                class="login-field__toggle"
                @click="showPassword = !showPassword"
                :aria-label="showPassword ? 'Parolni yashirish' : 'Parolni ko\'rsatish'"
              >
                <svg v-if="!showPassword" viewBox="0 0 24 24" fill="none">
                  <path d="M3 12s3.2-5.6 9-5.6S21 12 21 12s-3.2 5.6-9 5.6S3 12 3 12Z" />
                  <path d="M12 14.5a2.5 2.5 0 1 0 0-5 2.5 2.5 0 0 0 0 5Z" />
                </svg>
                <svg v-else viewBox="0 0 24 24" fill="none">
                  <path d="m3.5 3.5 17 17" />
                  <path d="M10.75 10.75A2.3 2.3 0 0 0 12 14.3c.55 0 1.06-.2 1.45-.5" />
                  <path d="M8.7 5.85A9.5 9.5 0 0 1 12 5.3c5.85 0 9 6.7 9 6.7a15.4 15.4 0 0 1-3.1 3.9" />
                  <path d="M6.2 6.9A15 15 0 0 0 3 12s3.15 6.7 9 6.7c1.85 0 3.42-.48 4.72-1.17" />
                </svg>
              </button>
            </span>
          </label>

          <div class="login-options">
            <label class="login-check">
              <input v-model="rememberMe" type="checkbox" />
              <span></span>
              <b>Meni eslab qolish</b>
            </label>
            <button type="button" class="login-forgot" @click="error = 'Parolni tiklash uchun administratorga murojaat qiling.'">
              Parolni unutdingizmi?
            </button>
          </div>

          <button class="login-submit" :disabled="auth.loading">
            <span aria-hidden="true">
              <svg viewBox="0 0 24 24" fill="none">
                <path d="M9.2 5.2H5.8a2 2 0 0 0-2 2v9.6a2 2 0 0 0 2 2h3.4" />
                <path d="M14 7.6 18.4 12 14 16.4" />
                <path d="M18.2 12H8.6" />
              </svg>
            </span>
            {{ auth.loading ? 'Kirilmoqda...' : 'Kirish' }}
          </button>

          <div v-if="error" class="login-error">{{ error }}</div>
        </form>

        <div class="login-safe">
          <span class="login-safe__icon" aria-hidden="true">
            <svg viewBox="0 0 24 24" fill="none">
              <path d="M12 3.5 19 6v5.4c0 4.1-2.8 7.9-7 9.1-4.2-1.2-7-5-7-9.1V6l7-2.5Z" />
              <path d="m8.8 12.1 2.1 2.1 4.6-4.7" />
            </svg>
          </span>
          <span>
            <strong>Xavfsiz kirish</strong>
            <small>Ma’lumotlaringiz yuqori darajada himoyalangan</small>
          </span>
        </div>
      </section>

      <section class="login-visual" aria-hidden="true">
        <div class="visual-card visual-card--main">
          <span class="visual-avatar"></span>
          <span class="visual-line visual-line--one"></span>
          <span class="visual-line visual-line--two"></span>
          <span class="visual-line visual-line--three"></span>
          <span class="visual-password">
            <i></i><i></i><i></i><i></i>
          </span>
          <span class="visual-lock">
            <svg viewBox="0 0 24 24" fill="none">
              <path d="M8 10V8a4 4 0 0 1 8 0v2" />
              <rect x="6" y="10" width="12" height="10" rx="2.4" />
            </svg>
          </span>
        </div>
        <div class="visual-card visual-card--chart">
          <span></span><span></span><span></span>
        </div>
        <div class="visual-shield">
          <svg viewBox="0 0 90 100" fill="none">
            <path d="M45 5 80 18v25c0 25-14 42-35 52C24 85 10 68 10 43V18L45 5Z" />
            <path d="m26 50 13 13 27-30" />
          </svg>
        </div>
        <div class="visual-base"></div>
      </section>
    </main>

    <footer class="login-footer">
  © 2026 <strong>AZIZ ACADEMY.</strong> Barcha huquqlar himoyalangan. 
      <br />
  <span>Created by <strong>CODINGWITHULUGBEK</strong></span>
</footer>
  </div>
</template>

<script setup>
import { onMounted, reactive, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../../stores/auth'

const form = reactive({ username: '', password: '' })
const error = ref('')
const showPassword = ref(false)
const rememberMe = ref(true)
const auth = useAuthStore()
const router = useRouter()

onMounted(() => {
  const savedUsername = localStorage.getItem('rememberedUsername')
  if (savedUsername) {
    form.username = savedUsername
  }
})

watch(rememberMe, (value) => {
  if (!value) {
    localStorage.removeItem('rememberedUsername')
  }
})

function getHomePath(user) {
  if (user?.role === 'boss' || user?.role === 'filial_rahbari') {
    return { path: '/boss', query: { tab: 'leads' } }
  }
  return `/${user?.role || 'login'}`
}

function goHome() {
  router.push('/')
}

async function submit() {
  error.value = ''
  try {
    const user = await auth.login(form)
    if (rememberMe.value) {
      localStorage.setItem('rememberedUsername', form.username)
    }
    router.push(getHomePath(user))
  } catch (e) {
    error.value =
      e.response?.data?.non_field_errors?.[0] ||
      e.response?.data?.detail ||
      'Login yoki parol xato'
  }
}
</script>

<style scoped>
.login-page {
  min-height: 100vh;
  position: relative;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  justify-content: center;
  padding: 48px 24px 26px;
  background:
    radial-gradient(circle at 0 0, rgba(115, 163, 248, 0.34) 0 0, rgba(115, 163, 248, 0.2) 96px, transparent 98px),
    radial-gradient(circle at 0 0, rgba(74, 132, 232, 0.19) 0 156px, transparent 158px),
    radial-gradient(circle at 16% 76%, rgba(104, 226, 197, 0.28), transparent 24%),
    linear-gradient(135deg, #f9fcff 0%, #edf5ff 43%, #eaf4ff 100%);
  color: #111827;
}

.login-page__orb,
.login-page__line,
.login-page__dots {
  position: absolute;
  pointer-events: none;
}

.login-page__orb--top {
  width: 520px;
  height: 520px;
  top: -240px;
  right: -120px;
  border-radius: 50%;
  background: radial-gradient(circle, rgba(147, 187, 255, 0.18), transparent 67%);
}

.login-page__orb--bottom {
  width: 620px;
  height: 620px;
  left: -240px;
  bottom: -270px;
  border-radius: 50%;
  background: radial-gradient(circle, rgba(61, 214, 190, 0.12), transparent 66%);
}

.login-page__dots--top {
  top: 16px;
  right: 68px;
  width: 144px;
  height: 120px;
  opacity: .52;
  background-image: radial-gradient(circle, rgba(55, 121, 236, .45) 0 2px, transparent 2.8px);
  background-size: 22px 22px;
}

.login-page__line--right {
  right: 95px;
  top: 215px;
  width: 540px;
  height: 390px;
  border: 2px solid rgba(112, 190, 245, .26);
  border-left-color: transparent;
  border-bottom-color: transparent;
  border-radius: 50%;
  transform: rotate(-10deg);
}

.login-page__line--left {
  left: -70px;
  bottom: 42px;
  width: 620px;
  height: 270px;
  border: 2px solid rgba(255, 255, 255, .72);
  border-right-color: transparent;
  border-top-color: transparent;
  border-radius: 50%;
  transform: rotate(8deg);
}

.login-shell {
  position: relative;
  z-index: 1;
  width: min(1180px, 100%);
  margin: auto;
  display: grid;
  grid-template-columns: minmax(420px, 535px) minmax(320px, 1fr);
  align-items: center;
  justify-content: center;
  gap: 36px;
}

.login-card {
  position: relative;
  width: 100%;
  max-width: 535px;
  margin-left: auto;
  padding: 52px 46px 28px;
  border-radius: 24px;
  border: 1px solid rgba(218, 227, 242, .84);
  background: rgba(255, 255, 255, .92);
  box-shadow:
    0 30px 85px rgba(57, 89, 139, .13),
    0 1px 0 rgba(255, 255, 255, .9) inset;
  backdrop-filter: blur(18px);
}

.login-brand {
  width: fit-content;
  margin: 0 auto 48px;
  display: flex;
  align-items: center;
  gap: 18px;
  border: 0;
  background: transparent;
  padding: 0;
  font: inherit;
  text-align: left;
  cursor: pointer;
}

.login-brand__logo {
  width: 76px;
  height: 78px;
  position: relative;
  display: grid;
  place-items: center;
  flex: 0 0 auto;
  background: linear-gradient(145deg, #1a61ff, #0746dc);
  clip-path: polygon(50% 0, 90% 15%, 86% 62%, 50% 100%, 14% 62%, 10% 15%);
  box-shadow: 0 14px 25px rgba(20, 92, 255, .23);
}

.login-brand__logo::before {
  content: '';
  position: absolute;
  inset: 10px 14px 20px;
  border: 4px solid rgba(255, 255, 255, .9);
  border-right-width: 8px;
  border-bottom: 0;
  clip-path: polygon(0 0, 100% 0, 100% 36%, 60% 36%, 60% 56%, 100% 56%, 100% 100%, 0 100%);
  opacity: .92;
}

.login-brand__mark {
  position: relative;
  z-index: 1;
  color: #fff;
  font-size: 21px;
  font-weight: 900;
  letter-spacing: -.08em;
  transform: translateY(-1px);
}

.login-brand__text strong {
  display: block;
  color: #0755f2;
  font-size: clamp(28px, 3vw, 34px);
  line-height: 1;
  font-weight: 900;
  letter-spacing: -.04em;
}

.login-brand__text small {
  display: block;
  margin-top: 10px;
  color: #627292;
  font-size: 20px;
  font-weight: 500;
}

.login-card__title {
  margin-bottom: 30px;
}

.login-card__title h1 {
  margin: 0 0 12px;
  color: #111827;
  font-size: 24px;
  line-height: 1.2;
  font-weight: 850;
  letter-spacing: -.03em;
}

.login-card__title p {
  margin: 0;
  color: #7483a2;
  font-size: 16px;
  line-height: 1.5;
}

.login-form {
  display: grid;
  gap: 22px;
}

.login-field {
  display: grid;
  gap: 11px;
}

.login-field__label {
  color: #182235;
  font-size: 14px;
  line-height: 1;
  font-weight: 800;
}

.login-field__control {
  position: relative;
  display: block;
}

.login-field__control input {
  width: 100%;
  height: 56px;
  border: 1px solid #d8e1ef;
  border-radius: 12px;
  padding: 0 58px 0 48px;
  background: rgba(255, 255, 255, .92);
  color: #16233a;
  font-size: 16px;
  font-weight: 600;
  outline: none;
  box-shadow: 0 4px 14px rgba(63, 94, 139, .04);
  transition: border-color .18s ease, box-shadow .18s ease, background .18s ease;
}

.login-field__control input::placeholder {
  color: #8796b5;
  font-weight: 500;
}

.login-field__control input:focus {
  border-color: #2463ff;
  background: #fff;
  box-shadow: 0 0 0 4px rgba(36, 99, 255, .1), 0 15px 28px rgba(62, 105, 184, .09);
}

.login-field__icon,
.login-field__toggle {
  position: absolute;
  top: 50%;
  transform: translateY(-50%);
  display: grid;
  place-items: center;
  color: #7587aa;
}

.login-field__icon {
  left: 17px;
  width: 22px;
  height: 22px;
}

.login-field__icon svg,
.login-field__toggle svg,
.login-submit svg,
.login-safe svg,
.visual-lock svg {
  width: 100%;
  height: 100%;
  stroke: currentColor;
  stroke-width: 2;
  stroke-linecap: round;
  stroke-linejoin: round;
}

.login-field__toggle {
  right: 12px;
  width: 34px;
  height: 34px;
  border: 0;
  border-radius: 10px;
  background: transparent;
  cursor: pointer;
  color: #7385a8;
  transition: color .18s ease, background .18s ease;
}

.login-field__toggle:hover {
  color: #145cff;
  background: #eff5ff;
}

.login-options {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  margin-top: -4px;
}

.login-check {
  display: inline-flex;
  align-items: center;
  gap: 9px;
  cursor: pointer;
  user-select: none;
  color: #63708e;
}

.login-check input {
  position: absolute;
  opacity: 0;
  pointer-events: none;
}

.login-check span {
  width: 20px;
  height: 20px;
  display: grid;
  place-items: center;
  border-radius: 5px;
  border: 1px solid #c9d5ea;
  background: #fff;
  box-shadow: 0 3px 10px rgba(54, 97, 170, .08);
}

.login-check span::after {
  content: '';
  width: 9px;
  height: 5px;
  border-left: 2px solid #fff;
  border-bottom: 2px solid #fff;
  transform: rotate(-45deg) translateY(-1px);
  opacity: 0;
}

.login-check input:checked + span {
  border-color: #145cff;
  background: #145cff;
}

.login-check input:checked + span::after {
  opacity: 1;
}

.login-check b,
.login-forgot {
  font-size: 15px;
  font-weight: 500;
}

.login-forgot {
  border: 0;
  padding: 0;
  background: transparent;
  color: #075cff;
  cursor: pointer;
  white-space: nowrap;
}

.login-forgot:hover {
  text-decoration: underline;
}

.login-submit {
  height: 60px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 13px;
  border: 0;
  border-radius: 12px;
  background: linear-gradient(180deg, #1261ff 0%, #0049ed 100%);
  color: #fff;
  font-size: 18px;
  font-weight: 850;
  cursor: pointer;
  box-shadow: 0 18px 38px rgba(0, 82, 255, .23), inset 0 1px 0 rgba(255, 255, 255, .26);
  transition: transform .16s ease, box-shadow .16s ease, opacity .16s ease;
}

.login-submit span {
  width: 26px;
  height: 26px;
}

.login-submit:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 22px 42px rgba(0, 82, 255, .29), inset 0 1px 0 rgba(255, 255, 255, .26);
}

.login-submit:disabled {
  opacity: .72;
  cursor: wait;
}

.login-error {
  padding: 13px 15px;
  border-radius: 12px;
  border: 1px solid rgba(236, 97, 97, .25);
  background: rgba(255, 237, 237, .9);
  color: #c24141;
  font-size: 14px;
  font-weight: 750;
}

.login-safe {
  margin-top: 38px;
  padding-top: 2px;
  display: flex;
  align-items: center;
  gap: 18px;
}

.login-safe__icon {
  width: 64px;
  height: 64px;
  display: grid;
  place-items: center;
  flex: 0 0 auto;
  border-radius: 14px;
  background: #f0f5ff;
  color: #065bff;
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, .75);
}

.login-safe__icon svg {
  width: 31px;
  height: 31px;
}

.login-safe strong {
  display: block;
  margin-bottom: 7px;
  color: #1d2433;
  font-size: 16px;
  font-weight: 850;
}

.login-safe small {
  display: block;
  color: #70809f;
  font-size: 14px;
  line-height: 1.35;
}

.login-visual {
  position: relative;
  min-height: 520px;
  margin-left: 8px;
}

.visual-card {
  position: absolute;
  border: 1px solid rgba(255, 255, 255, .72);
  background: linear-gradient(145deg, rgba(255,255,255,.78), rgba(218,233,255,.58));
  box-shadow: 0 30px 70px rgba(59, 111, 198, .16), inset 0 1px 0 rgba(255, 255, 255, .9);
  backdrop-filter: blur(12px);
}

.visual-card--main {
  width: 300px;
  height: 280px;
  top: 78px;
  left: 58px;
  border-radius: 34px;
  transform: rotate(8deg);
}

.visual-avatar {
  position: absolute;
  top: 49px;
  left: 55px;
  width: 64px;
  height: 64px;
  border-radius: 50%;
  background: linear-gradient(180deg, #8db7ff, #1f68f9);
  box-shadow: 0 12px 28px rgba(27, 104, 255, .28);
}

.visual-avatar::before,
.visual-avatar::after {
  content: '';
  position: absolute;
  left: 50%;
  transform: translateX(-50%);
  background: #fff;
}

.visual-avatar::before {
  top: 14px;
  width: 22px;
  height: 22px;
  border-radius: 50%;
}

.visual-avatar::after {
  bottom: 11px;
  width: 40px;
  height: 21px;
  border-radius: 20px 20px 10px 10px;
}

.visual-line {
  position: absolute;
  right: 45px;
  height: 15px;
  border-radius: 999px;
  background: rgba(255, 255, 255, .72);
}

.visual-line--one {
  top: 62px;
  width: 118px;
}

.visual-line--two {
  top: 96px;
  width: 126px;
}

.visual-line--three {
  top: 130px;
  width: 83px;
}

.visual-password {
  position: absolute;
  left: 26px;
  bottom: 46px;
  width: 215px;
  height: 68px;
  display: flex;
  align-items: center;
  gap: 15px;
  padding: 0 22px;
  border-radius: 20px;
  background: rgba(255,255,255,.85);
  box-shadow: 0 18px 34px rgba(78, 120, 191, .15);
}

.visual-password i {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  background: linear-gradient(180deg, #87b4ff, #2069ff);
}

.visual-lock {
  position: absolute;
  right: 24px;
  bottom: 58px;
  width: 27px;
  height: 27px;
  color: #5c8dff;
}

.visual-card--chart {
  left: -20px;
  bottom: 112px;
  width: 150px;
  height: 160px;
  display: flex;
  align-items: flex-end;
  gap: 13px;
  padding: 32px 28px;
  border-radius: 25px;
  transform: rotate(4deg);
}

.visual-card--chart span {
  width: 28px;
  border-radius: 12px;
  background: linear-gradient(180deg, #72ebec, #246dff);
  box-shadow: 0 10px 18px rgba(43, 117, 255, .18);
}

.visual-card--chart span:nth-child(1) { height: 63px; }
.visual-card--chart span:nth-child(2) { height: 82px; }
.visual-card--chart span:nth-child(3) { height: 116px; }

.visual-shield {
  position: absolute;
  left: 230px;
  bottom: 85px;
  width: 178px;
  height: 198px;
  filter: drop-shadow(0 25px 35px rgba(0, 142, 239, .22));
}

.visual-shield svg {
  width: 100%;
  height: 100%;
}

.visual-shield path:first-child {
  fill: url(#none);
  stroke: rgba(80, 190, 255, .62);
  stroke-width: 4;
}

.visual-shield path:first-child {
  fill: rgba(32, 190, 239, .34);
}

.visual-shield path:last-child {
  stroke: #fff;
  stroke-width: 9;
  stroke-linecap: round;
  stroke-linejoin: round;
}

.visual-base {
  position: absolute;
  left: 12px;
  bottom: 50px;
  width: 330px;
  height: 118px;
  border-radius: 50%;
  background: radial-gradient(ellipse at center, rgba(136, 188, 255, .26), rgba(136, 188, 255, .02) 72%);
}

.login-footer {
  position: relative;
  z-index: 1;
  margin-top: 32px;
  text-align: center;
  color: #667692;
  font-size: 14px;
}

.login-footer strong {
  color: #075cff;
}

@media (max-width: 1040px) {
  .login-shell {
    grid-template-columns: minmax(360px, 535px);
  }

  .login-card {
    margin: 0 auto;
  }

  .login-visual {
    display: none;
  }
}

@media (max-width: 620px) {
  .login-page {
    padding: 22px 14px 20px;
    justify-content: flex-start;
  }

  .login-page__dots--top,
  .login-page__line {
    display: none;
  }

  .login-shell {
    width: 100%;
    display: block;
  }

  .login-card {
    padding: 28px 18px 22px;
    border-radius: 20px;
  }

  .login-brand {
    margin-bottom: 34px;
    gap: 13px;
  }

  .login-brand__logo {
    width: 58px;
    height: 60px;
  }

  .login-brand__text strong {
    font-size: 24px;
  }

  .login-brand__text small {
    margin-top: 7px;
    font-size: 16px;
  }

  .login-card__title h1 {
    font-size: 22px;
  }

  .login-card__title p {
    font-size: 14px;
  }

  .login-options {
    align-items: flex-start;
    flex-direction: column;
    gap: 10px;
  }

  .login-submit {
    height: 56px;
    font-size: 17px;
  }

  .login-safe {
    margin-top: 28px;
    gap: 14px;
  }

  .login-safe__icon {
    width: 54px;
    height: 54px;
  }

  .login-footer {
    margin-top: 20px;
    font-size: 13px;
  }
}
</style>
