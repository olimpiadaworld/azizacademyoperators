<template>
  <div class="lead-capture-page">
    <div class="lead-capture-card glass">
      <div class="lead-capture-card__hero">
        <div>
          <div class="eyebrow">Online lead</div>
          <h1>Ma'lumotlaringizni qoldiring</h1>
          <p class="lead-capture-subtitle">Telefon uchun moslashtirilgan forma. Ma'lumot yuborilgach siz bilan tez orada bog'lanamiz.</p>
        </div>
        <div class="lead-capture-card__badge glass-soft">
          <strong>AZIZ ACADEMY</strong>
          <span>Tezkor ro'yxatdan o'tish</span>
        </div>
      </div>

      <div v-if="successMessage" class="success-banner">{{ successMessage }}</div>
      <div v-if="errorMessage" class="error-banner">{{ errorMessage }}</div>

      <form class="lead-capture-form" @submit.prevent="submitLead">
        <label>Ism familya kiriting</label>
        <input v-model="form.full_name" class="input" placeholder="Masalan: Ali Valiyev" />

        <label>Yoshingizni kiriting</label>
        <input v-model="form.age" type="number" min="1" class="input" placeholder="Masalan: 16" />

        <label>tel1</label>
        <input v-model="form.phone1" class="input" placeholder="998901234567" />

        <label>tel2</label>
        <input v-model="form.phone2" class="input" placeholder="Ixtiyoriy" />

        <label>tel3</label>
        <input v-model="form.phone3" class="input" placeholder="Ixtiyoriy" />

        <label>Qaysi fanga qiziqasiz?</label>
        <input v-model="form.interest_subject" class="input" placeholder="Masalan: Ingliz tili" />

        <label>Qayerda yashaysiz?</label>
        <select v-model="form.region" class="select">
          <option disabled value="">Hududni tanlang</option>
          <option>Yangiyol</option>
          <option>Chinoz</option>
          <option>Pitiletka</option>
        </select>

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
  full_name: '',
  age: '',
  phone1: '',
  phone2: '',
  phone3: '',
  interest_subject: '',
  region: '',
})

function resetForm() {
  form.full_name = ''
  form.age = ''
  form.phone1 = ''
  form.phone2 = ''
  form.phone3 = ''
  form.interest_subject = ''
  form.region = ''
}

async function submitLead() {
  errorMessage.value = ''
  successMessage.value = ''
  if (!form.full_name || !form.age || !form.phone1 || !form.interest_subject || !form.region) {
    errorMessage.value = 'Barcha majburiy maydonlarni to‘ldiring.'
    return
  }
  loading.value = true
  try {
    await client.post('public/online-leads/', { ...form, age: Number(form.age) })
    successMessage.value = 'Ma’lumotlaringiz muvaffaqiyatli yuborildi'
    resetForm()
  } catch (error) {
    errorMessage.value = error?.response?.data?.detail || 'Yuborishda xatolik yuz berdi.'
  } finally {
    loading.value = false
  }
}
</script>
