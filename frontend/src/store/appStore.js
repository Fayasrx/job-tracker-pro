import { create } from 'zustand'

export const useAppStore = create((set) => ({
    theme: 'dark',
    sidebarOpen: true,

    toggleTheme: () => set((s) => ({ theme: s.theme === 'dark' ? 'light' : 'dark' })),
    setSidebarOpen: (open) => set({ sidebarOpen: open }),
}))
