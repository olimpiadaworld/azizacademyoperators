<template>
  <div class="login-page">
    <div class="login-page__bg login-page__bg--left"></div>
    <div class="login-page__bg login-page__bg--right"></div>
    <div class="login-page__dust"></div>

    <section class="login-card">
      <div class="login-card__shine"></div>
      <div class="login-card__header">
        <div class="login-card__intro">
          <div class="login-card__badge">Premium Lead CRM</div>
          <h1>Login</h1>
          <p>
            Admin, boshliq va operatorlar uchun yagona, tartibli va chiroyli
            boshqaruv tizimi.
          </p>
        </div>

        <button
          class="login-brand"
          type="button"
          title="Bosh sahifaga qaytish"
          aria-label="Bosh sahifaga qaytish"
          @click="goHome"
        >
          <div class="login-brand__icon">A</div>
          <div>
            <strong>AZIZ ACADEMY</strong>
            <span>Lead boshqaruvi</span>
          </div>
        </button>
      </div>

      <form class="login-form" @submit.prevent="submit">
        <label class="login-field">
          <span class="login-field__label">Login</span>
          <div class="login-field__control">
            <span class="login-field__icon" aria-hidden="true">
              <svg viewBox="0 0 24 24" fill="none">
                <path d="M12 12a4 4 0 1 0-4-4 4 4 0 0 0 4 4Zm0 2c-4.418 0-8 2.239-8 5v1h16v-1c0-2.761-3.582-5-8-5Z" />
              </svg>
            </span>
            <input
              v-model="form.username"
              type="text"
              autocomplete="username"
              placeholder="Username"
            />
          </div>
        </label>

        <label class="login-field">
          <span class="login-field__label">Parol</span>
          <div class="login-field__control">
            <span class="login-field__icon" aria-hidden="true">
              <svg viewBox="0 0 24 24" fill="none">
                <path d="M17 10V8a5 5 0 1 0-10 0v2" />
                <rect x="4" y="10" width="16" height="10" rx="3" />
              </svg>
            </span>
            <input
              v-model="form.password"
              :type="showPassword ? 'text' : 'password'"
              autocomplete="current-password"
              placeholder="Password"
            />
            <button
              type="button"
              class="login-field__toggle"
              @click="showPassword = !showPassword"
              :aria-label="showPassword ? 'Parolni yashirish' : 'Parolni ko\'rsatish'"
            >
              <svg v-if="!showPassword" viewBox="0 0 24 24" fill="none">
                <path d="M2 12s3.5-6 10-6 10 6 10 6-3.5 6-10 6S2 12 2 12Z" />
                <circle cx="12" cy="12" r="3" />
              </svg>
              <svg v-else viewBox="0 0 24 24" fill="none">
                <path d="M3 3l18 18" />
                <path d="M10.58 10.58A2 2 0 0 0 12 14a2 2 0 0 0 1.42-.58" />
                <path d="M9.88 5.09A11.48 11.48 0 0 1 12 5c6.5 0 10 7 10 7a17.6 17.6 0 0 1-3.06 3.67" />
                <path d="M6.23 6.23A17.75 17.75 0 0 0 2 12s3.5 7 10 7a11.62 11.62 0 0 0 5.08-1.09" />
              </svg>
            </button>
          </div>
        </label>

        <button class="login-submit" :disabled="auth.loading">
          {{ auth.loading ? 'Kirilmoqda...' : 'Kirish' }}
        </button>

        <div v-if="error" class="login-error">{{ error }}</div>
      </form>
    </section>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../../stores/auth'

const form = reactive({ username: '', password: '' })
const error = ref('')
const showPassword = ref(false)
const auth = useAuthStore()
const router = useRouter()

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
    router.push(getHomePath(user))
  } catch (e) {
    error.value =
      e.response?.data?.non_field_errors?.[0] ||
      e.response?.data?.detail ||
      'Login xato'
  }
}
</script>

<style scoped>
.login-page {
  min-height: 100vh;
  position: relative;
  overflow: hidden;
  display: grid;
  place-items: center;
  padding: 32px 18px;
  background:
    radial-gradient(circle at top left, rgba(108, 166, 255, 0.38), transparent 25%),
    radial-gradient(circle at right center, rgba(140, 196, 255, 0.28), transparent 28%),
    linear-gradient(180deg, #eef5ff 0%, #edf3fb 42%, #edf3fb 100%);
}

.login-page__bg {
  position: absolute;
  border-radius: 50%;
  filter: blur(24px);
  pointer-events: none;
}

.login-page__bg--left {
  width: 380px;
  height: 380px;
  left: -110px;
  top: 40px;
  background: radial-gradient(circle, rgba(93, 155, 255, 0.34), rgba(93, 155, 255, 0.02) 72%);
}

.login-page__bg--right {
  width: 440px;
  height: 440px;
  right: -120px;
  bottom: -10px;
  background: radial-gradient(circle, rgba(150, 205, 255, 0.32), rgba(150, 205, 255, 0.02) 70%);
}

.login-page__dust {
  position: absolute;
  inset: 0;
  pointer-events: none;
  opacity: 0.65;
  background-image:
    radial-gradient(circle at 10% 18%, rgba(255,255,255,0.9) 0 2px, transparent 3px),
    radial-gradient(circle at 16% 22%, rgba(255,255,255,0.75) 0 1.5px, transparent 3px),
    radial-gradient(circle at 84% 18%, rgba(255,255,255,0.75) 0 2px, transparent 3px),
    radial-gradient(circle at 88% 25%, rgba(255,255,255,0.82) 0 1.5px, transparent 3px),
    radial-gradient(circle at 92% 15%, rgba(255,255,255,0.75) 0 1px, transparent 3px),
    radial-gradient(circle at 8% 70%, rgba(255,255,255,0.75) 0 1px, transparent 2px),
    radial-gradient(circle at 93% 74%, rgba(255,255,255,0.7) 0 1.5px, transparent 3px);
}

.login-card {
  position: relative;
  width: min(920px, 100%);
  padding: 38px 42px 36px;
  border-radius: 34px;
  border: 1px solid rgba(255, 255, 255, 0.75);
  background: linear-gradient(135deg, rgba(255,255,255,0.92), rgba(242,247,255,0.7));
  box-shadow:
    0 40px 90px rgba(77, 124, 180, 0.12),
    inset 0 1px 0 rgba(255,255,255,0.8),
    inset 0 -1px 0 rgba(180, 204, 235, 0.28);
  backdrop-filter: blur(14px);
}

.login-card__shine {
  position: absolute;
  inset: 1px;
  border-radius: 33px;
  pointer-events: none;
  background: linear-gradient(125deg, rgba(255,255,255,0.5), transparent 36%, rgba(159, 199, 255, 0.12) 75%, transparent 100%);
}

.login-card__header {
  position: relative;
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 26px;
  margin-bottom: 34px;
}

.login-card__intro {
  max-width: 510px;
}

.login-card__badge {
  width: fit-content;
  margin-bottom: 24px;
  padding: 9px 18px;
  border-radius: 999px;
  border: 1px solid rgba(118, 155, 225, 0.24);
  background: rgba(132, 167, 238, 0.12);
  color: #5f86d9;
  font-size: 16px;
  font-weight: 700;
}

.login-card h1 {
  margin: 0 0 18px;
  color: #41557f;
  font-size: clamp(44px, 7vw, 66px);
  line-height: 0.95;
  letter-spacing: -0.04em;
}

.login-card p {
  margin: 0;
  color: #6f81a8;
  font-size: 17px;
  line-height: 1.65;
}

.login-brand {
  min-width: 250px;
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 18px 20px;
  border-radius: 28px;
  border: 1px solid rgba(255,255,255,0.68);
  background: linear-gradient(180deg, rgba(255,255,255,0.82), rgba(236,243,255,0.72));
  box-shadow:
    0 16px 32px rgba(111, 154, 219, 0.12),
    inset 0 1px 0 rgba(255,255,255,0.75);
  cursor: pointer;
  text-align: left;
  appearance: none;
  font: inherit;
}

.login-brand:hover {
  transform: translateY(-1px);
}

.login-brand__icon {
  width: 56px;
  height: 56px;
  border-radius: 50%;
  display: grid;
  place-items: center;
  font-size: 36px;
  color: #fff;
  background: linear-gradient(180deg, #8ec5ff, #4f85ff);
  box-shadow: 0 10px 24px rgba(79, 133, 255, 0.25);
}

.login-brand strong {
  display: block;
  margin-bottom: 4px;
  color: #556a92;
  font-size: 19px;
  font-weight: 800;
}

.login-brand span {
  color: #7f91b0;
  font-size: 16px;
}

.login-form {
  position: relative;
  display: grid;
  gap: 18px;
}

.login-field {
  display: grid;
  gap: 10px;
}

.login-field__label {
  color: #5d7bc1;
  font-size: 16px;
  font-weight: 600;
}

.login-field__control {
  position: relative;
}

.login-field__control input {
  width: 100%;
  height: 68px;
  border: 1px solid rgba(181, 198, 225, 0.54);
  border-radius: 22px;
  padding: 0 72px 0 64px;
  background: rgba(255,255,255,0.75);
  box-shadow:
    inset 0 1px 0 rgba(255,255,255,0.7),
    0 8px 20px rgba(153, 179, 218, 0.08);
  color: #61759f;
  font-size: 18px;
  transition: border-color .2s ease, box-shadow .2s ease, background .2s ease;
}

.login-field__control input::placeholder {
  color: #9daece;
}

.login-field__control input:focus {
  outline: none;
  border-color: rgba(88, 141, 237, 0.55);
  box-shadow:
    0 0 0 4px rgba(110, 163, 255, 0.12),
    inset 0 1px 0 rgba(255,255,255,0.7),
    0 16px 30px rgba(113, 156, 223, 0.12);
  background: rgba(255,255,255,0.88);
}

.login-field__icon,
.login-field__toggle {
  position: absolute;
  top: 50%;
  transform: translateY(-50%);
  display: grid;
  place-items: center;
  color: #86aef1;
}

.login-field__icon {
  left: 22px;
  width: 28px;
  height: 28px;
}

.login-field__icon svg,
.login-field__toggle svg {
  width: 24px;
  height: 24px;
  stroke: currentColor;
  stroke-width: 1.7;
  stroke-linecap: round;
  stroke-linejoin: round;
}

.login-field__toggle {
  right: 16px;
  width: 40px;
  height: 40px;
  border: 0;
  background: transparent;
  border-radius: 12px;
  cursor: pointer;
  transition: background .2s ease, color .2s ease;
}

.login-field__toggle:hover {
  color: #5d8cf1;
  background: rgba(132, 167, 238, 0.12);
}

.login-submit {
  margin-top: 6px;
  height: 70px;
  border: 0;
  border-radius: 24px;
  background: linear-gradient(90deg, #2f6cf8 0%, #58c0ff 100%);
  color: #fff;
  font-size: 22px;
  font-weight: 800;
  cursor: pointer;
  box-shadow:
    0 20px 40px rgba(62, 127, 255, 0.28),
    inset 0 1px 0 rgba(255,255,255,0.25);
  transition: transform .18s ease, box-shadow .18s ease, opacity .18s ease;
}

.login-submit:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow:
    0 24px 45px rgba(62, 127, 255, 0.32),
    inset 0 1px 0 rgba(255,255,255,0.25);
}

.login-submit:disabled {
  cursor: wait;
  opacity: 0.78;
}

.login-error {
  padding: 14px 16px;
  border-radius: 18px;
  border: 1px solid rgba(255, 126, 126, 0.24);
  background: rgba(255, 236, 236, 0.72);
  color: #c74a4a;
  font-weight: 600;
}

@media (max-width: 900px) {
  .login-card {
    padding: 28px 22px 24px;
    border-radius: 26px;
  }

  .login-card__header {
    flex-direction: column;
    align-items: stretch;
    margin-bottom: 24px;
  }

  .login-brand {
    min-width: 0;
    width: 100%;
  }
}

@media (max-width: 640px) {
  .login-page {
    padding: 18px 12px;
  }

  .login-card {
    padding: 20px 16px 18px;
    border-radius: 24px;
  }

  .login-card__badge {
    margin-bottom: 18px;
    font-size: 14px;
  }

  .login-card h1 {
    margin-bottom: 14px;
    font-size: 44px;
  }

  .login-card p,
  .login-brand span,
  .login-field__label {
    font-size: 15px;
  }

  .login-field__control input {
    height: 60px;
    padding-left: 56px;
    padding-right: 58px;
    font-size: 17px;
    border-radius: 18px;
  }

  .login-submit {
    height: 62px;
    border-radius: 20px;
    font-size: 20px;
  }

  .login-brand {
    padding: 16px;
    border-radius: 22px;
  }

  .login-brand__icon {
    width: 48px;
    height: 48px;
    font-size: 30px;
  }

  .login-brand strong {
    font-size: 17px;
  }
}
</style>
