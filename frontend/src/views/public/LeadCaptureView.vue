<template>
  <div class="lead-capture-page">
    <div class="lead-capture-card glass">
      <div class="lead-capture-card__hero">
        <div>
          <div class="eyebrow">Online lead</div>
          <h1>Ma'lumotlaringizni qoldiring</h1>
          <p class="lead-capture-subtitle">Ma'lumot yuborilgach, boss panelidagi Online leadlar bo'limiga tushadi.</p>
        </div>
        <div class="lead-capture-card__badge glass-soft">
          <strong>AZIZ ACADEMY</strong>
          <span>Tezkor ro'yxatdan o'tish</span>
        </div>
      </div>

      <div v-if="successMessage" class="success-banner">{{ successMessage }}</div>
      <div v-if="errorMessage" class="error-banner">{{ errorMessage }}</div>

      <form class="lead-capture-form" @submit.prevent="submitLead">
        <label>T/SH</label>
        <input v-model="form.tsh" class="input" placeholder="Masalan: T/SH" />

        <label>Maktab</label>
        <input v-model="form.school" class="input" placeholder="Masalan: 25-maktab" />

        <label>Sinf</label>
        <input v-model="form.grade" class="input" placeholder="Masalan: 9-sinf" />

        <label>F.I.O</label>
        <input v-model="form.full_name" class="input" placeholder="Masalan: Ali Valiyev" />

        <label>Fan</label>
        <input v-model="form.subject" class="input" placeholder="Masalan: Ingliz tili" />

        <label>tel1</label>
        <input v-model="form.phone1" class="input" placeholder="998901234567" />

        <label>tel2</label>
        <input v-model="form.phone2" class="input" placeholder="Ixtiyoriy" />

        <label>tel3</label>
        <input v-model="form.phone3" class="input" placeholder="Ixtiyoriy" />

        <button class="btn full" :disabled="loading">{{ loading ? 'Yuborilmoqda...' : 'Yuborish' }}</button>
      </form>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue'
import client from '../../api/client'

const loading = ref(false)
const successMessage = ref('')
const errorMessage = ref('')
const form = reactive({
  tsh: '',
  school: '',
  grade: '',
  full_name: '',
  subject: '',
  phone1: '',
  phone2: '',
  phone3: '',
})

function resetForm() {
  form.tsh = ''
  form.school = ''
  form.grade = ''
  form.full_name = ''
  form.subject = ''
  form.phone1 = ''
  form.phone2 = ''
  form.phone3 = ''
}

async function submitLead() {
  errorMessage.value = ''
  successMessage.value = ''
  loading.value = true
  try {
    await client.post('public/online-leads/', {
      tsh: form.tsh,
      school: form.school,
      grade: form.grade,
      full_name: form.full_name,
      subject: form.subject,
      interest_subject: form.subject,
      phone1: form.phone1,
      phone2: form.phone2,
      phone3: form.phone3,
    })
    successMessage.value = 'Ma’lumotlaringiz muvaffaqiyatli yuborildi'
    resetForm()
  } catch (error) {
    errorMessage.value = error?.response?.data?.detail || 'Yuborishda xatolik yuz berdi.'
  } finally {
    loading.value = false
  }
}
</script>
