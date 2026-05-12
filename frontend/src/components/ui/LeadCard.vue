<template>
  <article class="lead-card lead-card--operator glass" :class="{ 'lead-card--busy': busy || reminderBusy }">
    <div v-if="busy || reminderBusy" class="lead-card__busy-overlay">
      <div class="loader-ring"></div>
      <p>{{ reminderBusy ? 'Eslatma saqlanmoqda...' : 'Status yangilanmoqda...' }}</p>
    </div>

    <div class="lead-card__header">
      <div class="lead-card__identity">
        <div class="lead-card__eyebrow">{{ lead.is_online ? 'Online lead' : 'Lead kartasi' }}</div>
        <h3>{{ lead.full_name || 'Ism yo‘q' }}</h3>
        <div class="lead-card__subline">
          <span class="lead-chip lead-chip--soft">ID: {{ lead.id }}</span>
          <span v-if="lead.is_online" class="lead-chip lead-chip--soft">Online lead</span>
          <span class="lead-chip lead-chip--status">{{ statusLabel }}</span>
        </div>
      </div>
      <div class="lead-card__date-box">
        <span>Yangilangan</span>
        <strong>{{ formattedUpdatedAt }}</strong>
      </div>
    </div>

    <div class="lead-card__section">
      <div class="lead-card__section-title">Telefon raqamlar</div>
      <div class="lead-card__phones lead-card__phones--stacked">
        <a v-if="lead.phone1" :href="`tel:${lead.phone1}`" class="contact-chip contact-chip--primary">
          <small>tel1</small>
          <strong>{{ formatPhone(lead.phone1) }}</strong>
        </a>
        <a v-if="lead.phone2" :href="`tel:${lead.phone2}`" class="contact-chip">
          <small>tel2</small>
          <strong>{{ formatPhone(lead.phone2) }}</strong>
        </a>
        <a v-if="lead.phone3" :href="`tel:${lead.phone3}`" class="contact-chip">
          <small>tel3</small>
          <strong>{{ formatPhone(lead.phone3) }}</strong>
        </a>
        <div v-if="!lead.phone1 && !lead.phone2 && !lead.phone3" class="contact-chip contact-chip--empty">
          Telefon raqami kiritilmagan
        </div>
      </div>
    </div>

    <div class="lead-card__section">
      <div class="lead-card__section-title">Lead ma’lumotlari</div>
      <div class="lead-card__meta-grid lead-card__meta-grid--operator">
        <div v-if="!lead.is_online" class="info-tile">
          <span>T/SH</span>
          <strong>{{ normalizeValue(lead.tsh) }}</strong>
        </div>
        <div class="info-tile">
          <span>{{ lead.is_online ? 'Hudud' : 'Maktab' }}</span>
          <strong>{{ normalizeValue(lead.is_online ? lead.online_region : (lead.display_school || lead.school)) }}</strong>
        </div>
        <div class="info-tile">
          <span>{{ lead.is_online ? 'Yosh' : 'Sinf' }}</span>
          <strong>{{ normalizeValue(lead.grade) }}</strong>
        </div>
        <div v-if="!lead.is_online" class="info-tile">
          <span>Fan</span>
          <strong>{{ normalizeValue(lead.subject) }}</strong>
        </div>
        <div v-if="!lead.is_online" class="info-tile">
          <span>Ball</span>
          <strong>{{ normalizeValue(lead.ball) }}</strong>
        </div>
        <div class="info-tile">
          <span>Hozirgi holat</span>
          <strong>{{ statusLabel }}</strong>
        </div>
        <div class="info-tile">
          <span>Izoh</span>
          <strong>{{ notePreview }}</strong>
        </div>
      </div>
    </div>

    <div class="lead-card__section lead-card__section--reminder">
      <div class="lead-card__reminder-head">
        <div>
          <div class="lead-card__section-title">Vaqt eslatmasi</div>
          <div class="lead-card__danger-text lead-card__danger-text--muted">Vaqt kelganda tizim xabari va ovoz chiqadi.</div>
        </div>
        <span class="lead-chip lead-chip--soft">{{ reminderDisplay }}</span>
      </div>
      <div class="lead-card__reminder-grid">
        <label class="lead-card__reminder-field">
          <span>Sana</span>
          <input v-model="reminderDate" class="input" type="date" :disabled="busy || reminderBusy" />
        </label>
        <label class="lead-card__reminder-field">
          <span>Soat</span>
          <input v-model="reminderTime" class="input" type="time" :disabled="busy || reminderBusy" />
        </label>
      </div>
      <input
        v-model="reminderNote"
        class="input"
        :disabled="busy || reminderBusy"
        placeholder="Masalan: 07.04 soat 13:20"
      />
      <div class="lead-card__inline-actions lead-card__inline-actions--reminder">
        <button class="button" type="button" :disabled="busy || reminderBusy || !canSaveReminder" @click="saveReminder">
          {{ hasReminder ? 'Vaqtni yangilash' : 'Vaqt qo‘shish' }}
        </button>
        <button v-if="hasReminder" class="button button--ghost" type="button" :disabled="busy || reminderBusy" @click="clearReminder">
          Tozalash
        </button>
      </div>
    </div>

    <div v-if="showInlineNote" class="lead-card__section lead-card__section--alert">
      <label class="lead-card__section-title lead-card__section-title--danger" :for="`lead-note-${lead.id}`">
        Izoh yozing
      </label>
      <div class="lead-card__danger-text">Tanlangan status uchun izoh kiritish majburiy.</div>
      <textarea
        :id="`lead-note-${lead.id}`"
        v-model="note"
        class="input note-input note-input--danger"
        :disabled="busy || reminderBusy"
        placeholder="Izoh yozing..."
      ></textarea>
      <div class="lead-card__inline-actions">
        <button class="button button--ghost" type="button" :disabled="busy || reminderBusy" @click="cancelInlineNote">Bekor qilish</button>
        <button class="button" type="button" :disabled="busy || reminderBusy || !note.trim()" @click="confirmInlineNote">Qabul qilish</button>
      </div>
    </div>

    <div v-else class="lead-card__hint lead-card__hint--soft">
      Atkaz, Maslahat va O'qiydi tugmalari bosilganda shu card ichida izoh kiritish oynasi chiqadi.
    </div>

    <div class="lead-card__actions lead-card__actions--operator">
      <button class="status-action sale" :disabled="busy || reminderBusy" @click="emitChange('sale')" title="Sotuv">
        <span></span>
        <small>Sotuv</small>
      </button>
      <button class="status-action otkaz" :disabled="busy || reminderBusy" @click="emitChange('otkaz')" title="Atkaz">
        <span></span>
        <small>Atkaz</small>
      </button>
      <button class="status-action wrong" :disabled="busy || reminderBusy" @click="emitChange('wrong_number')" title="Xato nomer">
        <span></span>
        <small>Xato nomer</small>
      </button>
      <button class="status-action open" :disabled="busy || reminderBusy" @click="emitChange('open_number')" title="O'chiq Nomer">
        <span></span>
        <small>O'chiq Nomer</small>
      </button>
      <button class="status-action advice" :disabled="busy || reminderBusy" @click="emitChange('advice')" title="Maslahat">
        <span></span>
        <small>Maslahat</small>
      </button>
      <button class="status-action other" :disabled="busy || reminderBusy" @click="emitChange('other')" title="O'qiydi">
        <span></span>
        <small>O'qiydi</small>
      </button>
    </div>
  </article>
</template>

<script setup>
import { computed, ref, watch } from 'vue'

const props = defineProps({
  lead: Object,
  busy: { type: Boolean, default: false },
  reminderBusy: { type: Boolean, default: false },
})
const emit = defineEmits(['change', 'save-reminder', 'clear-reminder'])
const note = ref('')
const pendingStatus = ref('')
const showInlineNote = ref(false)
const reminderDate = ref('')
const reminderTime = ref('')
const reminderNote = ref('')

const labels = {
  new: 'Biriktirilgan',
  sale: 'Sotuv',
  otkaz: 'Atkaz',
  wrong_number: 'Xato nomer',
  open_number: "O'chiq Nomer",
  advice: 'Maslahat',
  other: "O'qiydi",
}
const noteRequiredStatuses = ['otkaz', 'advice', 'other']

const statusLabel = computed(() => labels[props.lead?.current_status] || props.lead?.current_status || 'Holat yo‘q')
const formattedUpdatedAt = computed(() => {
  if (!props.lead?.updated_at) return '-'
  const date = new Date(props.lead.updated_at)
  return date.toLocaleDateString('uz-UZ', { day: '2-digit', month: '2-digit', year: 'numeric' })
})
const savedNote = computed(() => props.lead?.history?.[0]?.note?.trim() || '')
const notePreview = computed(() => note.value.trim() || savedNote.value || 'Izoh kiritilmagan')
const hasReminder = computed(() => Boolean(props.lead?.reminder_at))
const reminderDisplay = computed(() => formatReminderText(props.lead?.reminder_at))
const canSaveReminder = computed(() => Boolean(reminderDate.value && reminderTime.value))

watch(() => [props.lead?.id, props.lead?.reminder_at, props.lead?.reminder_note], () => {
  note.value = ''
  pendingStatus.value = ''
  showInlineNote.value = false
  syncReminderFields()
}, { immediate: true })

function syncReminderFields() {
  reminderDate.value = toDateInput(props.lead?.reminder_at)
  reminderTime.value = toTimeInput(props.lead?.reminder_at)
  reminderNote.value = props.lead?.reminder_note || ''
}

function normalizeValue(value) {
  if (value === null || value === undefined || value === '') return '-'
  return String(value).replace(/\.0$/, '')
}

function formatPhone(value) {
  return normalizeValue(value)
}

function toDateInput(value) {
  if (!value) return ''
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return ''
  return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')}`
}

function toTimeInput(value) {
  if (!value) return ''
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return ''
  return `${String(date.getHours()).padStart(2, '0')}:${String(date.getMinutes()).padStart(2, '0')}`
}

function formatReminderText(value) {
  if (!value) return 'Vaqt yo‘q'
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return 'Vaqt yo‘q'
  return `${String(date.getDate()).padStart(2, '0')}.${String(date.getMonth() + 1).padStart(2, '0')} soat ${String(date.getHours()).padStart(2, '0')}:${String(date.getMinutes()).padStart(2, '0')}`
}

function buildReminderIso() {
  if (!reminderDate.value || !reminderTime.value) return null
  const date = new Date(`${reminderDate.value}T${reminderTime.value}`)
  if (Number.isNaN(date.getTime())) return null
  return date.toISOString()
}

function saveReminder() {
  if (props.busy || props.reminderBusy || !canSaveReminder.value) return
  const reminderAt = buildReminderIso()
  if (!reminderAt) return
  emit('save-reminder', {
    id: props.lead.id,
    reminder_at: reminderAt,
    reminder_note: reminderNote.value.trim(),
  })
}

function clearReminder() {
  if (props.busy || props.reminderBusy) return
  reminderDate.value = ''
  reminderTime.value = ''
  reminderNote.value = ''
  emit('clear-reminder', { id: props.lead.id })
}

function cancelInlineNote() {
  if (props.busy || props.reminderBusy) return
  showInlineNote.value = false
  pendingStatus.value = ''
  note.value = ''
}

function confirmInlineNote() {
  if (props.busy || props.reminderBusy || !pendingStatus.value || !note.value.trim()) return
  emit('change', { id: props.lead.id, status: pendingStatus.value, note: note.value.trim() })
  showInlineNote.value = false
  pendingStatus.value = ''
}

function emitChange(status) {
  if (props.busy || props.reminderBusy) return
  if (noteRequiredStatuses.includes(status) && !note.value.trim()) {
    pendingStatus.value = status
    showInlineNote.value = true
    return
  }
  emit('change', { id: props.lead.id, status, note: note.value.trim() })
  showInlineNote.value = false
  pendingStatus.value = ''
  note.value = ''
}
</script>
