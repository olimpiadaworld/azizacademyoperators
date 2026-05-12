<template>
  <div class="grid operator-page operator-page--board">
    <div v-if="successMessage" class="success-banner">{{ successMessage }}</div>
    <div v-if="errorMessage" class="error-banner">{{ errorMessage }}</div>

    <div v-if="reminderAlerts.length || actionToast" class="reminder-fixed-stack">
      <div v-if="actionToast" class="reminder-fixed-card reminder-fixed-card--success">
        <button class="reminder-fixed-card__close" type="button" @click="hideActionToast">×</button>
        <div class="reminder-fixed-card__eyebrow">Eslatma</div>
        <h3>Vaqt saqlandi</h3>
        <p>{{ actionToast.message }}</p>
      </div>
      <div v-for="alert in reminderAlerts" :key="alert.key" class="reminder-fixed-card">
        <button class="reminder-fixed-card__close" type="button" @click="dismissReminder(alert.key)">×</button>
        <div class="reminder-fixed-card__eyebrow">Vaqt bo‘ldi</div>
        <h3>{{ alert.title }}</h3>
        <p>{{ alert.body }}</p>
        <div class="reminder-fixed-card__meta">{{ alert.timeLabel }}</div>
      </div>
    </div>

    <div v-if="statusModal.open" class="modal-overlay">
      <div class="modal-card glass status-note-modal">
        <div class="modal-card__head">
          <div>
            <div class="eyebrow">HOLATNI O‘ZGARTIRISH</div>
            <h3>{{ statusModalTitle }}</h3>
            <p>{{ statusModalSubtitle }}</p>
          </div>
          <button class="modal-close" type="button" @click="closeStatusModal">×</button>
        </div>

        <div class="status-note-modal__body">
          <div class="status-note-modal__current glass-soft">
            <strong>Eski izoh</strong>
            <p>{{ statusModal.existingNote || 'Hozircha izoh yo‘q.' }}</p>
          </div>

          <label class="status-note-modal__field">
            <span>Yangi izoh</span>
            <textarea
              v-model="statusModal.newNote"
              class="input note-input"
              placeholder="Yangi izoh yozing..."
              rows="5"
            ></textarea>
          </label>

          <p class="status-note-modal__hint">
            Holat o‘zgarganda eski izoh faqat ko‘rish uchun turadi. Saqlangandan keyin cardda faqat yangi izoh qoladi.
          </p>
        </div>

        <div class="status-note-modal__actions">
          <button class="btn ghost" type="button" @click="closeStatusModal">Bekor</button>
          <button class="btn primary" type="button" :disabled="!canSubmitStatusModal || processingLeadId === statusModal.lead?.id" @click="submitStatusModal">
            Saqlash va o‘tkazish
          </button>
        </div>
      </div>
    </div>

    <div v-if="assignedStatusModal.open" class="modal-overlay">
      <div class="modal-card glass assigned-status-modal">
        <div class="modal-card__head">
          <div>
            <div class="eyebrow">BIRIKTIRILGAN LEAD</div>
            <h3>Qaysi bo‘limga qo‘shmoqchisiz?</h3>
            <p>{{ assignedStatusModal.lead?.full_name || 'Lead' }} uchun bo‘limni tanlang.</p>
          </div>
          <button class="modal-close" type="button" @click="closeAssignedStatusModal">×</button>
        </div>

        <div class="assigned-status-modal__grid">
          <button class="assigned-status-option sale" type="button" @click="selectAssignedStatus('sale')">Sotuv</button>
          <button class="assigned-status-option otkaz" type="button" @click="selectAssignedStatus('otkaz')">Atkaz</button>
          <button class="assigned-status-option wrong" type="button" @click="selectAssignedStatus('wrong_number')">Xato</button>
          <button class="assigned-status-option open" type="button" @click="selectAssignedStatus('open_number')">O‘chiq</button>
          <button class="assigned-status-option advice" type="button" @click="selectAssignedStatus('advice')">Maslahat</button>
          <button class="assigned-status-option other" type="button" @click="selectAssignedStatus('other')">O'qiydi</button>
        </div>
      </div>
    </div>

    <div class="operator-board-top glass-soft">
      <div class="operator-board-top__info">
        <div class="operator-board-top__badges">
          <span class="badge">{{ topBadgeLabel }} • {{ visibleLeadCount }} ta</span>
          <span class="badge muted">{{ assignmentBadgeLabel }}</span>
          <span class="badge muted">Ko‘rinayotgan: {{ visibleLeadCount }} ta</span>
        </div>
        <div class="operator-board-top__metrics" v-if="statusSummaryItems.length">
          <span
            v-for="item in statusSummaryItems"
            :key="item.key"
            class="operator-count-pill"
            :class="`status-${item.key}`"
          >
            {{ item.title }}: {{ item.count }} ta
          </span>
        </div>
      </div>

      <div v-if="currentTab !== 'report'" class="operator-board-top__search">
        <input
          v-model="search"
          class="input"
          :disabled="loading"
          placeholder="Ism, nomer, maktab, izoh yoki vaqt"
          @keyup.enter="applyLeadSearch"
        />
        <input
          v-if="currentTab === 'general' || currentTab === 'assigned'"
          v-model="assignmentDateInput"
          class="input operator-board-top__date-input"
          :disabled="loading"
          placeholder="Biriktirilgan kun.oy (07.04)"
          inputmode="numeric"
          @keyup.enter="applyLeadSearch"
        />
        <button class="btn ghost" type="button" :disabled="loading" @click="applyLeadSearch">Qidirish</button>
        <button v-if="search || assignmentDateInput" class="btn ghost" type="button" :disabled="loading" @click="clearLeadSearch">Tozalash</button>
      </div>
    </div>

    <ResponsiveSwiper
      v-if="isCompact"
      :items="summaryCards"
      eyebrow="Operator statistikasi"
      title="Kunlik ko'rsatkichlar"
      wrapper-class="glass-soft stats-mobile-swiper stats-mobile-swiper--operator swipe-elevated"
      :desktop-slides="2"
      :tablet-slides="2"
      :mobile-slides="1"
      :tablet-breakpoint="980"
    >
      <template #default="{ item }">
        <StatCard :title="item.title" :value="item.value" :subtitle="item.subtitle" />
      </template>
    </ResponsiveSwiper>

    <div v-else class="grid cards operator-summary-cards operator-summary-cards--compact">
      <StatCard v-for="item in summaryCards" :key="item.title" :title="item.title" :value="item.value" :subtitle="item.subtitle" />
    </div>

    <section v-if="currentTab === 'report'" class="panel glass operator-report-panel">
      <div class="section-head section-head--wrap">
        <div>
          <div class="eyebrow">Kunlik hisobot</div>
          <h3>Operator bo‘yicha kunlik natijalar</h3>
          <p>Masalan: 07.04.2026 kuni nechta sotuv, atkaz va boshqa status bo‘lganini shu yerda ko‘rasiz.</p>
        </div>
        <span class="badge">So‘nggi {{ reportDays }} kun</span>
      </div>

      <div v-if="dailyHistory.length" class="operator-report-list">
        <article v-for="row in dailyHistory" :key="row.date" class="operator-report-card glass-soft">
          <div class="operator-report-card__date">{{ formatReportDate(row.date) }}</div>
          <div class="operator-report-card__stats">
            <span>Sotuv: <strong>{{ row.sale }}</strong></span>
            <span>Atkaz: <strong>{{ row.otkaz }}</strong></span>
            <span>Xato nomer: <strong>{{ row.wrong_number }}</strong></span>
            <span>O‘chiq nomer: <strong>{{ row.open_number }}</strong></span>
            <span>Maslahat: <strong>{{ row.advice }}</strong></span>
            <span>O'qiydi: <strong>{{ row.other }}</strong></span>
            <span>Jami action: <strong>{{ row.actions_total }}</strong></span>
          </div>
        </article>
      </div>
      <div v-else class="empty-state">Hali kunlik hisobot topilmadi.</div>
    </section>

    <section v-else-if="currentTab === 'assigned'" class="operator-new-leads panel glass">
      <div class="operator-new-leads__head">
        <div>
          <div class="eyebrow">BIRIKTIRILGAN LEADLAR</div>
          <h3>Admin biriktirgan yangi leadlar</h3>
          <p>Bu yerdagi leadga birinchi holat berilgach, u avtomatik umumiy bo‘limga o‘tadi.</p>
        </div>
        <span class="badge">{{ filteredAssignedLeads.length }} ta lead</span>
      </div>

      <div v-if="filteredAssignedLeads.length" class="operator-new-leads__grid operator-new-leads__grid--static">
        <OperatorLeadCompactCard
          v-for="lead in filteredAssignedLeads"
          :key="`new-${lead.id}`"
          :lead="lead"
          :busy="processingLeadId === lead.id"
          :reminder-busy="reminderSavingId === lead.id"
          :drag-disabled="true"
          @request-status-change="openStatusChangeModal"
          @save-reminder="saveReminder"
          @clear-reminder="clearReminder"
        />
      </div>
      <div v-else class="operator-new-leads__empty">
        Hozircha yangi biriktirilgan lead yo‘q yoki qidiruvga mos lead topilmadi.
      </div>
    </section>

    <section v-else-if="currentTab === 'timed'" class="operator-new-leads panel glass operator-timed-leads">
      <div class="operator-new-leads__head">
        <div>
          <div class="eyebrow">VAQT QO‘YILGANLAR</div>
          <h3>Eslatma vaqti qo‘yilgan leadlar</h3>
          <p>Qaysi leadlarga kun va soat qo‘yilgan bo‘lsa, hammasi shu yerda card ko‘rinishida turadi.</p>
        </div>
        <span class="badge">{{ filteredTimedLeads.length }} ta lead</span>
      </div>

      <ResponsiveSwiper
        v-if="filteredTimedLeads.length && isCompact"
        :items="filteredTimedLeads"
        eyebrow="Vaqt qo'yilganlar swiper"
        title="Eslatmalar cardlari"
        wrapper-class="glass-soft lead-mobile-swiper lead-mobile-swiper--operator swipe-elevated"
        :desktop-slides="2"
        :tablet-slides="1"
        :mobile-slides="1"
        :tablet-breakpoint="980"
      >
        <template #default="{ item: lead }">
          <OperatorLeadCompactCard
            :key="`timed-${lead.id}`"
            :lead="lead"
            :busy="processingLeadId === lead.id"
            :reminder-busy="reminderSavingId === lead.id"
            @request-status-change="openStatusChangeModal"
            @drag-start="handleCardDragStart"
            @drag-end="handleCardDragEnd"
            @save-reminder="saveReminder"
            @clear-reminder="clearReminder"
          />
        </template>
      </ResponsiveSwiper>
      <div v-else-if="filteredTimedLeads.length" class="operator-new-leads__grid">
        <OperatorLeadCompactCard
          v-for="lead in filteredTimedLeads"
          :key="`timed-${lead.id}`"
          :lead="lead"
          :busy="processingLeadId === lead.id"
          :reminder-busy="reminderSavingId === lead.id"
          :drag-disabled="true"
          @request-status-change="openStatusChangeModal"
          @save-reminder="saveReminder"
          @clear-reminder="clearReminder"
        />
      </div>
      <div v-else class="operator-new-leads__empty">
        Hozircha vaqt qo‘yilgan lead yo‘q yoki qidiruvga mos lead topilmadi.
      </div>
    </section>

    <div v-else class="operator-status-board-wrap panel glass panel--relative">
      <div v-if="loading" class="panel-loader-overlay">
        <div class="loader-ring"></div>
        <p>{{ loadingMessage }}</p>
      </div>

      <ResponsiveSwiper
        v-if="isCompact"
        :items="displaySections"
        eyebrow="Statuslar swiper"
        title="Har bo'lim alohida card bo'lib yuradi"
        wrapper-class="glass-soft operator-status-mobile-swiper swipe-elevated"
        :desktop-slides="2"
        :tablet-slides="1"
        :mobile-slides="1"
        :tablet-breakpoint="1100"
      >
        <template #default="{ item: section }">
          <section
            class="operator-status-column"
            :class="[`status-${section.key}`, { 'drop-active': dropTargetStatus === section.key }]"
            @dragover.prevent="handleColumnDragOver(section.key)"
            @dragleave="handleColumnDragLeave(section.key)"
            @drop.prevent="handleStatusDrop(section.key)"
          >
            <div class="operator-status-column__top">
              <div class="operator-status-arc" :class="`status-${section.key}`"></div>
              <h3>{{ section.title }}</h3>
              <span class="operator-status-count">{{ section.leads.length }} ta lead</span>
            </div>

            <div class="operator-status-column__cards">
              <OperatorLeadCompactCard
                v-for="lead in section.leads"
                :key="lead.id"
                :lead="lead"
                :busy="processingLeadId === lead.id"
                :reminder-busy="reminderSavingId === lead.id"
                @request-status-change="openStatusChangeModal"
                @drag-start="handleCardDragStart"
                @drag-end="handleCardDragEnd"
                @save-reminder="saveReminder"
                @clear-reminder="clearReminder"
              />
              <div v-if="!section.leads.length" class="operator-status-column__empty">
                Bu bo‘limda lead yo‘q.
              </div>
            </div>
          </section>
        </template>
      </ResponsiveSwiper>

      <div v-else class="operator-status-board" :class="{ 'content-dim': loading }">
        <section
          v-for="section in displaySections"
          :key="section.key"
          class="operator-status-column"
          :class="[`status-${section.key}`, { 'drop-active': dropTargetStatus === section.key }]"
          @dragover.prevent="handleColumnDragOver(section.key)"
          @dragleave="handleColumnDragLeave(section.key)"
          @drop.prevent="handleStatusDrop(section.key)"
        >
          <div class="operator-status-column__top">
            <div class="operator-status-arc" :class="`status-${section.key}`"></div>
            <h3>{{ section.title }}</h3>
            <span class="operator-status-count">{{ section.leads.length }} ta lead</span>
          </div>

          <div class="operator-status-column__cards">
            <OperatorLeadCompactCard
              v-for="lead in section.leads"
              :key="lead.id"
              :lead="lead"
              :busy="processingLeadId === lead.id"
              :reminder-busy="reminderSavingId === lead.id"
              @request-status-change="openStatusChangeModal"
              @drag-start="handleCardDragStart"
              @drag-end="handleCardDragEnd"
              @save-reminder="saveReminder"
              @clear-reminder="clearReminder"
            />
            <div v-if="!section.leads.length" class="operator-status-column__empty">
              Bu bo‘limda lead yo‘q.
            </div>
          </div>
        </section>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, onBeforeUnmount, onMounted, reactive, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import client from '../../api/client'
import OperatorLeadCompactCard from '../../components/ui/OperatorLeadCompactCard.vue'
import StatCard from '../../components/ui/StatCard.vue'
import ResponsiveSwiper from '../../components/ui/ResponsiveSwiper.vue'
import { useViewport } from '../../composables/useViewport'

const fetchStatusOrder = ['new', 'sale', 'otkaz', 'wrong_number', 'open_number', 'advice', 'other']
const sectionOrder = ['sale', 'otkaz', 'wrong_number', 'open_number', 'advice', 'other']
const sectionMeta = {
  sale: { title: 'Sotuvlar' },
  otkaz: { title: 'Atkaz' },
  wrong_number: { title: 'Xato nomer' },
  open_number: { title: "O'chiq Nomer" },
  advice: { title: 'Maslahat' },
  other: { title: "O'qiydi" },
}
const noteRequiredStatuses = ['otkaz', 'advice', 'other']
const statusLabels = { new: 'Biriktirilgan leadlar', sale: 'Sotuv', otkaz: 'Atkaz', wrong_number: 'Xato nomer', open_number: "O‘chiq nomer", advice: 'Maslahat', other: "O'qiydi" }
const sleep = (ms) => new Promise(resolve => setTimeout(resolve, ms))

const route = useRoute()
const router = useRouter()
const { isCompact } = useViewport(1100, 640)

const search = ref('')
const appliedSearch = ref('')
const assignmentDateInput = ref('')
const appliedAssignmentDate = ref('')
const loading = ref(false)
const loadingMessage = ref('Leadlar yuklanmoqda...')
const successMessage = ref('')
const errorMessage = ref('')
const processingLeadId = ref(null)
const reminderSavingId = ref(null)
const reminderAlerts = ref([])
const actionToast = ref(null)
const dailyHistory = ref([])
const draggedLead = ref(null)
const dropTargetStatus = ref('')
const statusModal = reactive({ open: false, lead: null, status: '', existingNote: '', newNote: '' })
const assignedStatusModal = reactive({ open: false, lead: null, existingNote: '' })
const reportDays = 31
const leadsByStatus = reactive(Object.fromEntries(fetchStatusOrder.map((key) => [key, []])))
const daily = reactive({ new: 0, sale: 0, otkaz: 0, advice: 0, open_number: 0, wrong_number: 0, other: 0, daily_sale: 0, daily_otkaz: 0, touched_today: 0, actions_today: 0 })
const summaryCards = computed(() => ([
  { title: 'Biriktirilgan leadlar', value: daily.new, subtitle: 'Yangi biriktirilgan leadlar' },
  { title: 'Bugungi sotuv', value: daily.daily_sale, subtitle: 'Sotuvga aylangan leadlar' },
  { title: 'Bugungi atkaz', value: daily.daily_otkaz, subtitle: 'Qayta ishlashga o‘tgan leadlar' },
  { title: 'Aloqa qilingan', value: daily.touched_today, subtitle: 'Bugun ishlangan leadlar' },
]))

let successTimer = null
let reminderCheckTimer = null
let actionToastTimer = null
const notifiedReminderKeys = new Set()

const currentTab = computed(() => ['assigned', 'timed', 'report'].includes(route.query.tab) ? route.query.tab : 'general')
const newlyAssignedLeads = computed(() => leadsByStatus.new || [])
const topBadgeLabel = computed(() => {
  if (currentTab.value === 'assigned') return 'Biriktirilgan leadlar'
  if (currentTab.value === 'timed') return "Vaqt qo'yilganlar"
  if (currentTab.value === 'report') return 'Kunlik hisobot'
  return 'Umumiy leadlar'
})

const assignmentBadgeLabel = computed(() => {
  if (!['general', 'assigned'].includes(currentTab.value)) return 'Barcha kunlar'
  return appliedAssignmentDate.value ? `Biriktirilgan sana: ${appliedAssignmentDate.value}` : 'Barcha kunlar'
})

const statusModalTitle = computed(() => {
  const leadName = statusModal.lead?.full_name || 'Lead'
  const label = statusLabels[statusModal.status] || 'yangi holat'
  return `${leadName} → ${label}`
})

const statusModalSubtitle = computed(() => {
  const current = statusLabels[statusModal.lead?.current_status] || 'joriy holat'
  return `Cardni sudrab tashlaganingizdan keyin yoki tugmani bosganingizdan keyin shu yerda izohni yangilab saqlaysiz. Hozirgi holat: ${current}.`
})

const canSubmitStatusModal = computed(() => {
  if (!statusModal.lead || !statusModal.status) return false
  const freshNote = String(statusModal.newNote || '').trim()
  return Boolean(freshNote)
})

function normalizeSearchValue(value) {
  return String(value || '').toLowerCase().trim()
}

function getLeadSearchNotes(lead) {
  const historyNotes = Array.isArray(lead?.history)
    ? lead.history.map(item => item?.note?.trim()).filter(Boolean).join(' ')
    : ''
  return `${historyNotes} ${lead?.reminder_note || ''}`.trim()
}

function formatReminderSearchText(value) {
  if (!value) return ''
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return ''
  const dd = String(date.getDate()).padStart(2, '0')
  const mm = String(date.getMonth() + 1).padStart(2, '0')
  const yyyy = String(date.getFullYear())
  const hh = String(date.getHours()).padStart(2, '0')
  const min = String(date.getMinutes()).padStart(2, '0')
  return `${dd}.${mm} ${hh}:${min} ${dd}.${mm}.${yyyy} ${hh}:${min} ${dd}.${mm} soat ${hh}:${min}`
}

function normalizeDayMonthInput(value) {
  const cleaned = String(value || '').replace(/\s+/g, '').replace(/[\/\-,]/g, '.').replace(/\.+/g, '.')
  if (!cleaned) return ''
  const match = cleaned.match(/^(\d{1,2})\.(\d{1,2})$/)
  if (!match) return ''
  const day = Number(match[1])
  const month = Number(match[2])
  if (!Number.isInteger(day) || !Number.isInteger(month)) return ''
  if (day < 1 || day > 31 || month < 1 || month > 12) return ''
  return `${String(day).padStart(2, '0')}.${String(month).padStart(2, '0')}`
}

function formatLeadAssignedDayMonth(value) {
  if (!value) return ''
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return ''
  const dd = String(date.getDate()).padStart(2, '0')
  const mm = String(date.getMonth() + 1).padStart(2, '0')
  return `${dd}.${mm}`
}

function leadMatchesAppliedSearch(lead) {
  const query = normalizeSearchValue(appliedSearch.value)
  if (!query) return true
  const haystack = [
    lead?.full_name,
    lead?.tsh,
    lead?.subject,
    lead?.ball,
    lead?.phone1,
    lead?.phone2,
    lead?.phone3,
    lead?.display_school,
    lead?.school,
    lead?.grade,
    lead?.online_region,
    getLeadSearchNotes(lead),
    formatReminderSearchText(lead?.reminder_at),
  ].map(normalizeSearchValue).join(' ')
  return haystack.includes(query)
}

function leadMatchesAssignedDate(lead) {
  if (!['general', 'assigned'].includes(currentTab.value)) return true
  if (!appliedAssignmentDate.value) return true
  return formatLeadAssignedDayMonth(lead?.created_at) === appliedAssignmentDate.value
}

function leadMatchesFilters(lead) {
  return leadMatchesAppliedSearch(lead) && leadMatchesAssignedDate(lead)
}

const filteredAssignedLeads = computed(() => newlyAssignedLeads.value.filter(leadMatchesFilters))
const filteredTimedLeads = computed(() => fetchStatusOrder
  .flatMap((status) => leadsByStatus[status] || [])
  .filter((lead) => Boolean(lead?.reminder_at))
  .filter(leadMatchesAppliedSearch))
const displaySections = computed(() => sectionOrder.map((key) => ({
  key,
  title: sectionMeta[key].title,
  leads: (leadsByStatus[key] || []).filter(leadMatchesFilters),
})))
const visibleLeadCount = computed(() => {
  if (currentTab.value === 'assigned') return filteredAssignedLeads.value.length
  if (currentTab.value === 'timed') return filteredTimedLeads.value.length
  if (currentTab.value === 'report') return dailyHistory.value.length
  return displaySections.value.reduce((sum, item) => sum + item.leads.length, 0)
})
const statusSummaryItems = computed(() => {
  if (currentTab.value === 'assigned') {
    return []
  }
  if (currentTab.value === 'timed') {
    return [{ key: 'new', title: "Vaqt qo'yilgan", count: filteredTimedLeads.value.length }]
  }
  if (currentTab.value === 'report') {
    const latest = dailyHistory.value[0]
    if (!latest) return []
    return [
      { key: 'sale', title: 'Sotuv', count: latest.sale },
      { key: 'otkaz', title: 'Atkaz', count: latest.otkaz },
      { key: 'advice', title: 'Maslahat', count: latest.advice },
      { key: 'other', title: "O'qiydi", count: latest.other },
    ]
  }
  return displaySections.value.map(section => ({ key: section.key, title: section.title, count: section.leads.length }))
})

watch(() => route.query.tab, (tab) => {
  if (!['assigned', 'general', 'timed', 'report'].includes(tab)) {
    router.replace({ path: '/operator', query: { ...route.query, tab: 'general' } })
  }
}, { immediate: true })

function showSuccess(message) {
  successMessage.value = message
  clearTimeout(successTimer)
  successTimer = setTimeout(() => { successMessage.value = '' }, 2800)
}

function showActionToast(message) {
  actionToast.value = { message }
  clearTimeout(actionToastTimer)
  actionToastTimer = setTimeout(() => {
    actionToast.value = null
  }, 2600)
}

function hideActionToast() {
  clearTimeout(actionToastTimer)
  actionToast.value = null
}

function applyLeadSearch() {
  appliedSearch.value = search.value.trim()
  appliedAssignmentDate.value = normalizeDayMonthInput(assignmentDateInput.value)
  if (assignmentDateInput.value && !appliedAssignmentDate.value) {
    errorMessage.value = "Sanani kun.oy ko'rinishida kiriting. Masalan: 07.04"
    return
  }
  if (errorMessage.value === "Sanani kun.oy ko'rinishida kiriting. Masalan: 07.04") {
    errorMessage.value = ''
  }
  assignmentDateInput.value = appliedAssignmentDate.value
}

function clearLeadSearch() {
  search.value = ''
  appliedSearch.value = ''
  assignmentDateInput.value = ''
  appliedAssignmentDate.value = ''
}

function formatReportDate(value) {
  if (!value) return '-'
  const [year, month, day] = String(value).split('-')
  if (!year || !month || !day) return value
  return `${day}.${month}.${year}`
}

async function fetchAllStatuses(message = 'Leadlar yuklanmoqda...') {
  loading.value = true
  loadingMessage.value = message
  errorMessage.value = ''
  const startedAt = Date.now()
  try {
    const responses = await Promise.all(fetchStatusOrder.map((status) => {
      const params = { current_status: status }
      return client.get('operator/leads/', { params })
    }))

    fetchStatusOrder.forEach((status, index) => {
      const data = responses[index].data
      leadsByStatus[status] = data.results || data || []
    })
  } catch (error) {
    errorMessage.value = error?.response?.data?.detail || 'Leadlarni yuklashda xatolik yuz berdi.'
  } finally {
    const elapsed = Date.now() - startedAt
    if (elapsed < 500) await sleep(500 - elapsed)
    loading.value = false
  }
}

async function fetchDaily() {
  try {
    const { data } = await client.get('operator/daily-results/')
    Object.assign(daily, data)
  } catch {
    // ignore
  }
}

async function fetchDailyHistory() {
  try {
    const { data } = await client.get('operator/daily-history/', { params: { days: reportDays } })
    dailyHistory.value = data?.results || []
  } catch {
    dailyHistory.value = []
  }
}

function updateLeadInLists(updatedLead) {
  fetchStatusOrder.forEach((status) => {
    leadsByStatus[status] = (leadsByStatus[status] || []).map((item) => (item.id === updatedLead.id ? updatedLead : item))
  })
}

function getLeadLatestNote(lead) {
  if (!lead) return ''
  const historyNote = Array.isArray(lead.history)
    ? lead.history.find((item) => item?.note?.trim())?.note?.trim() || ''
    : ''
  return historyNote || lead.reminder_note || ''
}

function buildLatestNote(newNote) {
  return String(newNote || '').trim()
}

function openAssignedStatusModal(lead) {
  assignedStatusModal.open = true
  assignedStatusModal.lead = lead
  assignedStatusModal.existingNote = getLeadLatestNote(lead)
}

function closeAssignedStatusModal() {
  assignedStatusModal.open = false
  assignedStatusModal.lead = null
  assignedStatusModal.existingNote = ''
}

async function selectAssignedStatus(status) {
  const lead = assignedStatusModal.lead
  const existingNote = assignedStatusModal.existingNote
  closeAssignedStatusModal()
  if (!lead || !status) return
  if (noteRequiredStatuses.includes(status)) {
    openStatusChangeModal({ lead, status, existingNote })
    return
  }
  await changeStatus({ id: lead.id, status, note: '' })
}

function openStatusChangeModal(payload) {
  const lead = payload?.lead || fetchStatusOrder.flatMap((status) => leadsByStatus[status] || []).find((item) => item.id === payload?.id)
  if (!lead || !payload?.status) return
  statusModal.open = true
  statusModal.lead = lead
  statusModal.status = payload.status
  statusModal.existingNote = payload.existingNote ?? getLeadLatestNote(lead)
  statusModal.newNote = ''
}

function closeStatusModal() {
  statusModal.open = false
  statusModal.lead = null
  statusModal.status = ''
  statusModal.existingNote = ''
  statusModal.newNote = ''
}

function handleCardDragStart(payload) {
  draggedLead.value = payload
}

function handleCardDragEnd() {
  draggedLead.value = null
  dropTargetStatus.value = ''
}

function handleColumnDragOver(statusKey) {
  if (!draggedLead.value?.lead) return
  dropTargetStatus.value = statusKey
}

function handleColumnDragLeave(statusKey) {
  if (dropTargetStatus.value === statusKey) {
    dropTargetStatus.value = ''
  }
}

function handleStatusDrop(statusKey) {
  const payload = draggedLead.value
  dropTargetStatus.value = ''
  handleCardDragEnd()
  if (!payload?.lead) return
  openStatusChangeModal({ lead: payload.lead, status: statusKey, existingNote: payload.existingNote })
}

async function submitStatusModal() {
  if (!statusModal.lead || !statusModal.status) return
  const latestNote = buildLatestNote(statusModal.newNote)
  if (!latestNote) {
    errorMessage.value = "Holatni o'zgartirish uchun yangi izoh kiriting."
    return
  }
  const payload = { id: statusModal.lead.id, status: statusModal.status, note: latestNote }
  closeStatusModal()
  await changeStatus(payload)
}

async function changeStatus(payload) {
  errorMessage.value = ''
  const nextStatus = payload?.status || ''
  const note = String(payload?.note || '').trim()

  if (noteRequiredStatuses.includes(nextStatus) && !note) {
    errorMessage.value = "Holatni o'zgartirish uchun yangi izoh kiriting."
    return
  }

  try {
    processingLeadId.value = payload.id
    await Promise.all([
      client.patch(`operator/leads/${payload.id}/change-status/`, { current_status: nextStatus, note }),
      sleep(450),
    ])
    await Promise.all([fetchAllStatuses('Leadlar yangilanmoqda...'), fetchDaily(), fetchDailyHistory()])
    showSuccess(`${statusLabels[nextStatus] || 'Tanlangan bo‘lim'} bo‘limiga o‘tkazildi`)
  } catch (error) {
    const backendNoteError = error?.response?.data?.note
    if (Array.isArray(backendNoteError) && backendNoteError.length) {
      errorMessage.value = backendNoteError[0]
    } else if (typeof backendNoteError === 'string' && backendNoteError) {
      errorMessage.value = backendNoteError
    } else {
      errorMessage.value = error?.response?.data?.detail || 'Statusni yangilashda xatolik yuz berdi.'
    }
  } finally {
    processingLeadId.value = null
  }
}

async function saveReminder(payload) {
  errorMessage.value = ''
  try {
    reminderSavingId.value = payload.id
    const { data } = await client.patch(`operator/leads/${payload.id}/reminder/`, {
      reminder_at: payload.reminder_at,
      reminder_note: payload.reminder_note || '',
    })
    notifiedReminderKeys.delete(buildReminderKey(data))
    updateLeadInLists(data)
    showActionToast('Lead uchun eslatma vaqti saqlandi.')
    await ensureNotificationPermission()
    if (currentTab.value === 'assigned') {
      openAssignedStatusModal(data)
    }
  } catch (error) {
    errorMessage.value = error?.response?.data?.detail || 'Vaqtni saqlashda xatolik yuz berdi.'
  } finally {
    reminderSavingId.value = null
  }
}

async function clearReminder(payload) {
  errorMessage.value = ''
  try {
    reminderSavingId.value = payload.id
    const { data } = await client.patch(`operator/leads/${payload.id}/reminder/`, {
      reminder_at: null,
      reminder_note: '',
    })
    notifiedReminderKeys.delete(buildReminderKey({ id: payload.id, reminder_at: data.reminder_at }))
    updateLeadInLists(data)
    showActionToast('Lead uchun vaqt olib tashlandi.')
  } catch (error) {
    errorMessage.value = error?.response?.data?.detail || 'Vaqtni tozalashda xatolik yuz berdi.'
  } finally {
    reminderSavingId.value = null
  }
}

function buildReminderKey(lead) {
  return `${lead?.id || 'x'}:${lead?.reminder_at || 'none'}`
}

async function ensureNotificationPermission() {
  if (typeof window === 'undefined' || !('Notification' in window)) return
  if (Notification.permission === 'default') {
    try {
      await Notification.requestPermission()
    } catch {
      // ignore
    }
  }
}

function speakReminder(text) {
  if (typeof window === 'undefined' || !('speechSynthesis' in window)) return
  try {
    window.speechSynthesis.cancel()
    const utterance = new SpeechSynthesisUtterance(text)
    utterance.lang = 'ru-RU'
    utterance.rate = 0.92
    utterance.pitch = 1
    utterance.volume = 1
    window.speechSynthesis.speak(utterance)
  } catch {
    // ignore speech issues
  }
}

function playReminderSound() {
  if (typeof window === 'undefined') return
  const AudioContextClass = window.AudioContext || window.webkitAudioContext
  if (!AudioContextClass) return
  const ctx = new AudioContextClass()
  const pattern = [980, 780, 980, 660, 980, 780]
  pattern.forEach((frequency, index) => {
    const oscillator = ctx.createOscillator()
    const gain = ctx.createGain()
    oscillator.type = index % 2 === 0 ? 'square' : 'sawtooth'
    oscillator.frequency.value = frequency
    const startAt = ctx.currentTime + index * 0.23
    gain.gain.setValueAtTime(0.0001, startAt)
    gain.gain.exponentialRampToValueAtTime(0.32, startAt + 0.02)
    gain.gain.exponentialRampToValueAtTime(0.0001, startAt + 0.2)
    oscillator.connect(gain)
    gain.connect(ctx.destination)
    oscillator.start(startAt)
    oscillator.stop(startAt + 0.22)
  })
  setTimeout(() => ctx.close().catch(() => {}), 2200)
}

function dismissReminder(key) {
  reminderAlerts.value = reminderAlerts.value.filter((item) => item.key !== key)
}

function notifyReminder(lead) {
  const when = new Date(lead.reminder_at)
  const timeLabel = `${String(when.getDate()).padStart(2, '0')}.${String(when.getMonth() + 1).padStart(2, '0')} ${String(when.getHours()).padStart(2, '0')}:${String(when.getMinutes()).padStart(2, '0')}`
  const body = `${lead.full_name} bilan ishlash vaqti bo‘ldi.`
  const reminderKey = buildReminderKey(lead)

  if (typeof window !== 'undefined' && 'Notification' in window && Notification.permission === 'granted') {
    try {
      new Notification('Lead vaqti bo‘ldi', { body: `${body} ${timeLabel}` })
    } catch {
      // ignore browser notification failures
    }
  }

  reminderAlerts.value = [
    { key: reminderKey, title: lead.full_name || 'Lead', body: `${body} Hozir bog‘laning.`, timeLabel },
    ...reminderAlerts.value.filter((item) => item.key !== reminderKey),
  ].slice(0, 3)

  playReminderSound()
  speakReminder(`Время пришло. ${lead.full_name || 'Лид'}`)
  showSuccess(`${body} ${timeLabel}`)
}

async function checkDueReminders() {
  try {
    const { data } = await client.get('operator/reminders/')
    const reminders = data.results || data
    if (!Array.isArray(reminders) || !reminders.length) return

    const now = Date.now()
    for (const lead of reminders) {
      if (!lead?.reminder_at) continue
      const reminderTime = new Date(lead.reminder_at).getTime()
      if (Number.isNaN(reminderTime) || reminderTime > now) continue
      const reminderKey = buildReminderKey(lead)
      if (notifiedReminderKeys.has(reminderKey)) continue

      notifiedReminderKeys.add(reminderKey)
      notifyReminder(lead)
      try {
        const { data: updatedLead } = await client.patch(`operator/leads/${lead.id}/reminder/`, { mark_as_notified: true })
        updateLeadInLists(updatedLead)
      } catch {
        // local state still prevents repetition this session
      }
    }
  } catch {
    // silent polling failure
  }
}

onMounted(async () => {
  await Promise.all([fetchAllStatuses(), fetchDaily(), fetchDailyHistory()])
  await ensureNotificationPermission()
  await checkDueReminders()
  reminderCheckTimer = window.setInterval(checkDueReminders, 15000)
})

onBeforeUnmount(() => {
  clearTimeout(successTimer)
  clearTimeout(actionToastTimer)
  if (reminderCheckTimer) window.clearInterval(reminderCheckTimer)
  closeStatusModal()
  handleCardDragEnd()
})
</script>
