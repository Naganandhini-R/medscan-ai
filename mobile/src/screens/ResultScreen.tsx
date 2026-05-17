import React, { useEffect, useState, useCallback } from 'react';
import {
  View,
  Text,
  StyleSheet,
  SafeAreaView,
  ScrollView,
  TouchableOpacity,
  StatusBar,
  Alert,
} from 'react-native';
import {
  CheckCircle2,
  Circle,
  ShieldCheck,
  AlertCircle,
  ArrowLeft,
  RefreshCw,
  Database,
  Search,
  Calendar,
  Box,
  Factory,
  ChevronRight,
  AlertTriangle,
  FileText,
  Volume2,
  Map as MapIcon,
  Archive,
  Zap,
  Cpu,
  Globe,
  Ban,
} from 'lucide-react-native';
import LinearGradient from 'react-native-linear-gradient';
import * as Animatable from 'react-native-animatable';
import Svg, { Path } from 'react-native-svg';
import Tts from 'react-native-tts';
import { getResult, ScanResult } from '../services/api.service';
import { NativeStackScreenProps } from '@react-navigation/native-stack';
import { RootStackParamList } from '../navigation/types';
import { Colors } from '../theme/Colors';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { useFocusEffect } from '@react-navigation/native';
import { translations, Language } from '../utils/translations';

type Props = NativeStackScreenProps<RootStackParamList, 'Result'>;

const Gauge = ({
  score,
  color,
  status,
  isDarkMode,
  t,
}: {
  score: number;
  color: string;
  status: string;
  isDarkMode: boolean;
  t: any;
}) => {
  const radius = 80;
  const strokeWidth = 15;
  const normalizedScore = Math.min(Math.max(score, 0), 1);
  const arcLength = Math.PI * radius;

  const statusLabel =
    status === 'GENUINE'
      ? t.genuine
      : status === 'SUSPICIOUS'
        ? t.suspicious
        : t.fake;

  return (
    <View style={styles.gaugeContainer}>
      <Svg width={200} height={120} viewBox="0 0 200 120">
        {/* Background Arc */}
        <Path
          d="M 20 100 A 80 80 0 0 1 180 100"
          fill="none"
          stroke={isDarkMode ? '#334155' : '#E2E8F0'}
          strokeWidth={strokeWidth}
          strokeLinecap="round"
        />
        {/* Progress Arc */}
        <Path
          d="M 20 100 A 80 80 0 0 1 180 100"
          fill="none"
          stroke={color}
          strokeWidth={strokeWidth}
          strokeLinecap="round"
          strokeDasharray={`${normalizedScore * (Math.PI * 80)} 500`}
        />
      </Svg>
      <View style={styles.gaugeTextContainer}>
        <Text style={[styles.gaugeStatus, { color }]}>{statusLabel}</Text>
      </View>
    </View>
  );
};

const DetailRow = ({ icon: Icon, label, value, isDarkMode }: any) => (
  <TouchableOpacity
    style={[
      styles.detailRow,
      isDarkMode && { backgroundColor: '#1E293B', borderColor: '#334155' },
    ]}>
    <View
      style={[
        styles.detailIconBox,
        isDarkMode && { backgroundColor: '#334155' },
      ]}>
      <Icon size={20} color={isDarkMode ? '#F8FAFC' : Colors.darkBlue} />
    </View>
    <View style={styles.detailInfo}>
      <Text style={[styles.detailLabel, isDarkMode && { color: '#94A3B8' }]}>
        {label}
      </Text>
      <Text style={[styles.detailValue, isDarkMode && { color: '#F8FAFC' }]}>
        {value}
      </Text>
    </View>
    <ChevronRight size={18} color={isDarkMode ? '#94A3B8' : Colors.textSub} />
  </TouchableOpacity>
);

const ProgressItem = ({ label, status, delay, isDarkMode }: any) => (
  <Animatable.View
    animation="fadeInLeft"
    delay={delay}
    style={styles.progressRow}>
    <View style={styles.iconCol}>
      {status === 'done' ? (
        <CheckCircle2
          color={isDarkMode ? Colors.success : Colors.primary}
          size={24}
        />
      ) : status === 'active' ? (
        <Animatable.View
          animation="rotate"
          iterationCount="infinite"
          duration={2000}>
          <RefreshCw
            color={isDarkMode ? Colors.success : Colors.primary}
            size={24}
          />
        </Animatable.View>
      ) : (
        <Circle color={isDarkMode ? '#334155' : '#E2E8F0'} size={24} />
      )}
    </View>
    <Text
      style={[
        styles.progressText,
        isDarkMode && { color: '#F8FAFC' },
        status === 'pending' &&
        (isDarkMode ? { color: '#475569' } : styles.pendingText),
      ]}>
      {label}
    </Text>
  </Animatable.View>
);

const SecurityCheckItem = ({
  icon: Icon,
  label,
  status,
  subtext,
  color,
}: any) => (
  <View style={styles.securityCheckItem}>
    <View style={[styles.securityIconBox, { backgroundColor: color + '15' }]}>
      <Icon size={20} color={color} />
    </View>
    <View style={{ flex: 1 }}>
      <Text style={styles.securityLabel}>{label}</Text>
      <Text style={[styles.securityStatusText, { color: color }]}>{status}</Text>
      {subtext && <Text style={styles.securitySubtext}>{subtext}</Text>}
    </View>
    {status === 'Verified' || status === 'Pass' ? (
      <CheckCircle2 size={20} color={Colors.success} />
    ) : (
      <AlertCircle size={20} color={color} />
    )}
  </View>
);

export default function ResultScreen({ route, navigation }: Props) {
  const { scanId } = route.params;
  const [result, setResult] = useState<ScanResult | null>(null);
  const [analysisStep, setAnalysisStep] = useState(0);
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [isDarkMode, setIsDarkMode] = useState(false);
  const [language, setLanguage] = useState<Language>('en');

  const t = translations[language];

  useFocusEffect(
    useCallback(() => {
      loadSettings();
    }, []),
  );

  const loadSettings = async () => {
    try {
      const savedMode = await AsyncStorage.getItem('darkMode');
      if (savedMode !== null) {
        setIsDarkMode(JSON.parse(savedMode));
      }
      const savedLang = await AsyncStorage.getItem('language');
      if (savedLang !== null) {
        setLanguage(savedLang as Language);
      }
    } catch (e) {
      console.log('Error loading settings', e);
    }
  };

  useEffect(() => {
    const interval = setInterval(() => {
      setAnalysisStep(prev => (prev < 3 ? prev + 1 : prev));
    }, 1200);

    const timer = setInterval(async () => {
      try {
        const res = await getResult(scanId);
        if (res.status !== 'PROCESSING') {
          setResult(res);
          clearInterval(timer);
          clearInterval(interval);
          setAnalysisStep(3);
        }
      } catch (error) {
        console.error(error);
      }
    }, 2000);

    return () => {
      clearInterval(timer);
      clearInterval(interval);
    };
  }, [scanId]);

  const speakResult = () => {
    if (!result) return;
    setIsSpeaking(true);
    const name = result.medicine_name || 'this medicine';

    // Red Protocol: Voice Alert
    let msg = '';
    if (result.status === 'FAKE' || result.status === 'COUNTERFEIT') {
      msg = `Result for ${name}: It is classified as FAKE. Do not consume.`;
    } else {
      msg = `Result for ${name}: It is classified as ${result.status}. ${result.expiry ? 'Expires on ' + result.expiry : ''
        }. ${result.data?.usage || ''}`;
    }

    Tts.stop();
    Tts.speak(msg);

    // Visual indicator timeout
    setTimeout(() => setIsSpeaking(false), 5000);
  };

  const addToCabinet = async () => {
    try {
      const currentCabinetStr = await AsyncStorage.getItem('cabinet');
      let currentCabinet = currentCabinetStr
        ? JSON.parse(currentCabinetStr)
        : [];

      // Check if already exists based on batch_id
      const exists = currentCabinet.find(
        (item: any) => item.id === result?.batch_id,
      );
      if (exists) {
        Alert.alert(
          'Already Added',
          'This medicine batch is already in your cabinet.',
        );
        navigation.navigate('Cabinet');
        return;
      }

      const itemToAdd = {
        id: result?.batch_id || `item_${Date.now()}`,
        name: result?.medicine_name || 'Unknown Medicine',
        brand: result?.manufacturer || 'Verified Manufacturer',
        stock: 10,
        maxStock: 10,
        expiry: result?.expiry || '2026-12-31',
        color: Colors.primary,
      };

      currentCabinet = [itemToAdd, ...currentCabinet];
      await AsyncStorage.setItem('cabinet', JSON.stringify(currentCabinet));

      Alert.alert(
        'Cabinet Updated',
        'Medicine successfully added to your AI Cabinet.',
      );
      navigation.navigate('Cabinet');
    } catch (error) {
      console.error('Failed to add to cabinet:', error);
      Alert.alert('Storage Error', 'Could not save medicine to cabinet.');
    }
  };

  if (!result || analysisStep < 3) {
    return (
      <LinearGradient
        colors={isDarkMode ? ['#0F172A', '#1E293B'] : ['#F8FAFC', '#EFF6FF']}
        style={styles.container}>
        <SafeAreaView style={styles.safeArea}>
          <StatusBar barStyle={isDarkMode ? 'light-content' : 'dark-content'} />
          <View style={styles.analyzingHeader}>
            <Animatable.View
              animation="pulse"
              iterationCount="infinite"
              style={styles.pulseContainer}>
              <Search size={40} color={Colors.primary} />
            </Animatable.View>
            <Text
              style={[styles.analyzingTitle, isDarkMode && { color: '#F8FAFC' }]}>
              {t.analyzing}
            </Text>
          </View>

          <View
            style={[
              styles.analysisCard,
              isDarkMode && {
                backgroundColor: '#1E293B',
                borderColor: '#334155',
              },
            ]}>
            <ProgressItem
              label={t.extractingDetails}
              status={analysisStep > 0 ? 'done' : 'active'}
              delay={300}
              isDarkMode={isDarkMode}
            />
            <ProgressItem
              label={t.verifyingBatch}
              status={
                analysisStep > 1
                  ? 'done'
                  : analysisStep === 1
                    ? 'active'
                    : 'pending'
              }
              delay={600}
              isDarkMode={isDarkMode}
            />
            <ProgressItem
              label={t.checkingBlockchain}
              status={
                analysisStep > 2
                  ? 'done'
                  : analysisStep === 2
                    ? 'active'
                    : 'pending'
              }
              delay={900}
              isDarkMode={isDarkMode}
            />
          </View>
        </SafeAreaView>
      </LinearGradient>
    );
  }

  const isGenuine = result.status === 'GENUINE';
  const isFake = result.status === 'FAKE' || result.status === 'COUNTERFEIT';

  // Status Logic
  let statusColor = Colors.success;
  if (result.status === 'SUSPICIOUS') statusColor = Colors.warning;
  if (isFake) statusColor = Colors.error;

  // Check for Banned Status
  const isBanned =
    result.data?.banned ||
    result.data?.status_notes?.some((n: string) =>
      n.toLowerCase().includes('banned'),
    );
  const bannedReason =
    result.data?.banned_reason || 'Harmful Side Effects - Banned by FDA';

  return (
    <SafeAreaView
      style={[
        styles.container,
        { backgroundColor: isDarkMode ? '#0F172A' : '#F8FAFC' },
      ]}>
      <StatusBar
        barStyle={isDarkMode ? 'light-content' : 'dark-content'}
        backgroundColor={isDarkMode ? '#0F172A' : '#F8FAFC'}
      />
      <ScrollView contentContainerStyle={styles.resultScroll}>
        <View style={styles.navHeader}>
          <TouchableOpacity
            onPress={() => navigation.navigate('Home')}
            style={[
              styles.backBtn,
              isDarkMode && {
                backgroundColor: '#1E293B',
                borderColor: '#334155',
              },
            ]}>
            <ArrowLeft
              color={isDarkMode ? '#F8FAFC' : Colors.textHeader}
              size={24}
            />
          </TouchableOpacity>
          <Text
            numberOfLines={1}
            style={[
              styles.navTitle,
              { flex: 1, textAlign: 'center' },
              isDarkMode && { color: '#F8FAFC' },
            ]}>
            {result?.medicine_name && result.medicine_name !== 'Unknown'
              ? result.medicine_name
              : t.forensicScan}
          </Text>
          <TouchableOpacity
            onPress={speakResult}
            style={[
              styles.speakerBtn,
              isSpeaking && styles.speakerActive,
              isDarkMode && {
                backgroundColor: isSpeaking ? Colors.primary : '#1E293B',
              },
            ]}>
            <Volume2
              size={24}
              color={
                isSpeaking ? '#FFF' : isDarkMode ? '#F8FAFC' : Colors.primary
              }
            />
          </TouchableOpacity>
        </View>

        {/* Status Gauge */}
        <View style={styles.gaugeSection}>
          <Gauge
            score={result.score}
            color={statusColor}
            status={result.status}
            isDarkMode={isDarkMode}
            t={t}
          />
        </View>

        {/* Government Banned Check */}
        {isBanned && (
          <Animatable.View
            animation="pulse"
            iterationCount="infinite"
            style={styles.bannedCard}>
            <Ban size={24} color="#FFF" />
            <View style={{ flex: 1 }}>
              <Text style={styles.bannedTitle}>FOUND IN BANNED LIST</Text>
              <Text style={styles.bannedDesc}>{bannedReason}</Text>
            </View>
          </Animatable.View>
        )}

        {/* Alert Card for Registry Gap / Fake */}
        {!result.blockchain_valid && !isGenuine && (
          <Animatable.View
            animation="shake"
            iterationCount={1}
            style={styles.alertCard}>
            <AlertTriangle size={24} color="#FFF" />
            <View style={{ flex: 1 }}>
              <Text style={styles.alertTitle}>
                {isFake ? 'Counterfeit Risk' : 'Registry Gap Detected'}
              </Text>
              <Text style={styles.alertDesc}>
                {isFake
                  ? 'This product has been flagged as fake. Do not consume.'
                  : 'This batch number was not registered by the official manufacturer. High risk of counterfeit.'}
              </Text>
            </View>
          </Animatable.View>
        )}

        <View
          style={[
            styles.detailsCard,
            isDarkMode && { backgroundColor: '#1E293B', borderColor: '#334155' },
          ]}>
          <DetailRow
            icon={Calendar}
            label={t.expiryDate}
            value={result.expiry || 'Unknown'}
            isDarkMode={isDarkMode}
          />
          <View
            style={[
              styles.rowDivider,
              isDarkMode && { backgroundColor: '#334155' },
            ]}
          />
          <DetailRow
            icon={Box}
            label={t.batchNo}
            value={result.batch_id || 'Unknown'}
            isDarkMode={isDarkMode}
          />
          <View
            style={[
              styles.rowDivider,
              isDarkMode && { backgroundColor: '#334155' },
            ]}
          />
          <DetailRow
            icon={Factory}
            label={t.manufacturer}
            value={result.manufacturer || 'Unknown'}
            isDarkMode={isDarkMode}
          />
        </View>

        <View
          style={[
            styles.securityCard,
            isDarkMode && { backgroundColor: '#1E293B', borderColor: '#334155' },
          ]}>
          <View style={styles.securityHeader}>
            <ShieldCheck
              size={20}
              color={isDarkMode ? '#60A5FA' : Colors.primary}
            />
            <Text
              style={[styles.securityTitle, isDarkMode && { color: '#F8FAFC' }]}>
              {t.securityBreakdown}
            </Text>
          </View>

          {/* Red Protocol: AI Vision Check */}
          <SecurityCheckItem
            icon={Cpu}
            label={t.aiVision}
            status={result.score > 0.8 ? t.pass : t.fail}
            subtext={
              result.score > 0.8
                ? 'Packaging matches original'
                : 'Packaging does not match original'
            }
            color={result.score > 0.8 ? Colors.success : Colors.error}
            isDarkMode={isDarkMode}
          />
          <View
            style={[
              styles.securityDivider,
              isDarkMode && { backgroundColor: '#334155' },
            ]}
          />

          {/* Red Protocol: Blockchain Check */}
          <SecurityCheckItem
            icon={Database}
            label={t.blockchain}
            status={result.blockchain_valid ? t.verified : t.unlinked}
            subtext={
              result.blockchain_valid
                ? 'Manufacturer batch signature valid'
                : 'Manufacturer has not created this batch'
            }
            color={result.blockchain_valid ? Colors.success : Colors.error}
            isDarkMode={isDarkMode}
          />
          <View
            style={[
              styles.securityDivider,
              isDarkMode && { backgroundColor: '#334155' },
            ]}
          />

          <SecurityCheckItem
            icon={Globe}
            label={t.pharmaNetwork}
            status={
              result.blockchain_valid || result.status === 'GENUINE' ? t.verified : t.connecting
            }
            subtext={
              result.data?.verification_source ||
              'Direct Manufacturer Authentication'
            }
            color={result.blockchain_valid || result.status === 'GENUINE' ? Colors.success : Colors.primary}
            isDarkMode={isDarkMode}
          />
        </View>

        {result.data?.status_notes?.length > 0 && (
          <View
            style={[
              styles.notesContainer,
              isDarkMode && {
                backgroundColor: '#1E293B',
                borderColor: '#334155',
              },
            ]}>
            {result.data.status_notes.map((note: string, idx: number) => (
              <View key={idx} style={styles.noteRow}>
                <CheckCircle2
                  size={14}
                  color={Colors.success}
                  style={{ marginTop: 2 }}
                />
                <Text
                  style={[styles.noteText, isDarkMode && { color: '#94A3B8' }]}>
                  {note}
                </Text>
              </View>
            ))}
          </View>
        )}

        <View style={styles.actionRow}>
          <TouchableOpacity
            style={[styles.reportBtn, isFake && styles.reportBtnLarge]}
            onPress={() =>
              navigation.navigate('ReportIssue', {
                medicineName: result.medicine_name || 'Unknown',
                batchId: result.batch_id || 'Unknown',
                scanId: scanId,
                manufacturer: result.manufacturer,
              })
            }>
            <AlertTriangle size={20} color="#FFF" />
            <Text style={styles.reportText}>Report Issue</Text>
          </TouchableOpacity>
          {!isFake && (
            <TouchableOpacity style={styles.cabinetBtn} onPress={addToCabinet}>
              <Archive size={20} color="#FFF" />
              <Text style={styles.cabinetText}>Add to Cabinet</Text>
            </TouchableOpacity>
          )}
        </View>

        {/* Safety Intervention Section */}
        <View style={styles.safetySection}>
          <View style={styles.safetyHeader}>
            <ShieldCheck
              size={20}
              color={isFake ? Colors.error : Colors.primary}
            />
            <Text style={[styles.safetyTitle, isFake && { color: Colors.error }]}>
              {isFake ? 'Safety Intervention' : 'Safety Check Breakdown'}
            </Text>
          </View>
          <View style={[styles.safetyCard, isFake && styles.safetyCardFake]}>
            {/* Dosage Warning */}
            <View style={styles.safetyItem}>
              <View
                style={[
                  styles.safetyIndicator,
                  { backgroundColor: isFake ? Colors.error : Colors.primary },
                ]}
              />
              <View style={{ flex: 1 }}>
                <Text style={styles.safetyLabel}>
                  {isFake ? 'Dosage / Usage:' : 'Chemical Content (Salt):'}
                </Text>
                <Text
                  style={[styles.safetyValue, isFake && styles.criticalText]}>
                  {isFake
                    ? 'DO NOT USE'
                    : result.data?.salt || 'Standard Formulation'}
                </Text>
              </View>
            </View>

            <View style={styles.safetyItem}>
              <View
                style={[
                  styles.safetyIndicator,
                  { backgroundColor: isGenuine ? Colors.success : Colors.error },
                ]}
              />
              <View style={{ flex: 1 }}>
                <Text style={styles.safetyLabel}>Side Effects:</Text>
                <Text
                  style={[styles.safetyValue, isFake && styles.criticalText]}>
                  {isFake
                    ? 'CRITICAL: Suspected Counterfeit - Health Risk'
                    : result.data?.side_effects ||
                    'No specific side effects reported.'}
                </Text>
              </View>
            </View>

            {!isFake && (
              <View style={styles.safetyItem}>
                <View
                  style={[
                    styles.safetyIndicator,
                    { backgroundColor: Colors.warning },
                  ]}
                />
                <View style={{ flex: 1 }}>
                  <Text style={styles.safetyLabel}>Storage Instructions:</Text>
                  <Text style={styles.safetyValue}>
                    {result.data?.storage || 'Store in a cool, dry place.'}
                  </Text>
                </View>
              </View>
            )}
          </View>
        </View>
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#F8FAFC' },
  safeArea: { flex: 1, justifyContent: 'center', padding: 30 },
  analyzingHeader: { alignItems: 'center', marginBottom: 50 },
  pulseContainer: {
    width: 100,
    height: 100,
    borderRadius: 50,
    backgroundColor: '#EFF6FF',
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 20,
  },
  analyzingTitle: { fontSize: 24, fontWeight: 'bold', color: Colors.textHeader },
  analysisCard: {
    backgroundColor: '#FFF',
    borderRadius: 24,
    padding: 24,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 10 },
    shadowOpacity: 0.1,
    shadowRadius: 20,
    elevation: 5,
  },
  progressRow: { flexDirection: 'row', alignItems: 'center', marginBottom: 20 },
  iconCol: { width: 40 },
  progressText: { fontSize: 16, fontWeight: '600', color: Colors.textHeader },
  pendingText: { color: Colors.textSub, fontWeight: '400' },

  resultScroll: { padding: 20, paddingBottom: 50 },
  navHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 20,
  },
  backBtn: {
    width: 40,
    height: 40,
    borderRadius: 20,
    backgroundColor: '#FFF',
    justifyContent: 'center',
    alignItems: 'center',
  },
  navTitle: { fontSize: 20, fontWeight: 'bold', color: Colors.textHeader },
  speakerBtn: {
    width: 44,
    height: 44,
    borderRadius: 22,
    backgroundColor: '#EFF6FF',
    justifyContent: 'center',
    alignItems: 'center',
  },
  speakerActive: { backgroundColor: Colors.primary },

  gaugeSection: { alignItems: 'center', marginBottom: 20 },
  gaugeContainer: {
    width: 200,
    height: 120,
    alignItems: 'center',
    position: 'relative',
  },
  gaugeTextContainer: { position: 'absolute', bottom: 10, alignItems: 'center' },
  gaugeStatus: { fontSize: 18, fontWeight: 'bold', textTransform: 'uppercase' },

  detailsCard: {
    backgroundColor: '#FFF',
    borderRadius: 20,
    padding: 10,
    marginBottom: 16,
    borderWidth: 1,
    borderColor: '#F1F5F9',
  },
  detailRow: { flexDirection: 'row', alignItems: 'center', padding: 15 },
  detailIconBox: {
    width: 40,
    height: 40,
    borderRadius: 10,
    backgroundColor: '#EFF6FF',
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
  rowDivider: { height: 1, backgroundColor: '#F1F5F9', marginHorizontal: 15 },

  notesContainer: {
    backgroundColor: '#FFF',
    padding: 12,
    borderRadius: 12,
    marginBottom: 15,
    borderWidth: 1,
    borderColor: '#F1F5F9',
    borderLeftWidth: 4,
    borderLeftColor: Colors.success,
    marginHorizontal: 5,
  },
  noteRow: { flexDirection: 'row', gap: 8, marginBottom: 8 },
  noteText: {
    fontSize: 13,
    color: Colors.textHeader,
    fontWeight: '500',
    flex: 1,
  },
  securityCard: {
    backgroundColor: '#FFF',
    borderRadius: 20,
    padding: 20,
    marginBottom: 20,
    borderWidth: 1,
    borderColor: '#F1F5F9',
  },
  securityHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 10,
    marginBottom: 20,
  },
  securityTitle: { fontSize: 16, fontWeight: 'bold', color: Colors.textHeader },
  securityCheckItem: { flexDirection: 'row', alignItems: 'center', gap: 15 },
  securityIconBox: {
    width: 40,
    height: 40,
    borderRadius: 10,
    justifyContent: 'center',
    alignItems: 'center',
  },
  securityLabel: { fontSize: 12, color: Colors.textSub, fontWeight: '600' },
  securityStatusText: {
    fontSize: 15,
    fontWeight: 'bold',
    color: Colors.textHeader,
    marginTop: 1,
  },
  securitySubtext: { fontSize: 11, color: Colors.textSub, marginTop: 2 },
  securityDivider: { height: 1, backgroundColor: '#F1F5F9', marginVertical: 15 },

  alertCard: {
    backgroundColor: Colors.error,
    borderRadius: 16,
    padding: 16,
    flexDirection: 'row',
    gap: 12,
    marginBottom: 25,
    borderWidth: 2,
    borderColor: '#FEF2F2',
  },
  alertTitle: { color: '#FFF', fontSize: 16, fontWeight: 'bold' },
  alertDesc: { color: '#FFDADA', fontSize: 12, marginTop: 4, lineHeight: 18 },

  bannedCard: {
    backgroundColor: '#7F1D1D',
    borderRadius: 16,
    padding: 16,
    flexDirection: 'row',
    gap: 12,
    marginBottom: 25,
    borderWidth: 2,
    borderColor: '#991B1B',
  },
  bannedTitle: { color: '#FFF', fontSize: 16, fontWeight: 'bold' },
  bannedDesc: { color: '#FCA5A5', fontSize: 12, marginTop: 4 },

  actionRow: { flexDirection: 'row', gap: 15, marginBottom: 30 },
  reportBtn: {
    flex: 1,
    height: 56,
    backgroundColor: Colors.error,
    borderRadius: 16,
    flexDirection: 'row',
    justifyContent: 'center',
    alignItems: 'center',
    gap: 8,
  },
  reportBtnLarge: {
    flex: 1,
    height: 56,
    backgroundColor: Colors.error,
    borderRadius: 16,
    flexDirection: 'row',
    justifyContent: 'center',
    alignItems: 'center',
    gap: 8,
  },
  reportText: { color: '#FFF', fontSize: 16, fontWeight: 'bold' },
  cabinetBtn: {
    flex: 1,
    height: 56,
    backgroundColor: Colors.darkBlue,
    borderRadius: 16,
    flexDirection: 'row',
    justifyContent: 'center',
    alignItems: 'center',
    gap: 8,
  },
  cabinetText: { color: '#FFF', fontSize: 16, fontWeight: 'bold' },

  safetySection: { marginTop: 10 },
  safetyHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 10,
    marginBottom: 15,
  },
  safetyTitle: { fontSize: 18, fontWeight: 'bold', color: Colors.textHeader },
  safetyCard: { backgroundColor: '#FFF', borderRadius: 20, padding: 20, gap: 20 },
  safetyCardFake: {
    backgroundColor: '#FEF2F2',
    borderColor: '#FCA5A5',
    borderWidth: 1,
  },
  safetyItem: { flexDirection: 'row', gap: 15 },
  safetyIndicator: { width: 8, height: 8, borderRadius: 4, marginTop: 6 },
  safetyLabel: { fontSize: 14, fontWeight: 'bold', color: Colors.textHeader },
  safetyValue: { fontSize: 12, color: Colors.textSub, marginTop: 2 },
  criticalText: { color: Colors.error, fontWeight: 'bold' },
});
