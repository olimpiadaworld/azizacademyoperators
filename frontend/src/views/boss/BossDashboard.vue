<template>
  <div class="grid boss-page">
    <div v-if="successMessage" class="success-banner">{{ successMessage }}</div>
    <div v-if="error" class="error-banner">{{ error }}</div>

    <div v-if="currentView === 'leads' && isCompactSwiperViewport" class="operator-swiper glass-soft stats-mobile-swiper">
      <div class="operator-swiper__head">
        <div>
          <div class="eyebrow">Asosiy ko'rsatkichlar</div>
          <strong>{{ isFilialRahbari ? "Filial rahbari kartalari" : "Operatorlar kartalari" }}</strong>
          <div class="operator-swiper__meta">{{ topStatsCurrentPositionLabel }}</div>
        </div>
        <div class="operator-swiper__controls">
          <button class="swiper-arrow" type="button" @click="prevTopStatsSlide" :disabled="!topStatsCanSlide" aria-label="Oldingi ko'rsatkich">←</button>
          <button class="swiper-arrow" type="button" @click="nextTopStatsSlide" :disabled="!topStatsCanSlide" aria-label="Keyingi ko'rsatkich">→</button>
        </div>
      </div>
      <div class="operator-swiper__viewport">
        <div class="operator-swiper__track" :style="topStatsTrackStyle">
          <div v-for="card in dashboardSummaryCards" :key="`top-stat-${card.title}`" class="operator-swiper__slide">
            <StatCard :title="card.title" :value="card.value" :subtitle="card.subtitle" />
          </div>
        </div>
      </div>
    </div>
    <div v-else-if="currentView === 'leads' && isFilialRahbari" class="grid cards">
      <StatCard title="Sotuvlar" :value="leads.length" subtitle="Ko'rish mumkin bo'lgan sotuvlar" />
      <StatCard title="Keldi" :value="arrivedCount" subtitle="Belgilangan kelganlar" />
      <StatCard title="Kelmadi" :value="notArrivedCount" subtitle="Belgilangan kelmaganlar" />
      <StatCard title="Huquq" :value="0" subtitle="Telegram lead va operator yaratish yopiq" />
    </div>
    <div v-else-if="currentView === 'leads'" class="grid cards">
      <StatCard title="Operatorlar" :value="operators.length" subtitle="Faol operatorlar" />
      <StatCard title="Harakatlar" :value="totalActionsToday" subtitle="Bugungi actionlar" />
      <StatCard title="Aloqa qilingan" :value="totalTouchedToday" subtitle="Bugun ishlangan leadlar" />
      <StatCard title="Online leadlar" :value="onlineLeads.length" subtitle="Biriktirilmagan yangi leadlar" />
    </div>

    <div v-if="currentView === 'leads' && !isFilialRahbari" class="panel glass">
      <div class="section-head">
        <div>
          <div class="eyebrow">Import</div>
          <h3>Leadlarni operatorga biriktirish</h3>
        </div>
      </div>
      <div class="toolbar toolbar--responsive">
        <select class="select" v-model="selectedOperator">
          <option disabled value="">Operator tanlang</option>
          <option value="all">Hammasiga</option>
          <option v-for="operator in operators" :key="operator.id" :value="String(operator.id)">{{ operator.full_name || operator.username }}</option>
        </select>
        <input type="file" @change="onFile" accept=".xlsx" class="input" />
        <button class="btn" @click="uploadFile">Excel yuklash</button>
      </div>
      <div class="file-box">Faqat .xlsx fayl. Ustunlar: №, T/SH, Maktab, Sinf, F.I.O, Fan, Ball, tel1, tel2, tel3. Ixtiyoriy: Filial</div>
      <div v-if="importResult" class="import-result-error" style="margin-top: 12px">
        {{ importResult }}
      </div>
    </div>

    <div v-if="!isFilialRahbari && currentView === 'online'" class="panel glass online-leads-panel">
      <div class="section-head section-head--wrap">
        <div>
          <div class="eyebrow">Online Leadlar</div>
          <h3>Saytdan kelgan yozuvlar</h3>
        </div>
        <div class="toolbar toolbar--compact">
          <input v-model="onlineSearch" class="input" placeholder="Ism yoki nomer bo‘yicha qidiring" @input="debouncedFetchOnlineLeads" />
          <select class="select" v-model="bulkOperatorId">
            <option disabled value="">Operator tanlang</option>
            <option value="all">Hammasiga</option>
            <option v-for="operator in operators" :key="`bulk-${operator.id}`" :value="String(operator.id)">
              {{ operator.full_name || operator.username }}
            </option>
          </select>
          <button class="btn" :disabled="bulkAssignLoading || !bulkOperatorId || !onlineLeads.length" @click="bulkAssignOnlineLeads">
            {{ bulkAssignLoading ? 'Biriktirilmoqda...' : 'Barchasini biriktirish' }}
          </button>
        </div>
      </div>

      <div v-if="!onlineLeads.length" class="empty-state">Online leadlar hali yo‘q.</div>
      <div v-else class="online-lead-grid">
        <article v-for="lead in onlineLeads" :key="lead.id" class="online-lead-card glass-soft">
          <div class="online-lead-card__head">
            <div>
              <h4>{{ lead.full_name || 'F.I.O kiritilmagan' }}</h4>
              <div class="online-lead-card__meta-row">
                <span class="badge">{{ lead.subject || lead.interest_subject || 'Fan kiritilmagan' }}</span>
                <span class="badge muted">{{ lead.grade || 'Sinf yo‘q' }}</span>
              </div>
            </div>
            <span class="badge">{{ formatDateTime(lead.submitted_at) }}</span>
          </div>
          <div class="online-lead-card__body">
            <span><strong>T/SH:</strong> {{ lead.tsh || '-' }}</span>
            <span><strong>Maktab:</strong> {{ lead.school || lead.display_school || '-' }}</span>
            <span><strong>Sinf:</strong> {{ lead.grade || '-' }}</span>
            <span><strong>F.I.O:</strong> {{ lead.full_name || '-' }}</span>
            <span><strong>Fan:</strong> {{ lead.subject || lead.interest_subject || '-' }}</span>
            <span><strong>tel1:</strong> {{ lead.phone1 || '-' }}</span>
            <span><strong>tel2:</strong> {{ lead.phone2 || '-' }}</span>
            <span><strong>tel3:</strong> {{ lead.phone3 || '-' }}</span>
          </div>
          <div class="online-lead-card__actions">
            <button class="btn ghost" @click="openAssignModal(lead)">Biriktirish</button>
          </div>
        </article>
      </div>
    </div>

    <div v-if="currentView === 'leads'" class="panel glass panel--relative panel--lead-section">
      <div v-if="loadingLeads" class="panel-loader-overlay">
        <div class="loader-ring"></div>
        <p>{{ loadingMessage }}</p>
      </div>

      <div class="section-head section-head--wrap" :class="{ 'content-dim': loadingLeads }">
        <div>
          <div class="eyebrow">Leadlar</div>
          <h3>{{ isFilialRahbari ? "Sotuvlar bo'limi" : "Statuslar bo'yicha leadlar" }}</h3>
        </div>
        <div class="toolbar toolbar--compact" :class="{ 'toolbar--boss-filters': !isFilialRahbari }">
          <select v-if="!isFilialRahbari" class="select" v-model="selectedOperatorFilter" :disabled="loadingLeads" @change="refreshLeadSections('Operator bo‘yicha filtrlanmoqda...')">
            <option value="all">Barcha operatorlar</option>
            <option v-for="operator in operators" :key="operator.id" :value="String(operator.id)">
              {{ operator.full_name || operator.username }}
            </option>
          </select>
          <div class="search-inline">
            <input
              v-model="searchText"
              class="input"
              :disabled="loadingLeads"
              placeholder="Lead qidirish"
              @keyup.enter="applyLeadSearch"
            />
            <button class="btn ghost" type="button" :disabled="loadingLeads" @click="applyLeadSearch">Qidirish</button>
            <button v-if="searchText" class="btn ghost" type="button" :disabled="loadingLeads" @click="clearLeadSearch">Tozalash</button>
          </div>
          <template v-if="!isFilialRahbari">
            <input class="input" type="date" v-model="selectedLeadDate" :disabled="loadingLeads" />
            <button v-if="selectedLeadDate" class="btn ghost" :disabled="loadingLeads" @click="clearLeadDateFilter">Tozalash</button>
          </template>
        </div>
      </div>

      <div class="lead-toolbar-info lead-toolbar-info--wrap" :class="{ 'content-dim': loadingLeads }">
        <span class="badge">{{ filteredSummaryText }}</span>
        <template v-if="!isFilialRahbari">
          <span class="badge">{{ leadDateFilterLabel }}</span>
          <span class="badge muted">Ko'rinayotgan: {{ totalVisibleStatusLeads }} ta</span>
        </template>
      </div>

      <div v-if="!loadingLeads && !currentLeadListCount" class="empty-state">
        Bu bo'limda hozircha lead yo'q.
      </div>

      <template v-else-if="isFilialRahbari">
        <div v-if="undecidedLeads.length" class="operator-swiper glass-soft filial-swiper" :class="{ 'content-dim': loadingLeads }">
          <div class="operator-swiper__head">
            <div>
              <div class="eyebrow">Sotuv cardlari</div>
              <strong>{{ filialCurrentPositionLabel }}</strong>
              <div class="operator-swiper__meta">Qolgan cardlar: {{ undecidedLeads.length }} ta</div>
            </div>
            <div class="operator-swiper__controls">
              <button class="swiper-arrow" type="button" @click="prevFilialSlide" :disabled="!filialCanSlide || loadingLeads" aria-label="Oldingi cardlar">←</button>
              <button class="swiper-arrow" type="button" @click="nextFilialSlide" :disabled="!filialCanSlide || loadingLeads" aria-label="Keyingi cardlar">→</button>
            </div>
          </div>

          <div class="operator-swiper__viewport">
            <div class="operator-swiper__track" :style="filialTrackStyle">
              <div v-for="lead in undecidedLeads" :key="lead.id" class="operator-swiper__slide">
                <article class="visit-mini-card glass">
                  <div class="visit-mini-card__head visit-mini-card__head--payment">
                    <span :class="['payment-dot', lead.payment_done ? 'is-paid' : 'is-unpaid']" :title="lead.payment_done ? 'To‘lov qilindi' : 'To‘lov qilinmadi'"></span>
                    <div>
                      <h4>{{ lead.full_name || "Ism yo'q" }}</h4>
                      <div class="boss-lead-item__chips">
                        <span class="badge">{{ currentStatusTitle }}</span>
                        <span class="badge muted">{{ lead.operator_name || 'Operator biriktirilmagan' }}</span>
                        <span :class="['badge', lead.payment_done ? 'payment-paid-badge' : 'payment-unpaid-badge']">{{ lead.payment_done ? 'To‘lov qilindi' : 'To‘lov qilinmadi' }}</span>
                      </div>
                    </div>
                  </div>
                  <div class="visit-mini-card__meta">
                    <span><strong>tel1:</strong> {{ lead.phone1 || '-' }}</span>
                    <span><strong>tel2:</strong> {{ lead.phone2 || '-' }}</span>
                    <span><strong>tel3:</strong> {{ lead.phone3 || '-' }}</span>
                    <span><strong>T/SH:</strong> {{ lead.tsh || '-' }}</span>
                    <span><strong>Maktab:</strong> {{ lead.display_school || lead.school || '-' }}</span>
                    <span><strong>Sinf:</strong> {{ lead.grade || '-' }}</span>
                    <span><strong>Fan:</strong> {{ lead.subject || '-' }}</span>
                    <span><strong>Ball:</strong> {{ lead.ball || '-' }}</span>
                    <span v-if="lead.operator_note" class="operator-note-line"><strong>Operator izohi:</strong> {{ lead.operator_note }}</span>
                    <span v-if="lead.operator_note_at" class="operator-note-line"><strong>Izoh vaqti:</strong> {{ formatDateTime(lead.operator_note_at) }}</span>
                    <span><strong>To‘lov:</strong> {{ lead.payment_done ? 'To‘lov qilindi' : 'To‘lov qilinmadi' }}</span>
                    <span v-if="lead.payment_done_at"><strong>To‘lov vaqti:</strong> {{ formatDateTime(lead.payment_done_at) }}</span>
                  </div>
                  <div class="visit-mini-card__actions">
                    <button class="btn" :disabled="decisionLoadingId === lead.id" @click="submitVisitDecision(lead.id, 'arrived')">
                      {{ decisionLoadingId === lead.id && pendingDecision === 'arrived' ? 'Saqlanmoqda...' : 'Keldi' }}
                    </button>
                    <button class="btn secondary" :disabled="decisionLoadingId === lead.id" @click="submitVisitDecision(lead.id, 'not_arrived')">
                      {{ decisionLoadingId === lead.id && pendingDecision === 'not_arrived' ? 'Saqlanmoqda...' : 'Kelmadi' }}
                    </button>
                  </div>
                </article>
              </div>
            </div>
          </div>
        </div>
        <div v-else class="empty-state">Ko‘rinadigan sotuvlar qolmadi. Keldi bosilgan leadlar barcha rahbarlardan yopiladi, Kelmadi bosilganlari faqat sizdan yopiladi.</div>
      </template>

      <template v-else>
        <div class="status-sections status-sections--board" :class="{ 'content-dim': loadingLeads }">
          <section
            v-for="card in statusCards"
            :key="`section-${card.key}`"
            class="status-section status-section--column"
            :class="[`status-${card.key}`]"
          >
            <div class="status-section__head status-section__head--column">
              <div class="status-section__arc"></div>
              <div class="status-section__title-wrap">
                <h3>{{ card.title }}</h3>
                <span class="badge muted">{{ getVisibleStatusLeads(card.key).length }} ta lead</span>
              </div>
            </div>

            <div v-if="getVisibleStatusLeads(card.key).length" class="status-card-stack">
              <article v-for="lead in getVisibleStatusLeads(card.key)" :key="`${card.key}-${lead.id}`" class="boss-lead-item glass boss-lead-item--status boss-lead-item--compact" :class="[`status-${card.key}`]">
                <div class="boss-lead-item__head boss-lead-item__head--compact">
                  <div>
                    <h4>{{ lead.full_name || "Ism yo'q" }}</h4>
                    <div class="boss-lead-item__chips boss-lead-item__chips--compact">
                      <span class="badge">{{ card.title }}</span>
                      <span v-if="lead.is_online" class="badge">Online lead</span>
                      <span class="badge muted">{{ lead.branch_name || lead.operator_name || 'Biriktirilmagan' }}</span>
                    </div>
                  </div>
                </div>
                <div class="boss-lead-item__meta boss-lead-item__meta--compact">
                  <span><strong>tel1:</strong> {{ lead.phone1 || '-' }}</span>
                  <span><strong>tel2:</strong> {{ lead.phone2 || '-' }}</span>
                  <span><strong>tel3:</strong> {{ lead.phone3 || '-' }}</span>
                  <span v-if="!lead.is_online"><strong>T/SH:</strong> {{ lead.tsh || '-' }}</span>
                  <span><strong>{{ lead.is_online ? 'Hudud' : 'Maktab' }}:</strong> {{ lead.is_online ? (lead.online_region || '-') : (lead.display_school || lead.school || '-') }}</span>
                  <span><strong>{{ lead.is_online ? 'Yosh' : 'Sinf' }}:</strong> {{ lead.age || lead.grade || '-' }}</span>
                  <span v-if="!lead.is_online"><strong>Fan:</strong> {{ lead.subject || '-' }}</span>
                  <span v-if="!lead.is_online"><strong>Ball:</strong> {{ lead.ball || '-' }}</span>
                  <span v-if="lead.reminder_at"><strong>Vaqt:</strong> {{ formatLeadReminder(lead) }}</span>
                  <span v-if="getLeadLatestNote(lead)"><strong>Izoh:</strong> {{ getLeadLatestNote(lead) }}</span>
                </div>
              </article>
            </div>
            <div v-else class="empty-state empty-state--status">Bu bo'limda hozircha lead yo'q.</div>
          </section>
        </div>
      </template>
    </div>

    <div v-if="isFilialRahbari && currentView === 'manager'" class="panel glass">
      <div class="section-head section-head--wrap">
        <div>
          <div class="eyebrow">Keldi / Kelmadi qismi</div>
          <h3>Belgilangan sotuvlar</h3>
        </div>
        <div class="decision-filter-stack">
          <div class="decision-filter-group">
            <button class="decision-filter-btn" :class="{ active: filialDecisionFilter === 'all' }" @click="filialDecisionFilter = 'all'">Hammasi</button>
            <button class="decision-filter-btn" :class="{ active: filialDecisionFilter === 'arrived' }" @click="filialDecisionFilter = 'arrived'">Keldi</button>
            <button class="decision-filter-btn" :class="{ active: filialDecisionFilter === 'not_arrived' }" @click="filialDecisionFilter = 'not_arrived'">Kelmadi</button>
          </div>
          <div class="decision-filter-group payment-filter-group">
            <button class="decision-filter-btn" :class="{ active: filialPaymentFilter === 'all' }" @click="filialPaymentFilter = 'all'">To‘lov: hammasi</button>
            <button class="decision-filter-btn" :class="{ active: filialPaymentFilter === 'paid' }" @click="filialPaymentFilter = 'paid'">To‘lov qildi</button>
            <button class="decision-filter-btn" :class="{ active: filialPaymentFilter === 'unpaid' }" @click="filialPaymentFilter = 'unpaid'">To‘lov qilmadi</button>
          </div>
        </div>
      </div>
      <div class="lead-toolbar-info">
        <span class="badge">Jami: {{ decidedLeads.length }} ta</span>
        <span class="badge not-arrived-badge">Kelmaganlar: {{ ownNotArrivedLeads.length }} ta</span>
        <span class="badge payment-paid-badge">To‘lov qildi: {{ filialPaymentDoneCount }}</span>
        <span class="badge payment-unpaid-badge">To‘lov qilmadi: {{ filialPaymentNotDoneCount }}</span>
        <span class="badge muted">Ko'rinayotgan: {{ filteredDecidedLeads.length }} ta</span>
      </div>

      <div v-if="ownNotArrivedLeads.length" class="table-wrap decision-stats-table">
        <table>
          <thead>
            <tr>
              <th colspan="10">Kelmaganlar qatori — faqat siz Kelmadi bosgan leadlar</th>
            </tr>
            <tr>
              <th>F.I.O</th>
              <th>tel1</th>
              <th>tel2</th>
              <th>tel3</th>
              <th>T/SH</th>
              <th>Maktab</th>
              <th>Sinf</th>
              <th>Fan</th>
              <th>Ball</th>
              <th>Vaqt</th>
              <th>To‘lov</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="lead in ownNotArrivedLeads" :key="`own-not-arrived-${lead.id}`">
              <td>{{ lead.full_name || '-' }}</td>
              <td>{{ lead.phone1 || '-' }}</td>
              <td>{{ lead.phone2 || '-' }}</td>
              <td>{{ lead.phone3 || '-' }}</td>
              <td>{{ lead.tsh || '-' }}</td>
              <td>{{ lead.display_school || lead.school || '-' }}</td>
              <td>{{ lead.grade || '-' }}</td>
              <td>{{ lead.subject || '-' }}</td>
              <td>{{ lead.ball || '-' }}</td>
              <td>{{ formatDateTime(lead.updated_at) }}</td>
              <td><span :class="['payment-pill', lead.payment_done ? 'is-paid' : 'is-unpaid']">{{ lead.payment_done ? 'To‘lov qilindi' : 'To‘lov qilinmadi' }}</span></td>
            </tr>
          </tbody>
        </table>
      </div>

      <div v-if="!filteredDecidedLeads.length" class="empty-state">Bu filter bo'yicha belgilangan lead yo'q.</div>
      <template v-else>
        <div v-if="isCompactSwiperViewport" class="operator-swiper glass-soft lead-mobile-swiper filial-decision-swiper">
          <div class="operator-swiper__head">
            <div>
              <div class="eyebrow">Keldi / Kelmadi swiper</div>
              <strong>{{ filialDecisionCurrentPositionLabel }}</strong>
              <div class="operator-swiper__meta">Jami cardlar: {{ filteredDecidedLeads.length }} ta</div>
            </div>
            <div class="operator-swiper__controls">
              <button class="swiper-arrow" type="button" @click="prevFilialDecisionSlide" :disabled="!filialDecisionCanSlide" aria-label="Oldingi belgilangan card">←</button>
              <button class="swiper-arrow" type="button" @click="nextFilialDecisionSlide" :disabled="!filialDecisionCanSlide" aria-label="Keyingi belgilangan card">→</button>
            </div>
          </div>
          <div class="operator-swiper__viewport">
            <div class="operator-swiper__track" :style="filialDecisionTrackStyle">
              <div v-for="lead in filteredDecidedLeads" :key="`decided-${lead.id}`" class="operator-swiper__slide">
                <article class="visit-mini-card glass">
                  <div class="visit-mini-card__head">
                    <div>
                      <h4>{{ lead.full_name || "Ism yo'q" }}</h4>
                      <div class="boss-lead-item__chips">
                        <span class="badge">{{ (lead.decision || visitDecisionMap[lead.id]) === 'arrived' ? 'Keldi' : 'Kelmadi' }}</span>
                        <span class="badge muted">{{ lead.operator_name || 'Operator biriktirilmagan' }}</span>
                      </div>
                    </div>
                  </div>
                  <div class="visit-mini-card__meta">
                    <span><strong>tel1:</strong> {{ lead.phone1 || '-' }}</span>
                    <span><strong>tel2:</strong> {{ lead.phone2 || '-' }}</span>
                    <span><strong>tel3:</strong> {{ lead.phone3 || '-' }}</span>
                    <span><strong>T/SH:</strong> {{ lead.tsh || '-' }}</span>
                    <span><strong>Maktab:</strong> {{ lead.display_school || lead.school || '-' }}</span>
                    <span><strong>Sinf:</strong> {{ lead.grade || '-' }}</span>
                    <span><strong>Fan:</strong> {{ lead.subject || '-' }}</span>
                    <span><strong>Ball:</strong> {{ lead.ball || '-' }}</span>
                    <span v-if="lead.operator_note" class="operator-note-line"><strong>Operator izohi:</strong> {{ lead.operator_note }}</span>
                    <span v-if="lead.operator_note_at" class="operator-note-line"><strong>Izoh vaqti:</strong> {{ formatDateTime(lead.operator_note_at) }}</span>
                  </div>
                  <div class="visit-mini-card__actions">
                    <button class="btn" :class="{ 'is-active-choice': visitDecisionMap[lead.id] === 'arrived' }" :disabled="decisionLoadingId === lead.id" @click="submitVisitDecision(lead.id, 'arrived')">Keldi</button>
                    <button class="btn secondary" :class="{ 'is-active-choice': visitDecisionMap[lead.id] === 'not_arrived' }" :disabled="decisionLoadingId === lead.id" @click="submitVisitDecision(lead.id, 'not_arrived')">Kelmadi</button>
                    <button class="btn payment-btn" :class="{ 'is-active-choice': lead.payment_done }" :disabled="paymentLoadingId === lead.id || lead.payment_done" @click="markPaymentDone(lead.id)">{{ lead.payment_done ? 'To‘lov qilindi' : 'To‘lov qilindi' }}</button>
                  </div>
                </article>
              </div>
            </div>
          </div>
        </div>
        <div v-else class="boss-lead-list boss-lead-list--compact">
          <article v-for="lead in filteredDecidedLeads" :key="`decided-${lead.id}`" class="visit-mini-card glass">
            <div class="visit-mini-card__head visit-mini-card__head--payment">
              <span :class="['payment-dot', lead.payment_done ? 'is-paid' : 'is-unpaid']" :title="lead.payment_done ? 'To‘lov qilindi' : 'To‘lov qilinmadi'"></span>
              <div>
                <h4>{{ lead.full_name || "Ism yo'q" }}</h4>
                <div class="boss-lead-item__chips">
                  <span class="badge">{{ (lead.decision || visitDecisionMap[lead.id]) === 'arrived' ? 'Keldi' : 'Kelmadi' }}</span>
                  <span class="badge muted">{{ lead.operator_name || 'Operator biriktirilmagan' }}</span>
                  <span :class="['badge', lead.payment_done ? 'payment-paid-badge' : 'payment-unpaid-badge']">{{ lead.payment_done ? 'To‘lov qilindi' : 'To‘lov qilinmadi' }}</span>
                </div>
              </div>
            </div>
            <div class="visit-mini-card__meta">
              <span><strong>tel1:</strong> {{ lead.phone1 || '-' }}</span>
              <span><strong>tel2:</strong> {{ lead.phone2 || '-' }}</span>
              <span><strong>tel3:</strong> {{ lead.phone3 || '-' }}</span>
              <span><strong>T/SH:</strong> {{ lead.tsh || '-' }}</span>
              <span><strong>Maktab:</strong> {{ lead.display_school || lead.school || '-' }}</span>
              <span><strong>Sinf:</strong> {{ lead.grade || '-' }}</span>
              <span><strong>Fan:</strong> {{ lead.subject || '-' }}</span>
              <span><strong>Ball:</strong> {{ lead.ball || '-' }}</span>
                    <span v-if="lead.operator_note" class="operator-note-line"><strong>Operator izohi:</strong> {{ lead.operator_note }}</span>
                    <span v-if="lead.operator_note_at" class="operator-note-line"><strong>Izoh vaqti:</strong> {{ formatDateTime(lead.operator_note_at) }}</span>
              <span><strong>To‘lov:</strong> {{ lead.payment_done ? 'To‘lov qilindi' : 'To‘lov qilinmadi' }}</span>
              <span v-if="lead.payment_done_at"><strong>To‘lov vaqti:</strong> {{ formatDateTime(lead.payment_done_at) }}</span>
            </div>
            <div class="visit-mini-card__actions">
              <button class="btn" :class="{ 'is-active-choice': visitDecisionMap[lead.id] === 'arrived' }" :disabled="decisionLoadingId === lead.id" @click="submitVisitDecision(lead.id, 'arrived')">Keldi</button>
              <button class="btn secondary" :class="{ 'is-active-choice': visitDecisionMap[lead.id] === 'not_arrived' }" :disabled="decisionLoadingId === lead.id" @click="submitVisitDecision(lead.id, 'not_arrived')">Kelmadi</button>
              <button class="btn payment-btn" :class="{ 'is-active-choice': lead.payment_done }" :disabled="paymentLoadingId === lead.id || lead.payment_done" @click="markPaymentDone(lead.id)">{{ lead.payment_done ? 'To‘lov qilindi' : 'To‘lov qilindi' }}</button>
            </div>
          </article>
        </div>
      </template>
    </div>

    <div v-if="!isFilialRahbari && currentView === 'manager'" class="panel glass panel--manager-section">
      <div class="section-divider">
        <span class="section-divider__line"></span>
        <span class="section-divider__label">Leadlardan alohida nazorat bo‘limi</span>
        <span class="section-divider__line"></span>
      </div>
      <div class="section-head section-head--wrap">
        <div>
          <div class="eyebrow">Filial Rahbari nazorati</div>
          <h3>Keldi / Kelmadi belgilari</h3>
        </div>
        <div class="decision-panel-tools">
          <div class="decision-filter-stack">
            <div class="decision-filter-group">
              <button class="decision-filter-btn" :class="{ active: bossDecisionFilter === 'all' }" @click="bossDecisionFilter = 'all'">Hammasi</button>
              <button class="decision-filter-btn" :class="{ active: bossDecisionFilter === 'arrived' }" @click="bossDecisionFilter = 'arrived'">Keldi</button>
              <button class="decision-filter-btn" :class="{ active: bossDecisionFilter === 'not_arrived' }" @click="bossDecisionFilter = 'not_arrived'">Kelmadi</button>
            </div>
            <div class="decision-filter-group payment-filter-group">
              <button class="decision-filter-btn" :class="{ active: bossPaymentFilter === 'all' }" @click="bossPaymentFilter = 'all'">To‘lov: hammasi</button>
              <button class="decision-filter-btn" :class="{ active: bossPaymentFilter === 'paid' }" @click="bossPaymentFilter = 'paid'">To‘lov qildi</button>
              <button class="decision-filter-btn" :class="{ active: bossPaymentFilter === 'unpaid' }" @click="bossPaymentFilter = 'unpaid'">To‘lov qilmadi</button>
            </div>
          </div>
          <div class="decision-date-filter decision-date-filter--stacked">
            <select class="select" v-model="selectedBossRahbariFilter">
              <option value="all">Barcha filial rahbarlari</option>
              <option v-for="rahbar in bossRahbariOptions" :key="`rahbar-${rahbar.value}`" :value="rahbar.value">
                {{ rahbar.label }}
              </option>
            </select>
            <div class="decision-date-filter__row">
              <input class="input" type="date" v-model="selectedBossDecisionDate" />
              <button v-if="selectedBossDecisionDate || selectedBossRahbariFilter !== 'all'" class="btn ghost" @click="clearBossDecisionFilters">Tozalash</button>
            </div>
          </div>
        </div>
      </div>
      <div class="lead-toolbar-info lead-toolbar-info--wrap">
        <span class="badge">{{ bossDecisionDateLabel }}</span>
        <span class="badge">{{ bossDecisionRahbariLabel }}</span>
        <span class="badge">Jami: {{ scopedBossVisitDecisions.length }} ta</span>
        <span class="badge arrived-badge">Keldi: {{ bossArrivedCount }}</span>
        <span class="badge not-arrived-badge">Kelmadi: {{ bossNotArrivedCount }}</span>
        <span class="badge payment-paid-badge">To‘lov qildi: {{ bossPaymentDoneCount }}</span>
        <span class="badge payment-unpaid-badge">To‘lov qilmadi: {{ bossPaymentNotDoneCount }}</span>
        <span class="badge muted">Ko'rinayotgan: {{ filteredBossVisitDecisions.length }} ta</span>
      </div>

      <div class="decision-summary-grid">
        <article v-for="card in bossDecisionSummaryCards" :key="`boss-decision-summary-${card.title}`" class="decision-summary-card glass-soft">
          <span>{{ card.title }}</span>
          <strong>{{ card.value }}</strong>
          <small>{{ card.subtitle }}</small>
        </article>
      </div>

      <div v-if="bossRahbariDecisionStats.length" class="table-wrap decision-stats-table">
        <table>
          <thead>
            <tr>
              <th>Filial rahbari</th>
              <th>Jami</th>
              <th>Keldi</th>
              <th>Kelmadi</th>
              <th>To‘lov qildi</th>
              <th>To‘lov qilmadi</th>
              <th>Oxirgi belgi</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="row in bossRahbariDecisionStats" :key="`decision-stat-${row.key}`">
              <td>{{ row.name }}</td>
              <td>{{ row.total }}</td>
              <td>{{ row.arrived }}</td>
              <td>{{ row.not_arrived }}</td>
              <td>{{ row.payment_done }}</td>
              <td>{{ row.payment_not_done }}</td>
              <td>{{ formatDateTime(row.last_updated_at) }}</td>
            </tr>
          </tbody>
        </table>
      </div>

      <div v-if="!filteredBossVisitDecisions.length" class="empty-state">Filial rahbaridan hali belgi kelmagan.</div>
      <template v-else>
        <div v-if="isCompactSwiperViewport" class="operator-swiper glass-soft lead-mobile-swiper manager-mobile-swiper">
          <div class="operator-swiper__head">
            <div>
              <div class="eyebrow">Nazorat swiper</div>
              <strong>{{ bossDecisionCurrentPositionLabel }}</strong>
              <div class="operator-swiper__meta">Jami cardlar: {{ filteredBossVisitDecisions.length }} ta</div>
            </div>
            <div class="operator-swiper__controls">
              <button class="swiper-arrow" type="button" @click="prevBossDecisionSlide" :disabled="!bossDecisionCanSlide" aria-label="Oldingi nazorat cardi">←</button>
              <button class="swiper-arrow" type="button" @click="nextBossDecisionSlide" :disabled="!bossDecisionCanSlide" aria-label="Keyingi nazorat cardi">→</button>
            </div>
          </div>

          <div class="operator-swiper__viewport">
            <div class="operator-swiper__track" :style="bossDecisionTrackStyle">
              <div v-for="item in filteredBossVisitDecisions" :key="item.id" class="operator-swiper__slide">
                <div class="visit-mini-card glass">
                  <div class="visit-mini-card__head visit-mini-card__head--payment">
                    <span :class="['payment-dot', item.payment_done ? 'is-paid' : 'is-unpaid']" :title="item.payment_done ? 'To‘lov qilindi' : 'To‘lov qilinmadi'"></span>
                    <div>
                      <h4>{{ item.lead_name }}</h4>
                      <div class="boss-lead-item__chips">
                        <span class="badge">{{ item.decision === 'arrived' ? 'Keldi' : 'Kelmadi' }}</span>
                        <span class="badge muted">{{ item.filial_rahbari_name }}</span>
                        <span :class="['badge', item.payment_done ? 'payment-paid-badge' : 'payment-unpaid-badge']">{{ item.payment_done ? 'To‘lov qilindi' : 'To‘lov qilinmadi' }}</span>
                      </div>
                    </div>
                    <span class="badge">{{ formatDateTime(item.updated_at) }}</span>
                  </div>
                  <div class="visit-mini-card__meta">
                    <span><strong>tel1:</strong> {{ item.lead_phone || '-' }}</span>
                    <span><strong>tel2:</strong> {{ item.lead_phone2 || '-' }}</span>
                    <span><strong>tel3:</strong> {{ item.lead_phone3 || '-' }}</span>
                    <span><strong>T/SH:</strong> {{ item.tsh || '-' }}</span>
                    <span><strong>Maktab:</strong> {{ item.display_school || item.school || '-' }}</span>
                    <span><strong>Sinf:</strong> {{ item.grade || '-' }}</span>
                    <span><strong>Fan:</strong> {{ item.subject || '-' }}</span>
                    <span><strong>Ball:</strong> {{ item.ball || '-' }}</span>
                    <span v-if="item.operator_note" class="operator-note-line"><strong>Operator izohi:</strong> {{ item.operator_note }}</span>
                    <span v-if="item.operator_note_at" class="operator-note-line"><strong>Izoh vaqti:</strong> {{ formatDateTime(item.operator_note_at) }}</span>
                    <span><strong>Operator:</strong> {{ item.operator_name || '-' }}</span>
                    <span><strong>Holat:</strong> {{ item.decision === 'arrived' ? 'Keldi' : 'Kelmadi' }}</span>
                    <span><strong>To‘lov:</strong> {{ item.payment_done ? 'To‘lov qilindi' : 'To‘lov qilinmadi' }}</span>
                    <span v-if="item.payment_done_by_name"><strong>To‘lov qilgan:</strong> {{ item.payment_done_by_name }}</span>
                    <span v-if="item.payment_done_at"><strong>To‘lov vaqti:</strong> {{ formatDateTime(item.payment_done_at) }}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div v-else class="boss-lead-list boss-lead-list--compact">
          <div v-for="item in filteredBossVisitDecisions" :key="item.id" class="visit-mini-card glass">
            <div class="visit-mini-card__head visit-mini-card__head--payment">
              <span :class="['payment-dot', item.payment_done ? 'is-paid' : 'is-unpaid']" :title="item.payment_done ? 'To‘lov qilindi' : 'To‘lov qilinmadi'"></span>
              <div>
                <h4>{{ item.lead_name }}</h4>
                <div class="boss-lead-item__chips">
                  <span class="badge">{{ item.decision === 'arrived' ? 'Keldi' : 'Kelmadi' }}</span>
                  <span class="badge muted">{{ item.filial_rahbari_name }}</span>
                  <span :class="['badge', item.payment_done ? 'payment-paid-badge' : 'payment-unpaid-badge']">{{ item.payment_done ? 'To‘lov qilindi' : 'To‘lov qilinmadi' }}</span>
                </div>
              </div>
              <span class="badge">{{ formatDateTime(item.updated_at) }}</span>
            </div>
            <div class="visit-mini-card__meta">
              <span><strong>tel1:</strong> {{ item.lead_phone || '-' }}</span>
              <span><strong>tel2:</strong> {{ item.lead_phone2 || '-' }}</span>
              <span><strong>tel3:</strong> {{ item.lead_phone3 || '-' }}</span>
              <span><strong>Holat:</strong> {{ item.decision === 'arrived' ? 'Keldi' : 'Kelmadi' }}</span>
              <span><strong>To‘lov:</strong> {{ item.payment_done ? 'To‘lov qilindi' : 'To‘lov qilinmadi' }}</span>
              <span v-if="item.payment_done_by_name"><strong>To‘lov qilgan:</strong> {{ item.payment_done_by_name }}</span>
              <span v-if="item.payment_done_at"><strong>To‘lov vaqti:</strong> {{ formatDateTime(item.payment_done_at) }}</span>
            </div>
          </div>
        </div>
      </template>

      <section v-if="bossNotArrivedDecisions.length" class="panel glass-soft decision-detail-panel">
        <div class="section-head section-head--wrap">
          <div>
            <div class="eyebrow">Kelmadi bo'lganlar</div>
            <h4>Kimlar kelmadi — to'liq ma'lumot</h4>
          </div>
          <span class="badge not-arrived-badge">Jami: {{ bossNotArrivedDecisions.length }} ta</span>
        </div>
        <div class="table-wrap decision-detail-table">
          <table>
            <thead>
              <tr>
                <th>Filial rahbari</th>
                <th>F.I.O</th>
                <th>tel1</th>
                <th>tel2</th>
                <th>tel3</th>
                <th>T/SH</th>
                <th>Maktab</th>
                <th>Sinf</th>
                <th>Fan</th>
                <th>Ball</th>
                <th>Operator</th>
                <th>Vaqt</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="item in bossNotArrivedDecisions" :key="`not-arrived-detail-${item.id}`">
                <td>{{ item.filial_rahbari_name || '-' }}</td>
                <td>{{ item.lead_name || item.full_name || '-' }}</td>
                <td>{{ item.lead_phone || item.phone1 || '-' }}</td>
                <td>{{ item.lead_phone2 || item.phone2 || '-' }}</td>
                <td>{{ item.lead_phone3 || item.phone3 || '-' }}</td>
                <td>{{ item.tsh || '-' }}</td>
                <td>{{ item.display_school || item.school || '-' }}</td>
                <td>{{ item.grade || '-' }}</td>
                <td>{{ item.subject || '-' }}</td>
                <td>{{ item.ball || '-' }}</td>
                <td>{{ item.operator_name || '-' }}</td>
                <td>{{ formatDateTime(item.updated_at) }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>
    </div>

    <div v-if="!isFilialRahbari && currentView === 'operators'" class="panel glass">
      <div class="section-head section-head--wrap">
        <div>
          <div class="eyebrow">Operatorlar</div>
          <h3>Operator statistikasi</h3>
        </div>
      </div>

      <template v-if="sortedStatistics.length">
        <div class="operator-sales-chart glass-soft">
          <div class="operator-sales-chart__head">
            <div>
              <div class="eyebrow">Diagramma</div>
              <h4>Kim nechta sotuv qilgani</h4>
            </div>
            <div class="operator-sales-chart__summary">
              <span class="badge">Jami sotuv: {{ totalSalesCount }}</span>
              <span class="badge muted">Eng faol: {{ topSalesOperatorLabel }}</span>
            </div>
          </div>

          <div class="operator-sales-chart__list">
            <article v-for="row in salesChartData" :key="`operator-sale-chart-${row.operator_id}`" class="operator-sales-chart__item">
              <div class="operator-sales-chart__labels">
                <strong>{{ row.operator_name }}</strong>
                <span>{{ row.sale }} ta</span>
              </div>
              <div class="operator-sales-chart__bar-wrap">
                <div class="operator-sales-chart__bar" :style="{ width: getSalesBarWidth(row.sale) }"></div>
              </div>
            </article>
          </div>
        </div>

        <div v-if="operatorDonutSegments.length" class="operator-donut-card glass-soft">
          <div class="operator-donut-card__head">
            <div>
              <div class="eyebrow">Qo‘shimcha diagramma</div>
              <h4>Sotuvlar ulushi</h4>
            </div>
            <span class="badge">{{ operatorDonutSegments.length }} ta bo‘lim</span>
          </div>

          <div class="operator-donut-card__body">
            <div class="operator-donut-chart">
              <svg viewBox="0 0 180 180" aria-label="Operator sotuvlari donut diagrammasi">
                <circle class="operator-donut-chart__track" cx="90" cy="90" r="66" />
                <circle
                  v-for="segment in operatorDonutSegments"
                  :key="`operator-donut-${segment.key}`"
                  class="operator-donut-chart__segment"
                  cx="90"
                  cy="90"
                  r="66"
                  :stroke="segment.color"
                  :stroke-dasharray="segment.dasharray"
                  :stroke-dashoffset="segment.dashoffset"
                />
              </svg>
              <div class="operator-donut-chart__center">
                <strong>{{ totalSalesCount }}</strong>
                <span>jami sotuv</span>
              </div>
            </div>

            <div class="operator-donut-legend">
              <article
                v-for="segment in operatorDonutSegments"
                :key="`operator-donut-legend-${segment.key}`"
                class="operator-donut-legend__item"
              >
                <span class="operator-donut-legend__dot" :style="{ background: segment.color }"></span>
                <div class="operator-donut-legend__text">
                  <strong>{{ segment.operator_name }}</strong>
                  <span>{{ segment.sale }} ta • {{ formatPercent(segment.percent) }}</span>
                </div>
              </article>
            </div>
          </div>
        </div>

        <div v-if="topThreeOperators.length" class="operator-podium glass-soft">
          <div class="operator-podium__head">
            <div>
              <div class="eyebrow">Premium reyting</div>
              <h4>Eng kuchli operatorlar</h4>
            </div>
            <span class="badge">Top {{ topThreeOperators.length }}</span>
          </div>

          <div class="operator-podium__grid">
            <article
              v-for="(row, index) in topThreeOperators"
              :key="`operator-podium-${row.operator_id}`"
              class="operator-podium__card"
              :class="getPodiumToneClass(index)"
            >
              <div class="operator-podium__rank">#{{ index + 1 }}</div>
              <div class="operator-podium__medal">{{ podiumMedals[index] }}</div>
              <h5>{{ row.operator_name }}</h5>
              <div class="operator-podium__stats">
                <span><strong>{{ row.sale }}</strong> sotuv</span>
                <span><strong>{{ row.total }}</strong> jami</span>
                <span><strong>{{ row.conversion }}%</strong> conversion</span>
              </div>
            </article>
          </div>
        </div>
      </template>
      <div v-else class="empty-state">Operator statistikasi hali yo‘q.</div>

      <div v-if="isCompactSwiperViewport && sortedStatistics.length" class="operator-swiper glass-soft stats-mobile-swiper stats-mobile-swiper--operators">
        <div class="operator-swiper__head">
          <div>
            <div class="eyebrow">Operatorlar swiper</div>
            <strong>Operator statistikasi</strong>
            <div class="operator-swiper__meta">{{ operatorStatsCurrentPositionLabel }}</div>
          </div>
          <div class="operator-swiper__controls">
            <button class="swiper-arrow" type="button" @click="prevOperatorStatsSlide" :disabled="!operatorStatsCanSlide" aria-label="Oldingi operator">←</button>
            <button class="swiper-arrow" type="button" @click="nextOperatorStatsSlide" :disabled="!operatorStatsCanSlide" aria-label="Keyingi operator">→</button>
          </div>
        </div>
        <div class="operator-swiper__viewport">
          <div class="operator-swiper__track" :style="operatorStatsTrackStyle">
            <div v-for="(row, index) in sortedStatistics" :key="`operator-stat-card-${row.operator_id}`" class="operator-swiper__slide">
              <article class="operator-stat-card glass-soft" :class="getOperatorTierClass(index)">
                <div class="operator-stat-card__head">
                  <div class="operator-stat-card__title"><span class="operator-rank-badge">#{{ index + 1 }}</span><h4>{{ row.operator_name }}</h4></div>
                  <span class="badge">{{ row.conversion }}%</span>
                </div>
                <div class="operator-stat-card__grid">
                  <span><strong>Jami:</strong> {{ row.total }}</span>
                  <span><strong>Sotuv:</strong> {{ row.sale }}</span>
                  <span><strong>Harakat:</strong> {{ row.actions_today }}</span>
                  <span><strong>Aloqa:</strong> {{ row.touched_today }}</span>
                  <span><strong>Maslahat:</strong> {{ row.advice }}</span>
                  <span><strong>O'qiydi:</strong> {{ row.other }}</span>
                </div>
              </article>
            </div>
          </div>
        </div>
      </div>
      <div v-else class="table-wrap operator-premium-table-wrap">
        <table class="operator-premium-table">
          <thead>
            <tr>
              <th>№</th>
              <th>Operator</th>
              <th>Jami</th>
              <th>Sotuv</th>
              <th>Harakat</th>
              <th>Aloqa qilingan</th>
              <th>Maslahat</th>
              <th>O'qiydi</th>
              <th>Conversion</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(row, index) in sortedStatistics" :key="row.operator_id" :class="['operator-premium-row', getOperatorTierClass(index)]">
              <td>
                <div class="operator-rank-cell">
                  <span class="operator-rank-badge">#{{ index + 1 }}</span>
                  <span v-if="index < 3" class="operator-rank-medal">{{ podiumMedals[index] }}</span>
                </div>
              </td>
              <td>
                <div class="operator-name-cell">
                  <strong>{{ row.operator_name }}</strong>
                  <small v-if="index === 0">Eng ko'p sotuv</small>
                  <small v-else-if="index === 1">2-o'rin</small>
                  <small v-else-if="index === 2">3-o'rin</small>
                  <small v-else>Faol operator</small>
                </div>
              </td>
              <td>{{ row.total }}</td>
              <td><span class="operator-sale-chip">{{ row.sale }}</span></td>
              <td>{{ row.actions_today }}</td>
              <td>{{ row.touched_today }}</td>
              <td>{{ row.advice }}</td>
              <td>{{ row.other }}</td>
              <td>
                <div class="operator-conversion-cell">
                  <strong>{{ row.conversion }}%</strong>
                  <div class="operator-conversion-track">
                    <div class="operator-conversion-fill" :style="{ width: formatConversionWidth(row.conversion) }"></div>
                  </div>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <div v-if="!isFilialRahbari && showFullReportModal" class="modal-overlay modal-overlay--report">
      <div class="modal-card glass report-modal">
        <div class="modal-card__head">
          <div>
            <div class="eyebrow">Barcha narsa bo'yicha hisobot</div>
            <h3>Umumiy nazorat va kesimlar</h3>
          </div>
          <button class="modal-close" @click="closeFullReportModal">×</button>
        </div>

        <div class="toolbar toolbar--responsive report-filter-bar">
          <select class="select" v-model="fullReportOperatorId">
            <option value="">Barcha operatorlar</option>
            <option v-for="operator in operators" :key="`full-report-operator-${operator.id}`" :value="String(operator.id)">
              {{ operator.full_name || operator.username }}
            </option>
          </select>
          <div class="report-filter-field">
            <label>Dan</label>
            <input class="input" type="date" v-model="fullReportStartDate" />
          </div>
          <div class="report-filter-field">
            <label>Gacha</label>
            <input class="input" type="date" v-model="fullReportEndDate" />
          </div>
          <button class="btn" :disabled="fullReportLoading" @click="fetchFullReport">{{ fullReportLoading ? 'Yangilanmoqda...' : "Hisobotni ko'rish" }}</button>
          <button class="btn secondary" :disabled="fullReportExcelLoading || fullReportLoading" @click="downloadFullReportExcel">{{ fullReportExcelLoading ? 'Excel tayyorlanmoqda...' : 'Excel yuklash' }}</button>
          <button v-if="fullReportStartDate || fullReportEndDate || fullReportOperatorId" class="btn ghost" :disabled="fullReportLoading || fullReportExcelLoading" @click="clearFullReportFilters">Tozalash</button>
        </div>

        <div v-if="fullReportData" class="report-modal__body">
          <div class="lead-toolbar-info lead-toolbar-info--wrap">
            <span class="badge">Oraliq: {{ fullReportRangeLabel }}</span>
            <span class="badge">Operator: {{ fullReportData.selected_operator?.name || 'Barchasi' }}</span>
            <span class="badge">Online kelgan: {{ fullReportData.summary.online_submitted }}</span>
            <span class="badge">Online biriktirilgan: {{ fullReportData.summary.online_assigned }}</span>
            <span class="badge arrived-badge">Keldi: {{ fullReportData.summary.arrived }}</span>
            <span class="badge not-arrived-badge">Kelmadi: {{ fullReportData.summary.not_arrived }}</span>
          </div>

          <div class="report-stats-grid">
            <article class="report-stat-card glass-soft"><span>Lead biriktirildi</span><strong>{{ fullReportData.summary.assigned_leads }}</strong></article>
            <article class="report-stat-card glass-soft"><span>Sotildi</span><strong>{{ fullReportData.summary.sale }}</strong></article>
            <article class="report-stat-card glass-soft"><span>Atkaz</span><strong>{{ fullReportData.summary.otkaz }}</strong></article>
            <article class="report-stat-card glass-soft"><span>Xato nomer</span><strong>{{ fullReportData.summary.wrong_number }}</strong></article>
            <article class="report-stat-card glass-soft"><span>O'chiq nomer</span><strong>{{ fullReportData.summary.open_number }}</strong></article>
            <article class="report-stat-card glass-soft"><span>Maslahat</span><strong>{{ fullReportData.summary.advice }}</strong></article>
            <article class="report-stat-card glass-soft"><span>O'qiydi</span><strong>{{ fullReportData.summary.other }}</strong></article>
            <article class="report-stat-card glass-soft"><span>Jami action</span><strong>{{ fullReportData.summary.actions_total }}</strong></article>
          </div>

          <div class="report-section-grid">
            <section class="panel glass-soft">
              <div class="section-head">
                <div>
                  <div class="eyebrow">Kim tomondan</div>
                  <h4>Operatorlar kesimi</h4>
                </div>
              </div>
              <div class="table-wrap report-table-wrap">
                <table>
                  <thead>
                    <tr>
                      <th>Operator</th>
                      <th>Biriktirildi</th>
                      <th>Online</th>
                      <th>Sotuv</th>
                      <th>Atkaz</th>
                      <th>Maslahat</th>
                      <th>O'qiydi</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="row in fullReportData.operators" :key="`report-op-${row.operator_id}`">
                      <td>{{ row.operator_name }}</td>
                      <td>{{ row.assigned_leads }}</td>
                      <td>{{ row.online_assigned }}</td>
                      <td>{{ row.sale }}</td>
                      <td>{{ row.otkaz }}</td>
                      <td>{{ row.advice }}</td>
                      <td>{{ row.other }}</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </section>

            <section class="panel glass-soft">
              <div class="section-head">
                <div>
                  <div class="eyebrow">Kim tomondan</div>
                  <h4>Filial rahbarlari kesimi</h4>
                </div>
              </div>
              <div class="table-wrap report-table-wrap">
                <table>
                  <thead>
                    <tr>
                      <th>Filial rahbari</th>
                      <th>Jami</th>
                      <th>Keldi</th>
                      <th>Kelmadi</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="row in fullReportData.filial_rahbarlari" :key="`report-fr-${row.filial_rahbari_id || row.filial_rahbari_name}`">
                      <td>{{ row.filial_rahbari_name }}</td>
                      <td>{{ row.total }}</td>
                      <td>{{ row.arrived }}</td>
                      <td>{{ row.not_arrived }}</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </section>
          </div>

          <section class="panel glass-soft">
            <div class="section-head">
              <div>
                <div class="eyebrow">Sanalari bilan</div>
                <h4>Kunlik kesim</h4>
              </div>
            </div>
            <div class="table-wrap report-table-wrap">
              <table>
                <thead>
                  <tr>
                    <th>Sana</th>
                    <th>Biriktirildi</th>
                    <th>Sotuv</th>
                    <th>Atkaz</th>
                    <th>Xato</th>
                    <th>O'chiq</th>
                    <th>Maslahat</th>
                    <th>O'qiydi</th>
                    <th>Online keldi</th>
                    <th>Online biriktirildi</th>
                    <th>Keldi</th>
                    <th>Kelmadi</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="row in fullReportData.daily" :key="`report-day-${row.date}`">
                    <td>{{ formatInputDate(row.date) }}</td>
                    <td>{{ row.assigned_leads }}</td>
                    <td>{{ row.sale }}</td>
                    <td>{{ row.otkaz }}</td>
                    <td>{{ row.wrong_number }}</td>
                    <td>{{ row.open_number }}</td>
                    <td>{{ row.advice }}</td>
                    <td>{{ row.other }}</td>
                    <td>{{ row.online_submitted }}</td>
                    <td>{{ row.online_assigned }}</td>
                    <td>{{ row.arrived }}</td>
                    <td>{{ row.not_arrived }}</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </section>
        </div>
      </div>
    </div>

    <div v-if="!isFilialRahbari && openOperatorModal" class="modal-overlay">
      <div class="modal-card glass">
        <div class="modal-card__head">
          <div>
            <div class="eyebrow">Yangi operator</div>
            <h3>Operator yaratish</h3>
          </div>
          <button class="modal-close" @click="closeOperatorModal">×</button>
        </div>
        <form class="grid" @submit.prevent="createOperator">
          <input v-model="operatorForm.username" class="input" placeholder="Login kiriting" />
          <input v-model="operatorForm.password" type="password" class="input" placeholder="Parol kiriting" />
          <div class="branch-picker">
            <label>Filial biriktiring</label>
            <div class="branch-picker__grid">
              <label v-for="branch in branchOptions" :key="`operator-${branch.value}`" class="branch-check">
                <input type="checkbox" :value="branch.value" v-model="operatorForm.branch_names" />
                <span>{{ branch.label }}</span>
              </label>
            </div>
          </div>
          <button class="btn full">Yaratish</button>
        </form>
      </div>
    </div>

    <div v-if="!isFilialRahbari && assignLead" class="modal-overlay">
      <div class="modal-card glass">
        <div class="modal-card__head">
          <div>
            <div class="eyebrow">Online lead</div>
            <h3>Qaysi operatorga biriktirmoqchisiz?</h3>
          </div>
          <button class="modal-close" @click="closeAssignModal">×</button>
        </div>
        <div class="grid">
          <div class="file-box"><strong>{{ assignLead.full_name }}</strong> • {{ assignLead.phone1 }} • {{ assignLead.interest_subject }}</div>
          <select class="select" v-model="assignOperatorId">
            <option disabled value="">Operator tanlang</option>
            <option v-for="operator in operators" :key="`assign-${operator.id}`" :value="String(operator.id)">
              {{ operator.full_name || operator.username }}
            </option>
          </select>
          <button class="btn full" :disabled="assignLoading || !assignOperatorId" @click="assignOnlineLead">
            {{ assignLoading ? 'Tasdiqlanmoqda...' : 'Tasdiqlash' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, onBeforeUnmount, onMounted, reactive, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '../../stores/auth'
import client from '../../api/client'
import StatCard from '../../components/ui/StatCard.vue'

const auth = useAuthStore()
const route = useRoute()
const router = useRouter()
const isFilialRahbari = computed(() => auth.role === 'filial_rahbari')
const operators = ref([])
const statistics = ref([])
const leads = ref([])
const statusLeadBuckets = ref({ sale: [], otkaz: [], wrong_number: [], open_number: [], advice: [], other: [] })
const onlineLeads = ref([])
const visitDecisions = ref([])
const visitDecisionMap = ref({})
const currentView = ref('leads')
const loadingLeads = ref(false)
const loadingMessage = ref('Leadlar yuklanmoqda...')
const selectedFile = ref(null)
const selectedOperator = ref('')
const selectedOperatorFilter = ref('all')
const selectedLeadDate = ref('')
const successMessage = ref('')
const error = ref('')
const importResult = ref('')
const searchText = ref('')
const onlineSearch = ref('')
const openOperatorModal = ref(false)
const activeStatus = ref('sale')
const statusKeys = ['sale', 'otkaz', 'wrong_number', 'open_number', 'advice', 'other']
const viewportWidth = ref(typeof window !== 'undefined' ? window.innerWidth : 1400)
const currentFilialSlide = ref(0)
const currentFilialDecisionSlide = ref(0)
const currentBossLeadSlide = ref(0)
const currentBossDecisionSlide = ref(0)
const currentTopStatsSlide = ref(0)
const currentOperatorStatsSlide = ref(0)
const filialDecisionFilter = ref('all')
const filialPaymentFilter = ref('all')
const bossDecisionFilter = ref('all')
const bossPaymentFilter = ref('all')
const selectedBossDecisionDate = ref('')
const selectedBossRahbariFilter = ref('all')
const reportLoading = ref(false)
const fullReportExcelLoading = ref(false)
const showFullReportModal = ref(false)
const fullReportLoading = ref(false)
const fullReportData = ref(null)
const fullReportOperatorId = ref('')
const fullReportStartDate = ref('')
const fullReportEndDate = ref('')
const assignLead = ref(null)
const assignOperatorId = ref('')
const assignLoading = ref(false)
const bulkOperatorId = ref('')
const bulkAssignLoading = ref(false)
const decisionLoadingId = ref(null)
const paymentLoadingId = ref(null)
const pendingDecision = ref('')
const operatorForm = reactive({ username: '', password: '', branch_names: [] })
const branchOptions = [
  {
    "label": "Niyozbosh — Iroda",
    "value": "Niyozbosh",
    "leader": "Iroda"
  },
  {
    "label": "Kids 1 — Lobar",
    "value": "Kids 1",
    "leader": "Lobar"
  },
  {
    "label": "Kids 2 — Doniyor",
    "value": "Kids 2",
    "leader": "Doniyor"
  },
  {
    "label": "Gulbahor — Anvar",
    "value": "Gulbahor",
    "leader": "Anvar"
  },
  {
    "label": "Kids 3 — Nafisa",
    "value": "Kids 3",
    "leader": "Nafisa"
  },
  {
    "label": "Kasblar — Nigora",
    "value": "Kasblar",
    "leader": "Nigora"
  },
  {
    "label": "Xalqobod — Nilufar",
    "value": "Xalqobod",
    "leader": "Nilufar"
  },
  {
    "label": "Chinoz — Hudobergan",
    "value": "Chinoz",
    "leader": "Hudobergan"
  },
  {
    "label": "Olmozor — Suhrob",
    "value": "Olmozor",
    "leader": "Suhrob"
  },
  {
    "label": "Paxtazor — Abdulloh",
    "value": "Paxtazor",
    "leader": "Abdulloh"
  },
  {
    "label": "Mevazor — Dinara",
    "value": "Mevazor",
    "leader": "Dinara"
  },
  {
    "label": "Dostobod — Shoxriddin",
    "value": "Dostobod",
    "leader": "Shoxriddin"
  },
  {
    "label": "Qorg'onchi — Shoxriddin",
    "value": "Qorg'onchi",
    "leader": "Shoxriddin"
  },
  {
    "label": "Oqqo'rg'on — Odilbek",
    "value": "Oqqo'rg'on",
    "leader": "Odilbek"
  },
  {
    "label": "Qo'shyog'och",
    "value": "Qo'shyog'och",
    "leader": ""
  }
]
let successTimer = null
let searchTimer = null
let onlineSearchTimer = null
let filialRefreshTimer = null

const sleep = (ms) => new Promise(resolve => setTimeout(resolve, ms))

const statusMap = {
  sale: { title: 'Sotuvlar', subtitle: "Muvaffaqiyatli sotuvlar ro'yxati" },
  otkaz: { title: 'Atkaz', subtitle: "Qayta aloqa va o'tkaz holatlari" },
  wrong_number: { title: 'Xato nomer', subtitle: "Noto'g'ri raqamlar" },
  open_number: { title: "O'chiq Nomer", subtitle: "Aloqa bo'lmagan leadlar" },
  advice: { title: 'Maslahat', subtitle: 'Maslahat berilgan leadlar' },
  other: { title: "O'qiydi", subtitle: "O'qiydi natijadagi leadlar" },
}

const heroTitle = computed(() => isFilialRahbari.value ? 'Sotuvlar bo‘yicha filial nazorati' : 'Operatorlar va leadlar nazorati')
const heroText = computed(() => isFilialRahbari.value
  ? 'Bu panelda faqat sotuvlarni ko‘rasiz. Har bir sotuv cardida Keldi yoki Kelmadi tugmasi bor. Telegramdan kelgan leadlar va operator yaratish huquqi yopilgan.'
  : 'Operator yarating, excel yuklang, statuslar bo‘yicha leadlarni ko‘ring va online leadlarni operatorlarga biriktiring.')

const statusCards = computed(() => {
  if (isFilialRahbari.value) {
    return [{ key: 'sale', title: 'Sotuvlar', subtitle: 'Filial rahbari uchun ochiq bo‘lim', value: leads.value.length }]
  }

  const totals = statistics.value.reduce((acc, item) => {
    acc.sale += item.sale
    acc.otkaz += item.otkaz
    acc.wrong_number += item.wrong_number
    acc.open_number += item.open_number
    acc.advice += item.advice
    acc.other += item.other
    return acc
  }, { sale: 0, otkaz: 0, wrong_number: 0, open_number: 0, advice: 0, other: 0 })

  return Object.entries(statusMap).map(([key, meta]) => ({
    key,
    title: meta.title,
    subtitle: meta.subtitle,
    value: totals[key] || 0,
  }))
})

const currentStatusTitle = computed(() => statusMap[activeStatus.value]?.title || 'Leadlar')
function getVisibleStatusLeads(statusKey) {
  const source = statusLeadBuckets.value[statusKey] || []
  if (!selectedLeadDate.value) return source
  return source.filter(lead => toInputDate(lead.updated_at) === selectedLeadDate.value)
}
const totalVisibleStatusLeads = computed(() => statusKeys.reduce((sum, key) => sum + getVisibleStatusLeads(key).length, 0))
const visibleLeads = computed(() => {
  if (isFilialRahbari.value || !selectedLeadDate.value) return leads.value
  return leads.value.filter(lead => toInputDate(lead.updated_at) === selectedLeadDate.value)
})
const currentLeadListCount = computed(() => (isFilialRahbari.value ? leads.value.length : totalVisibleStatusLeads.value))
const leadDateFilterLabel = computed(() => selectedLeadDate.value ? `${formatInputDate(selectedLeadDate.value)} bo'yicha` : 'Barcha kunlar')
const filteredSummaryText = computed(() => {
  if (isFilialRahbari.value) return `Sotuvlar • ${leads.value.length} ta lead`
  const operatorName = selectedOperatorFilter.value === 'all'
    ? 'Barcha operatorlar'
    : (operators.value.find(item => String(item.id) === selectedOperatorFilter.value)?.full_name || 'Operator')
  return `${operatorName} • ${leads.value.length} ta lead`
})
const totalActionsToday = computed(() => statistics.value.reduce((sum, item) => sum + (item.actions_today || 0), 0))
const totalTouchedToday = computed(() => statistics.value.reduce((sum, item) => sum + (item.touched_today || 0), 0))
const sortedStatistics = computed(() => ([...statistics.value]
  .sort((a, b) => {
    const saleDiff = Number(b.sale || 0) - Number(a.sale || 0)
    if (saleDiff) return saleDiff
    const conversionDiff = Number(b.conversion || 0) - Number(a.conversion || 0)
    if (conversionDiff) return conversionDiff
    const touchedDiff = Number(b.touched_today || 0) - Number(a.touched_today || 0)
    if (touchedDiff) return touchedDiff
    return (a.operator_name || '').localeCompare(b.operator_name || '', 'uz')
  })))
const topThreeOperators = computed(() => sortedStatistics.value.slice(0, 3))
const podiumMedals = ['🥇', '🥈', '🥉']
const salesChartData = computed(() => (sortedStatistics.value
  .map(item => ({
    operator_id: item.operator_id,
    operator_name: item.operator_name,
    sale: Number(item.sale || 0),
    total: Number(item.total || 0),
    conversion: Number(item.conversion || 0),
  }))))
const donutPalette = ['#4f7cff', '#ff6b6b', '#22c55e', '#a855f7', '#06b6d4', '#f97316', '#84cc16', '#ec4899', '#14b8a6', '#e11d48']
const donutCircumference = 2 * Math.PI * 66
const maxOperatorSales = computed(() => Math.max(0, ...salesChartData.value.map(item => item.sale || 0)))
const totalSalesCount = computed(() => salesChartData.value.reduce((sum, item) => sum + item.sale, 0))
const operatorDonutSegments = computed(() => {
  const positiveRows = salesChartData.value.filter(item => item.sale > 0)
  if (!positiveRows.length || !totalSalesCount.value) return []

  const donutRows = positiveRows.length > 8
    ? [
        ...positiveRows.slice(0, 7),
        {
          operator_id: 'others',
          operator_name: 'Boshqalar',
          sale: positiveRows.slice(7).reduce((sum, item) => sum + item.sale, 0),
        },
      ]
    : positiveRows

  let offset = 0
  return donutRows.map((item, index) => {
    const percent = (item.sale / totalSalesCount.value) * 100
    const length = (percent / 100) * donutCircumference
    const segment = {
      ...item,
      key: item.operator_id,
      color: donutPalette[index % donutPalette.length],
      percent,
      dasharray: `${length} ${Math.max(donutCircumference - length, 0)}`,
      dashoffset: `${-offset}`,
    }
    offset += length
    return segment
  })
})
const topSalesOperatorLabel = computed(() => {
  if (!salesChartData.value.length) return "Yo'q"
  const top = salesChartData.value[0]
  return `${top.operator_name} (${top.sale} ta)`
})
const pageEyebrow = computed(() => isFilialRahbari.value ? 'Filial Rahbari paneli' : 'Boshliq paneli')
const dashboardSummaryCards = computed(() => {
  if (isFilialRahbari.value) {
    return [
      { title: 'Sotuvlar', value: leads.value.length, subtitle: "Ko'rish mumkin bo'lgan sotuvlar" },
      { title: 'Keldi', value: arrivedCount.value, subtitle: 'Belgilangan kelganlar' },
      { title: 'Kelmadi', value: notArrivedCount.value, subtitle: 'Belgilangan kelmaganlar' },
      { title: 'Huquq', value: 0, subtitle: 'Telegram lead va operator yaratish yopiq' },
    ]
  }
  return [
    { title: 'Operatorlar', value: operators.value.length, subtitle: 'Faol operatorlar' },
    { title: 'Harakatlar', value: totalActionsToday.value, subtitle: 'Bugungi actionlar' },
    { title: 'Aloqa qilingan', value: totalTouchedToday.value, subtitle: 'Bugun ishlangan leadlar' },
    { title: 'Online leadlar', value: onlineLeads.value.length, subtitle: 'Biriktirilmagan yangi leadlar' },
  ]
})
const arrivedCount = computed(() => (isFilialRahbari.value
  ? visitDecisions.value.filter(item => item.decision === 'arrived').length
  : Object.values(visitDecisionMap.value).filter(value => value === 'arrived').length))
const notArrivedCount = computed(() => (isFilialRahbari.value
  ? visitDecisions.value.filter(item => item.decision === 'not_arrived').length
  : Object.values(visitDecisionMap.value).filter(value => value === 'not_arrived').length))
const undecidedLeads = computed(() => leads.value.filter(lead => !visitDecisionMap.value[lead.id]))
const decidedLeads = computed(() => {
  if (isFilialRahbari.value) {
    return visitDecisions.value.map(decision => ({
      id: decision.lead || decision.lead_id,
      full_name: decision.full_name || decision.lead_name || '',
      phone1: decision.phone1 || decision.lead_phone || '',
      phone2: decision.phone2 || decision.lead_phone2 || '',
      phone3: decision.phone3 || decision.lead_phone3 || '',
      tsh: decision.tsh || '',
      school: decision.school || '',
      display_school: decision.display_school || decision.school || '',
      grade: decision.grade || '',
      subject: decision.subject || '',
      ball: decision.ball || '',
      operator_name: decision.operator_name || '',
      branch_name: decision.branch_name || '',
      decision: decision.decision,
      payment_done: !!decision.payment_done,
      payment_done_at: decision.payment_done_at,
      payment_done_by_name: decision.payment_done_by_name || '',
      updated_at: decision.updated_at,
    })).filter(item => item.id)
  }
  return leads.value.filter(lead => !!visitDecisionMap.value[lead.id])
})
const filteredDecidedLeads = computed(() => decidedLeads.value.filter((lead) => {
  const decisionOk = filialDecisionFilter.value === 'all' || (lead.decision || visitDecisionMap.value[lead.id]) === filialDecisionFilter.value
  const paymentOk = filialPaymentFilter.value === 'all'
    || (filialPaymentFilter.value === 'paid' && lead.payment_done)
    || (filialPaymentFilter.value === 'unpaid' && !lead.payment_done)
  return decisionOk && paymentOk
}))
const filialPaymentDoneCount = computed(() => decidedLeads.value.filter(lead => lead.payment_done).length)
const filialPaymentNotDoneCount = computed(() => decidedLeads.value.filter(lead => !lead.payment_done).length)
const ownNotArrivedLeads = computed(() => decidedLeads.value.filter(lead => (lead.decision || visitDecisionMap.value[lead.id]) === 'not_arrived'))
const dateFilteredBossVisitDecisions = computed(() => {
  if (!selectedBossDecisionDate.value) return visitDecisions.value
  return visitDecisions.value.filter(item => toInputDate(item.updated_at) === selectedBossDecisionDate.value)
})
const bossRahbariOptions = computed(() => {
  const map = new Map()
  dateFilteredBossVisitDecisions.value.forEach((item) => {
    const value = String(item.filial_rahbari_id || item.decided_by || item.filial_rahbari_name || '')
    const label = item.filial_rahbari_name || `Rahbar #${value}`
    if (value && !map.has(value)) map.set(value, { value, label })
  })
  return Array.from(map.values()).sort((a, b) => a.label.localeCompare(b.label, 'uz'))
})
const scopedBossVisitDecisions = computed(() => {
  if (selectedBossRahbariFilter.value === 'all') return dateFilteredBossVisitDecisions.value
  return dateFilteredBossVisitDecisions.value.filter((item) => String(item.filial_rahbari_id || item.decided_by || item.filial_rahbari_name || '') === selectedBossRahbariFilter.value)
})
const filteredBossVisitDecisions = computed(() => scopedBossVisitDecisions.value.filter((item) => {
  const decisionOk = bossDecisionFilter.value === 'all' || item.decision === bossDecisionFilter.value
  const paymentOk = bossPaymentFilter.value === 'all'
    || (bossPaymentFilter.value === 'paid' && item.payment_done)
    || (bossPaymentFilter.value === 'unpaid' && !item.payment_done)
  return decisionOk && paymentOk
}))
const bossArrivedCount = computed(() => scopedBossVisitDecisions.value.filter(item => item.decision === 'arrived').length)
const bossNotArrivedCount = computed(() => scopedBossVisitDecisions.value.filter(item => item.decision === 'not_arrived').length)
const bossPaymentDoneCount = computed(() => scopedBossVisitDecisions.value.filter(item => item.payment_done).length)
const bossPaymentNotDoneCount = computed(() => scopedBossVisitDecisions.value.filter(item => !item.payment_done).length)
const bossDecisionSummaryCards = computed(() => ([
  { title: 'Jami belgi', value: scopedBossVisitDecisions.value.length, subtitle: 'Filial rahbarlari bosgan jami qarorlar' },
  { title: 'Keldi', value: bossArrivedCount.value, subtitle: 'Kelgan deb belgilangan leadlar' },
  { title: 'Kelmadi', value: bossNotArrivedCount.value, subtitle: 'Kelmagan deb belgilangan leadlar' },
  { title: 'To‘lov qildi', value: bossPaymentDoneCount.value, subtitle: 'To‘lov qilingan leadlar' },
  { title: 'Rahbarlar', value: bossRahbariDecisionStats.value.length, subtitle: 'Belgi qo‘ygan filial rahbarlari' },
]))
const bossRahbariDecisionStats = computed(() => {
  const source = selectedBossRahbariFilter.value === 'all' ? dateFilteredBossVisitDecisions.value : scopedBossVisitDecisions.value
  const map = new Map()
  source.forEach((item) => {
    const key = String(item.filial_rahbari_id || item.decided_by || item.filial_rahbari_name || 'unknown')
    const row = map.get(key) || {
      key,
      name: item.filial_rahbari_name || `Rahbar #${key}`,
      total: 0,
      arrived: 0,
      not_arrived: 0,
      payment_done: 0,
      payment_not_done: 0,
      last_updated_at: item.updated_at,
    }
    row.total += 1
    if (item.decision === 'arrived') row.arrived += 1
    if (item.decision === 'not_arrived') row.not_arrived += 1
    if (item.payment_done) row.payment_done += 1
    if (!item.payment_done) row.payment_not_done += 1
    if (!row.last_updated_at || new Date(item.updated_at) > new Date(row.last_updated_at)) row.last_updated_at = item.updated_at
    map.set(key, row)
  })
  return Array.from(map.values()).sort((a, b) => b.total - a.total || a.name.localeCompare(b.name, 'uz'))
})
const bossNotArrivedDecisions = computed(() => scopedBossVisitDecisions.value.filter(item => item.decision === 'not_arrived'))
const bossDecisionDateLabel = computed(() => selectedBossDecisionDate.value ? `${formatInputDate(selectedBossDecisionDate.value)} kuni` : 'Barcha kunlar')
const bossDecisionRahbariLabel = computed(() => {
  if (selectedBossRahbariFilter.value === 'all') return 'Barcha filial rahbarlari'
  return bossRahbariOptions.value.find(item => item.value === selectedBossRahbariFilter.value)?.label || 'Tanlangan filial rahbari'
})
const fullReportRangeLabel = computed(() => {
  const start = fullReportData.value?.range?.start_date || fullReportStartDate.value
  const end = fullReportData.value?.range?.end_date || fullReportEndDate.value
  if (start && end) return `${formatInputDate(start)} - ${formatInputDate(end)}`
  if (start) return `${formatInputDate(start)} dan boshlab`
  if (end) return `${formatInputDate(end)} gacha`
  return 'Joriy oy'
})

function getLeadLatestNote(lead) {
  return lead?.history?.[0]?.note?.trim() || lead?.reminder_note || ''
}

function formatLeadReminder(lead) {
  if (!lead?.reminder_at) return ''
  return formatDateTime(lead.reminder_at)
}

const isMobileViewport = computed(() => viewportWidth.value <= 768)
const isCompactSwiperViewport = computed(() => viewportWidth.value <= 900)
const topStatsVisibleSlides = computed(() => (viewportWidth.value <= 560 ? 1 : 2))
const topStatsMaxSlide = computed(() => Math.max(0, dashboardSummaryCards.value.length - topStatsVisibleSlides.value))
const topStatsCanSlide = computed(() => dashboardSummaryCards.value.length > topStatsVisibleSlides.value)
const topStatsTrackStyle = computed(() => ({ transform: `translateX(-${currentTopStatsSlide.value * (100 / topStatsVisibleSlides.value)}%)` }))
const topStatsCurrentPositionLabel = computed(() => {
  if (!dashboardSummaryCards.value.length) return "Card yo'q"
  const start = Math.min(currentTopStatsSlide.value + 1, dashboardSummaryCards.value.length)
  const end = Math.min(currentTopStatsSlide.value + topStatsVisibleSlides.value, dashboardSummaryCards.value.length)
  return start === end ? `Hozir: ${start}-card` : `Hozir: ${start}-${end}-cardlar`
})
const operatorStatsVisibleSlides = computed(() => (viewportWidth.value <= 560 ? 1 : 2))
const operatorStatsMaxSlide = computed(() => Math.max(0, sortedStatistics.value.length - operatorStatsVisibleSlides.value))
const operatorStatsCanSlide = computed(() => sortedStatistics.value.length > operatorStatsVisibleSlides.value)
const operatorStatsTrackStyle = computed(() => ({ transform: `translateX(-${currentOperatorStatsSlide.value * (100 / operatorStatsVisibleSlides.value)}%)` }))
const operatorStatsCurrentPositionLabel = computed(() => {
  if (!sortedStatistics.value.length) return "Card yo'q"
  const start = Math.min(currentOperatorStatsSlide.value + 1, sortedStatistics.value.length)
  const end = Math.min(currentOperatorStatsSlide.value + operatorStatsVisibleSlides.value, sortedStatistics.value.length)
  return start === end ? `Hozir: ${start}-card` : `Hozir: ${start}-${end}-cardlar`
})
const bossLeadVisibleSlides = computed(() => (viewportWidth.value <= 560 ? 1 : 2))
const bossLeadMaxSlide = computed(() => Math.max(0, visibleLeads.value.length - bossLeadVisibleSlides.value))
const bossLeadCanSlide = computed(() => visibleLeads.value.length > bossLeadVisibleSlides.value)
const bossLeadTrackStyle = computed(() => ({ transform: `translateX(-${currentBossLeadSlide.value * (100 / bossLeadVisibleSlides.value)}%)` }))
const bossLeadCurrentPositionLabel = computed(() => {
  if (!visibleLeads.value.length) return "Card yo'q"
  const start = Math.min(currentBossLeadSlide.value + 1, visibleLeads.value.length)
  const end = Math.min(currentBossLeadSlide.value + bossLeadVisibleSlides.value, visibleLeads.value.length)
  return start === end ? `Hozir: ${start}-card` : `Hozir: ${start}-${end}-cardlar`
})
const bossDecisionVisibleSlides = computed(() => (viewportWidth.value <= 560 ? 1 : 2))
const bossDecisionMaxSlide = computed(() => Math.max(0, filteredBossVisitDecisions.value.length - bossDecisionVisibleSlides.value))
const bossDecisionCanSlide = computed(() => filteredBossVisitDecisions.value.length > bossDecisionVisibleSlides.value)
const bossDecisionTrackStyle = computed(() => ({ transform: `translateX(-${currentBossDecisionSlide.value * (100 / bossDecisionVisibleSlides.value)}%)` }))
const bossDecisionCurrentPositionLabel = computed(() => {
  if (!filteredBossVisitDecisions.value.length) return "Card yo'q"
  const start = Math.min(currentBossDecisionSlide.value + 1, filteredBossVisitDecisions.value.length)
  const end = Math.min(currentBossDecisionSlide.value + bossDecisionVisibleSlides.value, filteredBossVisitDecisions.value.length)
  return start === end ? `Hozir: ${start}-card` : `Hozir: ${start}-${end}-cardlar`
})
const filialDecisionVisibleSlides = computed(() => (viewportWidth.value <= 560 ? 1 : 2))
const filialDecisionMaxSlide = computed(() => Math.max(0, filteredDecidedLeads.value.length - filialDecisionVisibleSlides.value))
const filialDecisionCanSlide = computed(() => filteredDecidedLeads.value.length > filialDecisionVisibleSlides.value)
const filialDecisionTrackStyle = computed(() => ({ transform: `translateX(-${currentFilialDecisionSlide.value * (100 / filialDecisionVisibleSlides.value)}%)` }))
const filialDecisionCurrentPositionLabel = computed(() => {
  if (!filteredDecidedLeads.value.length) return "Card yo'q"
  const start = Math.min(currentFilialDecisionSlide.value + 1, filteredDecidedLeads.value.length)
  const end = Math.min(currentFilialDecisionSlide.value + filialDecisionVisibleSlides.value, filteredDecidedLeads.value.length)
  return start === end ? `Hozir: ${start}-card` : `Hozir: ${start}-${end}-cardlar`
})
const filialVisibleSlides = computed(() => (viewportWidth.value <= 560 ? 1 : 2))
const filialMaxSlide = computed(() => Math.max(0, undecidedLeads.value.length - filialVisibleSlides.value))
const filialCanSlide = computed(() => undecidedLeads.value.length > filialVisibleSlides.value)
const filialTrackStyle = computed(() => ({ transform: `translateX(-${currentFilialSlide.value * (100 / filialVisibleSlides.value)}%)` }))
const filialCurrentPositionLabel = computed(() => {
  if (!undecidedLeads.value.length) return "Card yo'q"
  const start = Math.min(currentFilialSlide.value + 1, undecidedLeads.value.length)
  const end = Math.min(currentFilialSlide.value + filialVisibleSlides.value, undecidedLeads.value.length)
  return start === end ? `Hozir: ${start}-card` : `Hozir: ${start}-${end}-cardlar`
})

function clearLeadDateFilter() {
  selectedLeadDate.value = ''
}

function formatPercent(value) {
  if (!Number.isFinite(value)) return '0%'
  const rounded = value >= 10 ? value.toFixed(0) : value.toFixed(1)
  return `${Number(rounded)}%`
}

function getSalesBarWidth(value) {
  if (!maxOperatorSales.value) return '0%'
  const percent = (Number(value || 0) / maxOperatorSales.value) * 100
  if (value > 0 && percent < 8) return '8%'
  return `${Math.min(percent, 100)}%`
}

function getOperatorTierClass(index) {
  if (index === 0) return 'tier-gold'
  if (index === 1) return 'tier-silver'
  if (index === 2) return 'tier-bronze'
  return 'tier-default'
}

function getPodiumToneClass(index) {
  if (index === 0) return 'operator-podium__card--gold'
  if (index === 1) return 'operator-podium__card--silver'
  if (index === 2) return 'operator-podium__card--bronze'
  return ''
}

function formatConversionWidth(value) {
  const number = Number(value || 0)
  return `${Math.max(6, Math.min(number, 100))}%`
}

function clearBossDecisionFilters() {
  selectedBossDecisionDate.value = ''
  selectedBossRahbariFilter.value = 'all'
  bossPaymentFilter.value = 'all'
}

function clampFilialSlide() {
  if (currentFilialSlide.value > filialMaxSlide.value) currentFilialSlide.value = filialMaxSlide.value
  if (currentFilialSlide.value < 0) currentFilialSlide.value = 0
}

function clampFilialDecisionSlide() {
  if (currentFilialDecisionSlide.value > filialDecisionMaxSlide.value) currentFilialDecisionSlide.value = filialDecisionMaxSlide.value
  if (currentFilialDecisionSlide.value < 0) currentFilialDecisionSlide.value = 0
}

function clampBossLeadSlide() {
  if (currentBossLeadSlide.value > bossLeadMaxSlide.value) currentBossLeadSlide.value = bossLeadMaxSlide.value
  if (currentBossLeadSlide.value < 0) currentBossLeadSlide.value = 0
}

function clampBossDecisionSlide() {
  if (currentBossDecisionSlide.value > bossDecisionMaxSlide.value) currentBossDecisionSlide.value = bossDecisionMaxSlide.value
  if (currentBossDecisionSlide.value < 0) currentBossDecisionSlide.value = 0
}

function clampTopStatsSlide() {
  if (currentTopStatsSlide.value > topStatsMaxSlide.value) currentTopStatsSlide.value = topStatsMaxSlide.value
  if (currentTopStatsSlide.value < 0) currentTopStatsSlide.value = 0
}

function clampOperatorStatsSlide() {
  if (currentOperatorStatsSlide.value > operatorStatsMaxSlide.value) currentOperatorStatsSlide.value = operatorStatsMaxSlide.value
  if (currentOperatorStatsSlide.value < 0) currentOperatorStatsSlide.value = 0
}

function nextTopStatsSlide() {
  if (!topStatsCanSlide.value) return
  currentTopStatsSlide.value = currentTopStatsSlide.value >= topStatsMaxSlide.value ? 0 : currentTopStatsSlide.value + 1
}

function prevTopStatsSlide() {
  if (!topStatsCanSlide.value) return
  currentTopStatsSlide.value = currentTopStatsSlide.value <= 0 ? topStatsMaxSlide.value : currentTopStatsSlide.value - 1
}

function nextOperatorStatsSlide() {
  if (!operatorStatsCanSlide.value) return
  currentOperatorStatsSlide.value = currentOperatorStatsSlide.value >= operatorStatsMaxSlide.value ? 0 : currentOperatorStatsSlide.value + 1
}

function prevOperatorStatsSlide() {
  if (!operatorStatsCanSlide.value) return
  currentOperatorStatsSlide.value = currentOperatorStatsSlide.value <= 0 ? operatorStatsMaxSlide.value : currentOperatorStatsSlide.value - 1
}

function nextBossLeadSlide() {
  if (!bossLeadCanSlide.value || loadingLeads.value) return
  currentBossLeadSlide.value = currentBossLeadSlide.value >= bossLeadMaxSlide.value ? 0 : currentBossLeadSlide.value + 1
}

function prevBossLeadSlide() {
  if (!bossLeadCanSlide.value || loadingLeads.value) return
  currentBossLeadSlide.value = currentBossLeadSlide.value <= 0 ? bossLeadMaxSlide.value : currentBossLeadSlide.value - 1
}

function nextBossDecisionSlide() {
  if (!bossDecisionCanSlide.value) return
  currentBossDecisionSlide.value = currentBossDecisionSlide.value >= bossDecisionMaxSlide.value ? 0 : currentBossDecisionSlide.value + 1
}

function prevBossDecisionSlide() {
  if (!bossDecisionCanSlide.value) return
  currentBossDecisionSlide.value = currentBossDecisionSlide.value <= 0 ? bossDecisionMaxSlide.value : currentBossDecisionSlide.value - 1
}


function nextFilialSlide() {
  if (!filialCanSlide.value || loadingLeads.value) return
  currentFilialSlide.value = currentFilialSlide.value >= filialMaxSlide.value ? 0 : currentFilialSlide.value + 1
}

function prevFilialSlide() {
  if (!filialCanSlide.value || loadingLeads.value) return
  currentFilialSlide.value = currentFilialSlide.value <= 0 ? filialMaxSlide.value : currentFilialSlide.value - 1
}

function nextFilialDecisionSlide() {
  if (!filialDecisionCanSlide.value) return
  currentFilialDecisionSlide.value = currentFilialDecisionSlide.value >= filialDecisionMaxSlide.value ? 0 : currentFilialDecisionSlide.value + 1
}

function prevFilialDecisionSlide() {
  if (!filialDecisionCanSlide.value) return
  currentFilialDecisionSlide.value = currentFilialDecisionSlide.value <= 0 ? filialDecisionMaxSlide.value : currentFilialDecisionSlide.value - 1
}

function handleResize() {
  viewportWidth.value = window.innerWidth
  clampFilialSlide()
  clampFilialDecisionSlide()
  clampBossLeadSlide()
  clampBossDecisionSlide()
  clampTopStatsSlide()
  clampOperatorStatsSlide()
}

function showSuccess(message) {
  successMessage.value = message
  clearTimeout(successTimer)
  successTimer = setTimeout(() => {
    successMessage.value = ''
  }, 2500)
}

function closeOperatorModal() {
  openOperatorModal.value = false
  operatorForm.username = ''
  operatorForm.password = ''
  operatorForm.branch_names = []
}

function onFile(event) {
  selectedFile.value = event.target.files[0]
}

function setStatus(status) {
  if (loadingLeads.value) return
  activeStatus.value = status
  refreshLeadSections('Bo‘lim almashtirilmoqda...')
}

function applyLeadSearch() {
  clearTimeout(searchTimer)
  refreshLeadSections('Leadlar qidirilmoqda...')
}

function clearLeadSearch() {
  searchText.value = ''
  clearTimeout(searchTimer)
  refreshLeadSections('Leadlar yangilanmoqda...')
}

function debouncedFetchOnlineLeads() {
  clearTimeout(onlineSearchTimer)
  clearInterval(filialRefreshTimer)
  onlineSearchTimer = setTimeout(() => fetchOnlineLeads(), 250)
}

function formatDateTime(value) {
  return new Date(value).toLocaleString('uz-UZ')
}

function toInputDate(value) {
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return ''
  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  return `${year}-${month}-${day}`
}

function formatInputDate(value) {
  if (!value) return ''
  const [year, month, day] = value.split('-')
  if (!year || !month || !day) return value
  return `${day}.${month}.${year}`
}

function normalizeView(view) {
  const allowedViews = isFilialRahbari.value ? ['leads', 'manager'] : ['leads', 'operators', 'manager', 'online']
  return allowedViews.includes(view) ? view : 'leads'
}

async function syncViewFromRoute(query = route.query) {
  const targetView = normalizeView(typeof query.tab === 'string' ? query.tab : 'leads')
  currentView.value = targetView

  if (targetView === 'online' && !isFilialRahbari.value && !onlineLeads.value.length) {
    await fetchOnlineLeads()
  }

  if (targetView === 'leads') {
    await refreshLeadSections('Leadlar yuklanmoqda...')
  }

  const action = typeof query.action === 'string' ? query.action : ''
  if (!action || isFilialRahbari.value) return

  if (action === 'daily-report') {
    await downloadDailyReport()
  } else if (action === 'full-report') {
    await openFullReportModal()
  } else if (action === 'create-operator') {
    openOperatorModal.value = true
  }

  const nextQuery = { ...route.query }
  delete nextQuery.action
  await router.replace({ path: '/boss', query: nextQuery })
}

async function setCurrentView(view) {
  const normalizedView = normalizeView(view)
  currentView.value = normalizedView
  await router.replace({ path: '/boss', query: { tab: normalizedView } })
  if (normalizedView === 'online' && !isFilialRahbari.value) {
    await fetchOnlineLeads()
  }
  if (normalizedView === 'leads') {
    await refreshLeadSections('Leadlar yuklanmoqda...')
  }
}

function openAssignModal(lead) {
  assignLead.value = lead
  assignOperatorId.value = ''
}

function closeAssignModal() {
  assignLead.value = null
  assignOperatorId.value = ''
}

async function assignOnlineLead() {
  if (!assignLead.value || !assignOperatorId.value) return
  assignLoading.value = true
  error.value = ''
  try {
    await client.post(`boss/online-leads/${assignLead.value.id}/assign/`, { operator_id: Number(assignOperatorId.value) })
    closeAssignModal()
    showSuccess('Online lead operatorga biriktirildi.')
    await Promise.all([fetchOnlineLeads(), refreshLeadSections('Leadlar yangilanmoqda...'), fetchStatistics()])
  } catch (e) {
    error.value = e.response?.data?.detail || 'Biriktirishda xatolik yuz berdi.'
  } finally {
    assignLoading.value = false
  }
}

async function bulkAssignOnlineLeads() {
  if (!bulkOperatorId.value) return
  bulkAssignLoading.value = true
  error.value = ''
  try {
    const { data } = await client.post('boss/online-leads/bulk-assign/', { operator_id: bulkOperatorId.value })
    showSuccess(data.detail || 'Online leadlar biriktirildi.')
    await Promise.all([fetchOnlineLeads(), refreshLeadSections('Leadlar yangilanmoqda...'), fetchStatistics()])
  } catch (e) {
    error.value = e.response?.data?.detail || 'Barchasini biriktirishda xatolik yuz berdi.'
  } finally {
    bulkAssignLoading.value = false
  }
}

async function submitVisitDecision(leadId, decision) {
  decisionLoadingId.value = leadId
  pendingDecision.value = decision
  error.value = ''
  try {
    const { data } = await client.post(`boss/leads/${leadId}/visit-decision/`, { decision })
    visitDecisionMap.value = {
      ...visitDecisionMap.value,
      [leadId]: data.decision,
    }
    showSuccess(data.decision === 'arrived' ? 'Keldi' : 'Kelmadi')
    if (isFilialRahbari.value) {
      await Promise.all([fetchVisitDecisions(), fetchLeads('Sotuvlar yangilanmoqda...')])
    }
  } catch (e) {
    error.value = e.response?.data?.detail || 'Belgini saqlashda xatolik yuz berdi.'
  } finally {
    decisionLoadingId.value = null
    pendingDecision.value = ''
  }
}

async function markPaymentDone(leadId) {
  paymentLoadingId.value = leadId
  error.value = ''
  try {
    await client.post(`boss/leads/${leadId}/payment-done/`)
    showSuccess('To‘lov qilindi')
    await fetchVisitDecisions()
  } catch (e) {
    error.value = e.response?.data?.detail || 'To‘lov belgisini saqlashda xatolik yuz berdi.'
  } finally {
    paymentLoadingId.value = null
  }
}


function closeFullReportModal() {
  showFullReportModal.value = false
}

function clearFullReportFilters() {
  fullReportOperatorId.value = ''
  fullReportStartDate.value = ''
  fullReportEndDate.value = ''
  fetchFullReport()
}

async function openFullReportModal() {
  showFullReportModal.value = true
  if (!fullReportData.value) {
    await fetchFullReport()
  }
}

async function fetchFullReport() {
  fullReportLoading.value = true
  error.value = ''
  try {
    const params = {}
    if (fullReportOperatorId.value) params.operator_id = fullReportOperatorId.value
    if (fullReportOperatorId.value) params.operator_id = fullReportOperatorId.value
    if (fullReportStartDate.value) params.start_date = fullReportStartDate.value
    if (fullReportEndDate.value) params.end_date = fullReportEndDate.value
    const { data } = await client.get('boss/statistics/full-report/', { params })
    fullReportData.value = data
  } catch (e) {
    error.value = e.response?.data?.detail || 'Umumiy hisobotni yuklashda xatolik yuz berdi.'
  } finally {
    fullReportLoading.value = false
  }
}


async function downloadFullReportExcel() {
  fullReportExcelLoading.value = true
  error.value = ''
  const startedAt = Date.now()
  try {
    const params = {}
    if (fullReportStartDate.value) params.start_date = fullReportStartDate.value
    if (fullReportEndDate.value) params.end_date = fullReportEndDate.value
    const response = await client.get('boss/statistics/full-report-excel/', { params, responseType: 'blob' })
    const blob = new Blob([response.data], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' })
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    const start = fullReportStartDate.value || 'boshlanish'
    const end = fullReportEndDate.value || 'bugun'
    link.href = url
    link.download = `boss_toliq_hisobot_${start}_${end}.xlsx`
    document.body.appendChild(link)
    link.click()
    link.remove()
    window.URL.revokeObjectURL(url)
    showSuccess('Excel yuklab olindi.')
  } catch (e) {
    error.value = e.response?.data?.detail || 'Excel hisobotni yuklab olishda xatolik yuz berdi.'
  } finally {
    const elapsed = Date.now() - startedAt
    if (elapsed < 500) await sleep(500 - elapsed)
    fullReportExcelLoading.value = false
  }
}

async function downloadDailyReport() {
  reportLoading.value = true
  error.value = ''
  const startedAt = Date.now()
  try {
    const response = await client.get('boss/statistics/daily-report/', { responseType: 'blob' })
    const blob = new Blob([response.data], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' })
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    const today = new Date().toISOString().slice(0, 10)
    link.href = url
    link.download = `boss_hisobot_${today}.xlsx`
    document.body.appendChild(link)
    link.click()
    link.remove()
    window.URL.revokeObjectURL(url)
    showSuccess('Hisobot yuklab olindi.')
  } catch (e) {
    error.value = e.response?.data?.detail || 'Hisobotni yuklab olishda xatolik yuz berdi.'
  } finally {
    const elapsed = Date.now() - startedAt
    if (elapsed < 500) await sleep(500 - elapsed)
    reportLoading.value = false
  }
}

async function fetchOperators() {
  if (isFilialRahbari.value) {
    operators.value = []
    return
  }
  const { data } = await client.get('boss/operators/')
  operators.value = data.results || data
}

async function fetchStatistics() {
  if (isFilialRahbari.value) {
    statistics.value = []
    return
  }
  const { data } = await client.get('boss/statistics/')
  statistics.value = data
}

async function fetchOnlineLeads() {
  if (isFilialRahbari.value) {
    onlineLeads.value = []
    return
  }
  const params = {}
  if (onlineSearch.value.trim()) params.search = onlineSearch.value.trim()
  const { data } = await client.get('boss/online-leads/', { params })
  onlineLeads.value = data.results || data
}

async function fetchVisitDecisions() {
  const { data } = await client.get('boss/lead-visit-decisions/')
  visitDecisions.value = data.results || data
  if (isFilialRahbari.value) {
    const mapped = {}
    visitDecisions.value.forEach((item) => {
      const leadId = item.lead || item.lead_id
      if (leadId) mapped[leadId] = item.decision
    })
    visitDecisionMap.value = mapped
  }
}

async function fetchStatusLeadBuckets(message = 'Leadlar yuklanmoqda...') {
  loadingLeads.value = true
  loadingMessage.value = message
  error.value = ''
  const startedAt = Date.now()
  try {
    const sharedParams = {}
    if (selectedOperatorFilter.value !== 'all') sharedParams.assigned_operator = selectedOperatorFilter.value
    if (searchText.value.trim()) sharedParams.search = searchText.value.trim()

    const responses = await Promise.all(statusKeys.map((statusKey) =>
      client.get('boss/leads/', { params: { ...sharedParams, current_status: statusKey } })
    ))

    const nextBuckets = {}
    responses.forEach((response, index) => {
      const key = statusKeys[index]
      nextBuckets[key] = response.data.results || response.data
    })
    statusLeadBuckets.value = nextBuckets
  } catch (e) {
    error.value = e.response?.data?.detail || 'Leadlarni yuklashda xatolik yuz berdi.'
  } finally {
    const elapsed = Date.now() - startedAt
    if (elapsed < 500) await sleep(500 - elapsed)
    loadingLeads.value = false
  }
}

function refreshLeadSections(message = 'Leadlar yuklanmoqda...') {
  if (isFilialRahbari.value) {
    return fetchLeads(message)
  }
  return fetchStatusLeadBuckets(message)
}

async function fetchLeads(message = 'Leadlar yuklanmoqda...') {
  loadingLeads.value = true
  loadingMessage.value = message
  error.value = ''
  const startedAt = Date.now()
  try {
    const params = { current_status: activeStatus.value }
    if (!isFilialRahbari.value && selectedOperatorFilter.value !== 'all') params.assigned_operator = selectedOperatorFilter.value
    if (searchText.value.trim()) params.search = searchText.value.trim()
    const { data } = await client.get('boss/leads/', { params })
    leads.value = data.results || data
    if (isFilialRahbari.value) {
      const mapped = { ...visitDecisionMap.value }
      leads.value.forEach((lead) => {
        const ownDecision = Array.isArray(lead.visit_decisions) ? lead.visit_decisions.find(item => item.decided_by === auth.user?.id) : null
        if (ownDecision) mapped[lead.id] = ownDecision.decision
      })
      visitDecisionMap.value = mapped
    }
    clampFilialSlide()
  } catch (e) {
    error.value = e.response?.data?.detail || 'Leadlarni yuklashda xatolik yuz berdi.'
  } finally {
    const elapsed = Date.now() - startedAt
    if (elapsed < 500) await sleep(500 - elapsed)
    loadingLeads.value = false
  }
}

async function createOperator() {
  error.value = ''
  if (!operatorForm.username || !operatorForm.password || !operatorForm.branch_names.length) {
    error.value = 'Login, parol va kamida bitta filial tanlang.'
    return
  }
  try {
    await client.post('boss/operators/', {
      username: operatorForm.username,
      password: operatorForm.password,
      branch_names: operatorForm.branch_names,
    })
    closeOperatorModal()
    showSuccess('Operator muvaffaqiyatli yaratildi.')
    await fetchOperators()
  } catch (e) {
    error.value = e.response?.data?.username?.[0] || e.response?.data?.detail || 'Operator yaratishda xatolik yuz berdi.'
  }
}

async function uploadFile() {
  error.value = ''
  importResult.value = ''
  if (!selectedOperator.value || !selectedFile.value) {
    error.value = 'Operator yoki Hammasiga variantini va excel faylni tanlang.'
    return
  }
  try {
    const formData = new FormData()
    formData.append('operator_id', selectedOperator.value)
    formData.append('file', selectedFile.value)
    const { data } = await client.post('boss/leads/import/', formData)
    const duplicateText = Number(data.duplicate_rows || 0) ? `, ${data.duplicate_rows} ta dublikat ham saqlandi` : ''
    importResult.value = data.operator_mode === 'all'
      ? `${data.success_rows} ta lead taqsimlab qo'shildi${duplicateText}, ${data.failed_rows} ta xato qator logga yozildi.`
      : `${data.success_rows} ta lead qo'shildi${duplicateText}, ${data.failed_rows} ta xato qator logga yozildi.`
    showSuccess('Excel muvaffaqiyatli yuklandi.')
    await fetchStatistics()
    await refreshLeadSections('Leadlar yangilanmoqda...')
  } catch (e) {
    const data = e.response?.data
    if (Array.isArray(data?.missing_columns) && data.missing_columns.length) {
      error.value = `Excel ustunlari yetishmayapti: ${data.missing_columns.join(', ')}`
    } else if (Array.isArray(data?.received_columns) && data.received_columns.length) {
      error.value = `${data?.detail || 'Excel yuklashda xatolik yuz berdi.'} Qabul qilingan ustunlar: ${data.received_columns.join(', ')}`
    } else if (!e.response && e.message?.includes('Network Error')) {
      error.value = 'Backend server ishlamayapti. Node.js serverni ishga tushiring va API manzilini tekshiring.'
    } else {
      error.value = data?.detail || 'Excel yuklashda xatolik yuz berdi.'
    }
  }
}


watch([dashboardSummaryCards, isCompactSwiperViewport], () => {
  clampTopStatsSlide()
})

watch([statistics, isCompactSwiperViewport], () => {
  clampOperatorStatsSlide()
})

watch([visibleLeads, isCompactSwiperViewport], () => {
  clampBossLeadSlide()
})

watch([filteredBossVisitDecisions, isCompactSwiperViewport], () => {
  clampBossDecisionSlide()
})

watch(undecidedLeads, () => {
  clampFilialSlide()
})

watch([filteredDecidedLeads, isCompactSwiperViewport], () => {
  clampFilialDecisionSlide()
})

watch(() => route.query, async (query) => {
  await syncViewFromRoute(query)
}, { deep: true })

onMounted(async () => {
  window.addEventListener('resize', handleResize)
  currentView.value = normalizeView(typeof route.query.tab === 'string' ? route.query.tab : 'leads')
  if (isFilialRahbari.value) {
    activeStatus.value = 'sale'
    await fetchVisitDecisions()
    await refreshLeadSections()
    filialRefreshTimer = setInterval(async () => {
      if (!loadingLeads.value) {
        await Promise.all([fetchVisitDecisions(), fetchLeads('Sotuvlar yangilanmoqda...')])
      }
    }, 15000)
    await syncViewFromRoute(route.query)
    return
  }
  await fetchOperators()
  await fetchStatistics()
  await refreshLeadSections()
  await fetchVisitDecisions()
  if (currentView.value === 'online') {
    await fetchOnlineLeads()
  } else {
    fetchOnlineLeads()
  }
  await syncViewFromRoute(route.query)
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', handleResize)
  clearTimeout(successTimer)
  clearTimeout(searchTimer)
  clearTimeout(onlineSearchTimer)
  clearInterval(filialRefreshTimer)
})
</script>


<style scoped>
.decision-summary-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(170px, 1fr));
  gap: 12px;
  margin: 14px 0;
}

.decision-summary-card {
  padding: 14px;
  border-radius: 18px;
  display: grid;
  gap: 6px;
}

.decision-summary-card span {
  font-size: 13px;
  opacity: .76;
}

.decision-summary-card strong {
  font-size: 28px;
  line-height: 1;
}

.decision-summary-card small {
  font-size: 12px;
  opacity: .7;
}

.decision-stats-table,
.decision-detail-table {
  margin: 12px 0 16px;
  max-height: 360px;
  overflow: auto;
}

.decision-detail-panel {
  margin-top: 18px;
  padding: 16px;
  border-radius: 22px;
}

.decision-detail-table table {
  min-width: 1180px;
}

.decision-detail-table th,
.decision-detail-table td {
  white-space: nowrap;
}

.decision-date-filter--stacked {
  display: flex;
  flex-direction: column;
  gap: 10px;
  min-width: 280px;
}

.decision-date-filter__row {
  display: flex;
  gap: 10px;
  align-items: center;
}

.toolbar--boss-filters {
  flex-wrap: wrap;
}

.toolbar--boss-filters .input[type="date"] {
  min-width: 180px;
}

@media (max-width: 700px) {
  .decision-date-filter--stacked {
    min-width: 100%;
  }

  .decision-date-filter__row {
    flex-direction: column;
    align-items: stretch;
  }
}
.operator-sales-chart {
  margin-bottom: 18px;
  padding: 18px;
  border-radius: 24px;
  display: grid;
  gap: 16px;
}

.operator-donut-card {
  margin-bottom: 18px;
  padding: 18px;
  border-radius: 24px;
  display: grid;
  gap: 18px;
}

.operator-donut-card__head {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 14px;
  flex-wrap: wrap;
}

.operator-donut-card__head h4 {
  margin: 4px 0 0;
}

.operator-donut-card__body {
  display: grid;
  grid-template-columns: minmax(220px, 320px) minmax(0, 1fr);
  gap: 24px;
  align-items: center;
}

.operator-donut-chart {
  position: relative;
  width: min(100%, 300px);
  aspect-ratio: 1;
  margin: 0 auto;
}

.operator-donut-chart svg {
  width: 100%;
  height: 100%;
  transform: rotate(-90deg);
}

.operator-donut-chart__track,
.operator-donut-chart__segment {
  fill: none;
  stroke-width: 28;
}

.operator-donut-chart__track {
  stroke: rgba(148, 163, 184, 0.18);
}

.operator-donut-chart__segment {
  stroke-linecap: butt;
  transition: stroke-dasharray .35s ease, stroke-dashoffset .35s ease;
}

.operator-donut-chart__center {
  position: absolute;
  inset: 50%;
  transform: translate(-50%, -50%);
  width: 46%;
  aspect-ratio: 1;
  border-radius: 999px;
  background: rgba(15, 23, 42, 0.9);
  border: 1px solid rgba(148, 163, 184, 0.18);
  display: grid;
  place-items: center;
  text-align: center;
  padding: 14px;
  box-shadow: 0 16px 32px rgba(15, 23, 42, 0.24);
}

.operator-donut-chart__center strong {
  display: block;
  font-size: 28px;
  line-height: 1;
  color: white;
}

.operator-donut-chart__center span {
  font-size: 12px;
  opacity: .74;
  text-transform: uppercase;
  letter-spacing: .08em;
    color: white;
}

.operator-donut-legend {
  display: grid;
  gap: 10px;
}

.operator-donut-legend__item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 14px;
  border-radius: 16px;
  background: rgba(15, 23, 42, 0.14);
  border: 1px solid rgba(148, 163, 184, 0.12);
}

.operator-donut-legend__dot {
  width: 12px;
  height: 12px;
  border-radius: 999px;
  flex-shrink: 0;
  box-shadow: 0 0 0 4px rgba(255, 255, 255, 0.04);
}

.operator-donut-legend__text {
  min-width: 0;
  display: grid;
  gap: 2px;
}

.operator-donut-legend__text strong {
  font-size: 14px;
}

.operator-donut-legend__text span {
  font-size: 13px;
  opacity: .75;
}

.operator-sales-chart__head {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 14px;
  flex-wrap: wrap;
}

.operator-sales-chart__head h4 {
  margin: 4px 0 0;
}

.operator-sales-chart__summary {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.operator-sales-chart__list {
  display: grid;
  gap: 12px;
}

.operator-sales-chart__item {
  display: grid;
  gap: 8px;
}

.operator-sales-chart__labels {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  flex-wrap: wrap;
}

.operator-sales-chart__labels strong {
  font-size: 14px;
}

.operator-sales-chart__labels span {
  font-size: 13px;
  opacity: .78;
}

.operator-sales-chart__bar-wrap {
  width: 100%;
  height: 14px;
  border-radius: 999px;
  background: rgba(148, 163, 184, 0.18);
  overflow: hidden;
}

.operator-sales-chart__bar {
  height: 100%;
  border-radius: inherit;
  background: linear-gradient(90deg, #2563eb 0%, #38bdf8 100%);
  transition: width .35s ease;
}


.operator-podium {
  margin-bottom: 18px;
  padding: 20px;
  border-radius: 24px;
  display: grid;
  gap: 16px;
}

.operator-podium__head {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 14px;
  flex-wrap: wrap;
}

.operator-podium__head h4 {
  margin: 4px 0 0;
}

.operator-podium__grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 14px;
}

.operator-podium__card {
  position: relative;
  overflow: hidden;
  padding: 20px;
  border-radius: 24px;
  border: 1px solid rgba(148, 163, 184, 0.18);
  background: linear-gradient(135deg, rgba(15, 23, 42, 0.92), rgba(30, 41, 59, 0.9));
  color: #fff;
  box-shadow: 0 20px 40px rgba(15, 23, 42, 0.18);
  display: grid;
  gap: 12px;
}

.operator-podium__card::after {
  content: '';
  position: absolute;
  inset: 0;
  background: radial-gradient(circle at top right, rgba(255,255,255,.24), transparent 42%);
  pointer-events: none;
}

.operator-podium__card--gold {
  background: linear-gradient(135deg, #1e293b, #7c5c12 58%, #f59e0b 100%);
}

.operator-podium__card--silver {
  background: linear-gradient(135deg, #1f2937, #64748b 62%, #cbd5e1 100%);
}

.operator-podium__card--bronze {
  background: linear-gradient(135deg, #2b2118, #7c4a2d 58%, #f97316 100%);
}

.operator-podium__rank,
.operator-podium__medal {
  position: relative;
  z-index: 1;
}

.operator-podium__rank {
  width: fit-content;
  padding: 6px 12px;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.16);
  font-size: 12px;
  font-weight: 700;
  letter-spacing: .08em;
}

.operator-podium__medal {
  font-size: 34px;
  line-height: 1;
}

.operator-podium__card h5 {
  margin: 0;
  position: relative;
  z-index: 1;
  font-size: 20px;
}

.operator-podium__stats {
  position: relative;
  z-index: 1;
  display: grid;
  gap: 6px;
  opacity: .95;
}

.operator-rank-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 42px;
  height: 42px;
  padding: 0 12px;
  border-radius: 999px;
  background: rgba(15, 23, 42, 0.08);
  color: #0f172a;
  font-size: 14px;
  font-weight: 800;
}

.operator-rank-medal {
  font-size: 20px;
  line-height: 1;
}

.operator-stat-card.tier-gold,
.operator-premium-row.tier-gold {
  background: linear-gradient(135deg, rgba(245, 158, 11, 0.16), rgba(255,255,255,0.98));
}

.operator-stat-card.tier-silver,
.operator-premium-row.tier-silver {
  background: linear-gradient(135deg, rgba(148, 163, 184, 0.18), rgba(255,255,255,0.98));
}

.operator-stat-card.tier-bronze,
.operator-premium-row.tier-bronze {
  background: linear-gradient(135deg, rgba(249, 115, 22, 0.16), rgba(255,255,255,0.98));
}

.operator-stat-card__title {
  display: flex;
  align-items: center;
  gap: 10px;
}

.operator-stat-card__title h4 {
  margin: 0;
}

.operator-premium-table-wrap {
  border-radius: 28px;
  border: 1px solid rgba(148, 163, 184, 0.16);
  background: linear-gradient(180deg, rgba(255,255,255,0.96), rgba(248,250,252,0.96));
  box-shadow: 0 22px 44px rgba(15, 23, 42, 0.08);
  overflow: hidden;
}

.operator-premium-table {
  min-width: 960px;
}

.operator-premium-table thead th {
  padding: 16px 14px;
  font-size: 12px;
  text-transform: uppercase;
  letter-spacing: .12em;
  color: #64748b;
  background: rgba(241, 245, 249, 0.95);
}

.operator-premium-table tbody td {
  padding: 16px 14px;
  vertical-align: middle;
}

.operator-premium-row {
  transition: transform .2s ease, box-shadow .2s ease, background .2s ease;
}

.operator-premium-row:hover {
  transform: translateY(-2px);
  box-shadow: inset 0 0 0 999px rgba(59, 130, 246, 0.03);
}

.operator-rank-cell {
  display: flex;
  align-items: center;
  gap: 10px;
}

.operator-name-cell {
  display: grid;
  gap: 4px;
}

.operator-name-cell strong {
  font-size: 15px;
}

.operator-name-cell small {
  color: #64748b;
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

.operator-conversion-cell {
  display: grid;
  gap: 8px;
  min-width: 110px;
}

.operator-conversion-track {
  width: 100%;
  height: 10px;
  border-radius: 999px;
  background: rgba(148, 163, 184, 0.18);
  overflow: hidden;
}

.operator-conversion-fill {
  height: 100%;
  border-radius: inherit;
  background: linear-gradient(90deg, #22c55e 0%, #14b8a6 100%);
}

@media (max-width: 800px) {
  .operator-donut-card__body {
    grid-template-columns: 1fr;
  }

  .operator-podium__grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 640px) {
  .operator-sales-chart,
  .operator-donut-card,
  .operator-podium {
    padding: 14px;
  }

  .operator-sales-chart__labels {
    align-items: flex-start;
    flex-direction: column;
  }

  .operator-donut-chart {
    width: min(100%, 240px);
  }

  .operator-donut-chart__center strong {
    font-size: 24px;
  }
}

.modal-overlay--report {
  align-items: flex-start;
  padding: 24px;
  overflow-y: auto;
}

.report-modal {
  width: min(1280px, 100%);
  max-height: none;
}

.report-modal__body {
  display: grid;
  gap: 18px;
}

.report-filter-bar {
  margin-bottom: 12px;
  align-items: end;
}

.report-filter-field {
  display: grid;
  gap: 6px;
  min-width: 180px;
}

.report-filter-field label {
  font-size: 12px;
  opacity: .8;
}

.report-stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
  gap: 12px;
}

.report-stat-card {
  padding: 14px;
  border-radius: 18px;
  display: grid;
  gap: 8px;
}

.report-stat-card span {
  font-size: 13px;
  opacity: .8;
}

.report-stat-card strong {
  font-size: 26px;
}

.report-section-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 16px;
}

.report-table-wrap {
  max-height: 320px;
  overflow: auto;
}

@media (max-width: 980px) {
  .report-section-grid {
    grid-template-columns: 1fr;
  }

  .modal-overlay--report {
    padding: 12px;
  }
}

.boss-page {
  gap: 18px;
}

.boss-subnav {
  padding: 14px 18px;
  border-radius: 18px;
  background: #ffffff;
  border: 1px solid #e5e7eb;
  box-shadow: none;
}

.boss-subnav__list {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 24px;
  flex-wrap: wrap;
}

.boss-subnav__link {
  display: inline-flex;
  align-items: center;
  padding-bottom: 8px;
  color: #111827;
  font-weight: 600;
  border-bottom: 2px solid transparent;
  transition: color .2s ease, border-color .2s ease;
}

.boss-subnav__link:hover,
.boss-subnav__link.active {
  color: #000000;
  border-bottom-color: #111827;
}

@media (max-width: 760px) {
  .boss-subnav {
    padding: 12px 14px;
  }

  .boss-subnav__list {
    justify-content: flex-start;
    gap: 14px 18px;
  }
}


.decision-filter-stack {
  display: flex;
  flex-direction: column;
  gap: 10px;
  align-items: flex-end;
}

.payment-filter-group .decision-filter-btn.active {
  background: rgba(34, 197, 94, 0.16);
  color: #047857;
  border-color: rgba(34, 197, 94, 0.28);
}

.visit-mini-card__head--payment {
  display: flex;
  align-items: flex-start;
  gap: 12px;
}

.payment-dot {
  width: 14px;
  height: 14px;
  border-radius: 999px;
  margin-top: 8px;
  flex: 0 0 auto;
  box-shadow: 0 0 0 5px rgba(148, 163, 184, 0.12);
}

.payment-dot.is-unpaid {
  background: #ef4444;
  box-shadow: 0 0 0 5px rgba(239, 68, 68, 0.14), 0 0 18px rgba(239, 68, 68, 0.35);
}

.payment-dot.is-paid {
  background: #22c55e;
  box-shadow: 0 0 0 5px rgba(34, 197, 94, 0.14), 0 0 18px rgba(34, 197, 94, 0.35);
}

.payment-paid-badge,
.payment-pill.is-paid {
  background: rgba(34, 197, 94, 0.14) !important;
  color: #047857 !important;
  border-color: rgba(34, 197, 94, 0.28) !important;
}

.payment-unpaid-badge,
.payment-pill.is-unpaid {
  background: rgba(239, 68, 68, 0.12) !important;
  color: #b91c1c !important;
  border-color: rgba(239, 68, 68, 0.24) !important;
}

.payment-pill {
  display: inline-flex;
  align-items: center;
  padding: 6px 10px;
  border-radius: 999px;
  font-size: 12px;
  font-weight: 700;
  border: 1px solid transparent;
}

.payment-btn {
  background: linear-gradient(90deg, #16a34a, #22c55e);
  color: #fff;
}

.payment-btn:disabled {
  opacity: .78;
}

@media (max-width: 760px) {
  .decision-filter-stack {
    align-items: stretch;
    width: 100%;
  }
}


.branch-picker {
  display: grid;
  gap: 10px;
  padding: 14px;
  border-radius: 18px;
  background: rgba(248, 250, 252, 0.88);
  border: 1px solid rgba(148, 163, 184, 0.18);
}
.branch-picker > label { font-weight: 800; color: #0f172a; }
.branch-picker__grid { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 8px; }
.branch-check { display: flex; align-items: center; gap: 8px; padding: 9px 10px; border-radius: 14px; background: white; border: 1px solid rgba(148, 163, 184, .22); font-size: 13px; cursor: pointer; }
.branch-check input { width: 16px; height: 16px; accent-color: #2563eb; }
@media (max-width: 640px) { .branch-picker__grid { grid-template-columns: 1fr; } }


.operator-note-line {
  grid-column: 1 / -1;
  padding: 10px 12px;
  border-radius: 14px;
  background: rgba(37, 99, 235, 0.08);
  border: 1px solid rgba(37, 99, 235, 0.14);
  color: #0f172a;
}

</style>
