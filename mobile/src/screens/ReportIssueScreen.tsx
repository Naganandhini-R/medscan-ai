import React, {useState, useEffect} from 'react';
import {
  View,
  Text,
  StyleSheet,
  SafeAreaView,
  TouchableOpacity,
  TextInput,
  ScrollView,
  StatusBar,
  Alert,
  ActivityIndicator,
} from 'react-native';
import {
  ArrowLeft,
  AlertTriangle,
  Send,
  Shield,
  Info,
  MapPin,
} from 'lucide-react-native';
import {Colors} from '../theme/Colors';
import {NativeStackScreenProps} from '@react-navigation/native-stack';
import {RootStackParamList} from '../navigation/types';

import {submitReport} from '../services/api.service';

type Props = NativeStackScreenProps<RootStackParamList, 'ReportIssue'>;

export default function ReportIssueScreen({route, navigation}: Props) {
  const {medicineName, batchId, scanId, manufacturer} = route.params;
  const [issueType, setIssueType] = useState('Counterfeit Suspected');
  const [description, setDescription] = useState('');
  const [location, setLocation] = useState('Detecting GPS...');
  const [loading, setLoading] = useState(false);
  const [gpsCoords, setGpsCoords] = useState({lat: 13.0827, lng: 80.2707}); // Default to Chennai for demo

  useEffect(() => {
    // Simulate GPS detection
    const timer = setTimeout(() => {
      setLocation('Pharmacy Cluster X, Zone 4 (Chennai)');
    }, 1500);
    return () => clearTimeout(timer);
  }, []);

  const handleSubmit = async () => {
    if (!description) {
      Alert.alert('Input Required', 'Please describe the issue you observed.');
      return;
    }

    setLoading(true);
    try {
      await submitReport({
        scan_id: scanId,
        medicine_name: medicineName || 'Unknown',
        batch_id: batchId || 'Unknown',
        issue_type: issueType,
        location_details: location,
        description: description,
        lat: gpsCoords.lat,
        lng: gpsCoords.lng,
        manufacturer: manufacturer,
      });

      Alert.alert(
        'Report Submitted',
        'Thank you for helping keep the community safe. The manufacturer and regulatory authorities have been notified.',
        [{text: 'OK', onPress: () => navigation.navigate('Home')}],
      );
    } catch (error) {
      console.error(error);
      Alert.alert(
        'Submission Failed',
        'Could not send report. Please try again later.',
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <SafeAreaView style={styles.container}>
      <StatusBar barStyle="dark-content" />
      <View
        style={[
          styles.header,
          issueType === 'Counterfeit Suspected' && styles.headerUrgent,
        ]}>
        <TouchableOpacity
          onPress={() => navigation.goBack()}
          style={styles.backBtn}>
          <ArrowLeft
            size={24}
            color={
              issueType === 'Counterfeit Suspected' ? '#FFF' : Colors.textHeader
            }
          />
        </TouchableOpacity>
        <Text
          style={[
            styles.title,
            issueType === 'Counterfeit Suspected' && {color: '#FFF'},
          ]}>
          Forensic Report: {batchId}
        </Text>
        <View style={{width: 40}} />
      </View>

      <ScrollView contentContainerStyle={styles.scrollContent}>
        <View
          style={[
            styles.warningBox,
            issueType === 'Counterfeit Suspected' && styles.warningBoxUrgent,
          ]}>
          <AlertTriangle
            size={24}
            color={
              issueType === 'Counterfeit Suspected' ? '#FFF' : Colors.warning
            }
          />
          <View style={styles.warningTextContainer}>
            <Text
              style={[
                styles.warningTitle,
                issueType === 'Counterfeit Suspected' && {color: '#FFF'},
              ]}>
              High Priority Case
            </Text>
            <Text
              style={[
                styles.warningSub,
                issueType === 'Counterfeit Suspected' && {color: '#FFEBEB'},
              ]}>
              Your report is anonymized and sent directly to Global Pharma
              Security and Local Regulatory Authorities.
            </Text>
          </View>
        </View>

        <View style={styles.formGroup}>
          <Text style={styles.label}>Medicine Context</Text>
          <View style={styles.disabledInput}>
            <Text style={styles.disabledText}>
              {medicineName} (Batch: {batchId})
            </Text>
          </View>
        </View>

        <View style={styles.formGroup}>
          <Text style={styles.label}>Incident Type</Text>
          <View style={styles.typeSelector}>
            {['Counterfeit Suspected', 'Banned Drug', 'Packaging Defect'].map(
              type => (
                <TouchableOpacity
                  key={type}
                  style={[
                    styles.typeBtn,
                    issueType === type && styles.typeBtnActive,
                    issueType === type &&
                      type !== 'Packaging Defect' && {
                        backgroundColor: Colors.error,
                        borderColor: Colors.error,
                      },
                  ]}
                  onPress={() => setIssueType(type)}>
                  <Text
                    style={[
                      styles.typeBtnText,
                      issueType === type && styles.typeBtnTextActive,
                    ]}>
                    {type}
                  </Text>
                </TouchableOpacity>
              ),
            )}
          </View>
        </View>

        <View style={styles.formGroup}>
          <View
            style={{
              flexDirection: 'row',
              justifyContent: 'space-between',
              alignItems: 'center',
              marginBottom: 8,
            }}>
            <Text style={styles.label}>Location of Purchase</Text>
            <View style={styles.gpsBadge}>
              <MapPin size={10} color={Colors.primary} />
              <Text style={styles.gpsText}>GPS Pre-filled</Text>
            </View>
          </View>
          <TextInput
            style={styles.input}
            value={location}
            onChangeText={setLocation}
            placeholder="Pharmacy name or street address"
          />
        </View>

        <View style={styles.formGroup}>
          <Text style={styles.label}>Observation / Forensic Details</Text>
          <TextInput
            style={[styles.input, styles.textArea]}
            value={description}
            onChangeText={setDescription}
            placeholder="e.g. Blurry logo, different font, bought at discounted price, weird smell..."
            multiline
            numberOfLines={4}
          />
        </View>

        <View style={styles.infoBox}>
          <Shield size={16} color={Colors.textSub} />
          <Text style={styles.infoText}>
            This report creates a digital footprint to help track counterfeit
            hotspots in your region.
          </Text>
        </View>

        <TouchableOpacity
          style={[
            styles.submitBtn,
            issueType === 'Counterfeit Suspected' && {
              backgroundColor: Colors.error,
            },
            loading && {opacity: 0.7},
          ]}
          onPress={handleSubmit}
          disabled={loading}>
          {loading ? (
            <ActivityIndicator color="#FFF" />
          ) : (
            <>
              <Send size={20} color="#FFF" style={{marginRight: 10}} />
              <Text style={styles.submitBtnText}>Submit Priority Report</Text>
            </>
          )}
        </TouchableOpacity>
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {flex: 1, backgroundColor: '#FFF'},
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingHorizontal: 20,
    paddingVertical: 15,
    borderBottomWidth: 1,
    borderBottomColor: '#F1F5F9',
  },
  headerUrgent: {backgroundColor: Colors.error, borderBottomWidth: 0},
  backBtn: {
    width: 40,
    height: 40,
    borderRadius: 20,
    justifyContent: 'center',
    alignItems: 'center',
  },
  title: {fontSize: 18, fontWeight: 'bold', color: Colors.textHeader},

  scrollContent: {padding: 20},
  warningBox: {
    flexDirection: 'row',
    backgroundColor: '#FFFBEB',
    padding: 15,
    borderRadius: 16,
    marginBottom: 25,
    borderWidth: 1,
    borderColor: '#FEF3C7',
  },
  warningBoxUrgent: {backgroundColor: '#7F1D1D', borderColor: '#991B1B'},
  warningTextContainer: {flex: 1, marginLeft: 12},
  warningTitle: {fontSize: 14, fontWeight: 'bold', color: '#92400E'},
  warningSub: {fontSize: 12, color: '#B45309', marginTop: 2, lineHeight: 18},

  formGroup: {marginBottom: 20},
  label: {fontSize: 14, fontWeight: '600', color: Colors.textHeader},
  input: {
    backgroundColor: '#F8FAFC',
    borderWidth: 1,
    borderColor: '#E2E8F0',
    borderRadius: 12,
    paddingHorizontal: 15,
    paddingVertical: 12,
    fontSize: 14,
    color: Colors.textHeader,
  },
  textArea: {height: 100, textAlignVertical: 'top'},
  disabledInput: {
    backgroundColor: '#F8FAFC',
    borderRadius: 12,
    padding: 14,
    borderWidth: 1,
    borderColor: '#E2E8F0',
    borderStyle: 'dashed',
  },
  disabledText: {color: Colors.textSub, fontSize: 14, fontWeight: '500'},

  typeSelector: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 10,
    marginTop: 10,
  },
  typeBtn: {
    paddingHorizontal: 15,
    paddingVertical: 10,
    borderRadius: 24,
    borderWidth: 1,
    borderColor: '#E2E8F0',
    backgroundColor: '#FFF',
  },
  typeBtnActive: {backgroundColor: Colors.primary, borderColor: Colors.primary},
  typeBtnText: {fontSize: 12, color: Colors.textSub, fontWeight: '500'},
  typeBtnTextActive: {color: '#FFF', fontWeight: 'bold'},

  gpsBadge: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#F0F9FF',
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 8,
    gap: 4,
  },
  gpsText: {fontSize: 10, color: Colors.primary, fontWeight: 'bold'},

  infoBox: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 25,
    gap: 8,
    backgroundColor: '#F8FAFC',
    padding: 12,
    borderRadius: 12,
  },
  infoText: {fontSize: 12, color: Colors.textSub, flex: 1},

  submitBtn: {
    backgroundColor: Colors.darkBlue,
    flexDirection: 'row',
    height: 60,
    borderRadius: 16,
    justifyContent: 'center',
    alignItems: 'center',
    elevation: 4,
    shadowColor: '#000',
    shadowOffset: {width: 0, height: 4},
    shadowOpacity: 0.2,
    shadowRadius: 8,
  },
  submitBtnText: {color: '#FFF', fontSize: 16, fontWeight: 'bold'},
});
