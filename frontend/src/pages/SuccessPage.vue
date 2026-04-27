<template>
  <q-page class="success-page">
    <div class="app-header">
      <div class="header-inner">
        <div class="logo"><span class="logo-y">Y</span>ellow</div>
      </div>
    </div>

    <div class="success-wrapper">
      <div class="success-card pop-in">
        <div class="checkmark-ring">
          <q-icon name="check" size="48px" color="dark" />
        </div>

        <h1 class="success-title">Application Submitted!</h1>
        <p class="success-sub">
          Great news, {{ store.submittedApplication?.first_name }}! Your application has been received and is being reviewed.
        </p>

        <div class="app-ref">
          <span class="ref-label">Application Reference</span>
          <span class="ref-number">#{{ String(store.submittedApplication?.id).padStart(6, '0') }}</span>
        </div>

        <!-- Summary card -->
        <div class="summary-card" v-if="store.submittedApplication">
          <div class="summary-row">
            <span>Phone</span>
            <strong>{{ store.selectedPhone?.brand }} {{ store.selectedPhone?.name }}</strong>
          </div>
          <div class="summary-row">
            <span>Daily Payment</span>
            <strong class="price-daily">R {{ store.submittedApplication?.daily_payment?.toFixed(2) }}</strong>
          </div>
          <div class="summary-row">
            <span>Loan Amount</span>
            <strong>R {{ formatMoney(store.submittedApplication?.loan_amount) }}</strong>
          </div>
          <div class="summary-row">
            <span>Term</span>
            <strong>360 days</strong>
          </div>
        </div>

        <div class="what-next">
          <div class="what-next-title">What happens next?</div>
          <div class="next-step" v-for="(step, i) in nextSteps" :key="i">
            <div class="next-step-num">{{ i + 1 }}</div>
            <span>{{ step }}</span>
          </div>
        </div>

        <q-btn
          label="Start a New Application"
          class="btn-primary full-width q-mt-lg"
          unelevated
          size="lg"
          @click="startNew"
          icon-right="add"
        />
      </div>
    </div>
  </q-page>
</template>

<script setup>
import { useRouter } from "vue-router";
import { useApplicationStore } from "../stores/application";

const router = useRouter();
const store = useApplicationStore();

const nextSteps = [
  "Our team will review your application within 24 hours",
  "You'll receive an SMS and email with the outcome",
  "If approved, pay your deposit and collect your phone",
];

function formatMoney(val) {
  if (val == null) return "0.00";
  return Number(val).toLocaleString("en-ZA", { minimumFractionDigits: 2, maximumFractionDigits: 2 });
}

function startNew() {
  store.reset();
  router.push("/");
}
</script>

<style scoped>
.success-page {
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
}

.logo {
  font-size: 1.4rem;
  font-weight: 800;
  color: white;
}

.logo-y {
  color: var(--yellow);
}

.success-wrapper {
  max-width: 480px;
  margin: 0 auto;
  padding: 32px 16px 64px;
}

.success-card {
  background: white;
  border-radius: 24px;
  padding: 36px 28px;
  border: 1px solid var(--border);
  text-align: center;
  box-shadow: 0 4px 32px rgba(0,0,0,0.06);
}

.checkmark-ring {
  width: 88px;
  height: 88px;
  border-radius: 50%;
  background: var(--yellow);
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 20px;
  box-shadow: 0 8px 24px rgba(245, 196, 0, 0.35);
}

.success-title {
  font-size: 1.6rem;
  font-weight: 800;
  letter-spacing: -0.03em;
  margin: 0 0 8px;
  color: var(--dark);
}

.success-sub {
  font-size: 0.9rem;
  color: var(--text-muted);
  line-height: 1.6;
  margin: 0 0 20px;
}

.app-ref {
  display: inline-flex;
  flex-direction: column;
  align-items: center;
  background: var(--bg);
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 12px 24px;
  margin-bottom: 24px;
}

.ref-label {
  font-size: 0.7rem;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: var(--text-muted);
  font-weight: 600;
}

.ref-number {
  font-family: var(--font-mono);
  font-size: 1.4rem;
  font-weight: 700;
  color: var(--dark);
  letter-spacing: 0.05em;
}

.summary-card {
  background: var(--bg);
  border-radius: 12px;
  padding: 4px 0;
  margin-bottom: 24px;
  text-align: left;
}

.summary-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 16px;
  font-size: 0.87rem;
  border-bottom: 1px solid var(--border);
}

.summary-row:last-child {
  border-bottom: none;
}

.summary-row span {
  color: var(--text-muted);
}

.what-next {
  background: #f0fdf4;
  border: 1px solid #bbf7d0;
  border-radius: 12px;
  padding: 16px;
  text-align: left;
  margin-bottom: 8px;
}

.what-next-title {
  font-size: 0.78rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  color: #166534;
  margin-bottom: 10px;
}

.next-step {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  font-size: 0.83rem;
  color: #15803d;
  padding: 4px 0;
}

.next-step-num {
  min-width: 20px;
  height: 20px;
  border-radius: 50%;
  background: var(--success);
  color: white;
  font-size: 0.7rem;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
}

.btn-primary {
  background: var(--yellow) !important;
  color: var(--dark) !important;
  font-weight: 700 !important;
  border-radius: 12px !important;
}
</style>
