import React, { useState } from 'react';

const GroupedVesselTypes = ({ groupedTypes }) => {
  const [expandedGroups, setExpandedGroups] = useState({});

  const toggleGroup = (groupName) => {
    setExpandedGroups(prev => ({
      ...prev,
      [groupName]: !prev[groupName]
    }));
  };

  return (
    <ul>
      <li><strong>Vessel Types:</strong>
        <ul>
          {Object.entries(groupedTypes).map(([group, subtypes]) => (
            <li key={group}>
              {group} ({Object.values(subtypes).reduce((a, b) => a + b, 0)})
              {Object.keys(subtypes).length > 1 && (
                <>
                  <button onClick={() => toggleGroup(group)} className="toggle-button">
                    {expandedGroups[group] ? 'Hide' : 'See more'}
                  </button>
                  {expandedGroups[group] && (
                    <ul className="grouped-subtypes">
                      {Object.entries(subtypes).map(([subtype, count]) => (
                        <li key={subtype}>{subtype}: {count}</li>
                      ))}
                    </ul>
                  )}
                </>
              )}
            </li>
          ))}
        </ul>
      </li>
    </ul>
  );
};

export default GroupedVesselTypes;
