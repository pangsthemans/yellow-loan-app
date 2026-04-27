<template>
  <q-page class="app-page">
    <!-- Header -->
    <div class="app-header">
      <div class="header-inner">
        <div class="logo">
          <span class="logo-y">Y</span>ellow
        </div>
        <div class="header-tagline">Phone Financing</div>
      </div>
    </div>

    <!-- Step indicator -->
    <div class="step-bar">
      <div class="step-bar-inner">
        <div
          v-for="step in steps"
          :key="step.num"
          class="step-item"
          :class="{ 'step-active': currentStep === step.num, 'step-done': currentStep > step.num }"
        >
          <div class="step-pill" :class="currentStep > step.num ? 'done' : currentStep === step.num ? 'active' : 'pending'">
            <q-icon v-if="currentStep > step.num" name="check" size="14px" />
            <span v-else>{{ step.num }}</span>
          </div>
          <span class="step-label">{{ step.label }}</span>
        </div>
        <div class="step-connector" v-for="n in 3" :key="'c'+n" :style="{ left: `calc(${(n) * 25}% - 12px)` }" />
      </div>
    </div>

    <!-- Form content -->
    <div class="form-wrapper">
      <transition name="slide-fade" mode="out-in">
        <!-- STEP 1: Biographical -->
        <div v-if="currentStep === 1" key="step1" class="form-card">
          <div class="step-heading">
            <div class="step-num-badge">01</div>
            <div>
              <h2 class="step-title">Personal Details</h2>
              <p class="step-sub">We need to verify your identity</p>
            </div>
          </div>

          <q-form @submit.prevent="handleStep1Submit" ref="form1">
            <div class="field-row">
              <q-input
                v-model="store.bio.first_name"
                label="First Name"
                outlined
                :rules="[v => !!v?.trim() || 'Required', v => v?.trim().length >= 2 || 'Min 2 characters']"
                class="field-half"
              >
                <template #prepend><q-icon name="person" color="grey-6" /></template>
              </q-input>
              <q-input
                v-model="store.bio.last_name"
                label="Last Name"
                outlined
                :rules="[v => !!v?.trim() || 'Required', v => v?.trim().length >= 2 || 'Min 2 characters']"
                class="field-half"
              >
                <template #prepend><q-icon name="person" color="grey-6" /></template>
              </q-input>
            </div>

            <q-input
              v-model="store.bio.id_number"
              label="SA ID Number"
              outlined
              mask="#############"
              hint="13-digit South African ID number"
              :rules="[v => !!v || 'Required', v => v.length === 13 || 'Must be 13 digits']"
              :error="idError !== null"
              :error-message="idError"
              @update:model-value="clearIdError"
              class="q-mt-md"
            >
              <template #prepend><q-icon name="badge" color="grey-6" /></template>
              <template #append>
                <q-spinner v-if="validatingId" color="primary" size="20px" />
                <q-icon v-else-if="store.idValidation?.valid" name="verified" color="positive" />
              </template>
            </q-input>

            <!-- ID validated info pill -->
            <transition name="fade">
              <div v-if="store.idValidation?.valid" class="id-info-pill q-mt-sm q-mb-md">
                <q-icon name="cake" size="16px" color="primary" />
                <span>DOB: {{ formatDate(store.idValidation.dob) }}</span>
                <span class="divider">·</span>
                <span>Age: <strong>{{ store.idValidation.age }}</strong></span>
                <span class="divider">·</span>
                <span class="risk-chip">Risk Group {{ store.idValidation.risk_group }}</span>
              </div>
            </transition>

            <q-input
              v-model="store.bio.date_of_birth"
              label="Date of Birth"
              outlined
              type="date"
              :readonly="store.idValidation?.valid"
              :rules="[v => !!v || 'Required']"
              :hint="store.idValidation?.valid ? 'Auto-filled from ID number' : ''"
              class="q-mt-sm"
            >
              <template #prepend><q-icon name="calendar_today" color="grey-6" /></template>
            </q-input>

            <div class="form-actions q-mt-lg">
              <q-btn
                label="Continue"
                type="submit"
                class="btn-primary full-width"
                unelevated
                size="lg"
                :loading="validatingId"
                icon-right="arrow_forward"
              />
            </div>
          </q-form>
        </div>

        <!-- STEP 2: Income -->
        <div v-else-if="currentStep === 2" key="step2" class="form-card">
          <div class="step-heading">
            <div class="step-num-badge">02</div>
            <div>
              <h2 class="step-title">Income Details</h2>
              <p class="step-sub">We use this to personalise your options</p>
            </div>
          </div>

          <q-form @submit.prevent="handleStep2Submit" ref="form2">
            <q-input
              v-model.number="store.income.monthly_income"
              label="Monthly Income (R)"
              outlined
              type="number"
              prefix="R"
              :rules="[v => !!v || 'Required', v => v > 0 || 'Must be greater than 0']"
              hint="Your gross monthly salary or income"
            >
              <template #prepend><q-icon name="payments" color="grey-6" /></template>
            </q-input>

            <!-- Document upload -->
            <div class="upload-zone q-mt-lg" @click="triggerFileInput" @dragover.prevent @drop.prevent="handleFileDrop">
              <input ref="fileInput" type="file" accept=".pdf,.jpg,.jpeg,.png" @change="handleFileSelect" style="display:none" />
              <div v-if="!store.income.document_filename" class="upload-prompt">
                <q-icon name="upload_file" size="40px" color="grey-5" />
                <p class="upload-title">Upload Proof of Income</p>
                <p class="upload-sub">Payslip, bank statement, or letter of employment<br/>PDF, JPG, PNG · Max 5MB</p>
              </div>
              <div v-else class="upload-success">
                <q-icon name="description" size="28px" color="positive" />
                <span class="upload-filename">{{ store.income.document_filename }}</span>
                <q-btn flat round icon="close" size="sm" color="grey-6" @click.stop="clearDocument" />
              </div>
            </div>

            <div class="form-actions q-mt-lg row q-gutter-sm">
              <q-btn outline label="Back" @click="store.prevStep()" class="btn-back col" size="lg" />
              <q-btn
                label="Continue"
                type="submit"
                class="btn-primary col-8"
                unelevated
                size="lg"
                icon-right="arrow_forward"
              />
            </div>
          </q-form>
        </div>

        <!-- STEP 3: Phone selection -->
        <div v-else-if="currentStep === 3" key="step3" class="form-card form-card-wide">
          <div class="step-heading">
            <div class="step-num-badge">03</div>
            <div>
              <h2 class="step-title">Choose Your Phone</h2>
              <p class="step-sub">
                Pricing based on your Risk Group {{ store.riskGroup }} profile
                <q-chip dense color="yellow-2" text-color="dark" class="q-ml-xs">{{ store.riskGroupLabel }}</q-chip>
              </p>
            </div>
          </div>

          <div v-if="store.phonesLoading" class="phones-loading">
            <q-spinner-dots color="primary" size="40px" />
            <p>Finding your options...</p>
          </div>

          <div v-else>
            <!-- Affordability notice -->
            <div v-if="hiddenCount > 0" class="affordability-notice q-mb-md">
              <q-icon name="info" size="18px" />
              <span>{{ hiddenCount }} phone{{ hiddenCount > 1 ? 's' : '' }} hidden — monthly payment exceeds 1/10 of your income</span>
            </div>

            <div v-if="affordablePhones.length === 0" class="no-phones">
              <q-icon name="phone_disabled" size="48px" color="grey-5" />
              <p>No phones are affordable with your current income.</p>
              <q-btn flat label="Go back and update income" @click="store.prevStep()" color="primary" />
            </div>

            <div v-else class="phones-grid">
              <div
                v-for="phone in affordablePhones"
                :key="phone.id"
                class="phone-card yellow-card"
                :class="{ 'phone-card-selected': store.selectedPhone?.id === phone.id }"
                @click="store.selectedPhone = phone"
              >
                <div class="phone-card-body">
                  <div class="phone-brand">{{ phone.brand }}</div>
                  <div class="phone-name">{{ phone.name }}</div>
                  <p class="phone-desc">{{ phone.description }}</p>

                  <div class="phone-pricing">
                    <div class="pricing-row">
                      <span class="pricing-label">Daily payment</span>
                      <span class="price-daily">R {{ phone.daily_payment.toFixed(2) }}</span>
                    </div>
                    <div class="pricing-breakdown">
                      <div class="breakdown-item">
                        <span>Cash price</span>
                        <span>R {{ formatMoney(phone.cash_price) }}</span>
                      </div>
                      <div class="breakdown-item">
                        <span>Deposit ({{ (phone.deposit_percent * 100).toFixed(0) }}%)</span>
                        <span>R {{ formatMoney(phone.deposit_amount) }}</span>
                      </div>
                      <div class="breakdown-item">
                        <span>Loan amount</span>
                        <span>R {{ formatMoney(phone.loan_amount) }}</span>
                      </div>
                      <div class="breakdown-item text-grey-6">
                        <span>Interest rate</span>
                        <span>{{ (phone.interest_rate * 100).toFixed(0) }}% p.a.</span>
                      </div>
                    </div>
                  </div>
                </div>

                <div class="phone-select-indicator">
                  <q-icon
                    :name="store.selectedPhone?.id === phone.id ? 'radio_button_checked' : 'radio_button_unchecked'"
                    :color="store.selectedPhone?.id === phone.id ? 'primary' : 'grey-4'"
                    size="22px"
                  />
                </div>
              </div>
            </div>

            <div class="form-actions q-mt-lg row q-gutter-sm" v-if="affordablePhones.length > 0">
              <q-btn outline label="Back" @click="store.prevStep()" class="btn-back col" size="lg" />
              <q-btn
                label="Review Application"
                class="btn-primary col-8"
                unelevated
                size="lg"
                icon-right="arrow_forward"
                :disable="!store.selectedPhone"
                @click="store.nextStep()"
              />
            </div>
          </div>
        </div>

        <!-- STEP 4: Review & Submit -->
        <div v-else-if="currentStep === 4" key="step4" class="form-card">
          <div class="step-heading">
            <div class="step-num-badge">04</div>
            <div>
              <h2 class="step-title">Review & Submit</h2>
              <p class="step-sub">Please confirm your application details</p>
            </div>
          </div>

          <div class="review-section">
            <div class="review-group">
              <div class="review-group-title">
                <q-icon name="person" size="16px" />Personal
              </div>
              <div class="review-row">
                <span>Full Name</span>
                <strong>{{ store.bio.first_name }} {{ store.bio.last_name }}</strong>
              </div>
              <div class="review-row">
                <span>ID Number</span>
                <strong class="mono">{{ store.bio.id_number }}</strong>
              </div>
              <div class="review-row">
                <span>Date of Birth</span>
                <strong>{{ formatDate(store.bio.date_of_birth) }}</strong>
              </div>
              <div class="review-row">
                <span>Age / Risk Group</span>
                <strong>{{ store.applicantAge }} years · Group {{ store.riskGroup }}</strong>
              </div>
            </div>

            <div class="review-group">
              <div class="review-group-title">
                <q-icon name="payments" size="16px" />Income
              </div>
              <div class="review-row">
                <span>Monthly Income</span>
                <strong>R {{ formatMoney(store.income.monthly_income) }}</strong>
              </div>
              <div class="review-row" v-if="store.income.document_filename">
                <span>Proof Document</span>
                <strong>{{ store.income.document_filename }}</strong>
              </div>
            </div>

            <div class="review-group" v-if="store.selectedPhone">
              <div class="review-group-title">
                <q-icon name="phone_iphone" size="16px" />Selected Phone
              </div>
              <div class="review-row">
                <span>Device</span>
                <strong>{{ store.selectedPhone.brand }} {{ store.selectedPhone.name }}</strong>
              </div>
              <div class="review-row">
                <span>Cash Price</span>
                <strong>R {{ formatMoney(store.selectedPhone.cash_price) }}</strong>
              </div>
              <div class="review-row">
                <span>Deposit Required</span>
                <strong>R {{ formatMoney(store.selectedPhone.deposit_amount) }}</strong>
              </div>
              <div class="review-row">
                <span>Loan Amount</span>
                <strong>R {{ formatMoney(store.selectedPhone.loan_amount) }}</strong>
              </div>
              <div class="review-row highlight">
                <span>Daily Payment</span>
                <strong class="price-daily">R {{ store.selectedPhone.daily_payment.toFixed(2) }}</strong>
              </div>
              <div class="review-row text-grey-6">
                <span>Interest Rate</span>
                <strong>{{ (store.selectedPhone.interest_rate * 100).toFixed(0) }}% p.a.</strong>
              </div>
            </div>
          </div>

          <div v-if="store.error" class="error-banner q-mt-md">
            <q-icon name="error" size="18px" />
            <span>{{ store.error }}</span>
          </div>

          <div class="form-actions q-mt-lg row q-gutter-sm">
            <q-btn outline label="Back" @click="store.prevStep()" class="btn-back col" size="lg" />
            <q-btn
              label="Submit Application"
              class="btn-primary col-8"
              unelevated
              size="lg"
              :loading="store.submitting"
              @click="handleSubmit"
              icon-right="check"
            />
          </div>

          <p class="legal-note q-mt-md">
            By submitting, you confirm that all information provided is accurate. This application is subject to credit approval.
          </p>
        </div>
      </transition>
    </div>
  </q-page>
</template>

<script setup>
import { ref, computed, watch } from "vue";
import { useRouter } from "vue-router";
import { useApplicationStore } from "../stores/application";
import { useQuasar } from "quasar";

const store = useApplicationStore();
const router = useRouter();
const $q = useQuasar();

const currentStep = computed(() => store.currentStep);

const steps = [
  { num: 1, label: "Personal" },
  { num: 2, label: "Income" },
  { num: 3, label: "Phone" },
  { num: 4, label: "Review" },
];

// ── Step 1 ────────────────────────────────────────────────────────────────────
const form1 = ref(null);
const validatingId = ref(false);
const idError = ref(null);

function clearIdError() {
  idError.value = null;
  if (store.idValidation?.valid) store.idValidation = null;
}

async function handleStep1Submit() {
  const valid = await form1.value?.validate();
  if (!valid) return;

  if (!store.idValidation?.valid) {
    validatingId.value = true;
    const result = await store.validateID(store.bio.id_number);
    validatingId.value = false;

    if (!result.valid) {
      idError.value = result.error;
      return;
    }
    // Auto-fill DOB from ID
    store.bio.date_of_birth = result.dob;
  }

  store.nextStep();
}

// ── Step 2 ────────────────────────────────────────────────────────────────────
const form2 = ref(null);
const fileInput = ref(null);

function triggerFileInput() {
  fileInput.value?.click();
}

async function handleFileSelect(event) {
  const file = event.target.files[0];
  if (file) await processFile(file);
}

async function handleFileDrop(event) {
  const file = event.dataTransfer.files[0];
  if (file) await processFile(file);
}

async function processFile(file) {
  if (file.size > 5 * 1024 * 1024) {
    $q.notify({ type: "negative", message: "File must be under 5MB" });
    return;
  }
  const reader = new FileReader();
  reader.onload = (e) => {
    store.income.document_data = e.target.result.split(",")[1]; // strip base64 prefix
    store.income.document_filename = file.name;
  };
  reader.readAsDataURL(file);
}

function clearDocument() {
  store.income.document_filename = "";
  store.income.document_data = "";
  if (fileInput.value) fileInput.value.value = "";
}

async function handleStep2Submit() {
  const valid = await form2.value?.validate();
  if (!valid) return;
  await store.fetchPhones();
  store.nextStep();
}

// ── Step 3 ────────────────────────────────────────────────────────────────────
const affordablePhones = computed(() => store.phones.filter((p) => p.affordable));
const hiddenCount = computed(() => store.phones.filter((p) => !p.affordable).length);

// ── Step 4 ────────────────────────────────────────────────────────────────────
async function handleSubmit() {
  try {
    const app = await store.submitApplication();
    router.push(`/success/${app.id}`);
  } catch (e) {
    // error already set in store
  }
}

// ── Utilities ─────────────────────────────────────────────────────────────────
function formatDate(dateStr) {
  if (!dateStr) return "";
  const d = new Date(dateStr + "T00:00:00");
  return d.toLocaleDateString("en-ZA", { day: "numeric", month: "long", year: "numeric" });
}

function formatMoney(val) {
  if (val == null) return "0.00";
  return Number(val).toLocaleString("en-ZA", { minimumFractionDigits: 2, maximumFractionDigits: 2 });
}
</script>

<style scoped>
.app-page {
  background: var(--bg);
  min-height: 100vh;
}

.app-header {
  background: var(--dark);
  padding: 16px 20px;
}

.header-inner {
  max-width: 640px;
  margin: 0 auto;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.logo {
  font-size: 1.4rem;
  font-weight: 800;
  color: white;
  letter-spacing: -0.02em;
}

.logo-y {
  color: var(--yellow);
}

.header-tagline {
  font-size: 0.78rem;
  color: rgba(255,255,255,0.5);
  text-transform: uppercase;
  letter-spacing: 0.08em;
}

/* Step Bar */
.step-bar {
  background: white;
  border-bottom: 1px solid var(--border);
  padding: 16px 20px;
  position: sticky;
  top: 0;
  z-index: 10;
}

.step-bar-inner {
  max-width: 500px;
  margin: 0 auto;
  display: flex;
  align-items: center;
  justify-content: space-between;
  position: relative;
}

.step-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  position: relative;
  z-index: 2;
}

.step-label {
  font-size: 0.68rem;
  font-weight: 500;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.step-active .step-label {
  color: var(--dark);
  font-weight: 700;
}

.step-done .step-label {
  color: var(--dark);
}

/* Form wrapper */
.form-wrapper {
  max-width: 560px;
  margin: 0 auto;
  padding: 24px 16px 48px;
}

.form-card-wide {
  max-width: 100%;
}

.form-card {
  background: white;
  border-radius: 20px;
  padding: 28px 24px;
  border: 1px solid var(--border);
  box-shadow: 0 2px 16px rgba(0,0,0,0.04);
}

.step-heading {
  display: flex;
  align-items: flex-start;
  gap: 14px;
  margin-bottom: 28px;
}

.step-num-badge {
  font-family: var(--font-mono);
  font-size: 1.8rem;
  font-weight: 700;
  color: var(--yellow);
  line-height: 1;
  min-width: 48px;
}

.step-title {
  font-size: 1.3rem;
  font-weight: 700;
  margin: 0 0 4px;
  color: var(--dark);
  letter-spacing: -0.02em;
}

.step-sub {
  font-size: 0.85rem;
  color: var(--text-muted);
  margin: 0;
}

.field-row {
  display: flex;
  gap: 12px;
}

.field-half {
  flex: 1;
}

/* ID info pill */
.id-info-pill {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  background: var(--yellow-light);
  border: 1px solid #e8d800;
  border-radius: 24px;
  padding: 6px 14px;
  font-size: 0.82rem;
  color: var(--dark);
}

.id-info-pill .divider {
  color: #ccc;
}

.risk-chip {
  font-weight: 700;
  background: var(--yellow);
  border-radius: 12px;
  padding: 1px 8px;
  font-size: 0.75rem;
}

/* Upload zone */
.upload-zone {
  border: 2px dashed var(--border);
  border-radius: 14px;
  padding: 28px 20px;
  text-align: center;
  cursor: pointer;
  transition: all 0.2s;
  background: #fafafa;
}

.upload-zone:hover {
  border-color: var(--yellow);
  background: var(--yellow-light);
}

.upload-title {
  font-weight: 600;
  margin: 8px 0 4px;
  color: var(--dark);
}

.upload-sub {
  font-size: 0.78rem;
  color: var(--text-muted);
  margin: 0;
  line-height: 1.6;
}

.upload-success {
  display: flex;
  align-items: center;
  gap: 10px;
  justify-content: center;
}

.upload-filename {
  font-size: 0.85rem;
  font-weight: 500;
  color: var(--dark);
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 200px;
  white-space: nowrap;
}

/* Phone grid */
.phones-loading {
  text-align: center;
  padding: 48px 0;
  color: var(--text-muted);
}

.affordability-notice {
  display: flex;
  align-items: center;
  gap: 8px;
  background: #fff8e1;
  border: 1px solid #ffe082;
  border-radius: 10px;
  padding: 10px 14px;
  font-size: 0.82rem;
  color: #7c5800;
}

.phones-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
  gap: 14px;
}

.phone-card {
  cursor: pointer;
  transition: all 0.2s;
  position: relative;
  padding: 18px;
}

.phone-brand {
  font-size: 0.72rem;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: var(--text-muted);
  font-weight: 600;
}

.phone-name {
  font-size: 1.1rem;
  font-weight: 700;
  color: var(--dark);
  margin: 2px 0 6px;
  letter-spacing: -0.01em;
}

.phone-desc {
  font-size: 0.78rem;
  color: var(--text-muted);
  line-height: 1.5;
  margin: 0 0 14px;
}

.phone-pricing {
  border-top: 1px solid var(--border);
  padding-top: 12px;
}

.pricing-row {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  margin-bottom: 8px;
}

.pricing-label {
  font-size: 0.72rem;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  color: var(--text-muted);
  font-weight: 600;
}

.pricing-breakdown {
  background: var(--bg);
  border-radius: 8px;
  padding: 8px 10px;
  margin-top: 6px;
}

.breakdown-item {
  display: flex;
  justify-content: space-between;
  font-size: 0.76rem;
  color: var(--text-muted);
  padding: 2px 0;
}

.breakdown-item span:last-child {
  font-weight: 500;
  color: var(--dark);
}

.phone-select-indicator {
  position: absolute;
  top: 14px;
  right: 14px;
}

.no-phones {
  text-align: center;
  padding: 48px 0;
  color: var(--text-muted);
}

/* Review */
.review-section {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.review-group {
  border: 1px solid var(--border);
  border-radius: 12px;
  overflow: hidden;
}

.review-group-title {
  background: var(--bg);
  padding: 8px 14px;
  font-size: 0.72rem;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: var(--text-muted);
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 6px;
  border-bottom: 1px solid var(--border);
}

.review-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 14px;
  font-size: 0.87rem;
  border-bottom: 1px solid var(--border);
}

.review-row:last-child {
  border-bottom: none;
}

.review-row span {
  color: var(--text-muted);
}

.review-row.highlight {
  background: var(--yellow-light);
}

.mono {
  font-family: var(--font-mono);
  letter-spacing: 0.04em;
}

/* Buttons */
.btn-primary {
  background: var(--yellow) !important;
  color: var(--dark) !important;
  font-weight: 700 !important;
  border-radius: 12px !important;
  font-size: 1rem !important;
}

.btn-back {
  border-radius: 12px !important;
  border-color: var(--border) !important;
  color: var(--text-muted) !important;
}

.error-banner {
  display: flex;
  align-items: center;
  gap: 8px;
  background: #fef2f2;
  border: 1px solid #fecaca;
  border-radius: 10px;
  padding: 12px 14px;
  font-size: 0.85rem;
  color: #c0392b;
}

.legal-note {
  font-size: 0.72rem;
  color: var(--text-muted);
  text-align: center;
  line-height: 1.5;
}

/* Transitions */
.slide-fade-enter-active,
.slide-fade-leave-active {
  transition: all 0.25s ease;
}

.slide-fade-enter-from {
  transform: translateX(20px);
  opacity: 0;
}

.slide-fade-leave-to {
  transform: translateX(-20px);
  opacity: 0;
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

@media (max-width: 480px) {
  .field-row {
    flex-direction: column;
    gap: 0;
  }
  .form-card {
    padding: 20px 16px;
  }
  .phones-grid {
    grid-template-columns: 1fr;
  }
}
</style>
