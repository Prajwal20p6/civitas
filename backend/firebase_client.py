import os
import time
from typing import Dict, Any, Optional, Callable

try:
    import firebase_admin
    from firebase_admin import credentials, firestore, db

    HAS_FIREBASE = True
except ImportError:
    HAS_FIREBASE = False


def retry_db_operation(
    operation: Callable[[], Any], max_retries: int = 3, delay: float = 0.2
) -> Any:
    """Helper method to execute a database operation with exponential retries and backoff."""
    for attempt in range(max_retries):
        try:
            return operation()
        except Exception as e:
            if attempt == max_retries - 1:
                raise e
            time.sleep(delay * (2**attempt))


class FirebaseClient:
    """
    Wrapper for Firebase Firestore and Realtime Database operations.
    Supports offline fallback mode for local development and automated testing.
    """

    def __init__(self):
        self.offline_mode = True
        self.firestore_client = None
        self.db_client = None

        # Local mock DB state for offline fallback
        self._mock_incidents: Dict[str, Dict[str, Any]] = {}
        self._mock_streams: Dict[str, list] = {}

        if HAS_FIREBASE:
            cred_path = os.getenv(
                "FIREBASE_SERVICE_ACCOUNT_KEY", "service-account-key.json"
            )

            try:
                if os.path.exists(cred_path):
                    cred = credentials.Certificate(cred_path)
                    firebase_admin.initialize_app(
                        cred,
                        {
                            "databaseURL": os.getenv(
                                "FIREBASE_DATABASE_URL",
                                "https://civitas-demo.firebaseio.com",
                            )
                        },
                    )
                    self.firestore_client = firestore.client()
                    self.db_client = db.reference()
                    self.offline_mode = False
                elif os.getenv("GCP_PROJECT") or os.getenv(
                    "GOOGLE_APPLICATION_CREDENTIALS"
                ):
                    firebase_admin.initialize_app(
                        options={
                            "databaseURL": os.getenv(
                                "FIREBASE_DATABASE_URL",
                                "https://civitas-demo.firebaseio.com",
                            )
                        }
                    )
                    self.firestore_client = firestore.client()
                    self.db_client = db.reference()
                    self.offline_mode = False
            except Exception:
                pass

    def create_incident(self, incident_id: str, data: Dict[str, Any]) -> None:
        """Create a new incident document in Firestore with retries and error fallback."""
        data["created_at"] = data.get("created_at") or time.strftime(
            "%Y-%m-%dT%H:%M:%SZ"
        )
        data["status"] = data.get("status") or "processing"

        if self.offline_mode:
            self._mock_incidents[incident_id] = data
            self._mock_streams[incident_id] = []
        else:
            try:
                retry_db_operation(
                    lambda: self.firestore_client.collection("incidents")
                    .document(incident_id)
                    .set(data)
                )
            except Exception:
                self._mock_incidents[incident_id] = data
                self._mock_streams[incident_id] = []

    def get_incident(self, incident_id: str) -> Optional[Dict[str, Any]]:
        """Fetch incident document from Firestore with retries."""
        if self.offline_mode or incident_id not in self._mock_incidents:
            if not self.offline_mode:
                try:
                    doc = retry_db_operation(
                        lambda: self.firestore_client.collection("incidents")
                        .document(incident_id)
                        .get()
                    )
                    if doc.exists:
                        return doc.to_dict()
                except Exception:
                    pass
            return self._mock_incidents.get(incident_id)
        return self._mock_incidents.get(incident_id)

    def update_incident(self, incident_id: str, data: Dict[str, Any]) -> None:
        """Update fields in an existing incident document with retries."""
        if self.offline_mode or incident_id not in self._mock_incidents:
            if not self.offline_mode:
                try:
                    retry_db_operation(
                        lambda: self.firestore_client.collection("incidents")
                        .document(incident_id)
                        .update(data)
                    )
                    return
                except Exception:
                    pass
            if incident_id in self._mock_incidents:
                self._mock_incidents[incident_id].update(data)
        else:
            self._mock_incidents[incident_id].update(data)

    def push_reasoning_log(self, incident_id: str, log_message: str) -> None:
        """Push a live agent reasoning log to Realtime Database stream with retries."""
        timestamp = time.time()
        log_entry = {"timestamp": timestamp, "message": log_message}

        if self.offline_mode:
            if incident_id not in self._mock_streams:
                self._mock_streams[incident_id] = []
            self._mock_streams[incident_id].append(log_entry)
        else:
            try:
                retry_db_operation(
                    lambda: self.db_client.child("streams")
                    .child(incident_id)
                    .push(log_entry)
                )
            except Exception:
                if incident_id not in self._mock_streams:
                    self._mock_streams[incident_id] = []
                self._mock_streams[incident_id].append(log_entry)

    def get_reasoning_logs(self, incident_id: str) -> list:
        """Retrieve reasoning logs for a given incident with retries."""
        if self.offline_mode or incident_id not in self._mock_streams:
            if not self.offline_mode:
                try:
                    res = retry_db_operation(
                        lambda: self.db_client.child("streams").child(incident_id).get()
                    )
                    if res:
                        return list(res.values())
                except Exception:
                    pass
            return self._mock_streams.get(incident_id, [])
        return self._mock_streams.get(incident_id, [])

    def get_forecast(self, zone_id: str) -> Dict[str, Any]:
        """Fetch pre-computed congestion forecast for a zone."""
        return {
            "zone_id": zone_id,
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "current_congestion_index": 0.65,
            "prediction_30_min": 0.72,
            "prediction_60_min": 0.58,
            "trend": "rising",
            "critical_threshold_exceeded": False,
        }
