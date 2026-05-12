<template>
  <article
    class="glass-soft operator-compact-card"
    :class="[`status-${lead.current_status}`, { 'is-busy': busy || reminderBusy, 'is-draggable': dragEnabled, 'is-dragging': isDragging }]"
    :draggable="dragEnabled"
    @dragstart="handleDragStart"
    @dragend="handleDragEnd"
  >
    <div class="operator-compact-card__overlay" v-if="busy || reminderBusy">
      <div class="loader-ring"></div>
      <p>{{ reminderBusy ? 'Vaqt saqlanmoqda...' : 'Yangilanmoqda...' }}</p>
    </div>

    <div class="operator-compact-card__head">
      <div>
        <h4>{{ lead.full_name || 'Ism yo‘q' }}</h4>
        <div class="operator-compact-card__chips">
          <span v-if="showStatusChip" class="operator-chip operator-chip--status">{{ statusLabel }}</span>
          <span v-if="lead.is_online" class="operator-chip">Online lead</span>
          <span class="operator-chip muted-chip">{{ locationChip }}</span>
        </div>
      </div>
      <div class="operator-compact-card__time">{{ formattedUpdatedAt }}</div>
    </div>

    <div class="operator-compact-card__body">
      <div class="operator-compact-card__info-grid">
        <button
          type="button"
          class="operator-phone-copy-row"
          title="Bosib nusxa oling"
          :class="{ 'is-copyable': hasCopyablePhone(lead.phone1), 'is-copied': copiedPhoneKey === 'phone1' }"
          :disabled="!hasCopyablePhone(lead.phone1)"
          draggable="false"
          @click.stop.prevent="copyPhone(lead.phone1, 'phone1')"
          @pointerdown.stop
          @dragstart.stop.prevent
          @mousedown.stop.prevent
        >
          <span class="operator-phone-copy-row__text"><strong>tel1:</strong> {{ formatPhone(lead.phone1) }}</span>
          <span class="operator-phone-copy-row__hint">{{ copiedPhoneKey === 'phone1' ? 'Nusxalandi' : 'Bosib nusxa oling' }}</span>
        </button>

        <button
          type="button"
          class="operator-phone-copy-row"
          :class="{ 'is-copyable': hasCopyablePhone(lead.phone2), 'is-copied': copiedPhoneKey === 'phone2' }"
          :disabled="!hasCopyablePhone(lead.phone2)"
          draggable="false"
          @click.stop.prevent="copyPhone(lead.phone2, 'phone2')"
          @pointerdown.stop
          @dragstart.stop.prevent
          @mousedown.stop.prevent
        >
          <span class="operator-phone-copy-row__text"><strong>tel2:</strong> {{ formatPhone(lead.phone2) }}</span>
          <span class="operator-phone-copy-row__hint">{{ copiedPhoneKey === 'phone2' ? 'Nusxalandi' : 'Bosib nusxa oling' }}</span>
        </button>

        <button
          type="button"
          class="operator-phone-copy-row"
          :class="{ 'is-copyable': hasCopyablePhone(lead.phone3), 'is-copied': copiedPhoneKey === 'phone3' }"
          :disabled="!hasCopyablePhone(lead.phone3)"
          draggable="false"
          @click.stop.prevent="copyPhone(lead.phone3, 'phone3')"
          @pointerdown.stop
          @dragstart.stop.prevent
          @mousedown.stop.prevent
        >
          <span class="operator-phone-copy-row__text"><strong>tel3:</strong> {{ formatPhone(lead.phone3) }}</span>
          <span class="operator-phone-copy-row__hint">{{ copiedPhoneKey === 'phone3' ? 'Nusxalandi' : 'Bosib nusxa oling' }}</span>
        </button>

        <p v-if="!lead.is_online"><strong>T/SH:</strong> {{ normalizeValue(lead.tsh) }}</p>
        <p><strong>{{ lead.is_online ? 'Hudud' : 'Maktab' }}:</strong> {{ primaryPlace }}</p>
        <p><strong>{{ lead.is_online ? 'Yosh' : 'Sinf' }}:</strong> {{ secondaryPlaceValue }}</p>
        <p v-if="!lead.is_online"><strong>Fan:</strong> {{ normalizeValue(lead.subject) }}</p>
        <p v-if="!lead.is_online"><strong>Ball:</strong> {{ normalizeValue(lead.ball) }}</p>
        <p v-if="hasReminder"><strong>Vaqt:</strong> {{ reminderDisplay }}</p>
        <p v-if="savedNote" class="operator-compact-card__note-preview"><strong>Izoh:</strong> {{ savedNote }}</p>
      </div>
    </div>

    <div class="operator-compact-card__reminder-card">
      <div class="operator-compact-card__reminder-head">
        <strong>Eslatma vaqti</strong>
        <span>{{ hasReminder ? reminderDisplay : 'Hali qo‘yilmagan' }}</span>
      </div>

      <div class="operator-compact-card__reminder-grid">
        <label class="operator-field">
          <span>Kun / oy</span>
          <input
            v-model="reminderDayMonth"
            class="input input--compact"
            type="text"
            inputmode="numeric"
            maxlength="5"
            placeholder="07.04"
            :disabled="busy || reminderBusy"
          />
        </label>

        <label class="operator-field">
          <span>Soat</span>
          <input
            v-model="reminderTime"
            class="input input--compact"
            type="time"
            :disabled="busy || reminderBusy"
          />
        </label>
      </div>

      <div class="operator-compact-card__reminder-actions">
        <button class="mini-action mini-action--primary reminder-save" type="button" :disabled="busy || reminderBusy || !canSaveReminder" @click="saveReminder">
          Saqlash
        </button>
        <button v-if="hasReminder" class="mini-action" type="button" :disabled="busy || reminderBusy" @click="clearReminder">
          Tozalash
        </button>
      </div>
    </div>

    <div class="operator-compact-card__actions">
      <button class="status-mini sale" :disabled="busy || reminderBusy" @click="requestStatusChange('sale')">Sotuv</button>
      <button class="status-mini otkaz" :disabled="busy || reminderBusy" @click="requestStatusChange('otkaz')">Atkaz</button>
      <button class="status-mini wrong" :disabled="busy || reminderBusy" @click="requestStatusChange('wrong_number')">Xato</button>
      <button class="status-mini open" :disabled="busy || reminderBusy" @click="requestStatusChange('open_number')">O‘chiq</button>
      <button class="status-mini advice" :disabled="busy || reminderBusy" @click="requestStatusChange('advice')">Maslahat</button>
      <button class="status-mini other" :disabled="busy || reminderBusy" @click="requestStatusChange('other')">O'qiydi</button>
    </div>
  </article>
</template>

<script setup>
import { computed, ref, watch } from 'vue'

const props = defineProps({
  lead: { type: Object, required: true },
  busy: { type: Boolean, default: false },
  reminderBusy: { type: Boolean, default: false },
  dragDisabled: { type: Boolean, default: false },
})

const emit = defineEmits(['request-status-change', 'save-reminder', 'clear-reminder', 'drag-start', 'drag-end'])

const reminderDayMonth = ref('')
const reminderTime = ref('')
const isDragging = ref(false)
const copiedPhoneKey = ref('')
let copiedPhoneTimer = null
const dragEnabled = computed(() => !props.busy && !props.reminderBusy && !props.dragDisabled)

const labels = {
  new: 'Biriktirilgan',
  sale: 'Sotuv',
  otkaz: 'Atkaz',
  wrong_number: 'Xato nomer',
  open_number: "O'chiq nomer",
  advice: 'Maslahat',
  other: "O'qiydi",
}

const statusLabel = computed(() => labels[props.lead?.current_status] || 'Holat')
const latestHistoryNote = computed(() => {
  const firstWithNote = Array.isArray(props.lead?.history)
    ? props.lead.history.find(item => item?.note?.trim())
    : null
  return firstWithNote?.note?.trim() || ''
})
const savedNote = computed(() => latestHistoryNote.value || props.lead?.reminder_note || '')
const hasReminder = computed(() => Boolean(props.lead?.reminder_at))
const reminderDisplay = computed(() => formatReminderText(props.lead?.reminder_at))
const canSaveReminder = computed(() => Boolean(normalizeDayMonth(reminderDayMonth.value) && reminderTime.value))
const primaryPlace = computed(() => normalizeValue(props.lead?.is_online ? props.lead?.online_region : (props.lead?.display_school || props.lead?.school)))
const secondaryPlaceValue = computed(() => normalizeValue(props.lead?.grade))
const locationChip = computed(() => props.lead?.is_online ? `Yosh: ${secondaryPlaceValue.value}` : `Sinf: ${secondaryPlaceValue.value}`)
const showStatusChip = computed(() => props.lead?.current_status === 'new')
const formattedUpdatedAt = computed(() => {
  if (!props.lead?.updated_at) return '-'
  const date = new Date(props.lead.updated_at)
  if (Number.isNaN(date.getTime())) return '-'
  return `${String(date.getDate()).padStart(2, '0')}.${String(date.getMonth() + 1).padStart(2, '0')} ${String(date.getHours()).padStart(2, '0')}:${String(date.getMinutes()).padStart(2, '0')}`
})

watch(() => [props.lead?.id, props.lead?.reminder_at], () => {
  reminderDayMonth.value = toDayMonthInput(props.lead?.reminder_at)
  reminderTime.value = toTimeInput(props.lead?.reminder_at)
}, { immediate: true })

function normalizeValue(value) {
  if (value === null || value === undefined || value === '') return '-'
  return String(value).replace(/\.0$/, '')
}

function formatPhone(value) {
  return normalizeValue(value)
}

function normalizedPhoneValue(value) {
  const formatted = formatPhone(value)
  if (!formatted || formatted === '-') return ''
  return String(formatted).trim()
}

function hasCopyablePhone(value) {
  return Boolean(normalizedPhoneValue(value))
}

async function copyPhone(value, key) {
  const phone = normalizedPhoneValue(value)
  if (!phone) return

  try {
    if (navigator?.clipboard?.writeText) {
      await navigator.clipboard.writeText(phone)
    } else {
      const textarea = document.createElement('textarea')
      textarea.value = phone
      textarea.setAttribute('readonly', '')
      textarea.style.position = 'absolute'
      textarea.style.left = '-9999px'
      document.body.appendChild(textarea)
      textarea.select()
      document.execCommand('copy')
      document.body.removeChild(textarea)
    }

    copiedPhoneKey.value = key
    if (copiedPhoneTimer) clearTimeout(copiedPhoneTimer)
    copiedPhoneTimer = setTimeout(() => {
      copiedPhoneKey.value = ''
    }, 1400)
  } catch (error) {
    console.error("Telefon raqamni nusxalab bo'lmadi", error)
  }
}

function toDayMonthInput(value) {
  if (!value) return ''
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return ''
  return `${String(date.getDate()).padStart(2, '0')}.${String(date.getMonth() + 1).padStart(2, '0')}`
}

function toTimeInput(value) {
  if (!value) return ''
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return ''
  return `${String(date.getHours()).padStart(2, '0')}:${String(date.getMinutes()).padStart(2, '0')}`
}

function normalizeDayMonth(value) {
  const raw = String(value || '').replace(/[^\d]/g, '')
  if (raw.length < 4) return ''
  const day = raw.slice(0, 2)
  const month = raw.slice(2, 4)
  const dayNum = Number(day)
  const monthNum = Number(month)
  if (Number.isNaN(dayNum) || Number.isNaN(monthNum)) return ''
  if (dayNum < 1 || dayNum > 31 || monthNum < 1 || monthNum > 12) return ''
  return `${day.padStart(2, '0')}.${month.padStart(2, '0')}`
}

function formatReminderText(value) {
  if (!value) return ''
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return ''
  return `${String(date.getDate()).padStart(2, '0')}.${String(date.getMonth() + 1).padStart(2, '0')} soat ${String(date.getHours()).padStart(2, '0')}:${String(date.getMinutes()).padStart(2, '0')}`
}

function buildReminderIso() {
  const dayMonth = normalizeDayMonth(reminderDayMonth.value)
  if (!dayMonth || !reminderTime.value) return null
  const [day, month] = dayMonth.split('.')
  const currentYear = new Date().getFullYear()
  const date = new Date(`${currentYear}-${month}-${day}T${reminderTime.value}`)
  if (Number.isNaN(date.getTime())) return null
  return date.toISOString()
}

function saveReminder() {
  if (props.busy || props.reminderBusy || !canSaveReminder.value) return
  const reminderAt = buildReminderIso()
  if (!reminderAt) return
  emit('save-reminder', { id: props.lead.id, reminder_at: reminderAt, reminder_note: '' })
}

function clearReminder() {
  if (props.busy || props.reminderBusy) return
  reminderDayMonth.value = ''
  reminderTime.value = ''
  emit('clear-reminder', { id: props.lead.id })
}

function requestStatusChange(status) {
  if (props.busy || props.reminderBusy) return
  emit('request-status-change', { lead: props.lead, status, existingNote: savedNote.value })
}

function handleDragStart(event) {
  if (!dragEnabled.value) {
    event.preventDefault()
    return
  }
  isDragging.value = true
  try {
    event.dataTransfer.effectAllowed = 'move'
    event.dataTransfer.setData('text/plain', String(props.lead?.id || ''))
  } catch {
    // ignore drag data issues
  }
  emit('drag-start', { lead: props.lead, existingNote: savedNote.value })
}

function handleDragEnd() {
  if (!dragEnabled.value) return
  isDragging.value = false
  emit('drag-end', props.lead?.id)
}
</script>

<style scoped>
.operator-compact-card {
  position: relative;
  transition: transform 0.18s ease, box-shadow 0.18s ease, opacity 0.18s ease;
}

.operator-compact-card.is-draggable {
  cursor: grab;
}

.operator-compact-card.is-dragging {
  opacity: 0.5;
  transform: rotate(1deg) scale(0.985);
}

.operator-compact-card__info-grid {
  display: grid;
  gap: 8px;
}

.operator-phone-copy-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
  width: 100%;
  min-width: 0;
  padding: 10px 12px;
  border-radius: 14px;
  border: 1px dashed rgba(148, 163, 184, 0.35);
  background: rgba(255, 255, 255, 0.55);
  text-align: left;
  transition: border-color 0.18s ease, background 0.18s ease, transform 0.18s ease, box-shadow 0.18s ease, color 0.18s ease;
}

.operator-phone-copy-row.is-copyable {
  cursor: pointer;
}

.operator-phone-copy-row.is-copyable:hover,
.operator-phone-copy-row.is-copyable:focus-visible {
  border-color: rgba(59, 130, 246, 0.5);
  background: rgba(239, 246, 255, 0.95);
  transform: translateY(-1px);
  box-shadow: 0 10px 24px rgba(37, 99, 235, 0.12);
}

.operator-phone-copy-row.is-copied {
  border-color: #2563eb;
  background: rgba(219, 234, 254, 0.95);
}

.operator-phone-copy-row:disabled {
  cursor: default;
  opacity: 0.75;
}

.operator-phone-copy-row__text {
  min-width: 0;
  word-break: break-word;
  color: #0f172a;
}

.operator-phone-copy-row__hint {
  flex-shrink: 0;
  font-size: 11px;
  font-weight: 700;
  color: #2563eb;
  white-space: nowrap;
}

.operator-phone-copy-row.is-copied .operator-phone-copy-row__hint {
  color: #1d4ed8;
}

.operator-compact-card__reminder-card {
  display: grid;
  gap: 12px;
  margin-top: 14px;
  padding: 14px;
  border-radius: 18px;
  background: rgba(255, 255, 255, 0.72);
  border: 1px solid rgba(148, 163, 184, 0.18);
}

.operator-compact-card__reminder-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
  flex-wrap: wrap;
}

.operator-compact-card__reminder-head strong {
  font-size: 13px;
  color: #0f172a;
}

.operator-compact-card__reminder-head span {
  font-size: 12px;
  color: #64748b;
}

.operator-compact-card__reminder-grid {
  display: grid;
  grid-template-columns: minmax(0, 1.15fr) minmax(0, 0.85fr);
  gap: 10px;
}

.operator-field {
  display: grid;
  gap: 6px;
}

.operator-field span {
  font-size: 11px;
  font-weight: 700;
  color: #64748b;
  text-transform: uppercase;
  letter-spacing: 0.08em;
}

.operator-compact-card__reminder-actions {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 10px;
}

.operator-compact-card__reminder-actions .mini-action {
  width: 100%;
  min-width: 0;
  justify-content: center;
}

.reminder-save {
  width: 100%;
  min-width: 0;
}

.muted-chip {
  color: #475569;
}

.operator-compact-card__note-preview {
  grid-column: 1 / -1;
}

@media (max-width: 640px) {
  .operator-phone-copy-row {
    align-items: flex-start;
    flex-direction: column;
  }

  .operator-phone-copy-row__hint {
    white-space: normal;
  }

  .operator-compact-card__reminder-grid {
    grid-template-columns: 1fr;
  }

  .operator-compact-card__reminder-actions {
    grid-template-columns: 1fr;
  }
}
</style>
