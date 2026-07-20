<template>
  <div class="grid admin-page">
    <div class="hero glass panel">
      <div>
        <div class="eyebrow">Admin paneli</div>
        <h1 class="hero__title">CRM bo'yicha global nazorat</h1>
        <p class="hero__text">Boshliqlarni va Menenjerlarni yarating, umumiy statistikani ko'ring va tizimdagi barcha lead holatlarini yuqoridan turib nazorat qiling.</p>
      </div>
      <div class="hero__actions">
        <button class="btn secondary" :disabled="allReportsDownloading" @click="downloadAllReportsExcel">{{ allReportsDownloading ? 'Yuklanmoqda...' : 'Barcha hisobotlarni yuklash' }}</button>
        <button class="btn secondary" :disabled="monthlyReportDownloading" @click="openMonthlyReportModal">Oylik Hisobot yuklash</button>
        <button class="btn secondary" @click="openFilialModal = true">Menenjer yaratish</button>
        <button class="btn" @click="openBossModal = true">Boshliq yaratish</button>
        <button class="btn secondary" @click="openDirectorModal('director')">Bosh direktor yaratish</button>
        <button class="btn secondary" @click="openDirectorModal('director_deputy')">Bosh direktor o'rinbosari yaratish</button>
      </div>
    </div>

    <div v-if="error" class="error-banner">{{ error }}</div>
    <div v-if="success" class="success-banner">{{ success }}</div>

    <div v-if="currentAdminTab === 'database'" class="panel glass admin-database-panel">
      <div class="section-head section-head--wrap">
        <div>
          <div class="eyebrow">Ma'lumotlar bazasi</div>
          <h3>Hamma leadlar ma'lumotlari</h3>
          <p>Biriktirilgan, sotuv, atkaz va boshqa barcha leadlarni shu yerdan qidiring va kerak bo‘lsa o‘chiring.</p>
        </div>
        <div class="lead-toolbar-info lead-toolbar-info--wrap">
          <span class="badge">Jami: {{ adminDatabaseLeads.length }}</span>
          <span class="badge muted">Ko‘rinayotgan: {{ filteredAdminDatabaseLeads.length }}</span>
          <span class="badge selected-leads-badge">Tanlangan: {{ selectedAdminLeadIds.length }}</span>
        </div>
      </div>

      <div class="toolbar toolbar--responsive admin-database-toolbar">
        <input
          class="input admin-database-search"
          v-model="adminLeadSearch"
          placeholder="Lead qidirish: F.I.O, telefon, maktab, sinf, fan, operator..."
        />
        <select class="select" v-model="adminLeadStatusFilter">
          <option value="">Status</option>
          <option value="new">Biriktirilgan</option>
          <option value="sale">Sotuv</option>
          <option value="otkaz">Atkaz</option>
          <option value="wrong_number">Xato nomer</option>
          <option value="open_number">O‘chiq nomer</option>
          <option value="advice">Maslahat</option>
          <option value="other">O‘qiydi</option>
          <option value="not_answered">Ko'tarmadi</option>
        </select>
        <select class="select admin-operator-filter" v-model="adminLeadOperatorFilter">
          <option value="">Barcha operatorlar</option>
          <option v-for="operator in adminLeadOperatorOptions" :key="`admin-db-operator-${operator.id}`" :value="String(operator.id)">
            {{ operator.full_name || operator.username }}
          </option>
        </select>
        <button class="btn" :disabled="adminLeadsLoading" @click="fetchAdminDatabaseLeads">
          {{ adminLeadsLoading ? 'Yuklanmoqda...' : 'Yangilash' }}
        </button>
        <button class="btn danger" type="button" :disabled="!selectedAdminLeadIds.length || bulkLeadDeleteLoading" @click="openBulkLeadDeleteModal">
          {{ bulkLeadDeleteLoading ? 'O‘chirilmoqda...' : `Tanlanganlarni o‘chirish (${selectedAdminLeadIds.length})` }}
        </button>
        <button v-if="selectedAdminLeadIds.length" class="btn ghost" type="button" @click="clearSelectedAdminLeads">Tanlovni tozalash</button>
        <button v-if="adminLeadSearch || adminLeadStatusFilter || adminLeadOperatorFilter" class="btn ghost" type="button" @click="clearAdminLeadFilters">Tozalash</button>
      </div>

      <div class="table-wrap admin-database-table-wrap">
        <table class="admin-database-table">
          <thead>
            <tr>
              <th class="select-col">
                <input
                  type="checkbox"
                  :checked="adminAllFilteredSelected"
                  :indeterminate.prop="adminSomeFilteredSelected && !adminAllFilteredSelected"
                  :disabled="!filteredAdminDatabaseLeads.length"
                  @change="toggleAllFilteredAdminLeads"
                  title="Ko‘rinayotgan leadlarni tanlash"
                />
              </th>
              <th>F.I.O</th>
              <th>T/SH</th>
              <th>Maktab</th>
              <th>Sinf</th>
              <th>Fan</th>
              <th>Ball</th>
              <th>Telefonlar</th>
              <th>Status</th>
              <th>Operator</th>
              <th>Boss</th>
              <th>Izoh</th>
              <th>Vaqt</th>
              <th>Amal</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="lead in filteredAdminDatabaseLeads" :key="`admin-db-lead-${lead.id}`" :class="{ 'row-selected': selectedAdminLeadIds.includes(lead.id) }">
              <td class="select-col"><input type="checkbox" :value="lead.id" v-model="selectedAdminLeadIds" /></td>
              <td>{{ lead.full_name || '-' }}</td>
              <td>{{ lead.tsh || '-' }}</td>
              <td>{{ lead.display_school || lead.school || '-' }}</td>
              <td>{{ lead.grade || '-' }}</td>
              <td>{{ lead.subject || '-' }}</td>
              <td>{{ lead.ball || '-' }}</td>
              <td>
                <div class="lead-phone-list">
                  <span>{{ lead.phone1 || '-' }}</span>
                  <span v-if="lead.phone2">{{ lead.phone2 }}</span>
                  <span v-if="lead.phone3">{{ lead.phone3 }}</span>
                </div>
              </td>
              <td><span class="badge">{{ statusLabel(lead.current_status) }}</span></td>
              <td>{{ lead.operator_name || '-' }}</td>
              <td>{{ lead.boss_name || '-' }}</td>
              <td>{{ lead.operator_note || latestLeadNote(lead) || '-' }}</td>
              <td>{{ formatDateTime(lead.updated_at || lead.created_at) }}</td>
              <td>
                <button class="btn danger small" type="button" @click="openLeadDeleteModal(lead)">O‘chirish</button>
              </td>
            </tr>
            <tr v-if="!filteredAdminDatabaseLeads.length">
              <td colspan="14" class="empty-state">Lead topilmadi.</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <template v-else>
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

    <div class="panel glass admin-status-panel">
      <div class="section-head section-head--wrap">
        <div>
          <div class="eyebrow">Statuslar</div>
          <h3>Lead holatlari taqsimoti</h3>
          <p>Operator panelidagi kabi statuslar 2 sahifaga bo‘lindi.</p>
        </div>
        <span class="badge">Yangilar: {{ stats.new || 0 }}</span>
      </div>

      <div class="operator-status-page-tabs admin-status-page-tabs">
        <button
          type="button"
          class="operator-status-page-tab"
          :class="{ active: adminStatusPage === 'main' }"
          @click="adminStatusPage = 'main'"
        >
          1-sahifa
        </button>
        <button
          type="button"
          class="operator-status-page-tab"
          :class="{ active: adminStatusPage === 'extra' }"
          @click="adminStatusPage = 'extra'"
        >
          2-sahifa
        </button>
      </div>

      <div class="status-grid compact-grid admin-status-grid">
        <div
          v-for="item in activeAdminStatusItems"
          :key="`admin-status-${item.key}`"
          class="status-overview-card"
          :class="`status-${item.key}`"
        >
          <div class="status-overview-card__top">{{ item.title }}</div>
          <strong>{{ item.value }}</strong>
        </div>
      </div>
    </div>


    <div class="panel glass">
      <div class="section-head section-head--wrap">
        <div>
          <div class="eyebrow">Keldi / To‘lov nazorati</div>
          <h3>Menenjerlar belgilari</h3>
          <p>Keldi, Kelmadi, To‘lov qildi, To‘lov qilmadi va to‘lov qilmasdan ketganlar shu yerda ko‘rinadi.</p>
        </div>
        <div class="lead-toolbar-info lead-toolbar-info--wrap">
          <button class="btn secondary" type="button" :disabled="visitDecisionsExcelDownloading" @click="downloadVisitDecisionsExcel">
            {{ visitDecisionsExcelDownloading ? 'Excel tayyorlanmoqda...' : 'Nazorat Excel yuklash' }}
          </button>
          <span class="badge">Jami: {{ adminVisitDecisions.length }}</span>
          <span class="badge arrived-badge">Keldi: {{ adminArrivedCount }}</span>
          <span class="badge not-arrived-badge">Kelmadi: {{ adminNotArrivedCount }}</span>
          <span class="badge payment-paid-badge">To‘lov qildi: {{ adminPaymentDoneCount }}</span>
          <span class="badge payment-unpaid-badge">To‘lov qilmadi: {{ adminPaymentNotDoneCount }}</span>
          <span class="badge payment-left-without-badge">To‘lovsiz ketdi: {{ adminLeftWithoutPaymentCount }}</span>
          <span class="badge muted">Belgilanmagan: {{ adminPaymentPendingCount }}</span>
        </div>
      </div>
      <div class="table-wrap">
        <table>
          <thead>
            <tr>
              <th>F.I.O</th>
              <th>Menenjer</th>
              <th>Operator</th>
              <th>Qaror</th>
              <th>To‘lov</th>
              <th>Holatni belgilagan</th>
              <th>To‘lov vaqti</th>
              <th>Nazorat vaqti</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="item in adminVisitDecisions" :key="`admin-visit-${item.id}`">
              <td>{{ item.lead_name || item.full_name || '-' }}</td>
              <td>{{ item.filial_rahbari_name || '-' }}</td>
              <td>{{ item.operator_name || '-' }}</td>
              <td><span class="badge">{{ item.decision === 'arrived' ? 'Keldi' : 'Kelmadi' }}</span></td>
              <td><span :class="['badge', adminPaymentBadgeClass(item)]">{{ adminPaymentStatusLabel(item) }}</span></td>
              <td>{{ item.payment_status_by_name || '-' }}</td>
              <td>{{ item.payment_status_at ? formatDateTime(item.payment_status_at) : '-' }}</td>
              <td>{{ formatDateTime(item.updated_at) }}</td>
            </tr>
            <tr v-if="!adminVisitDecisions.length">
              <td colspan="8" class="empty-state">Hali Keldi/Kelmadi yoki To‘lov belgisi yo‘q.</td>
            </tr>
          </tbody>
        </table>
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
        <button class="btn secondary" :disabled="monthlyReportDownloading" @click="openMonthlyReportModal">
          {{ monthlyReportDownloading ? 'Excel tayyorlanmoqda...' : 'Oylik Hisobot yuklash' }}
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
                  <th>Xato</th>
                  <th>O‘chiq</th>
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
                  <td>{{ row.wrong_number }}</td>
                  <td>{{ row.open_number }}</td>
                  <td>{{ row.advice }}</td>
                  <td>{{ row.other }}</td>
                  <td>{{ row.not_answered || 0 }}</td>
                  <td>{{ row.actions_total }}</td>
                </tr>
                <tr v-if="!adminOperatorRows.length">
                  <td colspan="10" class="empty-state">Tanlangan filter bo‘yicha natija topilmadi.</td>
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
                  <td>{{ row.not_answered || 0 }}</td>
                  <td>{{ row.actions_total }}</td>
                </tr>
                <tr v-if="!adminDailyRows.length">
                  <td colspan="8" class="empty-state">Kunlik natija topilmadi.</td>
                </tr>
              </tbody>
            </table>
          </div>
        </section>

        <section class="panel glass-soft">
          <div class="section-head section-head--wrap">
            <div>
              <div class="eyebrow">Oyma-oy arxiv</div>
              <h3>Har oy alohida natija</h3>
              <p>Oy almashganda yangi oy avtomatik ochiladi, eski oylar esa shu jadvalda saqlanib turadi.</p>
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
                <tr v-for="row in adminMonthlyRows" :key="`admin-month-${row.month}`">
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
                <tr v-if="!adminMonthlyRows.length">
                  <td colspan="9" class="empty-state">Oyma-oy natija topilmadi.</td>
                </tr>
              </tbody>
            </table>
          </div>
        </section>
      </div>
    </div>

    <div class="panel glass staff-management-panel">
      <div class="section-head section-head--wrap">
        <div>
          <div class="eyebrow">Akkauntlar boshqaruvi</div>
          <h3>Menenjerlar va operatorlar umumiy ro‘yxati</h3>
          <p class="muted-text">Barcha menenjer va operatorlarni shu yerdan qidiring, tahrirlang yoki bir nechtasini belgilab o‘chiring.</p>
        </div>
        <div class="toolbar toolbar--compact">
          <input v-model="staffSearch" class="input" placeholder="Ism, login yoki filial bo‘yicha qidirish" />
          <button class="btn ghost" type="button" :disabled="staffLoading" @click="fetchStaffAccounts">Yangilash</button>
          <button class="btn" type="button" @click="openFilialModal = true">Yangi menenjer</button>
        </div>
      </div>

      <div class="staff-toolbar">
        <label class="staff-select-all">
          <input type="checkbox" :checked="allFilteredStaffSelected" :disabled="!filteredStaffAccounts.length" @change="toggleAllStaff" />
          <span>Ko‘rinayotganlarning barchasini tanlash</span>
        </label>
        <div class="staff-toolbar__actions">
          <span class="badge">Jami: {{ staffAccounts.length }}</span>
          <span class="badge">Tanlangan: {{ selectedStaffIds.length }}</span>
          <button class="btn danger" type="button" :disabled="staffDeleting || !selectedStaffIds.length" @click="deleteSelectedStaff">
            {{ staffDeleting ? 'O‘chirilmoqda...' : 'Tanlanganlarni o‘chirish' }}
          </button>
        </div>
      </div>

      <div v-if="staffLoading" class="empty-state">Akkauntlar yuklanmoqda...</div>
      <div v-else-if="!filteredStaffAccounts.length" class="empty-state">Operator yoki menenjer topilmadi.</div>
      <div v-else class="table-wrap staff-table-wrap">
        <table class="staff-table">
          <thead>
            <tr>
              <th>Tanlash</th>
              <th>Ism-familiya</th>
              <th>Rol</th>
              <th>Login</th>
              <th>Filial</th>
              <th>Amallar</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="person in filteredStaffAccounts" :key="`admin-staff-${person.id}`">
              <td><input type="checkbox" :value="person.id" v-model="selectedStaffIds" /></td>
              <td><strong>{{ person.full_name || '-' }}</strong></td>
              <td><span :class="['badge', person.role === 'filial_rahbari' ? 'arrived-badge' : 'muted']">{{ roleLabel(person.role) }}</span></td>
              <td>{{ person.username }}</td>
              <td>{{ person.branch_name || '-' }}</td>
              <td>
                <div class="staff-row-actions">
                  <button class="btn ghost small" type="button" @click="openUserEdit(person)">Tahrirlash</button>
                  <button class="btn danger small" type="button" :disabled="staffDeleting" @click="deleteOneStaff(person)">O‘chirish</button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <div class="panel glass">
      <div class="section-head section-head--wrap">
        <div>
          <div class="eyebrow">Rahbariyat</div>
          <h3>Boshliqlar va direktorlar</h3>
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
              <th>Holati</th>
              <th>Amal</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="person in nonStaffLeaders" :key="`${person.role}-${person.id}`">
              <td><span class="badge">{{ roleLabel(person.role) }}</span></td>
              <td>{{ person.full_name || '-' }}</td>
              <td>{{ person.username }}</td>
              <td>{{ person.phone || '-' }}</td>
              <td><span class="badge">{{ person.is_active ? 'Faol' : 'Nofaol' }}</span></td>
              <td>
                <div class="user-actions">
                  <button class="btn ghost small" type="button" @click="openUserEdit(person)">Tahrirlash</button>
                  <button
                    v-if="['director', 'director_deputy'].includes(person.role)"
                    class="btn danger small"
                    type="button"
                    :disabled="userDeleteLoading && userToDelete?.id === person.id"
                    @click="openUserDeleteModal(person)"
                  >
                    O‘chirish
                  </button>
                </div>
              </td>
            </tr>
            <tr v-if="!nonStaffLeaders.length">
              <td colspan="6" class="empty-state">Hali boshliq yoki direktor yaratilmagan.</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    </template>

    <div v-if="monthlyReportModalOpen" class="modal-overlay">
      <div class="modal-card glass confirm-delete-modal">
        <div class="modal-card__head">
          <div>
            <div class="eyebrow">Excel hisobot</div>
            <h3>Oylik hisobot yuklash</h3>
          </div>
          <button class="modal-close" @click="closeMonthlyReportModal">×</button>
        </div>
        <form class="grid" @submit.prevent="downloadMonthlyReportExcel">
          <div class="report-filter-field admin-report-field">
            <label>Qaysi oyning hisoboti kerak?</label>
            <input class="input" type="month" v-model="monthlyReportMonth" required />
          </div>
          <div class="modal-actions modal-actions--split">
            <button class="btn" type="submit" :disabled="monthlyReportDownloading || !monthlyReportMonth">
              {{ monthlyReportDownloading ? 'Yuklanmoqda...' : 'Excel yuklash' }}
            </button>
            <button class="btn ghost" type="button" :disabled="monthlyReportDownloading" @click="closeMonthlyReportModal">Bekor qilish</button>
          </div>
        </form>
      </div>
    </div>

    <div v-if="openFilialModal" class="modal-overlay">
      <div class="modal-card glass">
        <div class="modal-card__head">
          <div>
            <div class="eyebrow">Yangi menenjer</div>
            <h3>Menenjer yaratish</h3>
          </div>
          <button class="modal-close" @click="closeFilialModal">×</button>
        </div>
        <form class="grid" @submit.prevent="createFilialRahbari">
          <input v-model="filialForm.username" class="input" placeholder="Login" />
          <input v-model="filialForm.password" type="password" class="input" placeholder="Parol" />
          <div class="branch-picker">
            <label>Filial biriktiring</label>
            <div class="branch-picker__grid">
              <label v-for="branch in branchOptions" :key="`filial-${branch.value}`" class="branch-check">
                <input type="checkbox" :value="branch.value" v-model="filialForm.branch_names" />
                <span>{{ branch.label }}</span>
              </label>
            </div>
          </div>
          <button class="btn full">Saqlash</button>
        </form>
      </div>
    </div>

    <div v-if="openBossModal" class="modal-overlay">
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

    <div v-if="openDirectorModalFlag" class="modal-overlay">
      <div class="modal-card glass">
        <div class="modal-card__head">
          <div>
            <div class="eyebrow">{{ directorForm.role === 'director_deputy' ? "Yangi bosh direktor o'rinbosari" : 'Yangi bosh direktor' }}</div>
            <h3>{{ directorForm.role === 'director_deputy' ? "Bosh direktor o'rinbosari yaratish" : 'Bosh direktor yaratish' }}</h3>
          </div>
          <button class="modal-close" @click="closeDirectorModal">×</button>
        </div>
        <p class="confirm-delete-text" style="margin-bottom: 4px;">
          Bu foydalanuvchi butun tizimdagi barcha boshliqlar, operatorlar va sotuv statistikasini faqat ko'rish huquqi bilan kuzatib boradi.
        </p>
        <form class="grid" @submit.prevent="createDirector">
          <input v-model="directorForm.full_name" class="input" placeholder="To'liq ism" />
          <input v-model="directorForm.username" class="input" placeholder="Login" />
          <input v-model="directorForm.phone" class="input" placeholder="Telefon" />
          <input v-model="directorForm.password" type="password" class="input" placeholder="Parol" />
          <button class="btn full">Saqlash</button>
        </form>
      </div>
    </div>

    <div v-if="deleteLeadModalOpen" class="modal-overlay">
      <div class="modal-card glass confirm-delete-modal">
        <div class="modal-card__head">
          <div>
            <div class="eyebrow">Leadni o‘chirish</div>
            <h3>O‘chirmoqchimisiz?</h3>
          </div>
          <button class="modal-close" @click="closeLeadDeleteModal">×</button>
        </div>
        <p class="confirm-delete-text">
          <strong>{{ leadToDelete?.full_name || 'Nomsiz lead' }}</strong> ma’lumotlari o‘chiriladi. Bu amalni qaytarib bo‘lmaydi.
        </p>
        <div class="modal-actions modal-actions--split">
          <button class="btn danger" :disabled="leadDeleteLoading" @click="confirmDeleteLead">
            {{ leadDeleteLoading ? 'O‘chirilmoqda...' : 'Ha' }}
          </button>
          <button class="btn ghost" :disabled="leadDeleteLoading" @click="closeLeadDeleteModal">Yo‘q</button>
        </div>
      </div>
    </div>

    <div v-if="bulkLeadDeleteModalOpen" class="modal-overlay">
      <div class="modal-card glass confirm-delete-modal">
        <div class="modal-card__head">
          <div>
            <div class="eyebrow">Tanlangan leadlarni o‘chirish</div>
            <h3>{{ selectedAdminLeadIds.length }} ta lead o‘chiriladi</h3>
          </div>
          <button class="modal-close" @click="closeBulkLeadDeleteModal">×</button>
        </div>
        <p class="confirm-delete-text">
          Tanlangan leadlar bazadan o‘chiriladi. Bu amalni qaytarib bo‘lmaydi.
        </p>
        <div class="modal-actions modal-actions--split">
          <button class="btn danger" :disabled="bulkLeadDeleteLoading" @click="confirmBulkDeleteLeads">
            {{ bulkLeadDeleteLoading ? 'O‘chirilmoqda...' : 'Ha, o‘chirish' }}
          </button>
          <button class="btn ghost" :disabled="bulkLeadDeleteLoading" @click="closeBulkLeadDeleteModal">Yo‘q</button>
        </div>
      </div>
    </div>

    <div v-if="userDeleteModalOpen" class="modal-overlay">
      <div class="modal-card glass confirm-delete-modal operator-delete-modal">
        <div class="modal-card__head">
          <div>
            <div class="eyebrow">{{ userToDelete?.role === 'operator' ? 'Operatorni o‘chirish' : 'Foydalanuvchini o‘chirish' }}</div>
            <h3>O‘chirmoqchimisiz?</h3>
          </div>
          <button class="modal-close" @click="closeUserDeleteModal">×</button>
        </div>

        <template v-if="userToDelete?.role === 'operator'">
          <p class="confirm-delete-text">
            <strong>{{ userToDelete?.full_name || userToDelete?.username }}</strong> operatorini o‘chirishdan oldin,
            unga tegishli barcha ma'lumotlar (leadlar, sotuvlar, tarix) qaysi operatorga o‘tishini tanlang.
          </p>

          <div v-if="!operatorTransferOptions.length" class="operator-transfer-empty">
            Boshqa faol operator topilmadi. Avval yangi operator yarating, so‘ng shu operatorni o‘chiring.
          </div>

          <div v-else class="operator-transfer-picker">
            <div class="eyebrow operator-transfer-picker__label">Bu operator ma'lumotlari qaysi operatorga o‘tsin?</div>
            <div class="operator-transfer-picker__grid">
              <button
                v-for="op in operatorTransferOptions"
                :key="`transfer-target-${op.id}`"
                type="button"
                class="operator-transfer-option"
                :class="{ 'operator-transfer-option--active': String(transferTargetOperatorId) === String(op.id) }"
                @click="transferTargetOperatorId = op.id"
              >
                <span class="operator-transfer-option__avatar">{{ (op.full_name || op.username || '?').slice(0, 1).toUpperCase() }}</span>
                <span class="operator-transfer-option__name">{{ op.full_name || op.username }}</span>
                <span v-if="String(transferTargetOperatorId) === String(op.id)" class="operator-transfer-option__check">✓</span>
              </button>
            </div>
          </div>

          <div class="modal-actions modal-actions--split">
            <button class="btn danger" :disabled="userDeleteLoading || !transferTargetOperatorId" @click="confirmDeleteUser">
              {{ userDeleteLoading ? 'O‘chirilmoqda...' : 'OK, ma’lumotlarni o‘tkazib o‘chirish' }}
            </button>
            <button class="btn ghost" :disabled="userDeleteLoading" @click="closeUserDeleteModal">Bekor qilish</button>
          </div>
        </template>

        <template v-else>
          <p class="confirm-delete-text">
            <strong>{{ userToDelete?.full_name || userToDelete?.username }}</strong> ro‘yxatdan olib tashlanadi.
          </p>
          <div class="modal-actions modal-actions--split">
            <button class="btn danger" :disabled="userDeleteLoading" @click="confirmDeleteUser">
              {{ userDeleteLoading ? 'O‘chirilmoqda...' : 'Ha, o‘chirish' }}
            </button>
            <button class="btn ghost" :disabled="userDeleteLoading" @click="closeUserDeleteModal">Yo‘q</button>
          </div>
        </template>
      </div>
    </div>

    <div v-if="openUserEditModal" class="modal-overlay">
      <div class="modal-card glass">
        <div class="modal-card__head">
          <div>
            <div class="eyebrow">Akkauntni tahrirlash</div>
            <h3>{{ editUserForm.full_name || editUserForm.username }} ma'lumotlarini o'zgartirish</h3>
          </div>
          <button class="modal-close" @click="closeUserEdit">×</button>
        </div>
        <form class="grid" @submit.prevent="saveUserEdit">
          <input v-model="editUserForm.full_name" class="input" placeholder="To'liq ism" />
          <input v-model="editUserForm.username" class="input" placeholder="Yangi login" />
          <div v-if="editingUser?.role === 'filial_rahbari' || editingUser?.role === 'operator'" class="branch-picker">
            <label>Filial(lar)</label>
            <div class="branch-picker__grid">
              <label v-for="branch in branchOptions" :key="`edit-${branch.value}`" class="branch-check">
                <input type="checkbox" :value="branch.value" v-model="editUserForm.branch_names" />
                <span>{{ branch.label }}</span>
              </label>
            </div>
          </div>
          <input v-model="editUserForm.password" type="password" class="input" placeholder="Yangi parol — o'zgarmasa bo'sh qoldiring" />
          <button class="btn full" :disabled="userEditLoading">{{ userEditLoading ? 'Saqlanmoqda...' : 'Saqlash' }}</button>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import client from '../../api/client'
import StatCard from '../../components/ui/StatCard.vue'
import ResponsiveSwiper from '../../components/ui/ResponsiveSwiper.vue'
import { useViewport } from '../../composables/useViewport'

const route = useRoute()

const stats = reactive({ bosses: 0, filial_rahbarlari: 0, operators: 0, leads: 0, sale: 0, otkaz: 0, open_number: 0, wrong_number: 0, advice: 0, other: 0, not_answered: 0, new: 0 })
const adminStatusPage = ref('main')
const adminStatusPageMap = {
  main: ['sale', 'open_number', 'advice'],
  extra: ['otkaz', 'wrong_number', 'other', 'not_answered'],
}
const adminStatusMeta = {
  sale: 'Sotuvlar',
  otkaz: 'Atkaz',
  wrong_number: 'Xato nomer',
  open_number: "O'chiq Nomer",
  advice: 'Maslahat',
  other: "O'qiydi",
  not_answered: "Ko'tarmadi",
}
const bosses = ref([])
const filialRahbarlari = ref([])
const users = ref([])
const directors = ref([])
const staffAccounts = ref([])
const selectedStaffIds = ref([])
const staffSearch = ref('')
const staffLoading = ref(false)
const staffDeleting = ref(false)
const adminVisitDecisions = ref([])
const adminDatabaseLeads = ref([])
const adminLeadSearch = ref('')
const adminLeadStatusFilter = ref('')
const adminLeadOperatorFilter = ref('')
const selectedAdminLeadIds = ref([])
const adminLeadsLoading = ref(false)
const deleteLeadModalOpen = ref(false)
const leadToDelete = ref(null)
const leadDeleteLoading = ref(false)
const bulkLeadDeleteModalOpen = ref(false)
const bulkLeadDeleteLoading = ref(false)
const userDeleteModalOpen = ref(false)
const userToDelete = ref(null)
const userDeleteLoading = ref(false)
const transferTargetOperatorId = ref('')
const adminReportLoading = ref(false)
const allReportsDownloading = ref(false)
const visitDecisionsExcelDownloading = ref(false)
const monthlyReportModalOpen = ref(false)
const monthlyReportDownloading = ref(false)
const monthlyReportMonth = ref(new Date().toISOString().slice(0, 7))
const adminReportData = ref(null)
const reportOperators = ref([])
const reportFilters = reactive({ boss_id: '', operator_id: '', date: '', month: '' })
const openBossModal = ref(false)
const openFilialModal = ref(false)
const openDirectorModalFlag = ref(false)
const openUserEditModal = ref(false)
const editingUser = ref(null)
const userEditLoading = ref(false)
const error = ref('')
const success = ref('')
const form = reactive({ full_name: '', username: '', phone: '', password: '' })
const filialForm = reactive({ username: '', password: '', branch_names: [] })
const directorForm = reactive({ full_name: '', username: '', phone: '', password: '', role: 'director' })
const editUserForm = reactive({ full_name: '', username: '', phone: '', branch_name: '', branch_names: [], password: '' })
const { isCompact } = useViewport(960, 640)
const branchOptions = [
  { label: 'Niyozbosh Menenjeri', value: 'Niyozbosh' },
  { label: 'Kids 1 Menenjeri', value: 'Kids 1' },
  { label: 'Kids 2 Menenjeri', value: 'Kids 2' },
  { label: 'Gulbahor Menenjeri', value: 'Gulbahor' },
  { label: 'Kids 3 Menenjeri', value: 'Kids 3' },
  { label: 'Kasblar Menenjeri', value: 'Kasblar' },
  { label: 'Xalqobod Menenjeri', value: 'Xalqobod' },
  { label: 'Chinoz Menenjeri', value: 'Chinoz' },
  { label: 'Olmazor Menenjeri', value: 'Olmozor' },
  { label: 'Paxtazor Menenjeri', value: 'Paxtazor' },
  { label: 'Mevazor Menenjeri', value: 'Mevazor' },
  { label: 'Dostobod Menenjeri', value: 'Dostobod' },
  { label: 'Qorg\'onchi Menenjeri', value: 'Qorg\'onchi' },
  { label: 'Oqqo\'rg\'on Menenjeri', value: 'Oqqo\'rg\'on' },
  { label: 'Qo\'shyog\'och Menenjeri', value: 'Qo\'shyog\'och' },
]

function branchStringToArray(value) {
  if (Array.isArray(value)) return value
  return String(value || '').split(',').map(item => item.trim()).filter(Boolean)
}

const currentAdminTab = computed(() => {
  const tab = typeof route.query.tab === 'string' ? route.query.tab : 'main'
  return tab === 'database' ? 'database' : 'main'
})

const statusLabels = {
  new: 'Biriktirilgan',
  sale: 'Sotuv',
  otkaz: 'Atkaz',
  wrong_number: 'Xato nomer',
  open_number: 'O‘chiq nomer',
  advice: 'Maslahat',
  other: 'O‘qiydi',
  not_answered: "Ko'tarmadi",
}

const activeAdminStatusItems = computed(() => {
  const keys = adminStatusPageMap[adminStatusPage.value] || adminStatusPageMap.main
  return keys.map((key) => ({
    key,
    title: adminStatusMeta[key] || statusLabel(key),
    value: stats[key] || 0,
  }))
})

const adminLeadOperatorOptions = computed(() => (
  users.value
    .filter(user => user.role === 'operator')
    .slice()
    .sort((a, b) => String(a.full_name || a.username || '').localeCompare(String(b.full_name || b.username || ''), 'uz'))
))

const filteredAdminDatabaseLeads = computed(() => {
  const search = adminLeadSearch.value.trim().toLowerCase()
  const operatorId = adminLeadOperatorFilter.value ? Number(adminLeadOperatorFilter.value) : null
  return adminDatabaseLeads.value.filter((lead) => {
    const statusOk = !adminLeadStatusFilter.value || lead.current_status === adminLeadStatusFilter.value
    if (!statusOk) return false
    const operatorOk = !operatorId || Number(lead.assigned_operator) === operatorId
    if (!operatorOk) return false
    if (!search) return true
    return [
      lead.full_name,
      lead.tsh,
      lead.school,
      lead.display_school,
      lead.grade,
      lead.subject,
      lead.ball,
      lead.phone1,
      lead.phone2,
      lead.phone3,
      lead.operator_name,
      lead.boss_name,
      lead.current_status,
      lead.operator_note,
    ].some(value => String(value || '').toLowerCase().includes(search))
  })
})

const filteredAdminLeadIds = computed(() => filteredAdminDatabaseLeads.value.map(lead => lead.id))
const adminAllFilteredSelected = computed(() => (
  filteredAdminLeadIds.value.length > 0 && filteredAdminLeadIds.value.every(id => selectedAdminLeadIds.value.includes(id))
))
const adminSomeFilteredSelected = computed(() => filteredAdminLeadIds.value.some(id => selectedAdminLeadIds.value.includes(id)))
const selectedAdminLeads = computed(() => adminDatabaseLeads.value.filter(lead => selectedAdminLeadIds.value.includes(lead.id)))

const summaryCards = computed(() => ([
  { title: 'Boshliqlar', value: stats.bosses, subtitle: 'Tizimdagi boshliqlar' },
  { title: 'Menenjerlar', value: stats.filial_rahbarlari, subtitle: 'Menenjerlar soni' },
  { title: 'Operatorlar', value: stats.operators, subtitle: 'Jami operatorlar' },
  { title: 'Sotuvlar', value: stats.sale, subtitle: 'Muvaffaqiyatli natija' },
]))
const leaders = computed(() => (
  users.value.length || directors.value.length
    ? [...users.value, ...directors.value]
    : [...bosses.value, ...filialRahbarlari.value]
))
const nonStaffLeaders = computed(() => leaders.value.filter(person => !['operator', 'filial_rahbari'].includes(person.role)))
const filteredStaffAccounts = computed(() => {
  const search = staffSearch.value.trim().toLowerCase()
  if (!search) return staffAccounts.value
  return staffAccounts.value.filter(person => [person.full_name, person.username, person.branch_name, roleLabel(person.role)]
    .some(value => String(value || '').toLowerCase().includes(search)))
})
const allFilteredStaffSelected = computed(() => filteredStaffAccounts.value.length > 0
  && filteredStaffAccounts.value.every(person => selectedStaffIds.value.includes(person.id)))
const operatorTransferOptions = computed(() => (
  leaders.value
    .filter(person => person.role === 'operator' && person.is_active && person.id !== userToDelete.value?.id)
    .slice()
    .sort((a, b) => String(a.full_name || a.username || '').localeCompare(String(b.full_name || b.username || ''), 'uz'))
))
const adminArrivedCount = computed(() => adminVisitDecisions.value.filter(item => item.decision === 'arrived').length)
const adminNotArrivedCount = computed(() => adminVisitDecisions.value.filter(item => item.decision === 'not_arrived').length)
const adminPaymentDoneCount = computed(() => adminVisitDecisions.value.filter(item => adminPaymentStatus(item) === 'paid').length)
const adminPaymentNotDoneCount = computed(() => adminVisitDecisions.value.filter(item => adminPaymentStatus(item) === 'unpaid').length)
const adminLeftWithoutPaymentCount = computed(() => adminVisitDecisions.value.filter(item => adminPaymentStatus(item) === 'left_without_payment').length)
const adminPaymentPendingCount = computed(() => adminVisitDecisions.value.filter(item => adminPaymentStatus(item) === 'pending').length)
const adminOperatorRows = computed(() => adminReportData.value?.operator_rows || [])
const adminDailyRows = computed(() => adminReportData.value?.daily || [])
const adminMonthlyRows = computed(() => adminReportData.value?.monthly_archive || [])
const adminReportSummaryCards = computed(() => {
  if (!adminReportData.value?.summary) return []
  const summary = adminReportData.value.summary
  return [
    { title: 'Biriktirilgan', value: summary.assigned_leads, subtitle: 'Tanlangan oraliqda' },
    { title: 'Sotuv', value: summary.sale, subtitle: 'Muvaffaqiyatli leadlar' },
    { title: 'Atkaz', value: summary.otkaz, subtitle: 'Qayta ishlashga o‘tganlar' },
    { title: 'Xato nomer', value: summary.wrong_number, subtitle: 'Noto‘g‘ri raqamlar' },
    { title: 'O‘chiq nomer', value: summary.open_number, subtitle: 'Aloqa qilinmaganlar' },
    { title: 'Maslahat', value: summary.advice, subtitle: 'Maslahat berilganlar' },
    { title: 'Boshqa', value: summary.other, subtitle: 'Boshqa turdagi natija' },
    { title: "Ko'tarmadi", value: summary.not_answered || 0, subtitle: 'Telefon ko‘tarilmaganlar' },
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

function roleLabel(role) {
  if (role === 'filial_rahbari') return 'Menenjer'
  if (role === 'operator') return 'Operator'
  if (role === 'boss') return 'Boshliq'
  if (role === 'director') return 'Bosh direktor'
  if (role === 'director_deputy') return "Bosh direktor o'rinbosari"
  return role || '-'
}

function toggleAllStaff(event) {
  const ids = filteredStaffAccounts.value.map(person => person.id)
  if (event.target.checked) {
    selectedStaffIds.value = Array.from(new Set([...selectedStaffIds.value, ...ids]))
  } else {
    selectedStaffIds.value = selectedStaffIds.value.filter(id => !ids.includes(id))
  }
}

async function fetchStaffAccounts() {
  staffLoading.value = true
  try {
    const { data } = await client.get('admin/staff/')
    staffAccounts.value = data.results || data || []
    const activeIds = new Set(staffAccounts.value.map(person => person.id))
    selectedStaffIds.value = selectedStaffIds.value.filter(id => activeIds.has(id))
  } catch (e) {
    error.value = e.response?.data?.detail || 'Akkauntlarni yuklashda xatolik yuz berdi.'
  } finally {
    staffLoading.value = false
  }
}

async function deleteOneStaff(person) {
  if (!window.confirm(`${person.full_name || person.username} akkauntini o‘chirasizmi?`)) return
  staffDeleting.value = true
  resetMessages()
  try {
    await client.delete(`admin/staff/${person.id}/`)
    selectedStaffIds.value = selectedStaffIds.value.filter(id => id !== person.id)
    success.value = 'Akkaunt o‘chirildi.'
    await Promise.all([fetchStaffAccounts(), fetchUsers(), fetchFilialRahbarlari(), fetchStats()])
  } catch (e) {
    error.value = e.response?.data?.detail || 'Akkauntni o‘chirishda xatolik yuz berdi.'
  } finally {
    staffDeleting.value = false
  }
}

async function deleteSelectedStaff() {
  if (!selectedStaffIds.value.length) return
  if (!window.confirm(`${selectedStaffIds.value.length} ta akkauntni o‘chirasizmi?`)) return
  staffDeleting.value = true
  resetMessages()
  try {
    const { data } = await client.post('admin/staff/bulk-delete/', { ids: selectedStaffIds.value })
    success.value = data.detail || 'Tanlangan akkauntlar o‘chirildi.'
    selectedStaffIds.value = []
    await Promise.all([fetchStaffAccounts(), fetchUsers(), fetchFilialRahbarlari(), fetchStats()])
  } catch (e) {
    error.value = e.response?.data?.detail || 'Tanlangan akkauntlarni o‘chirishda xatolik yuz berdi.'
  } finally {
    staffDeleting.value = false
  }
}

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
  filialForm.username = ''
  filialForm.password = ''
  filialForm.branch_names = []
}

function openUserEdit(person) {
  editingUser.value = person
  editUserForm.full_name = person.full_name || ''
  editUserForm.username = person.username || ''
  editUserForm.phone = person.phone || ''
  editUserForm.branch_name = person.branch_name || ''
  editUserForm.branch_names = branchStringToArray(person.branch_names || person.branch_name)
  editUserForm.password = ''
  openUserEditModal.value = true
}

function closeUserEdit() {
  openUserEditModal.value = false
  editingUser.value = null
  editUserForm.full_name = ''
  editUserForm.username = ''
  editUserForm.phone = ''
  editUserForm.branch_name = ''
  editUserForm.branch_names = []
  editUserForm.password = ''
}

function openUserDeleteModal(person) {
  resetMessages()
  userToDelete.value = person
  transferTargetOperatorId.value = ''
  userDeleteModalOpen.value = true
}

function closeUserDeleteModal() {
  if (userDeleteLoading.value) return
  userDeleteModalOpen.value = false
  userToDelete.value = null
  transferTargetOperatorId.value = ''
}

async function confirmDeleteUser() {
  if (!userToDelete.value) return
  const isOperator = userToDelete.value.role === 'operator'
  if (isOperator && !transferTargetOperatorId.value) {
    error.value = 'Iltimos, ma’lumotlar o‘tkaziladigan operatorni tanlang.'
    return
  }
  userDeleteLoading.value = true
  resetMessages()
  try {
    const config = isOperator ? { data: { transfer_to: transferTargetOperatorId.value } } : undefined
    await client.delete(`${userApiBase(userToDelete.value.role)}/${userToDelete.value.id}/`, config)
    success.value = `${userToDelete.value.full_name || userToDelete.value.username} o‘chirildi${isOperator ? ' va ma’lumotlari boshqa operatorga o‘tkazildi.' : '.'}`
    userDeleteModalOpen.value = false
    userToDelete.value = null
    transferTargetOperatorId.value = ''
    await fetchBosses()
    await fetchFilialRahbarlari()
    await fetchUsers()
    await fetchDirectors()
    await fetchStats()
    await fetchAdminOperatorReport()
  } catch (e) {
    error.value = e.response?.data?.detail || 'Foydalanuvchini o‘chirishda xatolik yuz berdi.'
  } finally {
    userDeleteLoading.value = false
  }
}


function formatInputDate(value) {
  if (!value) return '-'
  const [year, month, day] = String(value).split('-')
  if (!year || !month || !day) return value
  return `${day}.${month}.${year}`
}

function formatDateTime(value) {
  if (!value) return '-'
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return String(value)
  return new Intl.DateTimeFormat('uz-UZ', { dateStyle: 'short', timeStyle: 'short' }).format(date)
}


function statusLabel(status) {
  return statusLabels[status] || status || '-'
}

function latestLeadNote(lead) {
  const history = Array.isArray(lead?.history) ? lead.history : []
  const saleNote = history.find(item => item.new_status === 'sale' && item.note)
  const anyNote = history.find(item => item.note)
  return saleNote?.note || anyNote?.note || ''
}

async function fetchAdminDatabaseLeads() {
  adminLeadsLoading.value = true
  resetMessages()
  try {
    const params = {}
    if (adminLeadStatusFilter.value) params.current_status = adminLeadStatusFilter.value
    if (adminLeadOperatorFilter.value) params.assigned_operator = adminLeadOperatorFilter.value
    const { data } = await client.get('admin/leads/', { params })
    adminDatabaseLeads.value = data.results || data
  } catch (e) {
    error.value = e.response?.data?.detail || 'Leadlar bazasini yuklashda xatolik yuz berdi.'
  } finally {
    adminLeadsLoading.value = false
  }
}

function clearAdminLeadFilters() {
  adminLeadSearch.value = ''
  adminLeadStatusFilter.value = ''
  adminLeadOperatorFilter.value = ''
  clearSelectedAdminLeads()
  fetchAdminDatabaseLeads()
}

function clearSelectedAdminLeads() {
  selectedAdminLeadIds.value = []
}

function toggleAllFilteredAdminLeads(event) {
  const ids = filteredAdminLeadIds.value
  if (event.target.checked) {
    selectedAdminLeadIds.value = Array.from(new Set([...selectedAdminLeadIds.value, ...ids]))
  } else {
    selectedAdminLeadIds.value = selectedAdminLeadIds.value.filter(id => !ids.includes(id))
  }
}

function openBulkLeadDeleteModal() {
  if (!selectedAdminLeadIds.value.length) return
  bulkLeadDeleteModalOpen.value = true
}

function closeBulkLeadDeleteModal() {
  bulkLeadDeleteModalOpen.value = false
}

function openLeadDeleteModal(lead) {
  leadToDelete.value = lead
  deleteLeadModalOpen.value = true
}

function closeLeadDeleteModal() {
  deleteLeadModalOpen.value = false
  leadToDelete.value = null
}

async function confirmDeleteLead() {
  if (!leadToDelete.value?.id) return
  leadDeleteLoading.value = true
  resetMessages()
  try {
    await client.delete(`admin/leads/${leadToDelete.value.id}/`)
    success.value = 'Lead o‘chirildi.'
    adminDatabaseLeads.value = adminDatabaseLeads.value.filter(item => item.id !== leadToDelete.value.id)
    selectedAdminLeadIds.value = selectedAdminLeadIds.value.filter(id => id !== leadToDelete.value.id)
    closeLeadDeleteModal()
    await fetchStats()
    await fetchAdminVisitDecisions()
  } catch (e) {
    error.value = e.response?.data?.detail || 'Leadni o‘chirishda xatolik yuz berdi.'
  } finally {
    leadDeleteLoading.value = false
  }
}

async function confirmBulkDeleteLeads() {
  const ids = selectedAdminLeads.value.map(lead => lead.id)
  if (!ids.length) return
  bulkLeadDeleteLoading.value = true
  resetMessages()
  try {
    const { data } = await client.delete('admin/leads/', { data: { ids } })
    const deletedIds = data.deleted_ids || ids
    adminDatabaseLeads.value = adminDatabaseLeads.value.filter(item => !deletedIds.includes(item.id))
    clearSelectedAdminLeads()
    closeBulkLeadDeleteModal()
    success.value = `${data.deleted_count || deletedIds.length} ta lead o‘chirildi.`
    await fetchStats()
    await fetchAdminVisitDecisions()
  } catch (e) {
    error.value = e.response?.data?.detail || 'Tanlangan leadlarni o‘chirishda xatolik yuz berdi.'
  } finally {
    bulkLeadDeleteLoading.value = false
  }
}

function adminPaymentStatus(item) {
  if (item?.payment_status) return item.payment_status
  if (item?.payment_done) return 'paid'
  if (item?.payment_not_done) return 'unpaid'
  if (item?.left_without_payment) return 'left_without_payment'
  return 'pending'
}

function adminPaymentStatusLabel(item) {
  const status = adminPaymentStatus(item)
  if (status === 'paid') return 'To‘lov qildi'
  if (status === 'unpaid') return 'To‘lov qilmadi'
  if (status === 'left_without_payment') return 'Keldi, to‘lov qilmasdan ketdi'
  return 'Belgilanmagan'
}

function adminPaymentBadgeClass(item) {
  const status = adminPaymentStatus(item)
  if (status === 'paid') return 'payment-paid-badge'
  if (status === 'unpaid') return 'payment-unpaid-badge'
  if (status === 'left_without_payment') return 'payment-left-without-badge'
  return 'muted'
}

async function downloadVisitDecisionsExcel() {
  visitDecisionsExcelDownloading.value = true
  resetMessages()
  try {
    const response = await client.get('admin/reports/visit-decisions-excel/', { responseType: 'blob' })
    downloadBlob(response.data, response.headers, 'admin_keldi_kelmadi_tolov_hisoboti.xlsx')
    success.value = 'Keldi, Kelmadi va to‘lov nazorati Excel formatda yuklandi.'
  } catch (e) {
    error.value = e.response?.data?.detail || 'Nazorat Excel hisobotini yuklashda xatolik yuz berdi.'
  } finally {
    visitDecisionsExcelDownloading.value = false
  }
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

function currentMonthValue() {
  const now = new Date()
  return `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}`
}

function openMonthlyReportModal() {
  resetMessages()
  monthlyReportMonth.value = reportFilters.month || currentMonthValue()
  monthlyReportModalOpen.value = true
}

function closeMonthlyReportModal() {
  if (monthlyReportDownloading.value) return
  monthlyReportModalOpen.value = false
}

async function downloadMonthlyReportExcel() {
  if (!monthlyReportMonth.value) {
    error.value = 'Avval oy tanlang.'
    return
  }

  monthlyReportDownloading.value = true
  resetMessages()
  try {
    const response = await client.get('admin/reports/monthly-sales-excel/', {
      params: { month: monthlyReportMonth.value },
      responseType: 'blob',
    })
    downloadBlob(response.data, response.headers, `oylik_sotuvlar_${monthlyReportMonth.value}.xlsx`)
    success.value = 'Oylik hisobot Excel formatda yuklandi.'
    monthlyReportModalOpen.value = false
  } catch (e) {
    error.value = e.response?.data?.detail || 'Oylik hisobotni yuklashda xatolik yuz berdi.'
  } finally {
    monthlyReportDownloading.value = false
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

async function fetchUsers() {
  const { data } = await client.get('admin/users/')
  users.value = data.results || data
}

async function fetchDirectors() {
  const { data } = await client.get('admin/directors/')
  directors.value = data.results || data
}

async function fetchAdminVisitDecisions() {
  const { data } = await client.get('admin/lead-visit-decisions/')
  adminVisitDecisions.value = data.results || data
}

function userApiBase(role) {
  return (role === 'director' || role === 'director_deputy') ? 'admin/directors' : 'admin/users'
}

async function saveUserEdit() {
  if (!editingUser.value) return
  userEditLoading.value = true
  resetMessages()
  try {
    const payload = {
      full_name: editUserForm.full_name,
      username: editUserForm.username,
      phone: editUserForm.phone,
      branch_name: editUserForm.branch_name,
      branch_names: editUserForm.branch_names,
    }
    if (editUserForm.password) payload.password = editUserForm.password
    await client.patch(`${userApiBase(editingUser.value.role)}/${editingUser.value.id}/`, payload)
    success.value = 'Akkaunt ma’lumotlari yangilandi.'
    closeUserEdit()
    await fetchBosses()
    await fetchFilialRahbarlari()
    await fetchUsers()
    await fetchDirectors()
    await fetchStats()
    await fetchStaffAccounts()
  } catch (e) {
    error.value = e.response?.data?.username?.[0] || e.response?.data?.detail || 'Foydalanuvchini yangilashda xatolik yuz berdi.'
  } finally {
    userEditLoading.value = false
  }
}

async function createBoss() {
  resetMessages()
  try {
    await client.post('admin/bosses/', { ...form })
    success.value = 'Boshliq muvaffaqiyatli yaratildi.'
    closeModal()
    await fetchBosses()
    await fetchUsers()
    await fetchStats()
  } catch (e) {
    error.value = e.response?.data?.username?.[0] || e.response?.data?.detail || 'Boshliq yaratishda xatolik yuz berdi.'
  }
}

function openDirectorModal(role) {
  resetMessages()
  directorForm.full_name = ''
  directorForm.username = ''
  directorForm.phone = ''
  directorForm.password = ''
  directorForm.role = role
  openDirectorModalFlag.value = true
}

function closeDirectorModal() {
  openDirectorModalFlag.value = false
}

async function createDirector() {
  resetMessages()
  if (!directorForm.username || !directorForm.password || !directorForm.full_name) {
    error.value = 'Ism, login va parol kiritish shart.'
    return
  }
  try {
    await client.post('admin/directors/', { ...directorForm })
    success.value = directorForm.role === 'director_deputy'
      ? "Bosh direktor o'rinbosari muvaffaqiyatli yaratildi."
      : 'Bosh direktor muvaffaqiyatli yaratildi.'
    closeDirectorModal()
    await fetchDirectors()
    await fetchUsers()
    await fetchStats()
  } catch (e) {
    error.value = e.response?.data?.username?.[0] || e.response?.data?.detail || 'Yaratishda xatolik yuz berdi.'
  }
}

async function createFilialRahbari() {
  resetMessages()
  if (!filialForm.username || !filialForm.password || !filialForm.branch_names.length) {
    error.value = 'Login, parol va kamida bitta filial tanlang.'
    return
  }
  try {
    await client.post('admin/filial-rahbarlari/', { ...filialForm })
    success.value = 'Menenjer muvaffaqiyatli yaratildi.'
    closeFilialModal()
    await fetchFilialRahbarlari()
    await fetchUsers()
    await fetchStats()
    await fetchStaffAccounts()
  } catch (e) {
    error.value = e.response?.data?.username?.[0] || e.response?.data?.detail || 'Menenjer yaratishda xatolik yuz berdi.'
  }
}

watch(adminDatabaseLeads, () => {
  const existingIds = new Set(adminDatabaseLeads.value.map(lead => lead.id))
  selectedAdminLeadIds.value = selectedAdminLeadIds.value.filter(id => existingIds.has(id))
})

watch([adminLeadStatusFilter, adminLeadOperatorFilter], () => {
  clearSelectedAdminLeads()
})

onMounted(async () => {
  await fetchStats()
  await fetchBosses()
  await fetchFilialRahbarlari()
  await fetchUsers()
  await fetchStaffAccounts()
  await fetchDirectors()
  await fetchAdminVisitDecisions()
  await fetchAdminOperatorReport()
  await fetchAdminDatabaseLeads()
})

watch(() => route.query.tab, (tab) => {
  if (tab === 'database' && !adminDatabaseLeads.value.length) fetchAdminDatabaseLeads()
})
</script>

<style scoped>
.payment-paid-badge { background: rgba(34, 197, 94, 0.14) !important; color: #047857 !important; border-color: rgba(34, 197, 94, 0.28) !important; }
.payment-unpaid-badge { background: rgba(239, 68, 68, 0.12) !important; color: #b91c1c !important; border-color: rgba(239, 68, 68, 0.24) !important; }

.admin-database-panel { gap: 18px; }
.admin-database-toolbar { margin-bottom: 16px; }
.admin-database-search { min-width: min(100%, 420px); }
.admin-operator-filter { min-width: min(100%, 240px); }
.selected-leads-badge { background: rgba(37, 99, 235, 0.10) !important; color: #1d4ed8 !important; border-color: rgba(37, 99, 235, 0.22) !important; }
.admin-database-table { min-width: 1340px; }
.admin-database-table th { white-space: nowrap; }
.select-col { width: 44px; text-align: center; }
.select-col input { width: 17px; height: 17px; accent-color: #2563eb; cursor: pointer; }
.row-selected { background: rgba(37, 99, 235, 0.045); }
.lead-phone-list { display: grid; gap: 3px; font-size: 13px; }
.btn.small { padding: 8px 12px; font-size: 12px; }
.user-actions { display: flex; flex-wrap: wrap; gap: 8px; align-items: center; }
.btn.danger { background: rgba(239, 68, 68, 0.12); color: #b91c1c; border: 1px solid rgba(239, 68, 68, 0.24); }
.btn.danger:hover { background: rgba(239, 68, 68, 0.18); }
.confirm-delete-modal { max-width: 460px; }
.confirm-delete-text { margin: 0; color: #475569; line-height: 1.6; }
.modal-actions { display: flex; gap: 10px; margin-top: 10px; }
.modal-actions--split { justify-content: flex-end; }

.operator-delete-modal { max-width: 540px; }
.operator-transfer-empty {
  margin-top: 12px;
  padding: 14px 16px;
  border-radius: 14px;
  background: rgba(239, 68, 68, 0.08);
  color: #b91c1c;
  border: 1px solid rgba(239, 68, 68, 0.18);
  font-size: 13.5px;
  line-height: 1.5;
}
.operator-transfer-picker { margin-top: 16px; }
.operator-transfer-picker__label { margin-bottom: 10px; font-weight: 600; color: #1e293b; letter-spacing: 0; text-transform: none; font-size: 13.5px; }
.operator-transfer-picker__grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(160px, 1fr));
  gap: 10px;
  max-height: 260px;
  overflow-y: auto;
  padding-right: 2px;
}
.operator-transfer-option {
  position: relative;
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 12px;
  border-radius: 14px;
  border: 1.5px solid rgba(148, 163, 184, 0.28);
  background: rgba(248, 250, 252, 0.9);
  cursor: pointer;
  text-align: left;
  transition: border-color 0.15s ease, background 0.15s ease, transform 0.1s ease;
}
.operator-transfer-option:hover { border-color: rgba(79, 124, 255, 0.55); transform: translateY(-1px); }
.operator-transfer-option--active {
  border-color: #4f7cff;
  background: rgba(79, 124, 255, 0.1);
  box-shadow: 0 0 0 3px rgba(79, 124, 255, 0.14);
}
.operator-transfer-option__avatar {
  flex-shrink: 0;
  width: 30px;
  height: 30px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #4f7cff, #7c9dff);
  color: #fff;
  font-weight: 700;
  font-size: 13px;
}
.operator-transfer-option__name { font-size: 13.5px; font-weight: 600; color: #1e293b; flex: 1; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.operator-transfer-option__check { color: #4f7cff; font-weight: 800; }

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

.payment-left-without-badge { background: rgba(249, 115, 22, 0.14) !important; color: #c2410c !important; border-color: rgba(249, 115, 22, 0.3) !important; }

.staff-management-panel { display: grid; gap: 18px; }
.staff-toolbar { display: flex; align-items: center; justify-content: space-between; gap: 14px; flex-wrap: wrap; }
.staff-select-all { display: inline-flex; align-items: center; gap: 9px; font-weight: 700; color: #334155; }
.staff-select-all input, .staff-table input[type="checkbox"] { width: 18px; height: 18px; accent-color: #2563eb; }
.staff-toolbar__actions, .staff-row-actions { display: flex; align-items: center; gap: 8px; flex-wrap: wrap; }
.staff-table th, .staff-table td { vertical-align: middle; }
.staff-table td:first-child, .staff-table th:first-child { text-align: center; width: 86px; }

@media (max-width: 760px) {
  .staff-toolbar { align-items: stretch; }
  .staff-toolbar__actions { width: 100%; }
  .staff-toolbar__actions .btn { flex: 1 1 100%; }
  .staff-row-actions { min-width: 220px; }
}

</style>
