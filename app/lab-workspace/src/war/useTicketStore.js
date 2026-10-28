import { create } from 'zustand';

export const useTicketStore = create(set => ({
  ticket: null,
  scenario: null,
  sla_left: null,
  setTicket(ticket, scenario, sla_left = null) {
    set({ ticket: ticket || null, scenario: scenario || null, sla_left: sla_left === null || sla_left === undefined ? null : Math.max(0, Number(sla_left) || 0) });
  },
  setSlaLeft(value) {
    set({ sla_left: value === null || value === undefined ? null : Math.max(0, Number(value) || 0) });
  },
  clearTicket() {
    set({ ticket: null, scenario: null, sla_left: null });
  },
}));
