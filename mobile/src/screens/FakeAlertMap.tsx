import React, { useEffect, useState } from 'react';
import { View, StyleSheet, Text, ActivityIndicator, TouchableOpacity } from 'react-native';
import MapView, { Marker, Callout } from 'react-native-maps';
import { ArrowLeft, AlertTriangle, RefreshCw } from 'lucide-react-native';
import { useNavigation } from '@react-navigation/native';
import { getNearbyFakes } from '../services/api.service';
import { Colors } from '../theme/Colors';

export default function FakeAlertMap() {
  const navigation = useNavigation();
  const [points, setPoints] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  const CHENNAI = {
    latitude: 13.0827,
    longitude: 80.2707,
    latitudeDelta: 0.5,
    longitudeDelta: 0.5,
  };

  const loadFakes = async () => {
    setLoading(true);
    try {
      // For demo, we scan around Chennai coordinates
      const data = await getNearbyFakes(CHENNAI.latitude, CHENNAI.longitude);
      setPoints(data);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadFakes();
  }, []);

  return (
    <View style={styles.container}>
      <MapView
        style={styles.map}
        initialRegion={CHENNAI}
        customMapStyle={mapStyle}>
        {points.map((p: any, i) => (
          <Marker
            key={i}
            coordinate={{ latitude: p.lat, longitude: p.lng }}
            pinColor={Colors.error}>
            <Callout>
              <View style={styles.callout}>
                <Text style={styles.calloutTitle}>FAKE DETECTED</Text>
                <Text style={styles.calloutSub}>Score: {Math.round(p.score * 100)}% Match</Text>
                <Text style={styles.calloutLink}>View Forensic Report</Text>
              </View>
            </Callout>
          </Marker>
        ))}
      </MapView>

      <View style={styles.overlay}>
        <TouchableOpacity
          style={styles.backBtn}
          onPress={() => navigation.goBack()}>
          <ArrowLeft size={24} color="#0F172A" />
        </TouchableOpacity>

        <View style={styles.statusCard}>
          <AlertTriangle size={20} color={Colors.error} />
          <Text style={styles.statusText}>
            {loading ? 'Scanning Region...' : `${points.length} Hotspots Identified`}
          </Text>
          {loading && <ActivityIndicator size="small" color={Colors.error} style={{ marginLeft: 10 }} />}
          {!loading && (
            <TouchableOpacity onPress={loadFakes}>
              <RefreshCw size={18} color="#64748B" style={{ marginLeft: 10 }} />
            </TouchableOpacity>
          )}
        </View>
      </View>
    </View>
  );
}

const mapStyle = [
  {
    "featureType": "administrative",
    "elementType": "geometry",
    "stylers": [{ "visibility": "off" }]
  },
  {
    "featureType": "poi",
    "stylers": [{ "visibility": "off" }]
  },
  {
    "featureType": "road",
    "elementType": "labels.icon",
    "stylers": [{ "visibility": "off" }]
  },
  {
    "featureType": "transit",
    "stylers": [{ "visibility": "off" }]
  }
];

const styles = StyleSheet.create({
  container: { flex: 1 },
  map: { ...StyleSheet.absoluteFillObject },
  overlay: {
    position: 'absolute',
    top: 50,
    left: 20,
    right: 20,
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  backBtn: {
    width: 44,
    height: 44,
    borderRadius: 22,
    backgroundColor: '#FFF',
    justifyContent: 'center',
    alignItems: 'center',
    elevation: 5,
    shadowColor: '#000',
    shadowOpacity: 0.1,
    shadowRadius: 10,
  },
  statusCard: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#FFF',
    paddingHorizontal: 15,
    paddingVertical: 10,
    borderRadius: 20,
    elevation: 5,
    shadowColor: '#000',
    shadowOpacity: 0.1,
    shadowRadius: 10,
  },
  statusText: {
    marginLeft: 8,
    fontWeight: 'bold',
    color: '#0F172A',
    fontSize: 14,
  },
  callout: {
    padding: 10,
    width: 150,
  },
  calloutTitle: {
    fontWeight: 'bold',
    color: Colors.error,
    fontSize: 12,
  },
  calloutSub: {
    fontSize: 10,
    color: '#64748B',
    marginTop: 2,
  },
  calloutLink: {
    fontSize: 10,
    color: Colors.primary,
    marginTop: 5,
    fontWeight: 'bold',
  }
});
