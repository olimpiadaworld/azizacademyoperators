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
        <div class="operator-compact-card__name-row">
          <h4 v-if="!isEditingName">{{ lead.full_name || 'Ism yo‘q' }}</h4>
          <form v-else class="operator-compact-card__name-edit" @submit.prevent="saveNameEdit">
            <input
              v-model="nameDraft"
              class="input input--compact"
              type="text"
              placeholder="Ism Familya"
              :disabled="nameSaving"
              @click.stop
              @mousedown.stop
              @pointerdown.stop
            />
            <button type="submit" class="mini-action mini-action--primary" :disabled="nameSaving || !nameDraft.trim()" @click.stop>
              {{ nameSaving ? '...' : 'Saqlash' }}
            </button>
            <button type="button" class="mini-action" :disabled="nameSaving" @click.stop="cancelNameEdit">Bekor</button>
          </form>
          <button
            v-if="!isEditingName"
            type="button"
            class="operator-name-edit-btn"
            title="Ism Familyani tahrirlash"
            draggable="false"
            @click.stop.prevent="startNameEdit"
            @pointerdown.stop
            @mousedown.stop.prevent
          >
            ✎
          </button>
        </div>
        <div class="operator-compact-card__chips">
          <span v-if="showStatusChip" class="operator-chip operator-chip--status">{{ statusLabel }}</span>
          <span v-if="lead.is_online" class="operator-chip">Online lead</span>
          <span v-if="lead.is_manual_entry" class="operator-chip operator-chip--incoming">Kiruvchi qo‘ng‘iroq</span>
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
          <span class="operator-phone-copy-row__hint">{{ copiedPhoneKey === 'phone1' ? '✓' : '📋' }}</span>
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
          <span class="operator-phone-copy-row__hint">{{ copiedPhoneKey === 'phone2' ? '✓' : '📋' }}</span>
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
          <span class="operator-phone-copy-row__hint">{{ copiedPhoneKey === 'phone3' ? '✓' : '📋' }}</span>
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
      <button class="status-mini sale" :disabled="busy || reminderBusy" @click="requestStatusChange('sale')"><span class="status-mini__dot"></span> Sotuv</button>
      <button class="status-mini otkaz" :disabled="busy || reminderBusy" @click="requestStatusChange('otkaz')"><span class="status-mini__dot"></span> Atkaz</button>
      <button class="status-mini wrong" :disabled="busy || reminderBusy" @click="requestStatusChange('wrong_number')"><span class="status-mini__dot"></span> Xato</button>
      <button class="status-mini open" :disabled="busy || reminderBusy" @click="requestStatusChange('open_number')"><span class="status-mini__dot"></span> O‘chiq</button>
      <button class="status-mini advice" :disabled="busy || reminderBusy" @click="requestStatusChange('advice')"><span class="status-mini__dot"></span> Maslahat</button>
      <button class="status-mini other" :disabled="busy || reminderBusy" @click="requestStatusChange('other')"><span class="status-mini__dot"></span> O'qiydi</button>
      <button class="status-mini not-answered" :disabled="busy || reminderBusy" @click="requestStatusChange('not_answered')"><span class="status-mini__dot"></span> Ko'tarmadi</button>
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

const emit = defineEmits(['request-status-change', 'save-reminder', 'clear-reminder', 'drag-start', 'drag-end', 'save-name'])

const reminderDayMonth = ref('')
const reminderTime = ref('')
const isDragging = ref(false)
const copiedPhoneKey = ref('')
let copiedPhoneTimer = null
const dragEnabled = computed(() => !props.busy && !props.reminderBusy && !props.dragDisabled)

const isEditingName = ref(false)
const nameDraft = ref('')
const nameSaving = ref(false)

function startNameEdit() {
  nameDraft.value = props.lead?.full_name || ''
  isEditingName.value = true
}

function cancelNameEdit() {
  isEditingName.value = false
  nameDraft.value = ''
}

async function saveNameEdit() {
  const value = nameDraft.value.trim()
  if (!value || nameSaving.value) return
  nameSaving.value = true
  try {
    await Promise.resolve(emit('save-name', { lead: props.lead, full_name: value }))
    isEditingName.value = false
  } finally {
    nameSaving.value = false
  }
}

const labels = {
  new: 'Biriktirilgan',
  sale: 'Sotuv',
  otkaz: 'Atkaz',
  wrong_number: 'Xato nomer',
  open_number: "O'chiq nomer",
  advice: 'Maslahat',
  other: "O'qiydi",
  not_answered: "Ko'tarmadi",
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

/* Screenshotga yaqin operator lead card dizayni */
.operator-compact-card.status-sale {
  border-color: rgba(37, 99, 235, 0.24);
  box-shadow: 0 18px 36px rgba(37, 99, 235, 0.08);
}

.operator-compact-card.status-open_number {
  border-color: rgba(34, 197, 94, 0.25);
  box-shadow: 0 18px 36px rgba(34, 197, 94, 0.08);
}

.operator-compact-card.status-advice {
  border-color: rgba(124, 58, 237, 0.22);
  box-shadow: 0 18px 36px rgba(124, 58, 237, 0.07);
}

.operator-compact-card.status-otkaz {
  border-color: rgba(239, 68, 68, 0.22);
}

.operator-compact-card.status-wrong_number {
  border-color: rgba(245, 158, 11, 0.25);
}

.operator-compact-card__head h4 {
  text-transform: uppercase;
  letter-spacing: .01em;
  font-weight: 900;
}

.operator-compact-card__time::before {
  content: '◷';
  margin-right: 6px;
  color: #64748b;
}

.operator-compact-card__info-grid {
  grid-template-columns: repeat(2, minmax(0, 1fr));
}

.operator-phone-copy-row {
  grid-column: 1 / -1;
  min-height: 36px;
  padding: 7px 10px;
  border-radius: 12px;
}

.operator-phone-copy-row__hint {
  width: 26px;
  height: 26px;
  border-radius: 8px;
  display: inline-grid;
  place-items: center;
  background: rgba(248, 250, 252, 0.94);
  border: 1px solid rgba(226, 232, 240, 0.95);
  color: #0f1f5c;
  font-size: 13px;
  line-height: 1;
}

.operator-phone-copy-row.is-copied .operator-phone-copy-row__hint {
  background: rgba(219, 234, 254, 0.95);
  color: #1d4ed8;
}

.operator-compact-card__reminder-card {
  background: linear-gradient(180deg, rgba(255,255,255,0.96), rgba(248,250,252,0.92));
}

.operator-compact-card.status-sale .reminder-save { background: linear-gradient(135deg, #2563eb, #1d4ed8); }
.operator-compact-card.status-open_number .reminder-save { background: linear-gradient(135deg, #22c55e, #16a34a); }
.operator-compact-card.status-advice .reminder-save { background: linear-gradient(135deg, #8b5cf6, #7c3aed); }
.operator-compact-card.status-otkaz .reminder-save { background: linear-gradient(135deg, #ef4444, #dc2626); }
.operator-compact-card.status-wrong_number .reminder-save { background: linear-gradient(135deg, #f59e0b, #d97706); }
.operator-compact-card.status-other .reminder-save { background: linear-gradient(135deg, #64748b, #334155); }
.operator-compact-card.status-not_answered .reminder-save { background: linear-gradient(135deg, #64748b, #334155); }

.status-mini {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.status-mini span {
  font-size: 15px;
  line-height: 1;
}

@media (max-width: 640px) {
  .operator-compact-card__info-grid {
    grid-template-columns: 1fr;
  }
}

.operator-compact-card {
  position: relative;
  padding: 18px;
  border-radius: 24px;
  background: rgba(255, 255, 255, 0.96);
  border: 1px solid rgba(226, 232, 240, 0.95);
  box-shadow: 0 16px 28px rgba(15, 23, 42, 0.05);
  transition: transform 0.18s ease, box-shadow 0.18s ease, opacity 0.18s ease;
}

.operator-compact-card.is-draggable {
  cursor: grab;
}

.operator-compact-card.is-dragging {
  opacity: 0.5;
  transform: rotate(1deg) scale(0.985);
}

.operator-compact-card__head {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  align-items: flex-start;
  margin-bottom: 14px;
}

.operator-compact-card__head h4 {
  margin: 0 0 8px;
  font-size: 18px;
  line-height: 1.25;
  color: #0f1f5c;
}

.operator-compact-card__chips {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.operator-chip {
  display: inline-flex;
  align-items: center;
  min-height: 30px;
  padding: 6px 12px;
  border-radius: 999px;
  background: rgba(239, 246, 255, 0.92);
  color: #2563eb;
  font-size: 12px;
  font-weight: 700;
  border: 1px solid rgba(191, 219, 254, 0.95);
}

.muted-chip {
  background: rgba(248,250,252,0.95);
  border-color: rgba(226,232,240,0.95);
  color: #64748b;
}

.operator-compact-card__time {
  flex-shrink: 0;
  padding: 8px 12px;
  border-radius: 999px;
  background: rgba(248,250,252,0.96);
  border: 1px solid rgba(226,232,240,0.95);
  color: #64748b;
  font-size: 12px;
  font-weight: 700;
}

.operator-compact-card__body {
  display: grid;
  gap: 14px;
}

.operator-compact-card__info-grid {
  display: grid;
  gap: 10px;
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
  border: 1px solid rgba(226,232,240,0.95);
  background: rgba(255,255,255,0.92);
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
  box-shadow: 0 10px 24px rgba(37, 99, 235, 0.1);
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

.operator-compact-card__info-grid p {
  margin: 0;
  padding: 2px 0;
  color: #334155;
  font-size: 14px;
}

.operator-compact-card__name-row {
  display: flex;
  align-items: center;
  gap: 8px;
}

.operator-name-edit-btn {
  flex-shrink: 0;
  width: 26px;
  height: 26px;
  border-radius: 8px;
  border: 1px solid rgba(148, 163, 184, 0.32);
  background: rgba(248, 250, 252, 0.92);
  color: #2563eb;
  font-size: 13px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: transform 0.14s ease, background 0.14s ease;
}

.operator-name-edit-btn:hover {
  background: #eff6ff;
  transform: translateY(-1px);
}

.operator-compact-card__name-edit {
  display: flex;
  align-items: center;
  gap: 6px;
  flex-wrap: wrap;
}

.operator-compact-card__name-edit .input--compact {
  min-width: 140px;
  height: 34px;
}

.operator-compact-card__name-edit .mini-action {
  min-height: 34px;
  padding: 0 10px;
  font-size: 12.5px;
}

.operator-chip--incoming {
  background: rgba(249, 115, 22, 0.14);
  color: #c2410c;
  border-color: rgba(249, 115, 22, 0.28);
}

.operator-compact-card__reminder-card {
  display: grid;
  gap: 12px;
  margin-top: 14px;
  padding: 14px;
  border-radius: 18px;
  background: rgba(248, 250, 252, 0.9);
  border: 1px solid rgba(226, 232, 240, 0.95);
}

.operator-compact-card__reminder-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
  flex-wrap: wrap;
}

.operator-compact-card__reminder-head strong {
  font-size: 14px;
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

.operator-compact-card__actions {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 10px;
  margin-top: 14px;
}

.status-mini {
  min-height: 44px;
  border-radius: 14px;
  font-weight: 700;
  background: #fff;
  border: 1px solid rgba(226,232,240,0.96);
  color: #0f1f5c;
}

.status-mini.sale { color: #2563eb; border-color: rgba(191,219,254,0.95); }
.status-mini.otkaz { color: #ef4444; border-color: rgba(252,165,165,0.9); }
.status-mini.wrong { color: #f59e0b; border-color: rgba(253,230,138,0.9); }
.status-mini.open { color: #16a34a; border-color: rgba(187,247,208,0.95); }
.status-mini.advice { color: #7c3aed; border-color: rgba(221,214,254,0.95); }
.status-mini.other { color: #475569; border-color: rgba(226,232,240,0.95); }
.status-mini.not-answered { color: #334155; border-color: rgba(148,163,184,0.95); }

.operator-compact-card__note-preview {
  grid-column: 1 / -1;
}

@media (max-width: 640px) {
  .operator-compact-card {
    padding: 16px;
  }

  .operator-compact-card__head {
    flex-direction: column;
  }

  .operator-phone-copy-row {
    align-items: flex-start;
    flex-direction: column;
  }

  .operator-phone-copy-row__hint {
    white-space: normal;
  }

  .operator-compact-card__reminder-grid,
  .operator-compact-card__reminder-actions,
  .operator-compact-card__actions {
    grid-template-columns: 1fr;
  }
}

/* Premium, ixcham status tugmalari */
.operator-compact-card__actions {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 8px;
  margin-top: 14px;
  padding-top: 12px;
  border-top: 1px solid rgba(226, 232, 240, 0.78);
}

.status-mini {
  min-height: 38px;
  padding: 0 12px;
  border-radius: 12px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 7px;
  border: 1px solid rgba(226, 232, 240, 0.95);
  background: rgba(255, 255, 255, 0.92);
  color: #0f1f5c;
  font-size: 13px;
  font-weight: 800;
  letter-spacing: -0.01em;
  box-shadow: 0 6px 16px rgba(15, 23, 42, 0.035);
  cursor: pointer;
  transition: transform 0.16s ease, box-shadow 0.16s ease, border-color 0.16s ease, background 0.16s ease;
}

.status-mini:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 12px 22px rgba(15, 23, 42, 0.075);
  background: #ffffff;
}

.status-mini:active:not(:disabled) {
  transform: translateY(0);
  box-shadow: 0 5px 12px rgba(15, 23, 42, 0.06);
}

.status-mini:disabled {
  cursor: not-allowed;
  opacity: 0.58;
}

.status-mini__dot {
  width: 8px;
  height: 8px;
  border-radius: 999px;
  flex: 0 0 auto;
  box-shadow: 0 0 0 4px rgba(148, 163, 184, 0.12);
}

.status-mini.sale { color: #1d4ed8; border-color: rgba(147, 197, 253, 0.7); background: rgba(239, 246, 255, 0.92); }
.status-mini.sale .status-mini__dot { background: #2563eb; box-shadow: 0 0 0 4px rgba(37, 99, 235, 0.11); }

.status-mini.otkaz { color: #dc2626; border-color: rgba(252, 165, 165, 0.68); background: rgba(254, 242, 242, 0.92); }
.status-mini.otkaz .status-mini__dot { background: #ef4444; box-shadow: 0 0 0 4px rgba(239, 68, 68, 0.11); }

.status-mini.wrong { color: #b45309; border-color: rgba(253, 230, 138, 0.75); background: rgba(255, 251, 235, 0.94); }
.status-mini.wrong .status-mini__dot { background: #f59e0b; box-shadow: 0 0 0 4px rgba(245, 158, 11, 0.12); }

.status-mini.open { color: #15803d; border-color: rgba(187, 247, 208, 0.82); background: rgba(240, 253, 244, 0.94); }
.status-mini.open .status-mini__dot { background: #22c55e; box-shadow: 0 0 0 4px rgba(34, 197, 94, 0.12); }

.status-mini.advice { color: #6d28d9; border-color: rgba(221, 214, 254, 0.86); background: rgba(245, 243, 255, 0.94); }
.status-mini.advice .status-mini__dot { background: #8b5cf6; box-shadow: 0 0 0 4px rgba(139, 92, 246, 0.12); }

.status-mini.other { color: #334155; border-color: rgba(203, 213, 225, 0.92); background: rgba(248, 250, 252, 0.95); }
.status-mini.other .status-mini__dot { background: #64748b; box-shadow: 0 0 0 4px rgba(100, 116, 139, 0.12); }

.operator-compact-card__reminder-actions {
  gap: 8px;
}

.operator-compact-card__reminder-actions .mini-action {
  min-height: 38px;
  border-radius: 12px;
  font-size: 13px;
  font-weight: 800;
  box-shadow: 0 8px 18px rgba(15, 23, 42, 0.05);
}

.operator-compact-card__reminder-actions .mini-action:not(.mini-action--primary) {
  background: rgba(255,255,255,0.92);
  color: #475569;
  border-color: rgba(226,232,240,0.95);
}

@media (max-width: 640px) {
  .operator-compact-card__actions {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .status-mini {
    min-height: 36px;
    font-size: 12px;
    padding: 0 10px;
  }
}

</style>
