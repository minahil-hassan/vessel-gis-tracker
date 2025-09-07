// src/components/PortCallsPopup.jsx

import { useEffect, useState } from 'react';
import axiosClient from '../api/axiosClient';

const PortCallsPopup = ({ mmsi }) => {
  const [portCalls, setPortCalls] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false);

  console.log("PortCallsPopup rendered with MMSI:", mmsi);

  useEffect(() => {
    setLoading(true);
    setError(false);

    axiosClient.get(`/vessel-popup/${mmsi}`)
      .then(res => {
        console.info("PortCallsPopup API response:", res);
        const { port_calls = [] } = res.data;
        setPortCalls(port_calls);
        setLoading(false);
      })
      .catch((err) => {
      console.error("Failed to fetch port calls", err);

      if (err.response?.status === 404) {
        setPortCalls([]); // Set empty port calls
      } else {
        setError(true); // Actual error (e.g. network, 500)
      }

      setLoading(false);
});
  }, [mmsi]);

  return (
    <div className="popup-section">
      <strong>Port Calls:</strong>
      {loading && <div>Loading...</div>}
      {!loading && error && <div>No port calls found</div>}
      {!loading && !error && (
        <ul className="port-calls">
          {portCalls.length > 0 ? (
            portCalls.map((port, idx) => <li key={idx}>{port}</li>)
          ) : (
            <li>No port calls detected</li>
          )}
        </ul>
      )}
    </div>
  );
};

export default PortCallsPopup;
