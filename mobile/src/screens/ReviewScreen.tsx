import React, { useEffect, useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  SafeAreaView,
  TouchableOpacity,
  Image,
  ScrollView,
  ActivityIndicator,
  StatusBar,
  Alert,
} from 'react-native';
import {
  ArrowLeft,
  CheckCircle2,
  AlertCircle,
  Calendar,
  Hash,
  ShieldCheck,
  ArrowRight,
  Factory,
} from 'lucide-react-native';
import LinearGradient from 'react-native-linear-gradient';
import * as Animatable from 'react-native-animatable';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { extractText } from '../services/ocr.service';
import { parseMedicineText } from '../utils/parser';
import { uploadScan } from '../services/api.service';
import { Colors } from '../theme/Colors';

import { NativeStackScreenProps } from '@react-navigation/native-stack';
import { RootStackParamList } from '../navigation/types';

type Props = NativeStackScreenProps<RootStackParamList, 'Review'>;

const OCRDetailCard = ({ icon: Icon, label, value, found }: any) => (
  <View style={[styles.detailCard, !found && styles.detailCardError]}>
    <View style={styles.detailIconBox}>
      <Icon size={20} color={found ? Colors.primary : Colors.error} />
    </View>
    <View style={styles.detailInfo}>
      <Text style={styles.detailLabel}>{label}</Text>
      <Text style={[styles.detailValue, !found && { color: Colors.error }]}>
        {found ? value : 'Detection Failed'}
      </Text>
    </View>
    {found ? (
      <CheckCircle2 size={18} color={Colors.success} />
    ) : (
      <AlertCircle size={18} color={Colors.error} />
    )}
  </View>
);

export default function ReviewScreen({ route, navigation }: Props) {
  const { images } = route.params;
  const [ocrResult, setOcrResult] = useState<any>(null);
  const [loadingOCR, setLoadingOCR] = useState(true);
  const [uploading, setUploading] = useState(false);

  useEffect(() => {
    async function runOCR() {
      try {
        setLoadingOCR(true);
        let combinedText = '';

        // Scan all available images to find the info
        const imageKeys: (keyof typeof images)[] = [
          'front',
          'back',
          'composition',
        ];
        for (const key of imageKeys) {
          const imagePath = images[key];
          if (imagePath) {
            const text = await extractText(imagePath);
            combinedText += text + '\n';
          }
        }

        const parsed = parseMedicineText(combinedText);
        setOcrResult(parsed);
      } catch (error) {
        console.error('OCR Error in Review:', error);
      } finally {
        setLoadingOCR(false);
      }
    }
    runOCR();
  }, [images]);

  const submitScan = async () => {
    setUploading(true);
    try {
      const userJson = await AsyncStorage.getItem('user');
      let userId = undefined;
      if (userJson) {
        userId = JSON.parse(userJson).id;
      }

      // Pass the extracted metadata to the backend
      const scanId = await uploadScan(images, { ...ocrResult, userId });
      navigation.navigate('Result', { scanId });
    } catch (error) {
      Alert.alert(
        'Upload Error',
        'Failed to upload scan results. Please check your connection.',
      );
    } finally {
      setUploading(false);
    }
  };

  const formatUri = (path: string) => {
    if (!path) return '';
    return path.startsWith('file://') ? path : `file://${path}`;
  };

  return (
    <SafeAreaView style={styles.container}>
      <StatusBar barStyle="dark-content" backgroundColor="#F8FAFC" />
      <ScrollView contentContainerStyle={styles.scrollContent}>
        <View style={styles.header}>
          <TouchableOpacity
            onPress={() =>
              navigation.reset({
                index: 0,
                routes: [{ name: 'Home' }, { name: 'Scan' }],
              })
            }
            style={styles.backBtn}>
            <ArrowLeft size={24} color={Colors.textHeader} />
          </TouchableOpacity>
          <Text style={styles.headerTitle}>Review Scan</Text>
          <View style={{ width: 44 }} />
        </View>

        <ScrollView
          horizontal
          showsHorizontalScrollIndicator={false}
          contentContainerStyle={styles.multiPreviewContainer}
          snapToInterval={310}
          decelerationRate="fast"
        >
          {images.front && (
            <View style={styles.previewBox}>
              <Image source={{ uri: formatUri(images.front) }} style={styles.previewImage} />
              <View style={styles.imageLabel}>
                <Text style={styles.imageLabelText}>Front View</Text>
              </View>
            </View>
          )}
          {images.back && (
            <View style={styles.previewBox}>
              <Image source={{ uri: formatUri(images.back) }} style={styles.previewImage} />
              <View style={styles.imageLabel}>
                <Text style={styles.imageLabelText}>Details View</Text>
              </View>
            </View>
          )}
          {images.composition && (
            <View style={styles.previewBox}>
              <Image source={{ uri: formatUri(images.composition) }} style={styles.previewImage} />
              <View style={styles.imageLabel}>
                <Text style={styles.imageLabelText}>Composition View</Text>
              </View>
            </View>
          )}
        </ScrollView>

        <View style={styles.infoSection}>
          <View style={styles.sectionHeader}>
            <Text style={styles.sectionTitle}>Detected Information</Text>
            <Text style={styles.sectionSub}>Verifying via AI OCR</Text>
          </View>

          {loadingOCR ? (
            <View style={styles.ocrLoading}>
              <ActivityIndicator size="large" color={Colors.primary} />
              <Text style={styles.loadingText}>Extracting details...</Text>
            </View>
          ) : (
            <Animatable.View animation="fadeIn" style={styles.detailsList}>
              <OCRDetailCard
                icon={Hash}
                label="Batch Number"
                value={ocrResult?.batchId}
                found={!!ocrResult?.batchId}
              />
              <OCRDetailCard
                icon={Calendar}
                label="Expiry Date"
                value={ocrResult?.expiryDate}
                found={
                  !!ocrResult?.expiryDate &&
                  ocrResult?.expiryDate !== 'NOT FOUND'
                }
              />
              <OCRDetailCard
                icon={Factory}
                label="Manufacturer"
                value={ocrResult?.manufacturer}
                found={
                  !!ocrResult?.manufacturer &&
                  ocrResult?.manufacturer !== 'Unknown'
                }
              />

              {!ocrResult?.batchId && (
                <View style={styles.warningBox}>
                  <AlertCircle size={16} color={Colors.error} />
                  <Text style={styles.warningText}>
                    Information not found. You can still proceed to online
                    verification.
                  </Text>
                </View>
              )}
            </Animatable.View>
          )}
        </View>

        <View style={styles.actionSection}>
          <TouchableOpacity
            style={[
              styles.verifyButton,
              (uploading || loadingOCR) && styles.btnDisabled,
            ]}
            onPress={submitScan}
            disabled={uploading || loadingOCR}>
            <LinearGradient
              colors={['#2196F3', '#0D47A1']}
              style={styles.btnGradient}
              start={{ x: 0, y: 0 }}
              end={{ x: 1, y: 0 }}>
              {uploading ? (
                <ActivityIndicator color="#FFF" />
              ) : (
                <>
                  <ShieldCheck
                    color="#FFF"
                    size={24}
                    style={{ marginRight: 10 }}
                  />
                  <Text style={styles.btnText}>Proceed to Verification</Text>
                  <ArrowRight color="#FFF" size={20} style={{ marginLeft: 10 }} />
                </>
              )}
            </LinearGradient>
          </TouchableOpacity>

          <TouchableOpacity
            style={styles.retakeBtn}
            onPress={() => navigation.navigate('Scan')}>
            <Text style={styles.retakeText}>Retake Photo</Text>
          </TouchableOpacity>
        </View>
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#F8FAFC' },
  scrollContent: { paddingBottom: 50 },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingHorizontal: 20,
    paddingVertical: 15,
  },
  backBtn: {
    width: 44,
    height: 44,
    borderRadius: 22,
    backgroundColor: '#FFF',
    justifyContent: 'center',
    alignItems: 'center',
    borderWidth: 1,
    borderColor: '#F1F5F9',
  },
  headerTitle: { fontSize: 20, fontWeight: 'bold', color: Colors.textHeader },

  multiPreviewContainer: {
    paddingHorizontal: 20,
    paddingVertical: 10,
    gap: 15,
  },
  previewBox: {
    width: 300,
    height: 200,
    borderRadius: 24,
    overflow: 'hidden',
    backgroundColor: '#000',
    elevation: 8,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.1,
    shadowRadius: 10,
  },
  previewImage: {
    width: '100%',
    height: '100%',
  },
  imageLabel: {
    position: 'absolute',
    bottom: 0,
    left: 0,
    right: 0,
    backgroundColor: 'rgba(0,0,0,0.6)',
    paddingVertical: 10,
    alignItems: 'center',
  },
  imageLabelText: {
    color: '#FFF',
    fontSize: 14,
    fontWeight: 'bold',
    letterSpacing: 1,
  },

  infoSection: { paddingHorizontal: 20, marginTop: 10 },
  sectionHeader: { marginBottom: 20 },
  sectionTitle: { fontSize: 20, fontWeight: 'bold', color: Colors.textHeader },
  sectionSub: { fontSize: 14, color: Colors.textSub, marginTop: 4 },

  ocrLoading: { padding: 40, alignItems: 'center' },
  loadingText: { marginTop: 15, fontSize: 14, color: Colors.textSub },

  detailsList: { gap: 15 },
  detailCard: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#FFF',
    padding: 16,
    borderRadius: 20,
    borderWidth: 1,
    borderColor: '#ECFDF5',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.05,
    shadowRadius: 5,
    elevation: 2,
  },
  detailCardError: { borderColor: '#FEE2E2', backgroundColor: '#FEF2F2' },
  detailIconBox: {
    width: 44,
    height: 44,
    borderRadius: 12,
    backgroundColor: '#F8FAFC',
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 15,
  },
  detailInfo: { flex: 1 },
  detailLabel: { fontSize: 12, color: Colors.textSub },
  detailValue: {
    fontSize: 16,
    fontWeight: 'bold',
    color: Colors.textHeader,
    marginTop: 2,
  },

  warningBox: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 10,
    padding: 12,
    backgroundColor: '#FFFBEB',
    borderRadius: 12,
    marginTop: 5,
  },
  warningText: { flex: 1, fontSize: 12, color: '#92400E', lineHeight: 18 },

  actionSection: { padding: 20, marginTop: 20, gap: 15 },
  verifyButton: {
    height: 60,
    borderRadius: 16,
    overflow: 'hidden',
    elevation: 4,
  },
  btnGradient: {
    flex: 1,
    flexDirection: 'row',
    justifyContent: 'center',
    alignItems: 'center',
    paddingHorizontal: 20,
  },
  btnText: { color: '#FFF', fontSize: 18, fontWeight: 'bold' },
  btnDisabled: { opacity: 0.7 },

  retakeBtn: { height: 50, justifyContent: 'center', alignItems: 'center' },
  retakeText: { color: Colors.textSub, fontSize: 16, fontWeight: '600' },
});
