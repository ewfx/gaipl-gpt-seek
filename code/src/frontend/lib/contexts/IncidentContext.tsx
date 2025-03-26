'use client';

import React, { createContext, useContext, useState, useCallback } from 'react';

type IncidentContextType = {
  refreshKey: number;
  refreshIncidents: () => void;
  triggerRefresh: () => void;
};

const IncidentContext = createContext<IncidentContextType>({
  refreshKey: 0,
  refreshIncidents: () => {},
  triggerRefresh: () => {},
});

export const useIncidentContext = () => useContext(IncidentContext);

export const IncidentProvider = ({ children }: { children: React.ReactNode }) => {
  const [refreshKey, setRefreshKey] = useState(0);

  const triggerRefresh = useCallback(() => {
    setRefreshKey(prev => prev + 1);
  }, []);

  const refreshIncidents = useCallback(() => {
    triggerRefresh();
  }, [triggerRefresh]);

  return (
    <IncidentContext.Provider value={{ refreshKey, refreshIncidents, triggerRefresh }}>
      {children}
    </IncidentContext.Provider>
  );
}; 