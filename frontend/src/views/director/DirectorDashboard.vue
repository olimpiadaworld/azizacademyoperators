<template>
  <div class="grid director-page">
    <div class="hero glass panel">
      <div>
        <div class="eyebrow">Bosh direktor paneli</div>
        <h1 class="hero__title">Butun tizim bo'yicha nazorat</h1>
        <p class="hero__text">
          Barcha boshliqlar va operatorlarning tanlangan davr bo'yicha natijalari, kim yaxshi ishlayotgani va aloqalar
          shu yerdan kuzatiladi. Bu panel faqat ko'rish uchun — hech narsani o'zgartirib bo'lmaydi.
        </p>
      </div>
      <div class="hero__actions">
        <span class="badge muted">{{ periodLabel }}</span>
        <button class="btn secondary" :disabled="loading" @click="fetchStatistics">
          {{ loading ? 'Yangilanmoqda...' : 'Yangilash' }}
        </button>
      </div>
    </div>

    <div class="panel glass filter-panel">
      <div class="section-head section-head--wrap">
        <div>
          <div class="eyebrow">Davr filtri</div>
          <h3>Hohlagan kun yoki oyni tanlang</h3>
        </div>
      </div>
      <div class="filter-panel__modes">
        <button type="button" class="btn small" :class="{ ghost: filterMode !== 'day' }" @click="setFilterMode('day')">Bitta kun</button>
        <button type="button" class="btn small" :class="{ ghost: filterMode !== 'month' }" @click="setFilterMode('month')">Bitta oy</button>
        <button type="button" class="btn small" :class="{ ghost: filterMode !== 'range' }" @click="setFilterMode('range')">Oraliq</button>
      </div>
      <div class="filter-panel__fields">
        <label v-if="filterMode === 'day'" class="filter-field">
          <span>Kun</span>
          <input class="input" type="date" v-model="filterDate" />
        </label>
        <label v-if="filterMode === 'month'" class="filter-field">
          <span>Oy</span>
          <input class="input" type="month" v-model="filterMonth" />
        </label>
        <template v-if="filterMode === 'range'">
          <label class="filter-field">
            <span>Boshlanish sanasi</span>
            <input class="input" type="date" v-model="filterStartDate" />
          </label>
          <label class="filter-field">
            <span>Tugash sanasi</span>
            <input class="input" type="date" v-model="filterEndDate" />
          </label>
        </template>
        <button class="btn" type="button" :disabled="loading" @click="applyFilter">Qidirish</button>
        <button class="btn ghost" type="button" :disabled="loading" @click="resetFilterToToday">Bugungi kunga qaytish</button>
      </div>
    </div>

    <div v-if="error" class="error-banner">{{ error }}</div>

    <div class="grid summary-grid">
      <StatCard title="Boshliqlar" :value="summary.bosses ?? 0" subtitle="Tizimdagi boshliqlar" />
      <StatCard title="Operatorlar" :value="summary.operators ?? 0" subtitle="Faol operatorlar" />
      <StatCard title="Davr sotuvi" :value="summary.period_sale ?? 0" :subtitle="periodLabel" />
      <StatCard title="Biriktirilgan" :value="summary.total ?? 0" subtitle="Shu davrda biriktirilgan leadlar" />
      <StatCard title="Aloqa qilingan" :value="summary.touched_period ?? 0" subtitle="Shu davrda aloqa qilingan leadlar" />
      <StatCard title="Konversiya" :value="`${summary.conversion ?? 0}%`" subtitle="Sotuv / biriktirilgan" />
    </div>

    <div class="panel glass">
      <div class="section-head section-head--wrap">
        <div>
          <div class="eyebrow">{{ periodLabel }}</div>
          <h3>Statuslar bo'yicha taqsimot</h3>
        </div>
      </div>
      <div class="grid status-grid">
        <div v-for="item in statusSummaryItems" :key="item.key" class="status-chip">
          <span class="status-chip__label">{{ item.label }}</span>
          <strong class="status-chip__value">{{ item.value }}</strong>
        </div>
      </div>
    </div>

    <div class="panel glass">
      <div class="section-head section-head--wrap">
        <div>
          <div class="eyebrow">Reyting</div>
          <h3>Eng zo'r operatorlar</h3>
        </div>
        <span class="badge muted">{{ periodLabel }}</span>
      </div>

      <div v-if="topOperatorsPeriod.length" class="director-podium">
        <div
          v-for="(row, index) in topOperatorsPeriod.slice(0, 3)"
          :key="`podium-${row.operator_id}`"
          class="director-podium__card"
          :class="`director-podium__card--${index === 0 ? 'gold' : index === 1 ? 'silver' : 'bronze'}`"
        >
          <div class="director-podium__rank">#{{ index + 1 }}</div>
          <div class="director-podium__medal">{{ index === 0 ? '🥇' : index === 1 ? '🥈' : '🥉' }}</div>
          <h5>{{ row.operator_name }}</h5>
          <div class="director-podium__stats">
            <span>Boshliq: {{ row.boss_name }}</span>
            <span>Sotuv: {{ row.period_sale }}</span>
          </div>
        </div>
      </div>
      <p v-else class="empty-state">Tanlangan davrda ma'lumot yo'q.</p>

      <div v-if="topOperatorsPeriod.length > 3" class="table-wrap">
        <table>
          <thead>
            <tr>
              <th>№</th>
              <th>Operator</th>
              <th>Boshliq</th>
              <th>Sotuv</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(row, index) in topOperatorsPeriod.slice(3)" :key="`rank-rest-${row.operator_id}`">
              <td>{{ index + 4 }}</td>
              <td>{{ row.operator_name }}</td>
              <td>{{ row.boss_name }}</td>
              <td><span class="operator-sale-chip">{{ row.period_sale }}</span></td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <div class="panel glass">
      <div class="section-head section-head--wrap">
        <div>
          <div class="eyebrow">Boshliqlar kesimida</div>
          <h3>Har bir boshliq natijasi</h3>
        </div>
        <div class="lead-toolbar-info lead-toolbar-info--wrap">
          <span class="badge">Jami boshliq: {{ bossRows.length }}</span>
        </div>
      </div>
      <div class="table-wrap">
        <table>
          <thead>
            <tr>
              <th>Boshliq</th>
              <th>Operatorlar</th>
              <th>Biriktirilgan</th>
              <th>Sotuv</th>
              <th>Atkaz</th>
              <th>Maslahat</th>
              <th>Aloqa qilingan</th>
              <th>Konversiya</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="row in sortedBossRows" :key="`boss-row-${row.boss_id}`">
              <td>{{ row.boss_name }}</td>
              <td>{{ row.operator_count }}</td>
              <td>{{ row.total }}</td>
              <td><span class="operator-sale-chip">{{ row.period_sale }}</span></td>
              <td>{{ row.otkaz }}</td>
              <td>{{ row.advice }}</td>
              <td>{{ row.touched_period }}</td>
              <td>
                <div class="operator-conversion-cell">
                  <div class="operator-conversion-track">
                    <div class="operator-conversion-fill" :style="{ width: `${Math.min(row.conversion, 100)}%` }"></div>
                  </div>
                  <span>{{ row.conversion }}%</span>
                </div>
              </td>
            </tr>
            <tr v-if="!bossRows.length">
              <td colspan="8" class="empty-state">Hozircha boshliq topilmadi.</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <div class="panel glass">
      <div class="section-head section-head--wrap">
        <div>
          <div class="eyebrow">Operatorlar</div>
          <h3>Barcha operatorlar bo'yicha to'liq statistika</h3>
        </div>
        <div class="toolbar toolbar--responsive">
          <input class="input" v-model="operatorSearch" placeholder="Operator yoki boshliq qidirish..." />
          <select class="select" v-model="operatorBossFilter">
            <option value="">Barcha boshliqlar</option>
            <option v-for="row in bossRows" :key="`filter-boss-${row.boss_id}`" :value="String(row.boss_id)">
              {{ row.boss_name }}
            </option>
          </select>
        </div>
      </div>
      <div class="table-wrap">
        <table>
          <thead>
            <tr>
              <th>№</th>
              <th>Operator</th>
              <th>Boshliq</th>
              <th>Biriktirilgan</th>
              <th>Sotuv</th>
              <th>Atkaz</th>
              <th>Maslahat</th>
              <th>Ko'tarmadi</th>
              <th>Aloqa qilingan</th>
              <th>Konversiya</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(row, index) in filteredOperatorRows" :key="`op-row-${row.operator_id}`">
              <td>{{ index + 1 }}</td>
              <td>{{ row.operator_name }}</td>
              <td>{{ row.boss_name }}</td>
              <td>{{ row.total }}</td>
              <td><span class="operator-sale-chip">{{ row.period_sale }}</span></td>
              <td>{{ row.otkaz }}</td>
              <td>{{ row.advice }}</td>
              <td>{{ row.not_answered || 0 }}</td>
              <td>{{ row.touched_period }}</td>
              <td>
                <div class="operator-conversion-cell">
                  <div class="operator-conversion-track">
                    <div class="operator-conversion-fill" :style="{ width: `${Math.min(row.conversion, 100)}%` }"></div>
                  </div>
                  <span>{{ row.conversion }}%</span>
                </div>
              </td>
            </tr>
            <tr v-if="!filteredOperatorRows.length">
              <td colspan="10" class="empty-state">Operator topilmadi.</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import client from '../../api/client'
import StatCard from '../../components/ui/StatCard.vue'

const loading = ref(false)
const error = ref('')
const summary = ref({})
const bossRows = ref([])
const operatorRows = ref([])
const topOperatorsPeriod = ref([])
const periodStartDate = ref('')
const periodEndDate = ref('')

const operatorSearch = ref('')
const operatorBossFilter = ref('')

function todayIso() {
  const d = new Date()
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`
}

const filterMode = ref('day') // 'day' | 'month' | 'range'
const filterDate = ref(todayIso())
const filterMonth = ref(todayIso().slice(0, 7))
const filterStartDate = ref(todayIso())
const filterEndDate = ref(todayIso())

const statusLabels = {
  new: 'Biriktirilgan',
  sale: 'Sotuv',
  otkaz: 'Atkaz',
  wrong_number: 'Xato nomer',
  open_number: "O'chiq nomer",
  advice: 'Maslahat',
  other: "O'qiydi",
  not_answered: "Ko'tarmadi",
}

const statusSummaryItems = computed(() => (
  Object.entries(statusLabels).map(([key, label]) => ({ key, label, value: summary.value[key] || 0 }))
))

function formatDisplayDate(iso) {
  if (!iso) return ''
  const [year, month, day] = iso.split('-')
  if (!year || !month || !day) return iso
  return `${day}.${month}.${year}`
}

const periodLabel = computed(() => {
  if (!periodStartDate.value) return "Ma'lumot yuklanmoqda..."
  if (periodStartDate.value === periodEndDate.value) {
    return `${formatDisplayDate(periodStartDate.value)} kuni`
  }
  return `${formatDisplayDate(periodStartDate.value)} — ${formatDisplayDate(periodEndDate.value)}`
})

const sortedBossRows = computed(() => (
  bossRows.value.slice().sort((a, b) => b.period_sale - a.period_sale)
))

const filteredOperatorRows = computed(() => {
  const search = operatorSearch.value.trim().toLowerCase()
  return operatorRows.value
    .filter((row) => {
      const bossOk = !operatorBossFilter.value || String(row.boss_id) === operatorBossFilter.value
      if (!bossOk) return false
      if (!search) return true
      return [row.operator_name, row.boss_name].some(value => String(value || '').toLowerCase().includes(search))
    })
    .slice()
    .sort((a, b) => b.period_sale - a.period_sale)
})

function setFilterMode(mode) {
  filterMode.value = mode
}

function applyFilter() {
  fetchStatistics()
}

function resetFilterToToday() {
  filterMode.value = 'day'
  filterDate.value = todayIso()
  fetchStatistics()
}

function buildFilterParams() {
  if (filterMode.value === 'day') {
    return { date: filterDate.value }
  }
  if (filterMode.value === 'month') {
    return { month: filterMonth.value }
  }
  return { start_date: filterStartDate.value, end_date: filterEndDate.value }
}

async function fetchStatistics() {
  loading.value = true
  error.value = ''
  try {
    const { data } = await client.get('director/statistics/', { params: buildFilterParams() })
    summary.value = data.summary || {}
    bossRows.value = data.boss_rows || []
    operatorRows.value = data.operator_rows || []
    topOperatorsPeriod.value = data.top_operators_period || []
    periodStartDate.value = data.start_date || ''
    periodEndDate.value = data.end_date || ''
  } catch (e) {
    error.value = e.response?.data?.detail || 'Statistikani yuklashda xatolik yuz berdi.'
  } finally {
    loading.value = false
  }
}

onMounted(fetchStatistics)
</script>

<style scoped>
.filter-panel__modes {
  display: flex;
  gap: 8px;
  margin-bottom: 14px;
  flex-wrap: wrap;
}

.filter-panel__fields {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
  align-items: flex-end;
}

.filter-field {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.filter-field span {
  font-size: 12px;
  font-weight: 700;
  color: #64748b;
  text-transform: uppercase;
  letter-spacing: 0.06em;
}

.summary-grid {
  grid-template-columns: repeat(auto-fit, minmax(190px, 1fr));
}

.status-grid {
  grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
  gap: 12px;
}

.status-chip {
  display: flex;
  flex-direction: column;
  gap: 6px;
  padding: 14px 16px;
  border-radius: 16px;
  background: rgba(148, 163, 184, 0.08);
  border: 1px solid rgba(148, 163, 184, 0.16);
}

.status-chip__label {
  font-size: 12.5px;
  color: #64748b;
  font-weight: 600;
}

.status-chip__value {
  font-size: 24px;
  font-weight: 800;
  color: #0f172a;
}

.director-toggle {
  display: flex;
  gap: 8px;
}

.director-podium {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 14px;
  margin-bottom: 20px;
}

.director-podium__card {
  position: relative;
  padding: 20px;
  border-radius: 18px;
  color: white;
  display: flex;
  flex-direction: column;
  gap: 8px;
  overflow: hidden;
}

.director-podium__card--gold {
  background: linear-gradient(135deg, #92610a, #f5b301 62%, #fde68a 100%);
}

.director-podium__card--silver {
  background: linear-gradient(135deg, #1f2937, #64748b 62%, #cbd5e1 100%);
}

.director-podium__card--bronze {
  background: linear-gradient(135deg, #2b2118, #7c4a2d 58%, #f97316 100%);
}

.director-podium__rank {
  width: fit-content;
  padding: 6px 12px;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.16);
  font-size: 12px;
  font-weight: 700;
  letter-spacing: .08em;
}

.director-podium__medal {
  font-size: 32px;
  line-height: 1;
}

.director-podium__card h5 {
  margin: 0;
  font-size: 19px;
}

.director-podium__stats {
  display: grid;
  gap: 4px;
  font-size: 13px;
  opacity: 0.95;
}

.operator-sale-chip {
  display: inline-flex;
  min-width: 44px;
  justify-content: center;
  padding: 8px 12px;
  border-radius: 999px;
  background: linear-gradient(90deg, #2563eb, #38bdf8);
  color: white;
  font-weight: 800;
}

.operator-sale-chip--daily {
  background: linear-gradient(90deg, #f97316, #fbbf24);
}

.operator-conversion-cell {
  display: grid;
  gap: 8px;
  min-width: 110px;
}

.operator-conversion-track {
  height: 6px;
  border-radius: 999px;
  background: rgba(148, 163, 184, 0.24);
  overflow: hidden;
}

.operator-conversion-fill {
  height: 100%;
  border-radius: 999px;
  background: linear-gradient(90deg, #2563eb, #38bdf8);
}
</style>
