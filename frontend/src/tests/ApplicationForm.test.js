import { describe, it, expect, vi } from "vitest";
import { mount } from "@vue/test-utils";
import { createPinia, setActivePinia } from "pinia";
import { createRouter, createWebHashHistory } from "vue-router";
import ApplicationForm from "../pages/ApplicationForm.vue";
import { useApplicationStore } from "../stores/application";

const router = createRouter({
  history: createWebHashHistory(),
  routes: [{ path: "/", component: ApplicationForm }],
});

function mountForm() {
  const pinia = createPinia();
  setActivePinia(pinia);
  return mount(ApplicationForm, {
    global: {
      plugins: [pinia, router],
    },
  });
}

describe("ApplicationForm — Step 1 (Personal Details)", () => {
  it("renders step 1 by default", () => {
    const wrapper = mountForm();
    expect(wrapper.text()).toContain("Personal Details");
    expect(wrapper.text()).toContain("We need to verify your identity");
  });

  it("shows the step number badge 01", () => {
    const wrapper = mountForm();
    expect(wrapper.text()).toContain("01");
  });

  it("does not show step 2 content on initial load", () => {
    const wrapper = mountForm();
    expect(wrapper.text()).not.toContain("Income Details");
  });

  it("does not show step 3 content on initial load", () => {
    const wrapper = mountForm();
    expect(wrapper.text()).not.toContain("Choose Your Phone");
  });

  it("shows all 4 step indicators", () => {
    const wrapper = mountForm();
    expect(wrapper.text()).toContain("Personal");
    expect(wrapper.text()).toContain("Income");
    expect(wrapper.text()).toContain("Phone");
    expect(wrapper.text()).toContain("Review");
  });

  it("shows the Continue button on step 1", () => {
    const wrapper = mountForm();
    expect(wrapper.text()).toContain("Continue");
  });
});


describe("ApplicationForm — Step Navigation", () => {
  it("advances to step 2 when store currentStep is set to 2", async () => {
    const wrapper = mountForm();
    const store = useApplicationStore();

    store.currentStep = 2;
    await wrapper.vm.$nextTick();

    expect(wrapper.text()).toContain("Income Details");
  });

  it("advances to step 3 when store currentStep is set to 3", async () => {
    const wrapper = mountForm();
    const store = useApplicationStore();

    store.currentStep = 3;
    await wrapper.vm.$nextTick();

    expect(wrapper.text()).toContain("Choose Your Phone");
  });

  it("advances to step 4 when store currentStep is set to 4", async () => {
    const wrapper = mountForm();
    const store = useApplicationStore();

    store.currentStep = 4;
    await wrapper.vm.$nextTick();

    expect(wrapper.text()).toContain("Review & Submit");
  });

  it("shows Back button from step 2 onwards", async () => {
    const wrapper = mountForm();
    const store = useApplicationStore();

    store.currentStep = 2;
    await wrapper.vm.$nextTick();

    expect(wrapper.text()).toContain("Back");
  });

  it("back button decrements the step", async () => {
    const wrapper = mountForm();
    const store = useApplicationStore();

    store.currentStep = 2;
    await wrapper.vm.$nextTick();

    const backBtn = wrapper.findAll("button").find(b => b.text().includes("Back"));
    await backBtn.trigger("click");

    expect(store.currentStep).toBe(1);
  });
});


describe("ApplicationForm — Step 2 (Income)", () => {
  it("renders income input", async () => {
    const wrapper = mountForm();
    const store = useApplicationStore();
    store.currentStep = 2;
    await wrapper.vm.$nextTick();

    expect(wrapper.text()).toContain("Monthly Income");
  });

  it("renders document upload zone", async () => {
    const wrapper = mountForm();
    const store = useApplicationStore();
    store.currentStep = 2;
    await wrapper.vm.$nextTick();

    expect(wrapper.text()).toContain("Upload Proof of Income");
  });

  it("shows filename when document is uploaded", async () => {
    const wrapper = mountForm();
    const store = useApplicationStore();
    store.currentStep = 2;
    store.income.document_filename = "payslip_march.pdf";
    await wrapper.vm.$nextTick();

    expect(wrapper.text()).toContain("payslip_march.pdf");
  });
});


describe("ApplicationForm — Step 3 (Phone Selection)", () => {
  it("shows loading state while fetching phones", async () => {
    const wrapper = mountForm();
    const store = useApplicationStore();
    store.currentStep = 3;
    store.phonesLoading = true;
    await wrapper.vm.$nextTick();

    expect(wrapper.text()).toContain("Finding your options");
  });

  it("shows phones when loaded", async () => {
    const wrapper = mountForm();
    const store = useApplicationStore();
    store.currentStep = 3;
    store.phones = [
      {
        id: 1,
        name: "Galaxy A55",
        brand: "Samsung",
        description: "A great phone",
        cash_price: 8999,
        deposit_percent: 0.1,
        deposit_amount: 899.9,
        loan_principal: 8099.1,
        interest_rate: 0.15,
        loan_amount: 9313.97,
        daily_payment: 25.87,
        monthly_payment: 776.16,
        affordable: true,
      },
    ];
    await wrapper.vm.$nextTick();

    expect(wrapper.text()).toContain("Samsung");
    expect(wrapper.text()).toContain("Galaxy A55");
  });

  it("hides unaffordable phones", async () => {
    const wrapper = mountForm();
    const store = useApplicationStore();
    store.currentStep = 3;
    store.phones = [
      { id: 1, name: "Cheap Phone", brand: "TECNO", affordable: true, daily_payment: 10, cash_price: 1000, deposit_percent: 0.1, deposit_amount: 100, loan_amount: 1000, interest_rate: 0.15, monthly_payment: 83, description: "" },
      { id: 2, name: "Expensive Phone", brand: "Apple", affordable: false, daily_payment: 200, cash_price: 30000, deposit_percent: 0.2, deposit_amount: 6000, loan_amount: 28000, interest_rate: 0.28, monthly_payment: 2333, description: "" },
    ];
    await wrapper.vm.$nextTick();

    expect(wrapper.text()).toContain("Cheap Phone");
    expect(wrapper.text()).not.toContain("Expensive Phone");
  });

  it("shows affordability notice when phones are hidden", async () => {
    const wrapper = mountForm();
    const store = useApplicationStore();
    store.currentStep = 3;
    store.phones = [
      { id: 1, name: "Cheap Phone", brand: "TECNO", affordable: true, daily_payment: 10, cash_price: 1000, deposit_percent: 0.1, deposit_amount: 100, loan_amount: 1000, interest_rate: 0.15, monthly_payment: 83, description: "" },
      { id: 2, name: "Expensive Phone", brand: "Apple", affordable: false, daily_payment: 200, cash_price: 30000, deposit_percent: 0.2, deposit_amount: 6000, loan_amount: 28000, interest_rate: 0.28, monthly_payment: 2333, description: "" },
    ];
    await wrapper.vm.$nextTick();

    expect(wrapper.text()).toContain("hidden");
  });

  it("Continue button is disabled when no phone selected", async () => {
    const wrapper = mountForm();
    const store = useApplicationStore();
    store.currentStep = 3;
    store.phones = [
      { id: 1, name: "Galaxy A55", brand: "Samsung", affordable: true, daily_payment: 25, cash_price: 8999, deposit_percent: 0.1, deposit_amount: 899, loan_amount: 9313, interest_rate: 0.15, monthly_payment: 776, description: "" },
    ];
    await wrapper.vm.$nextTick();

    const continueBtn = wrapper.findAll("button").find(b => b.text().includes("Review Application"));
    expect(continueBtn.attributes("disabled")).toBeDefined();
  });
});


describe("ApplicationForm — Step 4 (Review)", () => {
  it("shows applicant name in review", async () => {
    const wrapper = mountForm();
    const store = useApplicationStore();

    store.currentStep = 4;
    store.bio.first_name = "Thabo";
    store.bio.last_name = "Nkosi";
    store.bio.id_number = "9001155001083";
    store.bio.date_of_birth = "1990-01-15";
    store.idValidation = { valid: true, age: 36, risk_group: 2, dob: "1990-01-15" };
    store.income.monthly_income = 50000;
    store.selectedPhone = {
      id: 1, name: "Galaxy A55", brand: "Samsung",
      cash_price: 8999, deposit_amount: 899, loan_amount: 9313,
      daily_payment: 25.87, interest_rate: 0.15,
    };

    await wrapper.vm.$nextTick();

    expect(wrapper.text()).toContain("Thabo");
    expect(wrapper.text()).toContain("Nkosi");
  });

  it("shows selected phone in review", async () => {
    const wrapper = mountForm();
    const store = useApplicationStore();

    store.currentStep = 4;
    store.bio = { first_name: "Thabo", last_name: "Nkosi", id_number: "9001155001083", date_of_birth: "1990-01-15" };
    store.idValidation = { valid: true, age: 36, risk_group: 2, dob: "1990-01-15" };
    store.income.monthly_income = 50000;
    store.selectedPhone = {
      id: 1, name: "Galaxy A55", brand: "Samsung",
      cash_price: 8999, deposit_amount: 899, loan_amount: 9313,
      daily_payment: 25.87, interest_rate: 0.15,
    };

    await wrapper.vm.$nextTick();

    expect(wrapper.text()).toContain("Galaxy A55");
    expect(wrapper.text()).toContain("Samsung");
  });

  it("shows error message when submission fails", async () => {
    const wrapper = mountForm();
    const store = useApplicationStore();

    store.currentStep = 4;
    store.error = "An application already exists for this ID number";
    await wrapper.vm.$nextTick();

    expect(wrapper.text()).toContain("An application already exists for this ID number");
  });
});
