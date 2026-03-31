import { create } from 'zustand';
import { dashboardApi, PlayerResponse } from '../../UserDashboard/api/dashboardApi';

interface AdminFilterState {
  players: PlayerResponse[];
  selectedPlayerId: number | null;
  selectedDate: string;
  loadPlayers: () => Promise<void>;
  setPlayer: (id: number | null) => void;
  setDate: (date: string) => void;
  quickDate: (offset: number) => void;
}

export const useAdminFilter = create<AdminFilterState>((set, get) => ({
  players: [],
  selectedPlayerId: null,
  selectedDate: new Date().toISOString().slice(0, 10),

  loadPlayers: async () => {
    try {
      const res = await dashboardApi.getPlayers();
      const current = get().selectedPlayerId;
      const playerOnly = res.data.filter((p) => p.role === 'player');
      set({ players: playerOnly });
      if (playerOnly.length > 0 && !current) {
        set({ selectedPlayerId: playerOnly[0].id });
      }
    } catch {
      // ignore
    }
  },

  setPlayer: (id) => set({ selectedPlayerId: id }),

  setDate: (date) => set({ selectedDate: date }),

  quickDate: (offset) => {
    const d = new Date();
    d.setDate(d.getDate() + offset);
    set({ selectedDate: d.toISOString().slice(0, 10) });
  },
}));
