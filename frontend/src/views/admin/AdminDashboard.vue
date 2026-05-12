<template>
  <div class="grid admin-page">
    <div class="hero glass panel">
      <div>
        <div class="eyebrow">Admin paneli</div>
        <h1 class="hero__title">CRM bo'yicha global nazorat</h1>
        <p class="hero__text">Boshliqlarni va Filial Rahbarlarini yarating, umumiy statistikani ko'ring va tizimdagi barcha lead holatlarini yuqoridan turib nazorat qiling.</p>
      </div>
      <div class="hero__actions">
        <button class="btn secondary" :disabled="allReportsDownloading" @click="downloadAllReportsExcel">{{ allReportsDownloading ? 'Yuklanmoqda...' : 'Barcha hisobotlarni yuklash' }}</button>
        <button class="btn secondary" @click="openFilialModal = true">Filial Rahbari yaratish</button>
        <button class="btn" @click="openBossModal = true">Boshliq yaratish</button>
      </div>
    </div>

    <div v-if="error" class="error-banner">{{ error }}</div>
    <div v-if="success" class="success-banner">{{ success }}</div>

    <ResponsiveSwiper
      v-if="isCompact"
      :items="summaryCards"
      eyebrow="Admin statistikasi"
      title="Asosiy ko'rsatkichlar"
      wrapper-class="glass-soft stats-mobile-swiper stats-mobile-swiper--admin swipe-elevated"
      :desktop-slides="2"
      :tablet-slides="2"
      :mobile-slides="1"
      :tablet-breakpoint="960"
    >
      <template #default="{ item }">
        <StatCard :title="item.title" :value="item.value" :subtitle="item.subtitle" />
      </template>
    </ResponsiveSwiper>

    <div v-else class="grid cards">
      <StatCard v-for="item in summaryCards" :key="item.title" :title="item.title" :value="item.value" :subtitle="item.subtitle" />
    </div>

    <div class="panel glass">
      <div class="section-head section-head--wrap">
        <div>
          <div class="eyebrow">Statuslar</div>
          <h3>Lead holatlari taqsimoti</h3>
        </div>
        <span class="badge">Yangilar: {{ stats.new || 0 }}</span>
      </div>
      <div class="status-grid compact-grid">
        <div class="status-overview-card status-sale"><div class="status-overview-card__top">Sotuv</div><strong>{{ stats.sale }}</strong></div>
        <div class="status-overview-card status-otkaz"><div class="status-overview-card__top">Atkaz</div><strong>{{ stats.otkaz }}</strong></div>
        <div class="status-overview-card status-open_number"><div class="status-overview-card__top">O'chiq Nomer</div><strong>{{ stats.open_number }}</strong></div>
        <div class="status-overview-card status-wrong_number"><div class="status-overview-card__top">Xato nomer</div><strong>{{ stats.wrong_number }}</strong></div>
        <div class="status-overview-card status-advice"><div class="status-overview-card__top">Maslahat</div><strong>{{ stats.advice }}</strong></div>
        <div class="status-overview-card status-other"><div class="status-overview-card__top">Boshqa</div><strong>{{ stats.other }}</strong></div>
      </div>
    </div>


    <div class="panel glass">
      <div class="section-head section-head--wrap">
        <div>
          <div class="eyebrow">Operator hisobotlari</div>
          <h3>Kunlik va 1 oylik natijalar</h3>
          <p>Admin kerakli boshliqni, operatorni va sanani tanlab, nechta sotuv va nechta atkaz bo‘lganini shu yerda ko‘radi.</p>
        </div>
        <span class="badge">{{ adminReportRangeLabel }}</span>
      </div>

      <div class="toolbar toolbar--responsive admin-report-toolbar">
        <select class="select" v-model="reportFilters.boss_id" @change="handleBossChange">
          <option value="">Barcha boshliqlar</option>
          <option v-for="boss in bosses" :key="`report-boss-${boss.id}`" :value="String(boss.id)">
            {{ boss.full_name || boss.username }}
          </option>
        </select>

        <select class="select" v-model="reportFilters.operator_id">
          <option value="">Barcha operatorlar</option>
          <option v-for="operator in reportOperators" :key="`report-operator-${operator.id}`" :value="String(operator.id)">
            {{ operator.name }}
          </option>
        </select>

        <div class="report-filter-field admin-report-field">
          <label>Kun</label>
          <input class="input" type="date" v-model="reportFilters.date" @change="reportFilters.month = ''" />
        </div>

        <div class="report-filter-field admin-report-field">
          <label>Oy</label>
          <input class="input" type="month" v-model="reportFilters.month" @change="reportFilters.date = ''" />
        </div>

        <button class="btn" :disabled="adminReportLoading" @click="fetchAdminOperatorReport">
          {{ adminReportLoading ? 'Yuklanmoqda...' : "Hisobotni ko'rish" }}
        </button>
        <button class="btn secondary" :disabled="allReportsDownloading" @click="downloadAllReportsExcel">
          {{ allReportsDownloading ? 'Excel tayyorlanmoqda...' : 'Barcha hisobotlarni yuklash' }}
        </button>
        <button class="btn secondary" :disabled="adminReportLoading" @click="loadCurrentMonthReport">1 oylik natija</button>
        <button class="btn ghost" :disabled="adminReportLoading" @click="clearAdminReportFilters">Tozalash</button>
      </div>

      <ResponsiveSwiper
        v-if="adminReportData && isCompact"
        :items="adminReportSummaryCards"
        eyebrow="Hisobot kartalari"
        title="Tanlangan oraliq bo'yicha natija"
        wrapper-class="glass-soft stats-mobile-swiper stats-mobile-swiper--report swipe-elevated"
        :desktop-slides="2"
        :tablet-slides="2"
        :mobile-slides="1"
        :tablet-breakpoint="960"
      >
        <template #default="{ item }">
          <StatCard :title="item.title" :value="item.value" :subtitle="item.subtitle" />
        </template>
      </ResponsiveSwiper>

      <div v-else-if="adminReportData" class="grid cards admin-report-cards">
        <StatCard v-for="item in adminReportSummaryCards" :key="item.title" :title="item.title" :value="item.value" :subtitle="item.subtitle" />
      </div>

      <div v-if="adminReportData" class="lead-toolbar-info lead-toolbar-info--wrap" style="margin-top: 12px;">
        <span class="badge">Operator: {{ adminReportData.selected_operator?.name || 'Barchasi' }}</span>
        <span class="badge">Online biriktirilgan: {{ adminReportData.summary.online_assigned }}</span>
        <span class="badge muted">Kunlik qatorlar: {{ adminReportData.daily.length }}</span>
      </div>

      <div class="report-section-grid" style="margin-top: 18px;">
        <section class="panel glass-soft">
          <div class="section-head section-head--wrap">
            <div>
              <div class="eyebrow">Operatorlar kesimi</div>
              <h3>Kim nechta sotuv va atkaz qilgan</h3>
            </div>
          </div>
          <div class="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>Boshliq</th>
                  <th>Operator</th>
                  <th>Biriktirildi</th>
                  <th>Sotuv</th>
                  <th>Atkaz</th>
                  <th>Maslahat</th>
                  <th>Boshqa</th>
                  <th>Jami action</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="row in adminOperatorRows" :key="`admin-report-row-${row.operator_id}`">
                  <td>{{ row.boss_name }}</td>
                  <td>{{ row.operator_name }}</td>
                  <td>{{ row.assigned_leads }}</td>
                  <td>{{ row.sale }}</td>
                  <td>{{ row.otkaz }}</td>
                  <td>{{ row.advice }}</td>
                  <td>{{ row.other }}</td>
                  <td>{{ row.actions_total }}</td>
                </tr>
                <tr v-if="!adminOperatorRows.length">
                  <td colspan="8" class="empty-state">Tanlangan filter bo‘yicha natija topilmadi.</td>
                </tr>
              </tbody>
            </table>
          </div>
        </section>

        <section class="panel glass-soft">
          <div class="section-head section-head--wrap">
            <div>
              <div class="eyebrow">Kunlik natija</div>
              <h3>Sana bo‘yicha hisob</h3>
            </div>
          </div>
          <div class="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>Sana</th>
                  <th>Sotuv</th>
                  <th>Atkaz</th>
                  <th>Xato</th>
                  <th>O‘chiq</th>
                  <th>Maslahat</th>
                  <th>Boshqa</th>
                  <th>Jami action</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="row in adminDailyRows" :key="`admin-day-${row.date}`">
                  <td>{{ formatInputDate(row.date) }}</td>
                  <td>{{ row.sale }}</td>
                  <td>{{ row.otkaz }}</td>
                  <td>{{ row.wrong_number }}</td>
                  <td>{{ row.open_number }}</td>
                  <td>{{ row.advice }}</td>
                  <td>{{ row.other }}</td>
                  <td>{{ row.actions_total }}</td>
                </tr>
                <tr v-if="!adminDailyRows.length">
                  <td colspan="8" class="empty-state">Kunlik natija topilmadi.</td>
                </tr>
              </tbody>
            </table>
          </div>
        </section>
      </div>
    </div>

    <div class="panel glass">
      <div class="section-head section-head--wrap">
        <div>
          <div class="eyebrow">Rahbarlar</div>
          <h3>Faol foydalanuvchilar ro'yxati</h3>
        </div>
      </div>
      <div class="table-wrap">
        <table>
          <thead>
            <tr>
              <th>Rol</th>
              <th>F.I.SH</th>
              <th>Login</th>
              <th>Telefon</th>
              <th>Filial</th>
              <th>Holati</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="person in leaders" :key="`${person.role}-${person.id}`">
              <td><span class="badge">{{ person.role === 'filial_rahbari' ? 'Filial Rahbari' : 'Boshliq' }}</span></td>
              <td>{{ person.full_name || '-' }}</td>
              <td>{{ person.username }}</td>
              <td>{{ person.phone || '-' }}</td>
              <td>{{ person.branch_name || '-' }}</td>
              <td><span class="badge">{{ person.is_active ? 'Faol' : 'Nofaol' }}</span></td>
            </tr>
            <tr v-if="!leaders.length">
              <td colspan="6" class="empty-state">Hali rahbar yaratilmagan.</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <div v-if="openFilialModal" class="modal-overlay" @click.self="closeFilialModal">
      <div class="modal-card glass">
        <div class="modal-card__head">
          <div>
            <div class="eyebrow">Yangi filial rahbari</div>
            <h3>Filial Rahbari yaratish</h3>
          </div>
          <button class="modal-close" @click="closeFilialModal">×</button>
        </div>
        <form class="grid" @submit.prevent="createFilialRahbari">
          <input v-model="filialForm.full_name" class="input" placeholder="To'liq ism" />
          <input v-model="filialForm.username" class="input" placeholder="Login" />
          <input v-model="filialForm.phone" class="input" placeholder="Telefon" />
          <input v-model="filialForm.branch_name" class="input" placeholder="Filial nomi (masalan: Niyozbosh)" />
          <input v-model="filialForm.password" type="password" class="input" placeholder="Parol" />
          <button class="btn full">Saqlash</button>
        </form>
      </div>
    </div>

    <div v-if="openBossModal" class="modal-overlay" @click.self="closeModal">
      <div class="modal-card glass">
        <div class="modal-card__head">
          <div>
            <div class="eyebrow">Yangi boshliq</div>
            <h3>Boshliq yaratish</h3>
          </div>
          <button class="modal-close" @click="closeModal">×</button>
        </div>
        <form class="grid" @submit.prevent="createBoss">
          <input v-model="form.full_name" class="input" placeholder="To'liq ism" />
          <input v-model="form.username" class="input" placeholder="Login" />
          <input v-model="form.phone" class="input" placeholder="Telefon" />
          <input v-model="form.password" type="password" class="input" placeholder="Parol" />
          <button class="btn full">Saqlash</button>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import client from '../../api/client'
import StatCard from '../../components/ui/StatCard.vue'
import ResponsiveSwiper from '../../components/ui/ResponsiveSwiper.vue'
import { useViewport } from '../../composables/useViewport'

const stats = reactive({ bosses: 0, filial_rahbarlari: 0, operators: 0, leads: 0, sale: 0, otkaz: 0, open_number: 0, wrong_number: 0, advice: 0, other: 0, new: 0 })
const bosses = ref([])
const filialRahbarlari = ref([])
const adminReportLoading = ref(false)
const allReportsDownloading = ref(false)
const adminReportData = ref(null)
const reportOperators = ref([])
const reportFilters = reactive({ boss_id: '', operator_id: '', date: '', month: '' })
const openBossModal = ref(false)
const openFilialModal = ref(false)
const error = ref('')
const success = ref('')
const form = reactive({ full_name: '', username: '', phone: '', password: '' })
const filialForm = reactive({ full_name: '', username: '', phone: '', branch_name: '', password: '' })
const { isCompact } = useViewport(960, 640)

const summaryCards = computed(() => ([
  { title: 'Boshliqlar', value: stats.bosses, subtitle: 'Tizimdagi boshliqlar' },
  { title: 'Filial Rahbarlari', value: stats.filial_rahbarlari, subtitle: 'Filial rahbarlari soni' },
  { title: 'Operatorlar', value: stats.operators, subtitle: 'Jami operatorlar' },
  { title: 'Sotuvlar', value: stats.sale, subtitle: 'Muvaffaqiyatli natija' },
]))
const leaders = computed(() => [...bosses.value, ...filialRahbarlari.value])
const adminOperatorRows = computed(() => adminReportData.value?.operator_rows || [])
const adminDailyRows = computed(() => adminReportData.value?.daily || [])
const adminReportSummaryCards = computed(() => {
  if (!adminReportData.value?.summary) return []
  const summary = adminReportData.value.summary
  return [
    { title: 'Biriktirilgan', value: summary.assigned_leads, subtitle: 'Tanlangan oraliqda' },
    { title: 'Sotuv', value: summary.sale, subtitle: 'Muvaffaqiyatli leadlar' },
    { title: 'Atkaz', value: summary.otkaz, subtitle: 'Qayta ishlashga o‘tganlar' },
    { title: 'Maslahat', value: summary.advice, subtitle: 'Maslahat berilganlar' },
    { title: 'Boshqa', value: summary.other, subtitle: 'Boshqa turdagi natija' },
    { title: 'Jami action', value: summary.actions_total, subtitle: 'Barcha holat o‘zgarishlari' },
  ]
})
const adminReportRangeLabel = computed(() => {
  const start = adminReportData.value?.range?.start_date
  const end = adminReportData.value?.range?.end_date
  if (!start && !end) return "Hozircha hisobot yo'q"
  if (start === end) return `${formatInputDate(start)} kuni`
  return `${formatInputDate(start)} - ${formatInputDate(end)}`
})

function resetMessages() {
  error.value = ''
  success.value = ''
}

function closeModal() {
  openBossModal.value = false
  form.full_name = ''
  form.username = ''
  form.phone = ''
  form.password = ''
}

function closeFilialModal() {
  openFilialModal.value = false
  filialForm.full_name = ''
  filialForm.username = ''
  filialForm.phone = ''
  filialForm.branch_name = ''
  filialForm.password = ''
}


function formatInputDate(value) {
  if (!value) return '-'
  const [year, month, day] = String(value).split('-')
  if (!year || !month || !day) return value
  return `${day}.${month}.${year}`
}


function getFilenameFromDisposition(disposition, fallback) {
  if (!disposition) return fallback
  const utfMatch = disposition.match(/filename\*=UTF-8''([^;]+)/i)
  if (utfMatch?.[1]) return decodeURIComponent(utfMatch[1].replace(/"/g, ''))
  const regularMatch = disposition.match(/filename="?([^";]+)"?/i)
  return regularMatch?.[1] || fallback
}

function downloadBlob(data, headers, fallbackName) {
  const blob = new Blob([data], { type: headers?.['content-type'] || 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' })
  const url = window.URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = getFilenameFromDisposition(headers?.['content-disposition'], fallbackName)
  document.body.appendChild(link)
  link.click()
  link.remove()
  window.URL.revokeObjectURL(url)
}

async function downloadAllReportsExcel() {
  allReportsDownloading.value = true
  resetMessages()
  try {
    const response = await client.get('admin/reports/all-excel/', { responseType: 'blob' })
    downloadBlob(response.data, response.headers, 'barcha_hisobotlar.xlsx')
    success.value = 'Barcha hisobotlar Excel formatda yuklandi.'
  } catch (e) {
    error.value = e.response?.data?.detail || 'Barcha hisobotlarni yuklashda xatolik yuz berdi.'
  } finally {
    allReportsDownloading.value = false
  }
}

async function fetchAdminOperatorReport() {
  adminReportLoading.value = true
  resetMessages()
  try {
    const params = {}
    if (reportFilters.boss_id) params.boss_id = reportFilters.boss_id
    if (reportFilters.operator_id) params.operator_id = reportFilters.operator_id
    if (reportFilters.date) {
      params.date = reportFilters.date
    } else if (reportFilters.month) {
      params.month = reportFilters.month
    }
    const { data } = await client.get('admin/operator-report/', { params })
    adminReportData.value = data
    reportOperators.value = data.operators || []
  } catch (e) {
    error.value = e.response?.data?.detail || 'Operator hisobotini yuklashda xatolik yuz berdi.'
  } finally {
    adminReportLoading.value = false
  }
}

async function handleBossChange() {
  reportFilters.operator_id = ''
  await fetchAdminOperatorReport()
}

async function loadCurrentMonthReport() {
  const now = new Date()
  reportFilters.date = ''
  reportFilters.month = `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}`
  await fetchAdminOperatorReport()
}

async function clearAdminReportFilters() {
  reportFilters.boss_id = ''
  reportFilters.operator_id = ''
  reportFilters.date = ''
  reportFilters.month = ''
  await fetchAdminOperatorReport()
}

async function fetchStats() {
  const { data } = await client.get('admin/statistics/')
  Object.assign(stats, data)
}

async function fetchBosses() {
  const { data } = await client.get('admin/bosses/')
  bosses.value = data.results || data
}

async function fetchFilialRahbarlari() {
  const { data } = await client.get('admin/filial-rahbarlari/')
  filialRahbarlari.value = data.results || data
}

async function createBoss() {
  resetMessages()
  try {
    await client.post('admin/bosses/', { ...form })
    success.value = 'Boshliq muvaffaqiyatli yaratildi.'
    closeModal()
    await fetchBosses()
    await fetchStats()
  } catch (e) {
    error.value = e.response?.data?.username?.[0] || e.response?.data?.detail || 'Boshliq yaratishda xatolik yuz berdi.'
  }
}

async function createFilialRahbari() {
  resetMessages()
  try {
    await client.post('admin/filial-rahbarlari/', { ...filialForm })
    success.value = 'Filial Rahbari muvaffaqiyatli yaratildi.'
    closeFilialModal()
    await fetchFilialRahbarlari()
    await fetchStats()
  } catch (e) {
    error.value = e.response?.data?.username?.[0] || e.response?.data?.detail || 'Filial Rahbari yaratishda xatolik yuz berdi.'
  }
}

onMounted(async () => {
  await fetchStats()
  await fetchBosses()
  await fetchFilialRahbarlari()
  await fetchAdminOperatorReport()
})
</script>
