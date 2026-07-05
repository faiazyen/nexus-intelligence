import { create } from "zustand";

export interface OnboardingState {
  step: number;
  companyName: string;
  companyWebsite: string;
  companySize: string;
  offerDescription: string;
  icpIndustries: string[];
  icpSizeMin: string;
  icpSizeMax: string;
  icpTitles: string[];
  icpGeographies: string[];
  icpTechKeywords: string[];
  pastWinContext: string;
  selectedSignalTypes: string[];
  setField: <K extends keyof OnboardingState>(key: K, value: OnboardingState[K]) => void;
  toggleListValue: (
    key: "icpIndustries" | "icpTitles" | "icpGeographies" | "icpTechKeywords" | "selectedSignalTypes",
    value: string
  ) => void;
  next: () => void;
  back: () => void;
  goTo: (step: number) => void;
  reset: () => void;
}

const initialState = {
  step: 1,
  companyName: "",
  companyWebsite: "",
  companySize: "",
  offerDescription: "",
  icpIndustries: [] as string[],
  icpSizeMin: "50",
  icpSizeMax: "5000",
  icpTitles: [] as string[],
  icpGeographies: [] as string[],
  icpTechKeywords: [] as string[],
  pastWinContext: "",
  selectedSignalTypes: [
    "job_post",
    "leadership_change",
    "funding",
    "procurement_notice",
  ] as string[],
};

export const useOnboardingStore = create<OnboardingState>((set, get) => ({
  ...initialState,
  setField: (key, value) => set({ [key]: value } as Partial<OnboardingState>),
  toggleListValue: (key, value) => {
    const current = get()[key];
    const exists = current.includes(value);
    set({
      [key]: exists ? current.filter((v) => v !== value) : [...current, value],
    } as Partial<OnboardingState>);
  },
  next: () => set({ step: Math.min(get().step + 1, 6) }),
  back: () => set({ step: Math.max(get().step - 1, 1) }),
  goTo: (step) => set({ step }),
  reset: () => set({ ...initialState }),
}));
