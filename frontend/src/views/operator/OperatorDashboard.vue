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
          <button class="assigned-status-option not-answered" type="button" @click="selectAssignedStatus('not_answered')">Ko'tarmadi</button>
        </div>
      </div>
    </div>

    <div v-if="saleBranchModal.open" class="modal-overlay">
      <div class="modal-card glass assigned-status-modal">
        <div class="modal-card__head">
          <div>
            <div class="eyebrow">SOTUV FILIALI</div>
            <h3>Qaysi filial uchun Sotuv bo‘ldi?</h3>
            <p>{{ saleBranchModal.lead?.full_name || 'Lead' }} qaysi menenjer paneliga tushishini tanlang.</p>
          </div>
          <button class="modal-close" type="button" @click="closeSaleBranchModal">×</button>
        </div>

        <div class="assigned-status-modal__grid">
          <button
            v-for="branch in allSaleBranchNames"
            :key="branch"
            class="assigned-status-option sale"
            type="button"
            :disabled="processingLeadId === saleBranchModal.lead?.id"
            @click="confirmSaleBranch(branch)"
          >
            {{ branch }}
          </button>
        </div>
      </div>
    </div>

    <div v-if="addLeadModal.step === 'form'" class="modal-overlay">
      <div class="modal-card glass add-lead-modal">
        <div class="modal-card__head">
          <div>
            <div class="eyebrow">YANGI LEAD</div>
            <h3>Lead qo'shish</h3>
            <p>Kiruvchi qo'ng'iroq bo'yicha yangi mijoz ma'lumotlarini kiriting.</p>
          </div>
          <button class="modal-close" type="button" @click="closeAddLeadModal">×</button>
        </div>
        <form class="grid" @submit.prevent="submitAddLeadForm">
          <input v-model="addLeadModal.full_name" class="input" placeholder="Ism Familya" :disabled="addLeadModal.saving" required />
          <input v-model="addLeadModal.phone1" class="input" placeholder="Nomer 1" :disabled="addLeadModal.saving" required />
          <input v-model="addLeadModal.phone2" class="input" placeholder="Nomer 2" :disabled="addLeadModal.saving" />
          <input v-model="addLeadModal.subject" class="input" placeholder="Fan" :disabled="addLeadModal.saving" />
          <div class="modal-actions modal-actions--split">
            <button class="btn" type="submit" :disabled="addLeadModal.saving">{{ addLeadModal.saving ? 'Saqlanmoqda...' : 'OK' }}</button>
            <button class="btn ghost" type="button" :disabled="addLeadModal.saving" @click="closeAddLeadModal">Bekor qilish</button>
          </div>
        </form>
      </div>
    </div>

    <div v-if="addLeadModal.step === 'branch'" class="modal-overlay">
      <div class="modal-card glass assigned-status-modal">
        <div class="modal-card__head">
          <div>
            <div class="eyebrow">FILIAL</div>
            <h3>Qaysi filialga?</h3>
            <p>{{ addLeadModal.createdLead?.full_name || 'Lead' }} uchun filialni tanlang.</p>
          </div>
          <button class="modal-close" type="button" @click="closeAddLeadModal">×</button>
        </div>
        <div class="assigned-status-modal__grid">
          <button
            v-for="branch in allSaleBranchNames"
            :key="`add-lead-branch-${branch}`"
            class="assigned-status-option sale"
            type="button"
            @click="selectAddLeadBranch(branch)"
          >
            {{ branch }}
          </button>
        </div>
      </div>
    </div>

    <div v-if="addLeadModal.step === 'status'" class="modal-overlay">
      <div class="modal-card glass assigned-status-modal">
        <div class="modal-card__head">
          <div>
            <div class="eyebrow">HOLAT</div>
            <h3>Natijani tanlang</h3>
            <p>{{ addLeadModal.createdLead?.full_name || 'Lead' }} — {{ addLeadModal.branch }}</p>
          </div>
          <button class="modal-close" type="button" @click="closeAddLeadModal">×</button>
        </div>
        <div class="assigned-status-modal__grid">
          <button class="assigned-status-option sale" type="button" :disabled="processingLeadId === addLeadModal.createdLead?.id" @click="selectAddLeadStatus('sale')">Sotuv</button>
          <button class="assigned-status-option otkaz" type="button" :disabled="processingLeadId === addLeadModal.createdLead?.id" @click="selectAddLeadStatus('otkaz')">Atkaz</button>
          <button class="assigned-status-option advice" type="button" :disabled="processingLeadId === addLeadModal.createdLead?.id" @click="selectAddLeadStatus('advice')">Maslahat</button>
        </div>
      </div>
    </div>

    <div class="operator-board-top glass-soft">
      <div class="operator-board-top__info">
        <div class="operator-board-top__badges">
          <span class="badge">{{ topBadgeLabel }} • {{ visibleLeadCount }} ta</span>
          <span class="badge muted">{{ assignmentBadgeLabel }}</span>
          <span class="badge muted">Ko‘rinayotgan: {{ visibleLeadCount }} ta</span>
          <button class="btn small add-lead-btn" type="button" @click="openAddLeadModal">+ Lead qo'shish</button>
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
      :items="operatorMetricCards"
      eyebrow="Operator statistikasi"
      title="Kunlik ko'rsatkichlar"
      wrapper-class="glass-soft stats-mobile-swiper stats-mobile-swiper--operator swipe-elevated"
      :desktop-slides="2"
      :tablet-slides="2"
      :mobile-slides="1"
      :tablet-breakpoint="980"
    >
      <template #default="{ item }">
        <article class="operator-metric-card" :class="`operator-metric-card--${item.key}`">
          <div class="operator-metric-card__icon">{{ item.icon }}</div>
          <div class="operator-metric-card__content">
            <span class="operator-metric-card__label">{{ item.title }}</span>
            <strong class="operator-metric-card__value">{{ item.value }}</strong>
            <div class="operator-metric-card__action">{{ item.subtitle }} <span aria-hidden="true">›</span></div>
          </div>
        </article>
      </template>
    </ResponsiveSwiper>

    <div v-else class="operator-metric-grid">
      <article
        v-for="item in operatorMetricCards"
        :key="item.key"
        class="operator-metric-card"
        :class="`operator-metric-card--${item.key}`"
      >
        <div class="operator-metric-card__icon">{{ item.icon }}</div>
        <div class="operator-metric-card__content">
          <span class="operator-metric-card__label">{{ item.title }}</span>
          <strong class="operator-metric-card__value">{{ item.value }}</strong>
          <div class="operator-metric-card__action">{{ item.subtitle }} <span aria-hidden="true">›</span></div>
        </div>
      </article>
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
            <span>Ko'tarmadi: <strong>{{ row.not_answered || 0 }}</strong></span>
            <span>Jami action: <strong>{{ row.actions_total }}</strong></span>
          </div>
        </article>
      </div>
      <div v-else class="empty-state">Hali kunlik hisobot topilmadi.</div>

      <div class="operator-monthly-report glass-soft">
        <div class="section-head section-head--wrap">
          <div>
            <div class="eyebrow">Oyma-oy arxiv</div>
            <h3>Oylarga bo‘lingan natijalar</h3>
            <p>Eski oy natijalari saqlanadi, yangi oy avtomatik alohida ochiladi.</p>
          </div>
        </div>
        <div class="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Oy</th>
                <th>Biriktirildi</th>
                <th>Sotuv</th>
                <th>Atkaz</th>
                <th>Xato</th>
                <th>O‘chiq</th>
                <th>Maslahat</th>
                <th>O‘qiydi</th>
                <th>Ko'tarmadi</th>
                <th>Jami action</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="row in monthlyHistory" :key="`operator-month-${row.month}`">
                <td>{{ row.month_label || row.month }}</td>
                <td>{{ row.assigned_leads }}</td>
                <td>{{ row.sale }}</td>
                <td>{{ row.otkaz }}</td>
                <td>{{ row.wrong_number }}</td>
                <td>{{ row.open_number }}</td>
                <td>{{ row.advice }}</td>
                <td>{{ row.other }}</td>
                <td>{{ row.not_answered || 0 }}</td>
                <td>{{ row.actions_total }}</td>
              </tr>
              <tr v-if="!monthlyHistory.length">
                <td colspan="9" class="empty-state">Oyma-oy natija topilmadi.</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <div class="operator-visit-control glass-soft">
        <div class="section-head section-head--wrap">
          <div>
            <div class="eyebrow">Menenjer nazorati</div>
            <h3>Keldi / Kelmadi natijalari</h3>
            <p>Bu yerda faqat sizga biriktirilgan menenjerlar bosgan natijalar ko‘rinadi.</p>
          </div>
          <div class="operator-visit-control__summary">
            <span class="badge">Keldi: {{ operatorArrivedCount }}</span>
            <span class="badge muted">Kelmadi: {{ operatorNotArrivedCount }}</span>
            <span class="badge">To‘lov qildi: {{ operatorPaymentDoneCount }}</span>
            <span class="badge muted">To‘lov qilmadi: {{ operatorPaymentNotDoneCount }}</span>
          </div>
        </div>

        <div class="operator-visit-control__filters">
          <select class="select" v-model="operatorDecisionFilter">
            <option value="all">Keldi/Kelmadi</option>
            <option value="arrived">Keldi</option>
            <option value="not_arrived">Kelmadi</option>
          </select>
          <select class="select" v-model="operatorPaymentFilter">
            <option value="all">To‘lov</option>
            <option value="paid">To‘lov qildi</option>
            <option value="unpaid">To‘lov qilmadi</option>
            <option value="pending">Belgilanmagan</option>
          </select>
        </div>

        <div v-if="filteredOperatorVisitDecisions.length" class="operator-visit-control__grid">
          <article v-for="item in filteredOperatorVisitDecisions" :key="`operator-decision-${item.id}`" class="operator-visit-card">
            <div class="operator-visit-card__top">
              <span class="operator-visit-status" :class="item.decision === 'arrived' ? 'operator-visit-status--arrived' : 'operator-visit-status--not-arrived'">
                {{ item.decision === 'arrived' ? 'Keldi' : 'Kelmadi' }}
              </span>
              <span class="operator-visit-payment" :class="`operator-visit-payment--${operatorPaymentStatus(item)}`">
                {{ operatorPaymentStatusLabel(item) }}
              </span>
            </div>
            <h4>{{ item.lead_name || item.full_name || 'Lead' }}</h4>
            <div class="operator-visit-card__meta">
              <span><strong>Menenjer:</strong> {{ item.filial_rahbari_name || '-' }}</span>
              <span><strong>Filial:</strong> {{ item.filial_rahbari_branch || item.branch_name || '-' }}</span>
              <span><strong>Fan:</strong> {{ item.subject || '-' }}</span>
              <span><strong>Sinf:</strong> {{ item.grade || '-' }}</span>
              <span><strong>Tel:</strong> {{ item.lead_phone || item.phone1 || '-' }}</span>
              <span><strong>Vaqt:</strong> {{ formatDateTime(item.updated_at) }}</span>
              <span v-if="item.operator_note" class="operator-note-line"><strong>Sizning izohingiz:</strong> {{ item.operator_note }}</span>
              <span v-if="item.operator_note_at" class="operator-note-line"><strong>Izoh vaqti:</strong> {{ formatDateTime(item.operator_note_at) }}</span>
              <span v-if="operatorPaymentStatus(item) !== 'pending'"><strong>Holatni belgilagan:</strong> {{ item.payment_status_by_name || '-' }}</span>
              <span v-if="operatorPaymentStatus(item) !== 'pending'"><strong>To‘lov holati vaqti:</strong> {{ formatDateTime(item.payment_status_at) }}</span>
            </div>
          </article>
        </div>
        <div v-else class="empty-state">Sizga tegishli filiallar bo‘yicha Keldi/Kelmadi natijasi hali yo‘q.</div>
      </div>
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
          @save-name="saveLeadName"
        />
      </div>
      <div v-else class="operator-new-leads__empty">
        Hozircha yangi biriktirilgan lead yo‘q yoki qidiruvga mos lead topilmadi.
      </div>
    </section>

    <section v-else-if="currentTab === 'incoming'" class="operator-new-leads panel glass">
      <div class="operator-new-leads__head">
        <div>
          <div class="eyebrow">KIRUVCHI QO'NG'IROQLAR</div>
          <h3>Siz qo'lda qo'shgan leadlar</h3>
          <p>"Lead qo'shish" tugmasi orqali qo'shilgan barcha mijozlar shu yerda ko'rinadi.</p>
        </div>
        <span class="badge">{{ filteredIncomingLeads.length }} ta lead</span>
      </div>

      <div v-if="filteredIncomingLeads.length" class="operator-new-leads__grid operator-new-leads__grid--static">
        <OperatorLeadCompactCard
          v-for="lead in filteredIncomingLeads"
          :key="`incoming-${lead.id}`"
          :lead="lead"
          :busy="processingLeadId === lead.id"
          :reminder-busy="reminderSavingId === lead.id"
          :drag-disabled="true"
          @request-status-change="openStatusChangeModal"
          @save-reminder="saveReminder"
          @clear-reminder="clearReminder"
          @save-name="saveLeadName"
        />
      </div>
      <div v-else class="operator-new-leads__empty">
        Hozircha kiruvchi qo'ng'iroq orqali qo'shilgan lead yo'q.
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
            @save-name="saveLeadName"
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
          @save-name="saveLeadName"
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

      <div class="operator-status-page-tabs">
        <button
          type="button"
          class="operator-status-page-tab"
          :class="{ active: statusPage === 'main' }"
          @click="statusPage = 'main'"
        >
          1-sahifa
        </button>
        <button
          type="button"
          class="operator-status-page-tab"
          :class="{ active: statusPage === 'extra' }"
          @click="statusPage = 'extra'"
        >
          2-sahifa
        </button>
      </div>

      <ResponsiveSwiper
        v-if="isCompact"
        :items="activeStatusPageSections"
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
          @save-name="saveLeadName"
              />
              <div v-if="!section.leads.length" class="operator-status-column__empty">
                Bu bo‘limda lead yo‘q.
              </div>
            </div>
          </section>
        </template>
      </ResponsiveSwiper>

      <div
        v-else
        class="operator-status-board"
        :class="{ 'content-dim': loading, 'operator-status-board--extra': statusPage === 'extra' }"
      >
        <section
          v-for="section in activeStatusPageSections"
          :key="section.key"
          class="operator-status-column"
          :class="[`status-${section.key}`, { 'drop-active': dropTargetStatus === section.key }]"
          @dragover.prevent="handleColumnDragOver(section.key)"
          @dragleave="handleColumnDragLeave(section.key)"
          @drop.prevent="handleStatusDrop(section.key)"
        >
          <div class="operator-status-column__top">
            <div class="operator-status-column__title">
              <div class="operator-status-column__icon">{{ getStatusIcon(section.key) }}</div>
              <h3>{{ section.title }}</h3>
            </div>
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
          @save-name="saveLeadName"
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
import ResponsiveSwiper from '../../components/ui/ResponsiveSwiper.vue'
import { useViewport } from '../../composables/useViewport'
import { useAuthStore } from '../../stores/auth'

const fetchStatusOrder = ['new', 'sale', 'otkaz', 'wrong_number', 'open_number', 'advice', 'other', 'not_answered']
const sectionOrder = ['sale', 'otkaz', 'wrong_number', 'open_number', 'advice', 'other', 'not_answered']
const statusPageMap = {
  main: ['sale', 'open_number', 'advice'],
  extra: ['otkaz', 'wrong_number', 'other', 'not_answered'],
}
const sectionMeta = {
  sale: { title: 'Sotuvlar' },
  otkaz: { title: 'Atkaz' },
  wrong_number: { title: 'Xato nomer' },
  open_number: { title: "O'chiq Nomer" },
  advice: { title: 'Maslahat' },
  other: { title: "O'qiydi" },
  not_answered: { title: "Ko'tarmadi" },
}
const noteRequiredStatuses = ['sale', 'otkaz', 'advice', 'other']
const statusLabels = { new: 'Biriktirilgan leadlar', sale: 'Sotuv', otkaz: 'Atkaz', wrong_number: 'Xato nomer', open_number: "O‘chiq nomer", advice: 'Maslahat', other: "O'qiydi", not_answered: "Ko'tarmadi" }
const sleep = (ms) => new Promise(resolve => setTimeout(resolve, ms))

const route = useRoute()
const router = useRouter()
const { isCompact } = useViewport(1100, 640)
const authStore = useAuthStore()

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
const monthlyHistory = ref([])
const operatorVisitDecisions = ref([])
const operatorDecisionFilter = ref('all')
const operatorPaymentFilter = ref('all')
const statusPage = ref('main')
const draggedLead = ref(null)
const dropTargetStatus = ref('')
const statusModal = reactive({ open: false, lead: null, status: '', existingNote: '', newNote: '' })
const assignedStatusModal = reactive({ open: false, lead: null, existingNote: '' })
const saleBranchModal = reactive({ open: false, lead: null, existingNote: '' })
const addLeadModal = reactive({
  step: 'closed', // 'closed' | 'form' | 'branch' | 'status'
  full_name: '',
  phone1: '',
  phone2: '',
  subject: '',
  branch: '',
  saving: false,
  createdLead: null,
})
const apiOperatorBranchNames = ref([])
const allSaleBranchNames = [
  'Niyozbosh',
  'Kids 1',
  'Kids 2',
  'Gulbahor',
  'Kids 3',
  'Kasblar',
  'Xalqobod',
  'Chinoz',
  'Olmozor',
  'Paxtazor',
  'Mevazor',
  'Dostobod',
  "Qorg'onchi",
  "Oqqo'rg'on",
  "Qo'shyog'och",
]
const reportDays = 31
const leadsByStatus = reactive(Object.fromEntries(fetchStatusOrder.map((key) => [key, []])))
const daily = reactive({ new: 0, sale: 0, otkaz: 0, advice: 0, open_number: 0, wrong_number: 0, other: 0, not_answered: 0, daily_sale: 0, daily_otkaz: 0, touched_today: 0, actions_today: 0 })
const summaryCards = computed(() => ([
  { title: 'Biriktirilgan leadlar', value: daily.new, subtitle: 'Yangi biriktirilgan leadlar' },
  { title: 'Bugungi sotuv', value: daily.daily_sale, subtitle: 'Sotuvga aylangan leadlar' },
  { title: 'Bugungi atkaz', value: daily.daily_otkaz, subtitle: 'Qayta ishlashga o‘tgan leadlar' },
  { title: 'Aloqa qilingan', value: daily.touched_today, subtitle: 'Bugun ishlangan leadlar' },
]))

const operatorMetricCards = computed(() => ([
  { key: 'assigned', title: 'Biriktirilgan leadlar', value: daily.new, subtitle: 'Yangi biriktirilgan leadlar', icon: '👥' },
  { key: 'sale', title: 'Bugungi sotuv', value: daily.daily_sale, subtitle: 'Sotuvga aylangan leadlar', icon: '🛒' },
  { key: 'otkaz', title: 'Bugungi atkaz', value: daily.daily_otkaz, subtitle: 'Qayta ishlashga o‘tgan leadlar', icon: '📨' },
  { key: 'touched', title: 'Aloqa qilingan', value: daily.touched_today, subtitle: 'Bugun ishlangan leadlar', icon: '📞' },
]))

const statusIconMap = {
  sale: '🛒',
  open_number: '🔓',
  advice: '💬',
  otkaz: '📨',
  wrong_number: '⚠️',
  other: '📘',
  not_answered: '📵',
}

function getStatusIcon(statusKey) {
  return statusIconMap[statusKey] || '•'
}

let successTimer = null
let reminderCheckTimer = null
let actionToastTimer = null
const notifiedReminderKeys = new Set()

const currentTab = computed(() => ['assigned', 'incoming', 'timed', 'report'].includes(route.query.tab) ? route.query.tab : 'general')
const newlyAssignedLeads = computed(() => leadsByStatus.new || [])
const incomingLeads = ref([])
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

function normalizeOperatorBranchList(value) {
  const raw = Array.isArray(value)
    ? value
    : String(value || '').replace(';', ',').split(',')
  const names = raw
    .map((item) => String(item || '').trim())
    .map((item) => (/^\d+\s*-/.test(item) ? item.split('-', 2)[1].trim() : item))
    .filter(Boolean)
  return [...new Set(names)]
}

const operatorBranchNames = computed(() => {
  if (apiOperatorBranchNames.value.length) return apiOperatorBranchNames.value

  const user = authStore.user || JSON.parse(localStorage.getItem('user') || 'null') || {}
  const localBranches = Array.isArray(user.branch_names) && user.branch_names.length
    ? user.branch_names
    : user.branch_name
  return normalizeOperatorBranchList(localBranches)
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
const filteredIncomingLeads = computed(() => incomingLeads.value.filter(leadMatchesAppliedSearch))
const filteredTimedLeads = computed(() => fetchStatusOrder
  .flatMap((status) => leadsByStatus[status] || [])
  .filter((lead) => Boolean(lead?.reminder_at))
  .filter(leadMatchesAppliedSearch))
const displaySections = computed(() => sectionOrder.map((key) => ({
  key,
  title: sectionMeta[key].title,
  leads: (leadsByStatus[key] || []).filter(leadMatchesFilters),
})))
const activeStatusPageSections = computed(() => {
  const keys = statusPageMap[statusPage.value] || statusPageMap.main
  return displaySections.value.filter(section => keys.includes(section.key))
})
const visibleLeadCount = computed(() => {
  if (currentTab.value === 'assigned') return filteredAssignedLeads.value.length
  if (currentTab.value === 'incoming') return filteredIncomingLeads.value.length
  if (currentTab.value === 'timed') return filteredTimedLeads.value.length
  if (currentTab.value === 'report') return dailyHistory.value.length
  return activeStatusPageSections.value.reduce((sum, item) => sum + item.leads.length, 0)
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
      { key: 'not_answered', title: "Ko'tarmadi", count: latest.not_answered || 0 },
    ]
  }
  return activeStatusPageSections.value.map(section => ({ key: section.key, title: section.title, count: section.leads.length }))
})

function operatorPaymentStatus(item) {
  if (item?.payment_status) return item.payment_status
  if (item?.payment_done) return 'paid'
  if (item?.payment_not_done || item?.left_without_payment) return 'unpaid'
  return 'pending'
}

function operatorPaymentStatusLabel(item) {
  const status = operatorPaymentStatus(item)
  if (status === 'paid') return 'To‘lov qildi'
  if (status === 'unpaid') return 'To‘lov qilmadi'
  return 'Belgilanmagan'
}

const filteredOperatorVisitDecisions = computed(() => operatorVisitDecisions.value.filter((item) => {
  if (operatorDecisionFilter.value !== 'all' && item.decision !== operatorDecisionFilter.value) return false
  if (operatorPaymentFilter.value !== 'all' && operatorPaymentStatus(item) !== operatorPaymentFilter.value) return false
  return true
}))
const operatorArrivedCount = computed(() => operatorVisitDecisions.value.filter(item => item.decision === 'arrived').length)
const operatorNotArrivedCount = computed(() => operatorVisitDecisions.value.filter(item => item.decision === 'not_arrived').length)
const operatorPaymentDoneCount = computed(() => operatorVisitDecisions.value.filter(item => operatorPaymentStatus(item) === 'paid').length)
const operatorPaymentNotDoneCount = computed(() => operatorVisitDecisions.value.filter(item => operatorPaymentStatus(item) === 'unpaid').length)

function formatDateTime(value) {
  if (!value) return '-'
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return '-'
  const dd = String(date.getDate()).padStart(2, '0')
  const mm = String(date.getMonth() + 1).padStart(2, '0')
  const yyyy = date.getFullYear()
  const hh = String(date.getHours()).padStart(2, '0')
  const min = String(date.getMinutes()).padStart(2, '0')
  return `${dd}.${mm}.${yyyy} ${hh}:${min}`
}

watch(() => route.query.tab, (tab) => {
  if (!['assigned', 'general', 'incoming', 'timed', 'report'].includes(tab)) {
    router.replace({ path: '/operator', query: { ...route.query, tab: 'general' } })
  }
  if (tab === 'incoming') {
    fetchIncomingLeads()
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
      if (Array.isArray(data?.operator_branch_names)) {
        apiOperatorBranchNames.value = normalizeOperatorBranchList(data.operator_branch_names)
      }
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

async function fetchIncomingLeads() {
  try {
    const { data } = await client.get('operator/leads/incoming/')
    incomingLeads.value = data.results || data || []
  } catch (error) {
    errorMessage.value = error?.response?.data?.detail || "Kiruvchi qo'ng'iroqlarni yuklashda xatolik yuz berdi."
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
    const { data } = await client.get('operator/daily-history/', { params: { days: reportDays, months: 12 } })
    dailyHistory.value = data?.results || []
    monthlyHistory.value = data?.monthly_archive || []
  } catch {
    dailyHistory.value = []
    monthlyHistory.value = []
  }
}

async function fetchOperatorVisitDecisions() {
  try {
    const { data } = await client.get('operator/lead-visit-decisions/')
    operatorVisitDecisions.value = data?.results || data || []
  } catch {
    operatorVisitDecisions.value = []
  }
}

function updateLeadInLists(updatedLead) {
  fetchStatusOrder.forEach((status) => {
    leadsByStatus[status] = (leadsByStatus[status] || []).map((item) => (item.id === updatedLead.id ? updatedLead : item))
  })
  incomingLeads.value = incomingLeads.value.map((item) => (item.id === updatedLead.id ? updatedLead : item))
}


function extractApiError(error, fallback = 'Xatolik yuz berdi.') {
  const data = error?.response?.data
  if (!data) return fallback
  if (typeof data === 'string') return data || fallback
  if (data.detail) return String(data.detail)
  for (const key of ['note', 'selected_branch', 'current_status', 'status', 'non_field_errors']) {
    const value = data[key]
    if (Array.isArray(value) && value.length) return String(value[0])
    if (typeof value === 'string' && value) return value
  }
  const firstValue = Object.values(data).find(Boolean)
  if (Array.isArray(firstValue) && firstValue.length) return String(firstValue[0])
  if (typeof firstValue === 'string') return firstValue
  return fallback
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

function openSaleBranchModal(lead, existingNote = '') {
  saleBranchModal.open = true
  saleBranchModal.lead = lead
  saleBranchModal.existingNote = existingNote
}

function closeSaleBranchModal() {
  saleBranchModal.open = false
  saleBranchModal.lead = null
  saleBranchModal.existingNote = ''
}

async function confirmSaleBranch(branch) {
  const lead = saleBranchModal.lead
  const saleNote = saleBranchModal.existingNote
  closeSaleBranchModal()
  if (!lead || !branch) return
  await changeStatus({ id: lead.id, status: 'sale', note: saleNote, selected_branch: branch })
}

function openAddLeadModal() {
  addLeadModal.step = 'form'
  addLeadModal.full_name = ''
  addLeadModal.phone1 = ''
  addLeadModal.phone2 = ''
  addLeadModal.subject = ''
  addLeadModal.branch = ''
  addLeadModal.saving = false
  addLeadModal.createdLead = null
}

function closeAddLeadModal() {
  addLeadModal.step = 'closed'
  addLeadModal.full_name = ''
  addLeadModal.phone1 = ''
  addLeadModal.phone2 = ''
  addLeadModal.subject = ''
  addLeadModal.branch = ''
  addLeadModal.saving = false
  addLeadModal.createdLead = null
}

async function submitAddLeadForm() {
  if (!addLeadModal.full_name.trim() || !addLeadModal.phone1.trim()) {
    errorMessage.value = 'Ism Familya va Nomer 1 kiritish shart.'
    return
  }
  addLeadModal.saving = true
  errorMessage.value = ''
  try {
    const { data } = await client.post('operator/leads/create/', {
      full_name: addLeadModal.full_name.trim(),
      phone1: addLeadModal.phone1.trim(),
      phone2: addLeadModal.phone2.trim(),
      subject: addLeadModal.subject.trim(),
    })
    addLeadModal.createdLead = data
    addLeadModal.step = 'branch'
    incomingLeads.value = [data, ...incomingLeads.value]
    await Promise.all([fetchAllStatuses('Leadlar yangilanmoqda...'), fetchDaily()])
  } catch (error) {
    errorMessage.value = extractApiError(error, 'Lead qo‘shishda xatolik yuz berdi.')
  } finally {
    addLeadModal.saving = false
  }
}

function selectAddLeadBranch(branch) {
  addLeadModal.branch = branch
  addLeadModal.step = 'status'
}

async function selectAddLeadStatus(status) {
  const lead = addLeadModal.createdLead
  const branch = addLeadModal.branch
  if (!lead || !status) return
  closeAddLeadModal()
  if (status === 'sale') {
    await changeStatus({ id: lead.id, status: 'sale', note: `Kiruvchi qo‘ng‘iroq orqali qo‘shildi`, selected_branch: branch })
    return
  }
  await changeStatus({ id: lead.id, status, note: `Kiruvchi qo‘ng‘iroq orqali qo‘shildi | Filial: ${branch}` })
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

async function handleSaleStatusChange(lead, saleNote = '') {
  if (!lead) return
  const note = buildLatestNote(saleNote)
  if (!note) {
    errorMessage.value = "Sotuv qilish uchun izoh kiriting."
    return
  }

  // Yangi qoida: Sotuvda operatorga biriktirilgan filiallar emas,
  // barcha filiallar chiqadi. Qaysi filial tanlansa, lead o‘sha filial
  // rahbari paneliga tushadi.
  openSaleBranchModal(lead, note)
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
  const lead = statusModal.lead
  const status = statusModal.status
  const latestNote = buildLatestNote(statusModal.newNote)
  if (!latestNote) {
    errorMessage.value = status === 'sale' ? 'Sotuv qilish uchun izoh kiriting.' : "Holatni o'zgartirish uchun yangi izoh kiriting."
    return
  }
  closeStatusModal()
  if (status === 'sale') {
    await handleSaleStatusChange(lead, latestNote)
    return
  }
  await changeStatus({ id: lead.id, status, note: latestNote })
}

async function changeStatus(payload) {
  errorMessage.value = ''
  const nextStatus = payload?.status || ''
  const note = String(payload?.note || '').trim()

  if (noteRequiredStatuses.includes(nextStatus) && !note) {
    errorMessage.value = nextStatus === 'sale' ? 'Sotuv qilish uchun izoh kiriting.' : "Holatni o'zgartirish uchun yangi izoh kiriting."
    return
  }

  try {
    processingLeadId.value = payload.id
    const { data } = await client.patch(`operator/leads/${payload.id}/change-status/`, {
      current_status: nextStatus,
      status: nextStatus,
      note,
      selected_branch: payload?.selected_branch || '',
    })
    await sleep(250)
    updateLeadInLists(data)
    try {
      await Promise.all([fetchAllStatuses('Leadlar yangilanmoqda...'), fetchDaily(), fetchDailyHistory(), fetchOperatorVisitDecisions()])
    } catch (refreshError) {
      console.warn('Status yangilandi, lekin ro‘yxatni qayta yuklashda xatolik:', refreshError)
    }
    showSuccess(`${statusLabels[nextStatus] || 'Tanlangan bo‘lim'} bo‘limiga o‘tkazildi`)
  } catch (error) {
    errorMessage.value = extractApiError(error, 'Statusni yangilashda xatolik yuz berdi.')
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

async function saveLeadName(payload) {
  errorMessage.value = ''
  try {
    const { data } = await client.patch(`operator/leads/${payload.lead.id}/update-name/`, {
      full_name: payload.full_name,
    })
    updateLeadInLists(data)
    showActionToast('Lead ismi yangilandi.')
  } catch (error) {
    errorMessage.value = error?.response?.data?.detail || 'Ismni saqlashda xatolik yuz berdi.'
    throw error
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
  await Promise.all([fetchAllStatuses(), fetchDaily(), fetchDailyHistory(), fetchOperatorVisitDecisions()])
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

<style scoped>

/* Operator panel — screenshotdagi premium light dashboardga yaqinlashtirildi */
.operator-page--board {
  gap: 22px;
}

.operator-board-top {
  grid-template-columns: minmax(0, 0.95fr) minmax(640px, 1.05fr);
  align-items: center;
  padding: 24px 28px;
  border-radius: 24px;
  background: linear-gradient(180deg, rgba(255,255,255,0.99), rgba(248,251,255,0.98));
  box-shadow: 0 18px 46px rgba(15, 23, 42, 0.06);
}

.operator-board-top__badges,
.operator-board-top__metrics {
  gap: 10px 12px;
}

.operator-board-top__badges .badge,
.operator-count-pill {
  min-height: 38px;
  padding: 9px 16px;
  border-radius: 12px;
  background: #ffffff;
  border: 1px solid rgba(219, 234, 254, 0.95);
  box-shadow: 0 8px 18px rgba(15, 23, 42, 0.035);
}

.operator-count-pill.status-sale {
  background: rgba(239, 246, 255, 0.96);
  color: #2563eb;
}
.operator-count-pill.status-open_number {
  background: rgba(240, 253, 244, 0.96);
  color: #16a34a;
}
.operator-count-pill.status-advice {
  background: rgba(245, 243, 255, 0.96);
  color: #7c3aed;
}

.operator-board-top__search {
  grid-template-columns: minmax(260px, 1fr) minmax(260px, 0.9fr) minmax(190px, 220px) auto;
  gap: 14px;
}

.operator-board-top__search .input,
.operator-board-top__search .btn {
  min-height: 60px;
  border-radius: 16px;
  font-weight: 700;
}

.operator-board-top__search .input {
  background: #ffffff;
  border-color: rgba(203, 213, 225, 0.72);
  box-shadow: inset 0 1px 0 rgba(255,255,255,0.8), 0 8px 20px rgba(15,23,42,0.035);
}

.operator-board-top__search .btn.ghost:first-of-type {
  min-width: 220px;
  background: linear-gradient(135deg, #1d4ed8, #2563eb 54%, #3b82f6);
  border-color: transparent;
  color: white;
  box-shadow: 0 18px 34px rgba(37, 99, 235, 0.22);
}

.operator-board-top__search .btn.ghost:first-of-type::before {
  content: '🔍';
  margin-right: 8px;
}

.operator-metric-grid {
  gap: 22px;
}

.operator-metric-card {
  min-height: 150px;
  padding: 26px 28px;
  border-radius: 24px;
  background: linear-gradient(180deg, #ffffff, #fbfdff);
  box-shadow: 0 18px 42px rgba(15,23,42,0.055);
}

.operator-metric-card__icon {
  width: 78px;
  height: 78px;
  border-radius: 50%;
  font-size: 34px;
}

.operator-metric-card__label {
  color: #64748b;
  font-weight: 800;
}

.operator-metric-card__value {
  font-size: clamp(40px, 4.4vw, 60px);
}

.operator-metric-card__action {
  border-radius: 999px;
  background: #fff;
  box-shadow: 0 8px 18px rgba(15, 23, 42, 0.03);
}

.operator-status-board-wrap {
  padding: 0;
  background: transparent;
  border: none;
  box-shadow: none;
}

.operator-status-page-tabs {
  margin: 0 0 18px;
}

.operator-status-page-tab {
  min-width: 150px;
  min-height: 48px;
  border-radius: 12px;
}

.operator-status-board {
  gap: 32px;
}

.operator-status-column {
  min-height: 520px;
  padding: 18px 18px 20px;
  border-radius: 24px;
  box-shadow: 0 18px 42px rgba(15, 23, 42, 0.055);
}

.operator-status-column__top {
  padding: 0 2px;
}

.operator-status-column__title h3 {
  font-size: 20px;
  font-weight: 900;
}

.operator-status-column__icon {
  width: 46px;
  height: 46px;
  border-radius: 16px;
}

.operator-status-count {
  min-height: 34px;
  padding: 8px 16px;
  background: rgba(255,255,255,0.9);
  font-weight: 800;
}

.operator-status-column.status-sale .operator-status-count {
  color: #2563eb;
  border-color: rgba(191,219,254,0.95);
}
.operator-status-column.status-open_number .operator-status-count {
  color: #16a34a;
  border-color: rgba(187,247,208,0.95);
}
.operator-status-column.status-advice .operator-status-count {
  color: #7c3aed;
  border-color: rgba(221,214,254,0.95);
}
.operator-status-column.status-otkaz .operator-status-count {
  color: #ef4444;
  border-color: rgba(252,165,165,0.9);
}
.operator-status-column.status-wrong_number .operator-status-count {
  color: #d97706;
  border-color: rgba(253,230,138,0.9);
}
.operator-status-column.status-other .operator-status-count {
  color: #475569;
}

.operator-status-column__cards {
  gap: 18px;
}

.operator-new-leads,
.operator-report-panel {
  border-radius: 26px;
}

@media (max-width: 1280px) {
  .operator-board-top {
    grid-template-columns: 1fr;
  }

  .operator-board-top__search {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .operator-board-top__search .btn.ghost:first-of-type {
    min-width: 0;
  }
}

@media (max-width: 760px) {
  .operator-board-top {
    padding: 18px;
  }

  .operator-board-top__search {
    grid-template-columns: 1fr;
  }

  .operator-status-page-tab {
    min-width: 120px;
  }
}

.operator-page {
  gap: 18px;
}

.operator-board-top {
  display: grid;
  grid-template-columns: minmax(0, 1.2fr) minmax(520px, 1fr);
  gap: 18px;
  padding: 18px 20px;
  border-radius: 28px;
  background: linear-gradient(180deg, rgba(255,255,255,0.98), rgba(248,250,252,0.97));
  border: 1px solid rgba(226,232,240,0.95);
  box-shadow: 0 18px 36px rgba(15,23,42,0.05);
}

.operator-board-top__info,
.operator-board-top__search {
  display: grid;
  gap: 14px;
}

.operator-board-top__badges,
.operator-board-top__metrics {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.operator-count-pill {
  display: inline-flex;
  align-items: center;
  min-height: 44px;
  padding: 10px 16px;
  border-radius: 14px;
  background: rgba(255,255,255,0.96);
  border: 1px solid rgba(226,232,240,0.96);
  font-size: 14px;
  font-weight: 700;
  color: #0f1f5c;
}

.operator-count-pill.status-sale { color: #2563eb; }
.operator-count-pill.status-open_number { color: #16a34a; }
.operator-count-pill.status-advice { color: #7c3aed; }
.operator-count-pill.status-otkaz { color: #ef4444; }
.operator-count-pill.status-wrong_number { color: #f59e0b; }
.operator-count-pill.status-other { color: #475569; }

.operator-board-top__search {
  grid-template-columns: minmax(220px, 1fr) minmax(220px, 320px) minmax(180px, 220px) auto;
  align-items: stretch;
}

.operator-board-top__search .input,
.operator-board-top__search .btn {
  min-height: 54px;
  border-radius: 18px;
}

.operator-board-top__search .btn.ghost:first-of-type {
  background: linear-gradient(135deg, #2563eb, #3b82f6);
  color: #fff;
  border-color: transparent;
  box-shadow: 0 14px 28px rgba(37,99,235,0.2);
}

.operator-metric-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 18px;
}

.operator-metric-card {
  display: flex;
  align-items: center;
  gap: 18px;
  padding: 20px 22px;
  border-radius: 26px;
  background: linear-gradient(180deg, rgba(255,255,255,0.99), rgba(248,250,252,0.97));
  border: 1px solid rgba(226,232,240,0.96);
  box-shadow: 0 18px 32px rgba(15,23,42,0.04);
}

.operator-metric-card__icon {
  width: 66px;
  height: 66px;
  border-radius: 22px;
  display: grid;
  place-items: center;
  font-size: 30px;
  flex: 0 0 auto;
  background: linear-gradient(135deg, rgba(59,130,246,0.1), rgba(147,197,253,0.24));
}

.operator-metric-card--sale .operator-metric-card__icon { background: linear-gradient(135deg, rgba(34,197,94,0.12), rgba(134,239,172,0.25)); }
.operator-metric-card--otkaz .operator-metric-card__icon { background: linear-gradient(135deg, rgba(124,58,237,0.12), rgba(196,181,253,0.25)); }
.operator-metric-card--touched .operator-metric-card__icon { background: linear-gradient(135deg, rgba(37,99,235,0.12), rgba(191,219,254,0.28)); }

.operator-metric-card__content {
  display: grid;
  gap: 8px;
  min-width: 0;
}

.operator-metric-card__label {
  font-size: 15px;
  font-weight: 700;
  color: #64748b;
}

.operator-metric-card__value {
  font-size: clamp(34px, 4vw, 54px);
  line-height: 1;
  letter-spacing: -0.04em;
  color: #0f1f5c;
}

.operator-metric-card__action {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  width: fit-content;
  padding: 10px 16px;
  border-radius: 999px;
  border: 1px solid rgba(191,219,254,0.92);
  color: #2563eb;
  background: #fff;
  font-size: 13px;
  font-weight: 700;
}

.operator-status-board-wrap {
  padding-top: 18px;
  border-radius: 30px;
  background: linear-gradient(180deg, rgba(255,255,255,0.99), rgba(248,250,252,0.97));
  border: 1px solid rgba(226,232,240,0.95);
  box-shadow: 0 18px 38px rgba(15,23,42,0.05);
}

.operator-status-page-tabs {
  display: flex;
  justify-content: center;
  gap: 16px;
  margin: 4px 0 18px;
}

.operator-status-page-tab {
  min-width: 120px;
  min-height: 44px;
  padding: 10px 18px;
  border-radius: 16px;
  border: 1px solid rgba(226,232,240,0.96);
  background: #fff;
  color: #0f1f5c;
  font-size: 16px;
  font-weight: 700;
  box-shadow: 0 10px 24px rgba(15,23,42,0.04);
}

.operator-status-page-tab.active {
  background: linear-gradient(135deg, #2563eb, #3b82f6);
  border-color: transparent;
  color: #fff;
}

.operator-status-board {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
  gap: 24px;
}

.operator-status-board--extra {
  grid-template-columns: repeat(4, minmax(180px, 1fr)) !important;
}

.operator-status-board--extra .operator-status-column {
  min-width: 0;
}

.operator-status-column {
  padding: 18px;
  border-radius: 26px;
  background: linear-gradient(180deg, rgba(255,255,255,0.98), rgba(250,250,252,0.95));
  border: 1px solid rgba(226,232,240,0.95);
  box-shadow: 0 16px 30px rgba(15,23,42,0.04);
}

.operator-status-column.status-sale { background: linear-gradient(180deg, rgba(239,246,255,0.9), rgba(255,255,255,0.96)); }
.operator-status-column.status-open_number { background: linear-gradient(180deg, rgba(240,253,244,0.92), rgba(255,255,255,0.96)); }
.operator-status-column.status-advice { background: linear-gradient(180deg, rgba(245,243,255,0.94), rgba(255,255,255,0.96)); }
.operator-status-column.status-otkaz { background: linear-gradient(180deg, rgba(254,242,242,0.92), rgba(255,255,255,0.96)); }
.operator-status-column.status-wrong_number { background: linear-gradient(180deg, rgba(255,251,235,0.94), rgba(255,255,255,0.96)); }
.operator-status-column.status-other { background: linear-gradient(180deg, rgba(248,250,252,0.94), rgba(255,255,255,0.96)); }
.operator-status-column.status-not_answered { background: linear-gradient(180deg, rgba(241,245,249,0.94), rgba(255,255,255,0.96)); }

.operator-status-column__top {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 14px;
  margin-bottom: 16px;
}

.operator-status-column__title {
  display: flex;
  align-items: center;
  gap: 14px;
}

.operator-status-column__icon {
  width: 52px;
  height: 52px;
  border-radius: 18px;
  display: grid;
  place-items: center;
  font-size: 24px;
  background: rgba(255,255,255,0.92);
  border: 1px solid rgba(255,255,255,0.82);
  box-shadow: 0 10px 24px rgba(148,163,184,0.12);
}

.operator-status-column.status-sale .operator-status-column__icon { color: #2563eb; }
.operator-status-column.status-open_number .operator-status-column__icon { color: #16a34a; }
.operator-status-column.status-advice .operator-status-column__icon { color: #7c3aed; }
.operator-status-column.status-otkaz .operator-status-column__icon { color: #ef4444; }
.operator-status-column.status-wrong_number .operator-status-column__icon { color: #f59e0b; }
.operator-status-column.status-other .operator-status-column__icon { color: #475569; }
.operator-status-column.status-not_answered .operator-status-column__icon { color: #334155; }

.operator-status-column__top h3 {
  margin: 0;
  font-size: 18px;
  color: #0f1f5c;
}

.operator-status-count {
  display: inline-flex;
  align-items: center;
  padding: 8px 14px;
  border-radius: 999px;
  background: rgba(255,255,255,0.88);
  border: 1px solid rgba(226,232,240,0.9);
  font-size: 13px;
  font-weight: 700;
  color: #64748b;
}

.operator-status-column__cards {
  display: grid;
  gap: 16px;
}

.operator-new-leads,
.operator-report-panel {
  border-radius: 30px;
  background: linear-gradient(180deg, rgba(255,255,255,0.99), rgba(248,250,252,0.97));
  border: 1px solid rgba(226,232,240,0.95);
  box-shadow: 0 18px 38px rgba(15,23,42,0.05);
}

.operator-monthly-report {
  margin-top: 18px;
  padding: 18px;
  border-radius: 24px;
  background: rgba(255,255,255,0.72);
  border: 1px solid rgba(226,232,240,0.9);
}

.operator-monthly-report table {
  min-width: 920px;
}

.operator-note-line {
  grid-column: 1 / -1;
  padding: 10px 12px;
  border-radius: 14px;
  background: rgba(37, 99, 235, 0.08);
  border: 1px solid rgba(37, 99, 235, 0.14);
  color: #0f172a;
}

@media (max-width: 1280px) {
  .operator-board-top {
    grid-template-columns: 1fr;
  }

  .operator-board-top__search {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .operator-metric-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 1100px) {
  .operator-status-board {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 760px) {
  .operator-board-top {
    padding: 16px;
    border-radius: 24px;
  }

  .operator-board-top__search {
    grid-template-columns: 1fr;
  }

  .operator-metric-grid {
    grid-template-columns: 1fr;
  }

  .operator-metric-card {
    padding: 18px;
  }

  .operator-metric-card__icon {
    width: 58px;
    height: 58px;
    font-size: 26px;
  }

  .operator-status-column {
    padding: 16px;
  }

  .operator-status-column__top {
    flex-direction: column;
    align-items: flex-start;
  }
}

/* Ko'tarmadi column: 2-sahifada to'rtinchi bo'lim sifatida ko'rinishi uchun */
.operator-status-column.status-not_answered {
  background: linear-gradient(180deg, rgba(248,250,252,0.94), rgba(255,255,255,0.96));
  border-color: rgba(100,116,139,0.45);
}
.operator-status-column.status-not_answered .operator-status-count {
  color: #475569;
  border-color: rgba(148,163,184,0.9);
}


@media (max-width: 1180px) {
  .operator-status-board--extra {
    grid-template-columns: repeat(2, minmax(220px, 1fr)) !important;
  }
}

@media (max-width: 720px) {
  .operator-status-board--extra {
    grid-template-columns: 1fr !important;
  }
}

.add-lead-btn {
  padding: 8px 16px;
  border-radius: 999px;
  font-weight: 700;
  font-size: 13px;
  min-height: 0;
  height: auto;
  background: linear-gradient(135deg, #2563eb, #38bdf8);
  color: white;
  border: none;
  cursor: pointer;
  box-shadow: 0 8px 18px rgba(37, 99, 235, 0.24);
  transition: transform 0.15s ease;
}

.add-lead-btn:hover {
  transform: translateY(-1px);
}

.add-lead-modal {
  max-width: 440px;
}

.add-lead-modal .grid {
  gap: 12px;
}
</style>
