import { create } from 'zustand';

export type ToastType = 'success' | 'error' | 'warning' | 'info';

interface ToastItem {
  id: string;
  type: ToastType;
  message: string;
  duration: number;
}

interface ToastStore {
  toasts: ToastItem[];
  showToast: (type: ToastType, message: string, duration?: number) => void;
  removeToast: (id: string) => void;
}

const DEFAULT_DURATION: Record<ToastType, number> = {
  success: 3000,
  warning: 4000,
  error: 5000,
  info: 3000,
};

export const useToastStore = create<ToastStore>((set) => ({
  toasts: [],
  showToast: (type, message, duration) => {
    const id = `${Date.now()}-${Math.random().toString(36).slice(2, 7)}`;
    const ms = duration ?? DEFAULT_DURATION[type];
    set((state) => ({
      toasts: [...state.toasts, { id, type, message, duration: ms }],
    }));
    if (type !== 'error') {
      setTimeout(() => {
        set((state) => ({
          toasts: state.toasts.filter((t) => t.id !== id),
        }));
      }, ms);
    }
  },
  removeToast: (id) =>
    set((state) => ({
      toasts: state.toasts.filter((t) => t.id !== id),
    })),
}));
