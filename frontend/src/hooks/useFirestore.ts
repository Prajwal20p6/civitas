import { useState, useEffect } from 'react';
import { doc, onSnapshot } from 'firebase/firestore';
import { firestore } from '../../firebase';

export const useFirestore = (incidentId: string | null) => {
  const [incidentData, setIncidentData] = useState<any>(null);
  const [error, setError] = useState<any>(null);

  useEffect(() => {
    if (!incidentId || !firestore) {
      setIncidentData(null);
      return;
    }

    try {
      const docRef = doc(firestore, 'incidents', incidentId);
      const unsubscribe = onSnapshot(docRef, (docSnap) => {
        if (docSnap.exists()) {
          setIncidentData(docSnap.data());
        }
      }, (err) => {
        setError(err);
      });

      return () => unsubscribe();
    } catch (err) {
      console.warn("Firestore setup failed, offline mode enabled.", err);
    }
  }, [incidentId]);

  return { incidentData, error };
};
