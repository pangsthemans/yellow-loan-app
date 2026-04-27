import { config } from "@vue/test-utils";
import { Quasar } from "quasar";

config.global.plugins = [Quasar];
config.global.stubs = {
  // Stub Quasar components that need a full browser environment
  QLayout: { template: "<div><slot /></div>" },
  QPageContainer: { template: "<div><slot /></div>" },
  QPage: { template: "<div><slot /></div>" },
  QForm: { template: "<form @submit.prevent='$emit(\"submit\")'><slot /></form>" },
  QInput: {
    template: "<div><label>{{ label }}</label><input :value='modelValue' @input=\"$emit('update:modelValue', $event.target.value)\" /></div>",
    props: ["modelValue", "rules", "label"],
    emits: ["update:modelValue"],
  },
  QBtn: {
    template: "<button @click='$emit(\"click\")' :disabled='disable'><slot />{{ label }}</button>",
    props: ["label", "disable", "loading", "type"],
  },
  QIcon: { template: "<span />" },
  QSpinner: { template: "<span />" },
  QChip: { template: "<span><slot /></span>" },
  QSpinnerDots: { template: "<span />" },
  Transition: { template: "<div><slot /></div>" },
};