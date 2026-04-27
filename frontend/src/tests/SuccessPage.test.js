import { describe, it, expect, vi } from "vitest";
import { mount } from "@vue/test-utils";
import { createPinia, setActivePinia } from "pinia";
import { createRouter, createWebHashHistory } from "vue-router";
import SuccessPage from "../pages/SuccessPage.vue";
import { useApplicationStore } from "../stores/application";

const router = createRouter({
  history: createWebHashHistory(),
  routes: [{ path: "/", component: SuccessPage }],
});

function mountSuccess() {
  const pinia = createPinia();
  setActivePinia(pinia);
  return mount(SuccessPage, {
    global: {
      plugins: [pinia, router],
    },
  });
}

function seedStore(store, overrides = {}) {
  store.submittedApplication = {
    id: 42,
    first_name: "Thabo",
    last_name: "Nkosi",
    age: 36,
    risk_group: 2,
    daily_payment: 25.87,
    loan_amount: 9313.97,
    status: "completed",
    ...overrides,
  };
  store.selectedPhone = {
    id: 1,
    name: "Galaxy A55",
    brand: "Samsung",
    daily_payment: 25.87,
    cash_price: 8999,
    loan_amount: 9313.97,
  };
}


describe("SuccessPage — Layout", () => {
  it("renders the success title", () => {
    const wrapper = mountSuccess();
    expect(wrapper.text()).toContain("Application Submitted!");
  });

  it("renders the Yellow logo", () => {
    const wrapper = mountSuccess();
    expect(wrapper.text()).toContain("Yellow");
  });

  it("renders the what happens next section", () => {
    const wrapper = mountSuccess();
    expect(wrapper.text()).toContain("What happens next");
  });

  it("renders all 3 next steps", () => {
    const wrapper = mountSuccess();
    expect(wrapper.text()).toContain("review your application");
    expect(wrapper.text()).toContain("SMS");
    expect(wrapper.text()).toContain("deposit");
  });

  it("renders the start new application button", () => {
    const wrapper = mountSuccess();
    expect(wrapper.text()).toContain("Start a New Application");
  });
});


describe("SuccessPage — Application Data", () => {
  it("shows the applicant first name in the message", async () => {
    const wrapper = mountSuccess();
    const store = useApplicationStore();
    seedStore(store);
    await wrapper.vm.$nextTick();

    expect(wrapper.text()).toContain("Thabo");
  });

  it("displays the formatted application reference number", async () => {
    const wrapper = mountSuccess();
    const store = useApplicationStore();
    seedStore(store);
    await wrapper.vm.$nextTick();

    expect(wrapper.text()).toContain("000042");
  });

  it("pads short application IDs to 6 digits", async () => {
    const wrapper = mountSuccess();
    const store = useApplicationStore();
    seedStore(store, { id: 1 });
    await wrapper.vm.$nextTick();

    expect(wrapper.text()).toContain("000001");
  });

  it("shows the selected phone name", async () => {
    const wrapper = mountSuccess();
    const store = useApplicationStore();
    seedStore(store);
    await wrapper.vm.$nextTick();

    expect(wrapper.text()).toContain("Galaxy A55");
    expect(wrapper.text()).toContain("Samsung");
  });

  it("shows the daily payment amount", async () => {
    const wrapper = mountSuccess();
    const store = useApplicationStore();
    seedStore(store);
    await wrapper.vm.$nextTick();

    expect(wrapper.text()).toContain("25.87");
  });

  it("shows the loan amount", async () => {
    const wrapper = mountSuccess();
    const store = useApplicationStore();
    seedStore(store);
    await wrapper.vm.$nextTick();

    expect(wrapper.text()).toContain("9");
  });

  it("shows the loan term", async () => {
    const wrapper = mountSuccess();
    const store = useApplicationStore();
    seedStore(store);
    await wrapper.vm.$nextTick();

    expect(wrapper.text()).toContain("360 days");
  });
});


describe("SuccessPage — Actions", () => {
  it("resets store when start new application is clicked", async () => {
    const wrapper = mountSuccess();
    const store = useApplicationStore();
    seedStore(store);

    const resetSpy = vi.spyOn(store, "reset");

    const btn = wrapper.findAll("button").find(b =>
      b.text().includes("Start a New Application")
    );
    await btn.trigger("click");

    expect(resetSpy).toHaveBeenCalled();
  });

  it("navigates to / when start new application is clicked", async () => {
    const wrapper = mountSuccess();
    const store = useApplicationStore();
    seedStore(store);

    const pushSpy = vi.spyOn(router, "push");

    const btn = wrapper.findAll("button").find(b =>
      b.text().includes("Start a New Application")
    );
    await btn.trigger("click");

    expect(pushSpy).toHaveBeenCalledWith("/");
  });
});


describe("SuccessPage — Empty State", () => {
  it("renders without crashing when no application data exists", () => {
    const wrapper = mountSuccess();
    expect(wrapper.text()).toContain("Application Submitted!");
  });

  it("does not crash when loan amount is null", async () => {
    const wrapper = mountSuccess();
    const store = useApplicationStore();
    seedStore(store, { loan_amount: null, daily_payment: null });
    await wrapper.vm.$nextTick();

    expect(wrapper.text()).toContain("Application Submitted!");
  });
});
