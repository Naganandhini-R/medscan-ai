import numpy as np
from sqlalchemy.orm import Session
from app.models.scan import Scan
from datetime import datetime, timedelta
from app.core.logging import logger

class AnalyticsService:
    @staticmethod
    def detect_clone_outbreaks(
        db: Session,
        batch_id: str = None,
        manufacturer: str = None,
        medicine_name: str = None,
        hours: int = 24,
        min_scans: int = 3,
        radius_km: float = 10.0,
    ):
        """
        AI-Powered Outbreak Detection.
        Uses geospatial grouping to identify if fakes are concentrated in a specific area.
        """
        # 1. Fetch fake/suspicious scans from the last X hours
        time_threshold = datetime.utcnow() - timedelta(hours=hours)

        query = db.query(Scan).filter(
            Scan.created_at >= time_threshold,
            Scan.status.in_(["FAKE", "SUSPICIOUS"]),
            Scan.lat.isnot(None),
            Scan.lng.isnot(None),
        )

        if batch_id:
            query = query.filter(Scan.batch_id == batch_id)

        if manufacturer:
            query = query.filter(Scan.manufacturer.ilike(f"%{manufacturer}%"))

        if medicine_name:
            query = query.filter(Scan.medicine_name.ilike(f"%{medicine_name}%"))

        scans = query.all()

        if len(scans) < min_scans:
            return []

        # 2. Extract coordinates
        coords = np.array([[s.lat, s.lng] for s in scans])

        # 3. Simple Clustering Logic (Simulating K-Means/DBSCAN)
        # For a production app, we'd use sklearn.cluster.DBSCAN here.
        # We'll implement a fast distance-based grouping.
        clusters = []
        visited = set()

        for i in range(len(coords)):
            if i in visited:
                continue

            # Find all points within radius (approximate 1 degree lat = 111km)
            # 5km is roughly 0.045 degrees
            radius_deg = radius_km / 111.0

            distances = np.linalg.norm(coords - coords[i], axis=1)
            neighbor_indices = np.where(distances <= radius_deg)[0]

            if len(neighbor_indices) >= min_scans:
                cluster_scans = [scans[idx] for idx in neighbor_indices]

                # Calculate centroid
                centroid_lat = np.mean(coords[neighbor_indices, 0])
                centroid_lng = np.mean(coords[neighbor_indices, 1])

                clusters.append(
                    {
                        "id": f"outbreak_{len(clusters) + 1}",
                        "lat": centroid_lat,
                        "lng": centroid_lng,
                        "scan_count": len(cluster_scans),
                        "radius_km": radius_km,
                        "severity": (
                            "CRITICAL" if len(cluster_scans) > min_scans * 2 else "HIGH"
                        ),
                        "batch_ids": list(
                            set([s.batch_id for s in cluster_scans if s.batch_id])
                        ),
                        "medicine_names": list(
                            set(
                                [
                                    s.medicine_name
                                    for s in cluster_scans
                                    if s.medicine_name
                                ]
                            )
                        ),
                    }
                )

                for idx in neighbor_indices:
                    visited.add(idx)

        return clusters

    @staticmethod
    def get_heatmap_data(
        db: Session, manufacturer: str = None, medicine_name: str = None
    ):
        """
        Returns raw scan points for generating a heatmap on the dashboard.
        """
        query = db.query(Scan).filter(Scan.lat.isnot(None), Scan.lng.isnot(None))

        if manufacturer:
            query = query.filter(Scan.manufacturer.ilike(f"%{manufacturer}%"))

        if medicine_name:
            query = query.filter(Scan.medicine_name.ilike(f"%{medicine_name}%"))

        scans = query.all()

        return [
            {
                "lat": s.lat,
                "lng": s.lng,
                "weight": (
                    1.0
                    if s.status == "FAKE"
                    else (0.5 if s.status == "SUSPICIOUS" else 0.1)
                ),
                "status": s.status,
                "medicine": s.medicine_name,
            }
            for s in scans
        ]
