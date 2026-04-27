import { defineStore } from "pinia";
import axios from "axios";

const api = axios.create({ baseURL: import.meta.env.VITE_API_BASE_URL || "/api" });

export const useApplicationStore = defineStore("application", {
  state: () => ({
    // Step tracking
    currentStep: 1,
    totalSteps: 4,

    // Step 1: Bio data
    bio: {
      first_name: "",
      last_name: "",
      id_number: "",
      date_of_birth: "",
    },
    idValidation: null, // { valid, dob, age, gender, risk_group, error }

    // Step 2: Income
    income: {
      monthly_income: null,
      document_filename: "",
      document_data: "", // base64
    },

    // Step 3: Phone selection
    selectedPhone: null,
    phones: [],
    phonesLoading: false,

    // Submission
    submitting: false,
    submittedApplication: null,
    error: null,
  }),

  getters: {
    riskGroup: (state) => state.idValidation?.risk_group ?? null,
    applicantAge: (state) => state.idValidation?.age ?? null,
    riskGroupLabel: (state) => {
      const g = state.idValidation?.risk_group;
      if (g === 1) return "Group 1 (18–30)";
      if (g === 2) return "Group 2 (31–50)";
      if (g === 3) return "Group 3 (51–65)";
      return null;
    },
  },

  actions: {
    async validateID(idNumber) {
      try {
        const res = await api.post("/applications/validate-id", {
          id_number: idNumber,
        });
        this.idValidation = res.data;
        return res.data;
      } catch (err) {
        const msg = err.response?.data?.detail || "Validation failed";
        this.idValidation = { valid: false, error: msg };
        return this.idValidation;
      }
    },

    async fetchPhones() {
      if (!this.riskGroup) return;
      this.phonesLoading = true;
      try {
        const params = { risk_group: this.riskGroup };
        if (this.income.monthly_income) {
          params.monthly_income = this.income.monthly_income;
        }
        const res = await api.get("/phones/", { params });
        this.phones = res.data;
      } catch (err) {
        console.error("Failed to fetch phones", err);
      } finally {
        this.phonesLoading = false;
      }
    },

    async submitApplication() {
      this.submitting = true;
      this.error = null;
      try {
        const payload = {
          first_name: this.bio.first_name,
          last_name: this.bio.last_name,
          id_number: this.bio.id_number,
          date_of_birth: this.bio.date_of_birth,
          monthly_income: this.income.monthly_income,
          income_document_filename: this.income.document_filename || null,
          income_document_data: this.income.document_data || null,
          phone_id: this.selectedPhone.id,
        };
        const res = await api.post("/applications/", payload);
        this.submittedApplication = res.data;
        return res.data;
      } catch (err) {
        const msg =
          err.response?.data?.detail || "Submission failed. Please try again.";
        this.error = msg;
        throw new Error(msg);
      } finally {
        this.submitting = false;
      }
    },

    nextStep() {
      if (this.currentStep < this.totalSteps) this.currentStep++;
    },

    prevStep() {
      if (this.currentStep > 1) this.currentStep--;
    },

    reset() {
      this.$reset();
    },
  },
});
